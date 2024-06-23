from datetime import date, timedelta
from django.shortcuts import render,redirect
from shop.models import *
from user.models import CustomUser
from django.contrib import  auth,messages
from django.views.decorators.cache import cache_control,never_cache
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import F, Q
import razorpay 
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.contrib.auth.models import AnonymousUser
from guest_user.decorators import allow_guest_user

# Create your views here.


@never_cache
def home(request):
    
    maincategory=main_category.objects.all().order_by('id')
    prod=product.objects.filter(section__name='New products',is_deleted=False)
    context={
        'maincategory':maincategory,
        'prod':prod
    }
    
    return render(request,'main/home.html',context)

@allow_guest_user
def shop(request):
   
    maincategory=main_category.objects.all().order_by('id')
    
    
    sub=sub_category.objects.values('name').distinct()

    cat=category.objects.values('name').distinct()
    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        wish= wishlist.objects.filter(user=device_id).values('product')
    else:
        wish= wishlist.objects.filter(user=request.user).values('product')
    
    gender = request.GET.get('gender', None)
    type=request.GET.get('material', None)
    # cat=request.GET.get('category',None)
    user_input_search = request.GET.get('product')
    selected_sorting = request.GET.get('sort', 'Position')
    
    if gender:
        desired_main_category = main_category.objects.get(id=gender)
        prod= product.objects.filter(categories__category__maincat__name=desired_main_category,is_deleted=False)
    elif type:
        gold_categories = category.objects.filter(name__icontains=type)
        prod = product.objects.filter(categories__category__in=gold_categories,is_deleted=False)
    elif user_input_search:
        user_input_search = user_input_search.strip()
        pdt_container=product.objects.filter(product_name__icontains=user_input_search,is_deleted=False).order_by('id')
        if pdt_container:
            prod = pdt_container
        else:
            prod = pdt_container
            
            messages.info(request, f"There is no product with this name '{user_input_search}'")
    elif selected_sorting:
        if selected_sorting == "Position" :
            prod= product.objects.filter(is_deleted=False)
        elif selected_sorting == 'Name Ascen':
            prod= product.objects.filter(is_deleted=False).order_by('product_name')
        elif selected_sorting == 'Name Decen':
            prod= product.objects.filter(is_deleted=False).order_by('-product_name')
        elif selected_sorting == 'Price Ascen':
            prod= product.objects.filter(is_deleted=False).order_by('price')
        elif selected_sorting == 'Price Decen':
            prod= product.objects.filter(is_deleted=False).order_by('-price')
    else:
        prod=product.objects.filter(is_deleted=False).order_by('-id')
    page=Paginator(prod,6)
    page_number = request.GET.get('page')
    prod = page.get_page(page_number)
    
    context={
        'maincategory':maincategory,
        'prod':prod,
        'sub':sub,
        'cat':cat,
        'wish':wish,
        
    }
    
    return render(request,'main/shop.html',context)


def product_details(request,slug):
    maincategory=main_category.objects.all().order_by('id')
    prod=product.objects.get(slug=slug)
    feed= Feedback.objects.filter(product=prod)
    context={
        'maincategory':maincategory,
        'prod':prod,
        'feed':feed,
        }
    return render(request,'main/product_detail.html',context)


    
@login_required(login_url='login')
@allow_guest_user
def Profile(request):
    maincategory=main_category.objects.all().order_by('id')
    user=request.user
    cstmuser=CustomUser.objects.get(email=user)
    addrs=Address.objects.filter(user=user,is_deleted=False)
    orders = Order.objects.filter(user=request.user).order_by('-id')
    
    
    try:
        wallet = Wallet.objects.filter(user=user).order_by('-created_at')
        context={
        'maincategory':maincategory,
        'addrs':addrs,
        'orders':orders,
        'wallet':wallet,
        'cstmuser':cstmuser
        
        }
    except Wallet.DoesNotExist:
        
        
        context={
            'maincategory':maincategory,
            'addrs':addrs,
            'orders':orders,
            'wallet':0,
            
            }
    return render(request,'main/profile.html',context)

@login_required(login_url='login')
@allow_guest_user
def Profile_update(request,id):
   
    users = CustomUser.objects.get(id=id)
    if request.method == "POST":
    
        full_name=request.POST.get('full_name')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        ph_no=request.POST.get('ph_no')
        current=request.POST.get('password')
        
        users.full_name=full_name
        users.first_name=first_name
        users.last_name=last_name
        users.email=email
        users.ph_no=ph_no
        users.save() 
        if current != None and auth.authenticate(email=users, password=current):
            pass1=request.POST.get('newpass')
            pass2=request.POST.get('newpassconf')
            if pass1==pass2:
                users.set_password(pass1)
                users.save()
                print("changed")
            else :
                messages.error(request,'password didnt match!')
                print('not same')
        else:
            messages.error(request, "Your current password is incorrect.")
             
        return redirect("profile")


    return render(request,'main/profile.html')

@login_required(login_url='login')
def update_addrs(request,id):
    user=request.user
    addrs=Address.objects.get(user=user,id=id)
    if request.method=="POST":
        addrs.first_name=request.POST.get('adfirst_name')
        addrs.last_name=request.POST.get('adlast_name')
        addrs.email=request.POST.get('ademail')
        addrs.phoneNumber=request.POST.get('adph_no')
        addrs.addressline1=request.POST.get('adaddressline1')
        addrs.country=request.POST.get('adcountry')
        addrs.state=request.POST.get('adstate')
        addrs.city=request.POST.get('adcity')
        addrs.pin=request.POST.get('adpin')
        
        addrs.save()
        return redirect('profile')
def edit_addrs(request,id):
    maincategory=main_category.objects.all().order_by('id')
    user=request.user
    addrs=Address.objects.filter(user=user,id=id)
    context={
        'addrs':addrs,
        'maincategory':maincategory
    }
    
    return render(request,'main/edit_addrs.html',context)

@login_required(login_url='login')
@allow_guest_user
def add_adrs(request):
    maincategory=main_category.objects.all().order_by('id')
    if request.method=="POST":
        fname=request.POST.get('adfirst_name')
        lname=request.POST.get('adlast_name')
        email=request.POST.get('ademail')
        ph=request.POST.get('adph_no')
        add=request.POST.get('adaddressline1')
        country=request.POST.get('adcountry')
        state=request.POST.get('adstate')
        city=request.POST.get('adcity')
        pin=request.POST.get('adpin')
        check=request.POST.get('check','')
        
        
        Address.objects.create(
            user=request.user,
            first_name=fname,
            last_name=lname,
            email=email,
            phoneNumber=ph,
            addressline1=add,
            country=country,
            state=state,
            city=city,
            pin=pin
            
        )
        if check=="checkout":
            return redirect('checkout')
        else:
            return redirect('profile')
    context={
        
        'maincategory':maincategory
    }
        
    return render(request,'main/add_addrs.html',context)

@login_required(login_url='login')
def delete_adrs(request,id):
    addr = Address.objects.get(id=id)
    addr.is_deleted=True
    addr.save()
    return redirect('profile')



                



def cart_add(request):
    product_id=request.GET['id']
    cart = Cart(request)
    Product = product.objects.get(id=product_id)
    count=Product.stock
    cart.add(product=Product)
    return redirect("index")



def item_clear(request, id):
    cart = Cart(request)
    Product = product.objects.get(id=id)
    cart.remove(Product)
    return redirect("cart_detail")



def item_increment(request):
    product_id=request.GET['id']
    cart = Cart(request)
    Product = product.objects.get(id=product_id)
    cart.add(product=Product)
    return redirect("cart_detail")



def item_decrement(request, id):
    cart = Cart(request)
    Product = product.objects.get(id=id)
    
    cart.decrement(product=Product)
    
    
    return redirect("cart_detail")



def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


def cart_detail(request):
    maincategory=main_category.objects.all().order_by('id')
    Coupon=None
    valid=None
    invalid=None
    if request.method=='POST':
        coupn_code=request.POST.get('coupon')
        if coupn_code:
            try:
                Coupon=coupon.objects.get(code=coupn_code,is_active=True)
                valid = "is Applied"
                
            except:
                invalid = "invalid coupon code!"
        invalid = "Invalid coupon code!"
    context={
        'maincategory':maincategory,
        'Coupon':Coupon,
        'valid':valid,
        'invalid':invalid,
        
        }
    return render (request,'main/cart.html',context)
    
@login_required(login_url='login')
@csrf_exempt
@allow_guest_user
def checkout(request):
    cart_item = request.session.get(settings.CART_SESSION_ID, {})
    if not cart_item:
        print('no items')
    
      
    maincategory=main_category.objects.all().order_by('id')
    Coupon=None
    valid=None
    invalid=None
    if request.method=='POST':
        coupn_code=request.POST.get('coupon')
        if coupn_code:
            try:
                Coupon=coupon.objects.get(code=coupn_code,is_active=True)
                valid = "is Applied"
                
            except:
                invalid = "invalid coupon code!"
        invalid = "Invalid coupon code!"
    discount_price=None
    total_price = sum(int(item['price']) * int(item['quantity']) for item in cart_item.values())
    if total_price > 500:
        total_price+=150 
    if Coupon:
            discount = float(Coupon.discount)
            total_price = float(total_price)
            discount_price=total_price * discount / 100
            total_price = total_price - (total_price * discount / 100)
            
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    if not total_price:
        total_price=1
        
    
    payment=client.order.create(
        {
            "amount": total_price * 100,
            "currency":"INR",
            "payment_capture":1,
        }
    )
    print(payment)
    order_id=payment['id']
    
    cart=request.session.get('cart')
    user=request.user
    addrs=Address.objects.filter(user=user,is_deleted=False)
    context={
        'maincategory':maincategory,
        'cart':cart,
        'addrs':addrs,
        'maincategory':maincategory,
        'Coupon':Coupon,
        'valid':valid,
        'invalid':invalid,
        'order_id':order_id,
        'payment':payment,
        'discount_price':discount_price
        
        }
    return render(request,'main/checkout.html',context)

@allow_guest_user
@login_required(login_url='login')
@csrf_exempt
def place_order(request):
    discount=None
    user = request.user
    cart_item = request.session.get(settings.CART_SESSION_ID, {})
    
    
    if request.method == "POST":
        discount_price=None
        payment_method = request.POST.get('paymentmethod')
        address_id = request.POST.get('address')
        if address_id =='Choose':
            messages.error(request,"Please select an Address")
            return redirect('checkout')
        request.session['bill']=address_id
        request.session.save()
        discount= None
        discount=request.POST.get('dis')
        
        for product_id,quantity in cart_item.items():
            Product = product.objects.get(id=product_id)
            
        total_quantity = sum(item['quantity'] for item in cart_item.values())
        
        total_price = sum(int(item['price']) * int(item['quantity']) for item in cart_item.values())
        if total_price > 500:
            total_price+=150
        
        if discount:
            
            discount = float(discount)
            total_price = float(total_price)
            discount_price= total_price * discount / 100
            total_price = total_price - discount_price
            
    
            # Create the order
        if payment_method == 'cash':
            order = Order.objects.create(
                    user=user,
                    address_id=address_id,
                    payment_type=payment_method,
                    product=Product,
                    amount=total_price,
                    quantity=total_quantity,
                    coupon =discount_price
                    
                )
            
            order.save()
             
            message = f"New order placed by {request.user.full_name}"
            notification = Notification(sender=request.user, message=message, order=order)
            notification.save()
            
            
            for product_id,item in cart_item.items():
                Product = product.objects.get(id=product_id)
                order_item = OrderItem(
                    order=order,
                    product=Product,
                    quantity=item['quantity'],
                    image = item['product_image'],
                )
                order_item.save()
                if Product.stock >= item['quantity']:
                    Product.stock -= item['quantity']
                    Product.save()
            
            request.session['cart'] = {}
            return redirect('order_success') 
        
        
        

    return render(request,'main/checkout.html',{'total_price':total_price})

@allow_guest_user
@login_required(login_url='login')
def razorpayment(request):

    user = request.user
    cart_item = request.session.get(settings.CART_SESSION_ID, {})
    
    for product_id,quantity in cart_item.items():
            Product = product.objects.get(id=product_id)
            
    if request.method == 'POST':
                discountAmount=None
                totalprice =request.POST.get('tota_amount')
                billadd = request.POST.get('selected_address')
                discountAmount= request.POST.get('discountAmount')
                totalQuantity= request.POST.get('totalQuantity')
                razorpay_payment_id = request.POST.get('razorpay_payment_id')
                razorpay_order_id = request.POST.get('razorpay_order_id')
                razorpay_signature = request.POST.get('razorpay_signature')
                if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
                    print('invalid payment')
                order = Order.objects.create(
                        user=user,
                        address_id=billadd,
                        payment_type='Razorpay',
                        product=Product,
                        amount=totalprice,
                        quantity=totalQuantity,
                        coupon=discountAmount
                        
                    )
                
                order.save()
                message = f"New order placed by {request.user.full_name}"
                notification = Notification(sender=request.user, message=message, order=order)
                notification.save()
                
                
                Payment.objects.create(
                        order = order,
                        amount = totalprice,
                        razor_pay_order_id = razorpay_payment_id,
                        razor_pay_payment_id = razorpay_order_id,
                        razor_pay_payment_signature = razorpay_signature,
                    )
                
                
                for product_id,item in cart_item.items():
                    Product = product.objects.get(id=product_id)
                    order_item = OrderItem(
                        order=order,
                        product=Product,
                        quantity=item['quantity'],
                        image = item['product_image'],
                    )
                    order_item.save()
                    if Product.stock >= item['quantity']:
                        Product.stock -= item['quantity']
                        Product.save()
                
                request.session['cart'] = {}
                return redirect('order_success') 
        

@csrf_exempt
@allow_guest_user
def order_success(request):
    orders = Order.objects.filter(user=request.user)
    maincategory=main_category.objects.all().order_by('id')
    return render(request,'main/order_success.html',{'orders':orders,'maincategory':maincategory},)
        
    
def order_list(request):
    orders = Order.objects.filter(user=request.user).latest('-id')
    return render(request,'main/profile.html',{'orders':orders})

@allow_guest_user
@login_required(login_url='login')
def order_details(request,id):
    if request.method== 'POST':
        review = request.POST['review']
        prod=request.POST['product']
        prod=product.objects.get(id=prod)
        feedback = Feedback(name=request.user, review=review, product=prod)
        feedback.save()
    maincategory=main_category.objects.all().order_by('-id')

    orders = Order.objects.filter(id=id)

    order_items= OrderItem.objects.filter(order=id)
    total_price = Decimal(0)

    for item in order_items:
        item_total = item.product.price * item.quantity
        total_price += item_total
    
    
    context={
        'orders':orders,
        'maincategory':maincategory,
        'total_price':total_price,
    }
    return render(request,'main/order_details.html',context)



@login_required(login_url='login')
@allow_guest_user
def Wishlist(request):
    maincategory=main_category.objects.all().order_by('id')
    wish=wishlist.objects.filter(user=request.user)
    context={
        'maincategory':maincategory,
        'wish':wish,
    }
    return render(request,'main/wishlist.html',context)


@allow_guest_user
def addwish(request):
    product_id=request.GET['id']
    Product=product.objects.get(id=product_id)
    user=request.user
    Wishlist,created=wishlist.objects.get_or_create(product=Product,user=user)
    Wishlist.save()
    return redirect('shop')

def removewish(request,id):
    Wishlist=wishlist.objects.get(id=id)
    Wishlist.delete()
    return redirect('wishlist')

@allow_guest_user
@login_required(login_url='login')
def cancel(request,id):
    user=request.user
    usercustm=CustomUser.objects.get(email=user)
    OrderItem=Order.objects.get(id=id)
    prod=product.objects.get(product_name=OrderItem.product)
    prod.stock+=1
    prod.save()
    if OrderItem.status == 'completed' or OrderItem.status == 'delivered' and OrderItem.payment_type=='cash':
        wallet= Wallet.objects.create(
        user=user,
        order=OrderItem,
        amount=OrderItem.amount,
        status='Credited',
        )
        wallet.save()
        OrderItem.status='refunded'
        OrderItem.save()
        Order_item_amount = Decimal(OrderItem.amount)
        usercustm.wallet_bal+=Order_item_amount
    
    elif OrderItem.payment_type=='Razorpay':
        wallet= Wallet.objects.create(
        user=user,
        order=OrderItem,
        amount=OrderItem.amount,
        status='Credited',
        )
        wallet.save()
        
        OrderItem.status='refunded'
        OrderItem.save()
        Order_item_amount = Decimal(OrderItem.amount)
        usercustm.wallet_bal+=Order_item_amount
        print('wallte:',usercustm.wallet_bal)
        usercustm.save()
            
    else:
        OrderItem.status='cancelled'
        OrderItem.save()
    
    
    message = f"Order cancelled by {request.user.full_name}"
    notification = Notification(sender=request.user, message=message, order=OrderItem, type='cancelled')
    notification.save()
    return redirect('order_details',id)

def invoice(request,id):
    
    buf= io.BytesIO()
    c= canvas.Canvas(buf,pagesize=letter, bottomup=0)
    textob=c.beginText()
    textob.setTextOrigin(inch,inch)
    textob.setFont("Helvetica",14)
    orders = Order.objects.filter(id=id)
    order_items = OrderItem.objects.filter(order=id)
    lines = []
    lines.append("RUBY")    
    lines.append("Invoice:")    
    for o in orders:
        for i in order_items:
            lines.append(f"Name: {o.user.full_name}")
            lines.append(f"Product: {i.product.product_name}")
            lines.append(f"Quantity: {i.quantity}")
            lines.append(f"Price: {i.product.price}")
            lines.append(f"Payment Type: {o.payment_type}")
            lines.append(f"Payment ID: {o.payment_id}")
            lines.append(f"Amount: {o.amount}")
            lines.append(f"Coupon: {o.coupon}")
            lines.append(f"Address: {o.address.addressline1},phno:{o.address.phoneNumber},pin:{o.address.pin}")
            lines.append("")
    for line in lines:
        textob.textLine(line)
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
        
    return FileResponse(buf,as_attachment=True,filename='invoice.pdf')


def contact(request):
    return render(request,'main/contact.html')