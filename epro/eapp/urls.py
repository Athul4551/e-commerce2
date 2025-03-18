from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views
urlpatterns = [
   path('', views.firstpage, name='firstpage'),
   path('forgotpassword',views.getusername,name='forgotpassword'),
   path('verifyotp',views.verifyotp,name='verifyotp'),  
   path('passwordreset',views.passwordreset,name='passwordreset'),
   path('userlogin',views.userlogin,name="userlogin"),
   path('usersignup',views.usersignup,name="usersignup"),
   path('product/<int:id>',views.product,name='product'),
   path('review',views.review,name='review'),
   path('aboutus',views.aboutus,name='aboutus'),
   path('adminpage',views.adminpage,name='adminpage'),
   path('logout',views.logoutuser,name="logout"),
   path('add',views.add,name='add'),
   path('index',views.index,name='index'),
   path('deletion/<int:id>',views.delete_g,name='deletion'),
   path('edit_g/<int:id>',views.edit_g,name='edit_g'),
   path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
   path('cart/', views.cart_view, name='cart_view'),
   path('dele/<int:id>/', views.delete_cart, name='dele'),
   path('checkout/', views.checkout, name='checkout'),
   path('cart/increment/<int:id>/', views.increment_cart, name='increment_cart'),
   path('cart/decrement/<int:id>/', views.decrement_cart, name='decrement_cart'),
   path('sample',views.sample,name='sample'),
   path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
   path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
   path('search/', views.search_results, name='search_results'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)