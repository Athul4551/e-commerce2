from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime, timedelta
from .models import *
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required



def index(request):
    if request.method == 'POST' and 'image' in request.FILES:  
        myimage = request.FILES['image']  
        name=request.POST.get("todo")
        price=request.POST.get("date")
        # todo311=request.POST.get("course")
        quanty=request.POST.get("quant")
        mod=request.POST.get("model")
        off=request.POST.get("offers")
        obj=Gallery(name=name,price=price,model=mod,quantity=quanty,offers=off,feedimage=myimage,user=request.user)
        obj.save()
        data=Gallery.objects.all()
        return redirect(adminpage)
    gallery_images = Gallery.objects.all()
    return render(request, "index.html")
def verifyotp(request):
    if request.POST:
        otp = request.POST.get('otp')
        otp1 = request.session.get('otp')
        otp_time_str = request.session.get('otp_time')
        if otp_time_str:
            otp_time = datetime.fromisoformat(otp_time_str)  
            otp_expiry_time = otp_time + timedelta(minutes=5)
            if datetime.now() > otp_expiry_time:
                messages.error(request, 'OTP has expired. Please request a new one.')
                del request.session['otp']
                del request.session['otp_time']
                return redirect('verifyotp')
        if otp == otp1:
            del request.session['otp']
            del request.session['otp_time']
            return redirect('passwordreset')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    otp = ''.join(random.choices('123456789', k=6))
    request.session['otp'] = otp
    request.session['otp_time'] = datetime.now().isoformat()
    message = f'Your email verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email')]
    send_mail('Email Verification', message, email_from, recipient_list)

    return render(request, "otp.html")

def getusername(request):
    if request.POST:
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            request.session['email'] = user.email
            return redirect('verifyotp')
        except User.DoesNotExist:
            messages.error(request, "Username does not exist.")
            return redirect('getusername')

    return render(request, 'getusername.html')

def passwordreset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')
        if confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('email')
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                del request.session['email']
                messages.success(request, "Your password has been reset successfully.")
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)

                return redirect('sellerlogin')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return redirect('getusername')

    return render(request, "passwordreset.html")
# def firstpage(request):
#     gallery_images = Gallery.objects.all()
#     return render(request, "firstpage.html", {"gallery_images": gallery_images})
def firstpage(request): 
    gallery_images = Gallery.objects.all()  
    if request.user.is_authenticated:
        cart_item_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_item_count = 0 
    return render(request, "firstpage.html", {
        "gallery_images": gallery_images,
        "cart_item_count": cart_item_count
    })
def usersignup(request):
    if request.POST:
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')

        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('userlogin')  

    return render(request, "userregister.html")
def userlogin(request):
    if 'username' in request.session:
        return redirect('firstpage')  
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if user.is_superuser:
                return redirect('adminpage')
            return redirect('firstpage')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'userlogin.html')
# def product(request,id):
#     gallery_images =Gallery.objects.filter(pk=id)
#     return render(request,'products.html',{"gallery_images": gallery_images,})
def product(request, id):
    gallery_images = Gallery.objects.filter(pk=id)
    if request.user.is_authenticated:
        cart_item_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_item_count = 0 
    
    return render(request, 'products.html', {
        "gallery_images": gallery_images,
        "cart_item_count": cart_item_count
    })
def review(request):
    return render(request,"review.html")
def aboutus(request):
    return render(request,"aboutus.html")
def adminpage(request):
    data = Gallery.objects.all()
    gallery_images = Gallery.objects.filter(user=request.user)
    return render(request,'adminpage.html',{"gallery_images": gallery_images})
def delete_g(request,id):
    feeds=Gallery.objects.filter(pk=id)
    feeds.delete()
    return redirect('adminpage')
def add(request):
    return render(request,"index.html")
def logoutuser(request):
    logout(request)
    request.session.flush()
    return redirect(firstpage)
@login_required
def edit_g(request, id):
    gallery_image = get_object_or_404(Gallery, pk=id, user=request.user)
    
    if request.method == 'POST':
        myimage = request.FILES['image']  
        name=request.POST.get("todo")
        price=request.POST.get("date")
        # todo311=request.POST.get("course")
        quanty=request.POST.get("quant")
        mod=request.POST.get("model") 
        off=request.POST.get("offers")
        
        if not name or not price or not quanty or not mod or not off:
            messages.error(request, "All fields are required.")
            return render(request, 'index.html', {'data1': gallery_image})
        
        
        gallery_image.name = name
        gallery_image.price = price
        gallery_image.quantity = quanty
        gallery_image.model = mod
        gallery_image.offers = off
        if myimage: 
            gallery_image.feedimage = myimage
        gallery_image.save()

        messages.success(request, "Gallery item updated successfully!")
        return redirect('sellerfirstpage')

    # Handle GET request to display the form
    return render(request, 'index.html', {'data1': gallery_image})
# @login_required(login_url='userlogin')  # Redirect to your login page
# def add_to_cart(request, id):
#     product = get_object_or_404(Gallery, id=id)
#     cart_item, created = Cart.objects.get_or_create(
#         user=request.user,
#         product=product,
#         defaults={'quantity': 1}
#     )
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#     return redirect('cart_view')
@login_required(login_url='userlogin')
def add_to_cart(request, id):
    if 'username' in request.session:
        try:
            product = Gallery.objects.get(id=id)
        except Gallery.DoesNotExist:
        
            return redirect('product_not_found')  
    
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
        
        )
        if not created:
            if cart_item.product.quantity > cart_item.quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, "out of stock.")
                return redirect('cart_view')
        else:
            cart_item.quantity = 1
            cart_item.save()
            return redirect('cart_view')


# @login_required
# def increment_cart(request, id):
#     cart_item = get_object_or_404(Cart, pk=id, user=request.user)
#     cart_item.quantity += 1
#     cart_item.save()
#     return redirect('cart_view')

@login_required
def increment_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    if cart_item.product.quantity > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.error(request, "Not enough stock available.")

    return redirect('cart_view')

# @login_required
# def decrement_cart(request, id):
#     cart_item = get_object_or_404(Cart, pk=id, user=request.user)
#     if cart_item.quantity > 1:
#         cart_item.quantity -= 1
#         cart_item.save()
#     else:
#         cart_item.delete()
#     return redirect('cart_view')

@login_required
def decrement_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_view')

# @login_required
# def cart_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})

@login_required
def delete_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')

@login_required
def checkout(request):
    return render(request, 'checkout.html')
def sample(request):
    return redirect('add_to_cart')

@login_required
def buy_now(request, product_id):
    if 'username' in request.session:
        product = get_object_or_404(Gallery, id=product_id)

        if request.method == "POST":
            quantity = int(request.POST.get("quantity", 1))
            address = request.POST.get("address")
            payment_method = request.POST.get("payment_method")
            total_price = product.price * quantity  

            order = Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=total_price,
                address=address,
                payment_method=payment_method,
                status="Pending"
            )

            # Send email to admin
            admin_email = "admin@example.com"  # Replace with the admin's email
            subject = f"New Order Placed - {order.id}"
            message = f"""
            New Order Placed!

            Order ID: {order.id}
            User: {request.user.username}
            Product: {product.name}
            Quantity: {quantity}
            Total Price: ₹{total_price}
            Address: {address}
            Payment Method: {payment_method}

            Please process the order in the admin panel.
            """

            send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

            messages.success(request, "Order placed successfully! An email has been sent to the admin.")

            return redirect('order_confirmation', order_id=order.id)

        return render(request, "buy_now.html", {"product": product})

    else:
        return redirect('userlogin')
# @login_required
# def buy_now(request, product_id):
#     if 'username' in request.session:
#         product = get_object_or_404(Gallery, id=product_id)

#         if request.method == "POST":
#             quantity = int(request.POST.get("quantity", 1))

#             # Check if requested quantity is within available stock
#             if quantity > product.quantity:
#                 messages.error(request, "Out of stock! You cannot buy more than the available quantity.")
#                 return redirect('product', id=product_id)  # Redirect back to product page

#             address = request.POST.get("address")
#             payment_method = request.POST.get("payment_method")
#             total_price = product.price * quantity  

#             # Create the order
#             order = Order.objects.create(
#                 user=request.user,
#                 product=product,
#                 quantity=quantity,
#                 total_price=total_price,
#                 address=address,
#                 payment_method=payment_method,
#                 status="Pending"
#             )

#             # Deduct stock quantity
#             product.quantity -= quantity
#             product.save()

#             # Send email to admin
#             admin_email = "unni65129@gmail.com"  # Replace with actual admin email
#             subject = f"New Order Placed - {order.id}"
#             message = f"""
#             New Order Placed!

#             Order ID: {order.id}
#             User: {request.user.username}
#             Product: {product.name}
#             Quantity: {quantity}
#             Total Price: ₹{total_price}
#             Address: {address}
#             Payment Method: {payment_method}

#             Please process the order in the admin panel.
#             """
#             send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

#             messages.success(request, "Order placed successfully!")
#             return redirect('order_confirmation', order_id=order.id)

#         return render(request, "buy_now.html", {"product": product})

#     else:
#         return redirect('userlogin')



@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})
def search_results(request):
    query = request.GET.get('q')
    results = Gallery.objects.filter(name__icontains=query) if query else None
    return render(request, 'search_results.html', {'results': results, 'query': query}) 