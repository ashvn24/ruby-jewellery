from django.contrib import admin
from .models import *


# Register your models here.

class product_Images(admin.TabularInline):
    model = product_images
    
class add_descriptions(admin.TabularInline):
    model=add_description
    
class product_admin(admin.ModelAdmin):
    inlines=(product_Images,add_descriptions)



admin.site.register(main_category)
admin.site.register(category)
admin.site.register(sub_category)


admin.site.register(section)
admin.site.register(product,product_admin)
admin.site.register(product_images)
admin.site.register(add_description)
admin.site.register(cartitem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(wishlist)
admin.site.register(coupon)
admin.site.register(Payment)
admin.site.register(Wallet)
admin.site.register(Notification)
admin.site.register(Feedback)
