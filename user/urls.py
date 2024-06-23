from django.urls import path,include
from . import views

urlpatterns = [
    path('login/',views.loginpage,name='login'),
    path('register/',views.register,name='register'),
    path('userlog/',views.log,name='log'),
    path('logout/',views.logoutPage,name="logout"),
    path('verify/',views.verify_signup,name="verify_signup"),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    
    
    
    path('adminn/',views.admin,name='admin'),
    path('users/',views.admin_users,name='admin_users'),
    path('category/',views.categoryc,name='category'),
    path('products/',views.products,name='products'),
    
    path('edit_user/<int:id>',views.edit_user,name='edit_user'),
    # path('update_user/<int:id>',views.update_user,name='update_user'),
    # path('delete_user/<int:id>',views.delete_user,name='update_user'),
    path('block_user/<int:id>',views.block_user,name='block_user'),
    path('unblock_user/<int:id>',views.unblock_user,name='unblock_user'),
    # path('add_user/',views.add_user,name='add_user'),
    
    path('edit_main_category/<int:id>',views.edit_main_category,name='edit_main_category'),
    path('update_main_category/<int:id>',views.update_main_category,name='update_main_category'),
    path('add_main_category/',views.add_main_category,name='add_main_category'),
    path('delete_main_category/<int:id>',views.delete_main_category,name='delete_main_category'),
    
    path('edit_category/<int:id>',views.edit_category,name='edit_category'),
    path('delete_category/<int:id>',views.delete_category,name='edit_category'),
    path('add_category/',views.add_category,name="add_category"),
    path('update_category/<int:id>',views.update_category,name='update_category'),

    
    path('edit_subcategory/<int:id>',views.edit_subcategory,name='edit_subcategory'),
    path('delete_subcategory/<int:id>',views.delete_subcategory,name='edit_category'),
    path('add_subcategory/',views.add_subcategory,name='add_subcategory'),
    path('update_sub/<int:id>',views.update_sub,name='update_sub'),


    path('edit_products/<int:id>',views.edit_products,name="edit_products"),
    path('add_product/',views.add_product,name="add_product"),
    path('delete_product/<int:id>',views.delete_product,name="delete_product"),
    path('undo_delete_product/<int:id>',views.undo_delete_product,name="undo_delete_product"),
    path('view_more/',views.view_more,name="view_more"),
    path('update_product/<int:id>',views.update_product,name='update_product'),
    
    
    path('all_orders/',views.all_orders,name='all_orders'),
    path('update_order/<int:id>',views.update_order,name='update_order'),
    path('view_order/<int:id>',views.view_order,name="view_order"),
    
    path('coupon/',views.coupons,name="coupon"),
    path('add_coupon/',views.add_coupons,name="add_coupon"),
    path('coupon_activate/<int:id>/', views.couponactivate,name = 'couponactivate'),
    
    path('sale_report',views.sale_report,name="sale_report"),
]