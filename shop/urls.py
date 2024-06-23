from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='index'),
    path('shop/',views.shop,name='shop'),
    path('product/<slug:slug>',views.product_details,name='product_detail'),
    path('profile/',views.Profile,name='profile'),
    path('profile_update/<int:id>',views.Profile_update,name='profile_update'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',
         views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),
    path('edit_addrs/<int:id>',views.edit_addrs,name='edit_addrs'),
    path('update_addrs/<int:id>',views.update_addrs,name='update_addrs'),
    path('add_addrs/',views.add_adrs,name='add_addrs'),
    path('delete_addrs/<int:id>',views.delete_adrs,name='delete_addrs'),
    
    path('checkout/',views.checkout,name='checkout'),
    path('place_order/',views.place_order,name="place_order"),
    path('order_success/',views.order_success,name="order_success"),
    path('order_list/',views.order_list,name="order_list"),
    path('order_details/<int:id>',views.order_details,name='order_details'),
    
    path('wishlist/',views.Wishlist,name='wishlist'),
    path('addwish/',views.addwish,name='addwish'),
    path('removewish/<int:id>',views.removewish,name='removewish'),
    
    path('cancel/<int:id>',views.cancel,name='cancel'),
    
    path('razor/',views.razorpayment,name='razor'),
    
    path('invoice/<int:id>',views.invoice,name='invoice'),
    
    path('contact/',views.contact,name='contact'),
    # path('orders_by_week/',views.orders_by_week,name='orders_by_week')
        
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
