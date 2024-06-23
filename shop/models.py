from django.utils import timezone
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.db.models.signals import pre_save
from user.models import CustomUser
import uuid

# Create your models here.



class main_category(models.Model):
    name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    def __iter__(self):
        yield self.id
    
class category(models.Model):
    maincat=models.ForeignKey(main_category,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.maincat.name + '--' + self.name
       
    def __iter__(self):
        yield self.id
    
class sub_category(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE,)
    name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.category.maincat.name + '--' + self.category.name + '--' + self.name
    
class section(models.Model):
    name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.name 
    
class product(models.Model):
    stock=models.IntegerField()
    product_image=models.ImageField(upload_to='product_imgs')
    product_name=models.CharField(max_length=100)
    price=models.IntegerField()
    discount=models.IntegerField(blank=True,null=True)
    product_information=RichTextField()
    categories=models.ForeignKey(sub_category,on_delete=models.CASCADE)
    section=models.ForeignKey(section,on_delete=models.DO_NOTHING,blank=True,null=True)
    rating=models.IntegerField(blank=True,null=True)
    slug=models.SlugField(default='',max_length=500, null=True,blank=True)
    is_deleted=models.BooleanField(default=False)
    
        
    def __str__(self):
        return self.product_name
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={'slug': self.slug})
    def __iter__(self):
        yield self.id


    class Meta:
        db_table = "app_Product"

def create_slug(instance, new_slug=None):
    slug = slugify(instance.product_name)
    if new_slug is not None:
        slug = new_slug
    qs = product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, product)
class product_images(models.Model):
    product=models.ForeignKey(product,on_delete=models.CASCADE)
    images=models.ImageField(upload_to='product_imgs')

class add_description(models.Model):
    product=models.ForeignKey(product,on_delete=models.CASCADE)
    
    add_description=RichTextField()
    


    
    
class cartitem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_name=models.ForeignKey(product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    
    def __str__(self):
        return self.product_name.product_name
    

class Address(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20,blank=True,null=True)
    email = models.EmailField( unique=False)
    phoneNumber = models.CharField(max_length=15)
    addressline1 = models.CharField(max_length=255)
    addressline2 = models.CharField(max_length=255,blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    pin = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.first_name
    
class Order(models.Model):

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded','refunded'),
        ('on_hold','on_hold')

    )

    user           =   models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    address        =   models.ForeignKey(Address, on_delete=models.CASCADE)
    product        =   models.ForeignKey(product, on_delete=models.CASCADE, null=True, blank=True)
    amount         =   models.CharField(max_length=100)  
    payment_type   =   models.CharField(max_length=100)  
    status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity       =   models.IntegerField(default=0, null=True, blank=True)
    image          =   models.ImageField(upload_to='products/', null=True, blank=True)
    date           =   models.DateField(auto_now_add=True)
    payment_id     =   models.CharField(max_length=100,null=True,blank=True)
    coupon         =   models.CharField(max_length=30,null=True,blank=True)
    paid           =   models.BooleanField(default=False,blank=True)
    is_deleted     =   models.BooleanField(default=False,blank=True)
           
    
    def __str__(self):
        return f"Order #{self.pk} - {self.user}"
    
    def __iter__(self):
        yield self.pk
        
    
class OrderItem(models.Model):
    order          =   models.ForeignKey(Order,on_delete=models.CASCADE)
    product        =   models.ForeignKey(product,on_delete=models.CASCADE)
    quantity       =   models.IntegerField(default=1)
    image          =   models.ImageField(upload_to='products_order', null=True, blank=True)

    def __str__(self):
        return str(self.order)
    
    
class wishlist(models.Model):
    user           =   models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product        =   models.ForeignKey(product, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.full_name


class coupon(models.Model):
    
    code = models.CharField(max_length=15)
    discount = models.IntegerField()
    start_date = models.DateField()  
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.code
    
class used_coupon(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    code=models.ForeignKey(coupon,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.first_name
    
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razor_pay_order_id = models.CharField(max_length=100,blank=True)
    razor_pay_payment_id = models.CharField(max_length=100,blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100,blank=True)
    
    def __str__(self):
        return str(self.order.id)
    
class Wallet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_credit = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,blank=True)
    def __str__(self):
        return f"{self.amount} {self.is_credit}"

    def __iter__(self):
        yield self.pk
     
class Notification(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Replace 'Order' with your order model
    timestamp = models.DateTimeField(auto_now_add=True)
    type=models.CharField(max_length=20,blank=True)
    
class Feedback(models.Model):
    name=models.CharField(max_length=30)
    review=models.CharField(max_length=200)
    product=models.ForeignKey(product, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)