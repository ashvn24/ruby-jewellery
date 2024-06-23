from django.shortcuts import render, redirect
# from .models import CustomUser
from django.contrib import  auth,messages
from shop.models import *
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser
from shop.models import category,main_category,product,section,add_description,product_images,sub_category
from django.views.decorators.cache import cache_control,never_cache
from django.contrib.auth.decorators import login_required,user_passes_test
import smtplib
import secrets
from django.core.paginator import Paginator
from django.conf import settings
from cart.cart import Cart
from decimal import Decimal
from django.db.models import F,Q
from django.contrib import  messages
from datetime import date, datetime, timedelta
import time    
import openpyxl
from openpyxl.styles import Alignment
from django.http import HttpResponse


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def loginpage(request):
    if 'email' in request.session:
        # User is already authenticated and has an active session, so redirect to the desired page
        return redirect('index')# Replace 'index' with the URL name of your desired page
    
    maincategory = main_category.objects.all().order_by('id')
    context = {
        'maincategory': maincategory,
    }

    return render(request, 'main/loginpage.html', context)


@never_cache
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password1']
        full_name = request.POST.get('full_name', '')
        password2 = request.POST.get('password2')
        
        if not email or not full_name or not password or not password2:
            messages.error(request, 'Please input all the details to register')
            return redirect('login')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('login')
        
        if not validate_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return redirect('login')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already taken.')
            return redirect('login')
        
        otp, expiration_time = generate_otp()  # Generate OTP and expiration time
        sender_email = "ashwinvk77@gmail.com"
        receiver_mail = email
        password = "ktsg khti mimn zphi"
        
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_mail, otp)
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return redirect('login')
        
        user = CustomUser.objects.create_user(email=email, password=password, full_name=full_name)
        user.save()
        
        request.session['email'] = email
        request.session['otp'] = otp
        request.session['otp_expiration_time'] = expiration_time  # Store expiration time in session
        return redirect('verify_signup')
    
    return render(request, 'loginpage.html')


def resend_otp(request):
    if request.method == 'POST':
        email = request.session.get('email')
        if email:
            otp, expiration_time = generate_otp()  # Generate a new OTP and expiration time
            sender_email = "ashwinvk77@gmail.com"
            receiver_mail = email
            password = "ktsg khti mimn zphi"

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_mail, otp)
            except smtplib.SMTPAuthenticationError:
                print( 'Failed to send OTP email. Please check your email configuration.')
                return redirect('login')

            # Update the session with the new OTP and expiration time
            request.session['otp'] = otp
            request.session['otp_expiration_time'] = expiration_time
            return redirect('verify_signup')
            
        else:
            print( 'Email not found in the session.')
    
    # Redirect back to the login page
    return redirect('login')
                

def generate_otp(length=6, expiry_time=60):
    current_time = int(time.time())
    expiration_time = current_time + expiry_time
    otp = ''.join(secrets.choice("0123456789") for i in range(length))
    return otp, expiration_time
        
        
def validate_email(email):
    return '@' in email and '.' in email

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def verify_signup(request):
    if request.method == "POST":
        user = CustomUser.objects.get(email=request.session['email'])
        x = request.session.get('otp')
        otp = request.POST['otp']
        otp_expiration_time = request.session.get('otp_expiration_time')
        
        if int(time.time()) <= otp_expiration_time:
            if otp == x:
                user.is_verified = True
                user.save()
                del request.session['email']
                del request.session['otp']
                del request.session['otp_expiration_time']
                
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                device_id = request.COOKIES.get('device_id')
                response = redirect('index')
                response.delete_cookie('device_id')
                return response
            else:
                user.delete()
                # messages.info(request, "Invalid OTP")
                del request.session['email']
                return redirect('login')
        else:
            user.delete()
            # messages.info(request, "OTP has expired")
            del request.session['email']
            return redirect('login')
    
    return render(request, 'main/verify_otp.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def log(request):
    if 'email' in request.session:
        return redirect('index')
    if request.method == 'POST':
            login_email = request.POST['emaillog']
            login_password = request.POST['pswdlog']

            if not login_email and not login_password:  # Check if both username and password are blank
                messages.error(request, "Please enter a email and password.")
                return redirect('login')
            user = auth.authenticate(request, email=login_email, password=login_password, backend='django.contrib.auth.backends.ModelBackend')
            

            if user is not None:
                cart_item_db=cartitem.objects.filter(user=user)
                cart=Cart(request)
                for cart_item in cart_item_db:
                    product=cart_item.product_name
                    quantity=cart_item.quantity
                    cart.add(product,quantity=quantity)
                cart_item_db.delete()
                auth.login(request, user)
                request.session['email'] =  login_email
                
                return redirect('index')  # Redirect to the dashboard page after successful login
            else:
                
                messages.error(request, 'Invalid email or password.')
                return redirect('login')

    return render(request, 'main/loginpage.html')

@never_cache    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def logoutPage(request):
    if 'email' in request.session:
        cart_data=request.session.get(settings.CART_SESSION_ID,{})
        user=request.user
        for product_id,cart_item in cart_data.items():
            Product=product.objects.get(id=cart_item['product_id'])
            quantity=cart_item['quantity']
            cart_item_db,created=cartitem.objects.get_or_create(user=user,product_name=Product,defaults={'quantity':quantity})
            if not created:
                cart_item_db.quantity+=quantity
                cart_item_db.save()
        request.session.flush()
                
            
        
    logout(request)
    return redirect('login')

@user_passes_test(lambda u: u.is_staff, login_url='login')
@login_required(login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def admin(request):
    users=CustomUser.objects.all()
    notification=Notification.objects.all().order_by('-id')
    order=Order.objects.filter(status__in=['delivered', 'completed'])
    total_order=0
    total_revenue=0
    total_user=0
    for ord in order:
        total_order+=1
        total_revenue+=float(ord.amount)
    for usr in users:
        total_user+=1
    
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)

    if year is None:
        current_date = datetime.now()
        year = current_date.year
    else:
        year = int(year)

    if month is None:
        current_date = datetime.now()
        month = current_date.month
    else:
        month = int(month)

        
    first_day = date(int(year), int(month), 1)
    last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    orders_by_week = []
    current_week_start = first_day
    week_number = 1

    while current_week_start <= last_day:
        current_week_end = current_week_start + timedelta(days=6)

        # Count the number of orders for the current week
        week_orders_count = Order.objects.filter(date__range=(current_week_start, current_week_end),status__in=['delivered', 'completed']).count()

        # Append the week's orders count to the result list
        orders_by_week.append(week_orders_count)

        # Move to the next week
        current_week_start = current_week_end + timedelta(days=1)
        week_number += 1
    context={
        'order':order,
        'total_user':total_user,
        'total_order':total_order,
        'total_revenue':total_revenue,
        'notification':notification,
        'users':users,
        'orders_by_week': orders_by_week,
        'month':month,
    }
    return render(request,'admin/index1.html',context)


def sale_report(request):
    
    
    from io import BytesIO
    if request.method == 'POST':
        # Retrieve the date data from the POST request
        from_date = request.POST.get('fromDate')
        to_date = request.POST.get('toDate')
    
    start_date = from_date
    end_date = to_date

    # Query the Order objects within the specified date range and with 'completed' or 'delivered' status
    orders = Order.objects.filter(
        Q(status='completed') | Q(status='delivered'),
        date__gte=start_date,
        date__lte=end_date,
    )

    # Create an Excel workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Add headers to the worksheet
    headers = [
        "User",
        "Product",
        "Amount",
        "Payment Type",
        "Quantity",
        "Date",
    ]
    worksheet.append(headers)

    # Populate the worksheet with order details
    for order in orders:
        user_data = f"{order.user.first_name} ({order.user.email})"
        product_data = f"{order.product.product_name} " if order.product else ""
        amount_data = float(order.amount) if order.amount else 0.0
        payment_type_data = order.payment_type
        quantity_data = str(order.quantity) if isinstance(order.quantity, int) else ""
        date_data = order.date.strftime("%D/%M/%Y") if order.date else ""
        row_data = [
            user_data,
            product_data,
            amount_data,
            payment_type_data,
            quantity_data,
            date_data,
        ]
        worksheet.append(row_data)

    for cell in worksheet.iter_rows(min_row=2, min_col=3, max_col=3):
        for cell in cell:
            cell.number_format = "#,##0.00"
    # Customize column widths and alignment
    for column in worksheet.columns:
        max_length = 0
        column_name = column[0].column_letter
        for cell in column:
            try:
                value = cell.value
                cell.alignment = Alignment(wrap_text=True)
                if value is not None and len(str(value)) > max_length:
                    max_length = len(str(value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column_name].width = adjusted_width
        for cell in column:
            cell.alignment = Alignment(wrapText=True)

    # Create a response to return the Excel file for download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=order_details.xlsx'
    workbook.save(response)
    return response

    

@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def admin_logout(request):
    if 'login' in request.session:
        del request.session['login']
        auth.logout(request)
    return redirect('logout')


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def admin_users(request):
        users = CustomUser.objects.filter(is_staff= False)
        page=Paginator(users,10)
        page_number = request.GET.get('page')
        users = page.get_page(page_number)
        context = {
                'users': users,
            }
        return render(request,'admin/pages/tables/bas.html',context)

@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)    
def categoryc(request):
    maincategory=main_category.objects.all().order_by('id')
    
    context={
        'maincategory':maincategory,
    }
    
    return render(request,'admin/pages/tables/category.html',context)


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def products(request):
    prod=product.objects.all().order_by('-id')
    page=Paginator(prod,8)
    page_number = request.GET.get('page')
    prod = page.get_page(page_number)
    context={
        'prod':prod,
    }
    return render(request,'admin/pages/tables/products.html',context)


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def edit_user(request,id):
    users = CustomUser.objects.filter(id=id)
    context = {
                'users': users,
            }
    
    return render(request,'admin/pages/tables/edit_user.html',context)


def block_user(request,id):
    user=CustomUser.objects.get(id=id)
    
    user.is_active=False
    user.save()
    return redirect('admin_users')

def unblock_user(request,id):
    user=CustomUser.objects.get(id=id)
    
    user.is_active=True
    user.save()
    return redirect('admin_users')


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def edit_main_category(request,id):
    maincategory=main_category.objects.filter(id=id)
    context={
        'maincategory':maincategory,
    }
    return render(request,'admin/pages/tables/edit_main_category.html',context)


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def update_main_category(request,id):
    maincategory=main_category.objects.get(id=id)
    if request.method == "POST":
    
        name=request.POST.get('name')
        maincategory.name=name
        maincategory.save()
        return redirect('category')
    else:
        context={
            'maincategory':maincategory,
        }
    return render(request,'admin/pages/tables/edit_main_category.html',context)


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def add_main_category(request):
    if request.method=="POST":
        name=request.POST.get('name')
        cat=main_category.objects.create(name=name)
        return redirect('category')
    return render(request,'admin/pages/tables/add_main_category.html')

def delete_main_category(request,id):
    cat=main_category.objects.get(id=id)
    cat.delete()
    return redirect('category')

@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def edit_category(request,id):
    categ=category.objects.get(id=id)
    print(categ)
    context={
        'categ':categ,
    }

    return render(request,'admin/pages/tables/edit_category.html',{'categ':categ})

def delete_category(request,id):
    cat = category.objects.get(id=id).delete()
    return redirect('category')


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def add_category(request):
    maincategory=main_category.objects.all()
    context={
        'maincategory':maincategory
    }
    if request.method=='POST':
        mcat=request.POST.get('categories')
        cat=request.POST.get('name')
        main=main_category.objects.get(id=mcat)
        add=category.objects.create(maincat=main,name=cat)
        return redirect('category')
    return render(request,'admin/pages/tables/add_category.html',context)

def update_category(request,id):
    categ=category.objects.get(id=id)
    if request.method=="POST":
        categ.name=request.POST.get('name')
        categ.save()
        return redirect('category')
    else:
        return render(request,'admin/pages/tables/edit_category.html',{'categ':categ})
        


def edit_subcategory(request,id):
    sub=sub_category.objects.get(id=id)
    
    print(sub)
    context={
        'sub':sub
    }
    return render(request,'admin/pages/tables/edit_subcategory.html',{'sub':sub})

def delete_subcategory(request,id):
    cat = sub_category.objects.get(id=id).delete()
    return redirect('category')

def add_subcategory(request):
    cat=category.objects.all()
    context={
        'cat':cat
    }
    return render(request,'admin/pages/tables/add_subcategory.html',context)

def update_sub(request,id):
    sub=sub_category.objects.get(id=id)
    if request.method=="POST":
        sub.name=request.POST.get('name')
        sub.save()
        return redirect('category')
    return render(request,'admin/pages/tables/edit_subcategory.html',{'sub':sub})


@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def edit_products(request,id):
    sub=sub_category.objects.all()
    cat=main_category.objects.all()
    sec=section.objects.all()
    prod=product.objects.filter(id=id)
    print(prod)
    context={
        'sub':sub,
        'prod':prod,
        'cat':cat,
        'sec':sec
    }
    return render(request,'admin/pages/tables/edit_product.html',context)



def add_product(request):
    sub=sub_category.objects.all()
    cat=main_category.objects.all()
    sec=section.objects.all()
    context={
        'sub':sub,
        'cat':cat,
        'sec':sec
    }
    
    if request.method == 'POST':
        
        product_name = request.POST['product_name']
        price = request.POST['price']
        quantity = request.POST['quantity']
        product_image = request.FILES['product_image']
        categories = request.POST['categories']
        Section = request.POST['section']
        product_information = request.POST['product_information'] 
        images = request.FILES.getlist('images')  
        print('---------------------------------',product_image)
        sec=section.objects.get(id=Section)
        c=sub_category.objects.get(id=categories)
        print(c)
        
        # Create a new product instance and save it
        new_product = product.objects.create(
            stock=quantity,
            product_name=product_name,
            price=price,
            product_information=product_information,
            categories=c,
            section=sec,
            product_image=product_image,
        )

        
        for image in images:
            product_images.objects.create(product=new_product,images=image)

        # Create a new product description
        Add_description = request.POST['add_description']
        add_description.objects.create(product=new_product, add_description=Add_description)

       
        return redirect('products')  

    return render(request,'admin/pages/tables/add_products.html',context)

def delete_product(request,id):
    prd=product.objects.get(id=id)
    prd.is_deleted=True
    prd.save()
    return redirect('products')

def undo_delete_product(request,id):
    prd=product.objects.get(id=id)
    prd.is_deleted=False
    prd.save()
    return redirect('products')

def view_more(request,id):
    cat=main_category.objects.all()
    sec=section.objects.all()
    prod=product.objects.filter(id=id)
    print(prod)
    context={
        'prod':prod,
        'cat':cat,
        'sec':sec
    }
    return render(request,'admin/pages/tables/view_more.html',context)

def update_product(request,id):
    cat = category.objects.all()
    sec = section.objects.all()
    pro=product.objects.get(id=id)
    if request.method=='POST':
        pro.stock = request.POST['quantity']
        pro.product_name = request.POST['product_name']
        pro.price = request.POST['price']
        if 'product_image' in request.FILES:
            pro.product_image = request.FILES['product_image']
        category_id = request.POST['categories']
        print(category_id)
        section_id = request.POST['section']
        images = request.FILES.getlist('images')

        s = section.objects.get(id=section_id)
        c = sub_category.objects.get(id=category_id)
        pro.categories=c
        pro.section=s
        pro.save()
        if images:
            for img in images:
                product_image = product_images(product=pro)
                product_image.images = img
                product_image.save()
         
        return redirect('products')
    else:
        context={
            'pro':pro,
            'cat': cat,
            'sec': sec
        }
    return render(request, 'admin/pages/tables/view_more.html', context)



    
    
def all_orders(request):
    orders = Order.objects.all().order_by('-date')
    page=Paginator(orders,6)
    page_number = request.GET.get('page')
    orders = page.get_page(page_number)
    context={
        'orders':orders
    }
    
    return render(request,'admin/pages/tables/all_orders.html',context)

def view_order(request,id):
    orders = Order.objects.filter(id=id)

    order_items= OrderItem.objects.filter(order=id)
    total_price = Decimal(0)

    for item in order_items:
        item_total = item.product.price * item.quantity
        total_price += item_total
    
    
    context={
        'orders':orders,
        'total_price':total_price,
    }
    return render(request,'admin/pages/tables/order_detail.html',context)


def update_order(request,id):
    order = Order.objects.get(id=id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        return redirect('all_orders')
    return render(request,'admin/pages/tables/all_orders.html',{'order':order})
        

@user_passes_test(lambda u: u.is_staff, login_url='login')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def coupons(request):
    coupons=coupon.objects.all()
    today = timezone.now().date()
    for cpn in coupons:
        if cpn.end_date <= today:
            cpn.is_active = False
            cpn.save()        
    return render(request,'admin/pages/tables/coupon.html',{'coupons':coupons})

def add_coupons(request):
    if request.method == 'POST':
        code = request.POST['coupon-code']
        discount = request.POST['discount']
        start = request.POST['start']
        end = request.POST['end']

        # Check if the coupon code already exists
        existing_coupon = coupon.objects.filter(code=code).first()
        if existing_coupon:
            messages.error(request,"copoun code already exists")
            return redirect('coupon')
        # If the coupon code doesn't exist, create a new coupon
        new_coupon = coupon(
            code=code,
            discount=discount,
            start_date=start,
            end_date=end
        )
        new_coupon.save()

        return redirect('coupon')
    
def couponactivate(request, id):   
    Coupon = coupon.objects.get(id=id)   
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'active':
            Coupon.is_active = True
            Coupon.save()
        elif action == 'nonactive':
            Coupon.is_active = False
            Coupon.save()  
        return redirect('coupon')
     