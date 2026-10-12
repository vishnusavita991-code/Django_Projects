import io
from django.shortcuts import render, redirect, reverse, get_object_or_404
from . import forms, models
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from xhtml2pdf import pisa
from django.template.loader import get_template

CATEGORIES_LIST = ['Electronics', 'Fashion', 'Home & Living', 'Accessories', 'Gadgets']

def get_cart_count(request):
    if 'product_ids' in request.COOKIES:
        p_ids = request.COOKIES['product_ids']
        if p_ids:
            return len(set(p_ids.split('|')))
    return 0

def logout_view(request):
    logout(request)
    return render(request, 'ecom/logout.html')

def filter_and_sort_products(queryset, request):
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')
    query = request.GET.get('query', '').strip()

    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    if category and category != 'All':
        queryset = queryset.filter(category=category)

    if sort == 'price_asc':
        queryset = queryset.order_by('price')
    elif sort == 'price_desc':
        queryset = queryset.order_by('-price')
    elif sort == 'rating':
        queryset = queryset.order_by('-rating')
    elif sort == 'newest':
        queryset = queryset.order_by('-id')

    return queryset

def home_view(request):
    products = filter_and_sort_products(models.Product.objects.all(), request)
    cart_count = get_cart_count(request)
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    
    context = {
        'products': products,
        'product_count_in_cart': cart_count,
        'categories': CATEGORIES_LIST,
        'selected_category': request.GET.get('category', 'All'),
        'selected_sort': request.GET.get('sort', ''),
        'query': request.GET.get('query', '')
    }
    return render(request, 'ecom/index.html', context)

def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')

def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
            messages.success(request, "Account created successfully! Please log in.")
            return HttpResponseRedirect('customerlogin')
    return render(request, 'ecom/customersignup.html', context=mydict)

def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS ------------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    customercount = models.Customer.objects.all().count()
    productcount = models.Product.objects.all().count()
    ordercount = models.Orders.objects.all().count()
    pendingcount = models.Orders.objects.filter(status='Pending').count()
    confirmedcount = models.Orders.objects.filter(status='Order Confirmed').count()
    deliveredcount = models.Orders.objects.filter(status='Delivered').count()

    all_orders = models.Orders.objects.select_related('product', 'customer').all().order_by('-id')
    total_revenue = sum(o.product.price for o in all_orders if o.product)

    recent_orders = all_orders[:10]
    ordered_products = [o.product for o in recent_orders]
    ordered_bys = [o.customer for o in recent_orders]

    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'pendingcount': pendingcount,
        'confirmedcount': confirmedcount,
        'deliveredcount': deliveredcount,
        'total_revenue': total_revenue,
        'orders': recent_orders,
        'data': zip(ordered_products, ordered_bys, recent_orders),
    }
    return render(request, 'ecom/admin_dashboard.html', context=mydict)

@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers = models.Customer.objects.all()
    return render(request, 'ecom/view_customer.html', {'customers': customers})

@login_required(login_url='adminlogin')
def delete_customer_view(request, pk):
    customer = get_object_or_404(models.Customer, id=pk)
    user = customer.user
    user.delete()
    customer.delete()
    messages.success(request, "Customer deleted successfully.")
    return redirect('view-customer')

@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = get_object_or_404(models.Customer, id=pk)
    user = customer.user
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.FILES or None, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            messages.success(request, "Customer profile updated successfully.")
            return redirect('view-customer')
    return render(request, 'ecom/admin_update_customer.html', context=mydict)

@login_required(login_url='adminlogin')
def admin_products_view(request):
    products = models.Product.objects.all().order_by('-id')
    return render(request, 'ecom/admin_products.html', {'products': products})

@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm = forms.ProductForm()
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
            messages.success(request, "Product added successfully!")
            return HttpResponseRedirect('admin-products')
    return render(request, 'ecom/admin_add_products.html', {'productForm': productForm})

@login_required(login_url='adminlogin')
def delete_product_view(request, pk):
    product = get_object_or_404(models.Product, id=pk)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('admin-products')

@login_required(login_url='adminlogin')
def update_product_view(request, pk):
    product = get_object_or_404(models.Product, id=pk)
    productForm = forms.ProductForm(instance=product)
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            productForm.save()
            messages.success(request, "Product updated.")
            return redirect('admin-products')
    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})

@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    status_filter = request.GET.get('status', '')
    orders = models.Orders.objects.select_related('product', 'customer').all().order_by('-id')
    if status_filter:
        orders = orders.filter(status=status_filter)

    ordered_products = [o.product for o in orders]
    ordered_bys = [o.customer for o in orders]
    return render(request, 'ecom/admin_view_booking.html', {
        'orders': orders,
        'data': zip(ordered_products, ordered_bys, orders),
        'selected_status': status_filter
    })

@login_required(login_url='adminlogin')
def delete_order_view(request, pk):
    order = get_object_or_404(models.Orders, id=pk)
    order.delete()
    messages.success(request, "Order deleted.")
    return redirect('admin-view-booking')

@login_required(login_url='adminlogin')
def update_order_view(request, pk):
    order = get_object_or_404(models.Orders, id=pk)
    orderForm = forms.OrderForm(instance=order)
    if request.method == 'POST':
        orderForm = forms.OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            orderForm.save()
            messages.success(request, f"Order #{order.id} status updated to {order.status}.")
            return redirect('admin-view-booking')
    return render(request, 'ecom/update_order.html', {'orderForm': orderForm, 'order': order})

@login_required(login_url='adminlogin')
def quick_order_status_view(request, pk, status):
    order = get_object_or_404(models.Orders, id=pk)
    valid_statuses = ['Pending', 'Order Confirmed', 'Out for Delivery', 'Delivered']
    if status in valid_statuses:
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.id} status changed to '{status}'")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else 'admin-view-booking')

@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks = models.Feedback.objects.all().order_by('-id')
    return render(request, 'ecom/view_feedback.html', {'feedbacks': feedbacks})

#---------------------------------------------------------------------------------
#------------------------ PUBLIC & CUSTOMER VIEWS --------------------------------
#---------------------------------------------------------------------------------
def search_view(request):
    query = request.GET.get('query', '').strip()
    products = filter_and_sort_products(models.Product.objects.all(), request)
    cart_count = get_cart_count(request)
    word = f"Search Results for '{query}'" if query else "All Products"

    context = {
        'products': products,
        'word': word,
        'query': query,
        'product_count_in_cart': cart_count,
        'categories': CATEGORIES_LIST,
        'selected_category': request.GET.get('category', 'All'),
        'selected_sort': request.GET.get('sort', '')
    }

    if request.user.is_authenticated:
        return render(request, 'ecom/customer_home.html', context)
    return render(request, 'ecom/index.html', context)

def product_detail_view(request, pk):
    product = get_object_or_404(models.Product, id=pk)
    related_products = models.Product.objects.filter(category=product.category).exclude(id=pk)[:4]
    cart_count = get_cart_count(request)
    return render(request, 'ecom/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'product_count_in_cart': cart_count
    })

def add_to_cart_view(request, pk):
    product = get_object_or_404(models.Product, id=pk)
    product_ids = request.COOKIES.get('product_ids', '')

    if product_ids:
        parts = product_ids.split('|')
        if str(pk) not in parts:
            product_ids = product_ids + "|" + str(pk)
    else:
        product_ids = str(pk)

    counter = product_ids.split('|')
    cart_count = len(set(counter))

    # If AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        resp = JsonResponse({
            'status': 'success',
            'product_name': product.name,
            'cart_count': cart_count,
            'message': f"{product.name} added to cart!"
        })
        resp.set_cookie('product_ids', product_ids)
        return resp

    referer = request.META.get('HTTP_REFERER')
    dest = referer if referer else ('/customer-home' if request.user.is_authenticated else '/')
    response = redirect(dest)
    response.set_cookie('product_ids', product_ids)
    messages.success(request, f"{product.name} added to cart!")
    return response

def cart_view(request):
    cart_count = get_cart_count(request)
    products = []
    subtotal = 0
    original_total = 0

    if 'product_ids' in request.COOKIES and request.COOKIES['product_ids']:
        raw_ids = [pid for pid in request.COOKIES['product_ids'].split('|') if pid]
        unique_ids = list(set(raw_ids))
        products = list(models.Product.objects.filter(id__in=unique_ids))
        for p in products:
            subtotal += p.price
            original_total += (p.original_price if p.original_price else p.price)

    coupon = request.COOKIES.get('coupon_code', '')
    discount = 0
    if coupon.upper() == 'SAVE10':
        discount = int(subtotal * 0.10)
    elif coupon.upper() == 'WELCOME20':
        discount = int(subtotal * 0.20)

    shipping = 0 if subtotal >= 999 or subtotal == 0 else 99
    grand_total = max(0, subtotal - discount + shipping)
    savings = (original_total - subtotal) + discount

    context = {
        'products': products,
        'total': subtotal,
        'subtotal': subtotal,
        'original_total': original_total,
        'discount': discount,
        'coupon_code': coupon,
        'shipping': shipping,
        'grand_total': grand_total,
        'savings': savings,
        'product_count_in_cart': cart_count,
    }
    return render(request, 'ecom/cart.html', context)

def apply_coupon_view(request):
    code = request.POST.get('coupon', '').strip()
    response = redirect('cart')
    if code.upper() in ['SAVE10', 'WELCOME20']:
        messages.success(request, f"Coupon '{code.upper()}' applied!")
        response.set_cookie('coupon_code', code.upper())
    else:
        messages.error(request, "Invalid coupon code. Try 'SAVE10' or 'WELCOME20'")
    return response

def remove_coupon_view(request):
    response = redirect('cart')
    response.delete_cookie('coupon_code')
    messages.info(request, "Coupon removed.")
    return response

def remove_from_cart_view(request, pk):
    product_ids = request.COOKIES.get('product_ids', '')
    if product_ids:
        parts = [pid for pid in product_ids.split('|') if pid and pid != str(pk)]
        new_val = "|".join(set(parts))
        response = redirect('cart')
        if new_val:
            response.set_cookie('product_ids', new_val)
        else:
            response.delete_cookie('product_ids')
        messages.info(request, "Item removed from cart.")
        return response
    return redirect('cart')

def send_feedback_view(request):
    feedbackForm = forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm': feedbackForm})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = filter_and_sort_products(models.Product.objects.all(), request)
    cart_count = get_cart_count(request)
    context = {
        'products': products,
        'product_count_in_cart': cart_count,
        'categories': CATEGORIES_LIST,
        'selected_category': request.GET.get('category', 'All'),
        'selected_sort': request.GET.get('sort', ''),
        'query': request.GET.get('query', '')
    }
    return render(request, 'ecom/customer_home.html', context)

@login_required(login_url='customerlogin')
def customer_address_view(request):
    cart_count = get_cart_count(request)
    product_in_cart = cart_count > 0

    initial_data = {}
    try:
        cust = models.Customer.objects.get(user_id=request.user.id)
        initial_data = {
            'Email': request.user.email,
            'Mobile': cust.mobile,
            'Address': cust.address
        }
    except Exception:
        pass

    addressForm = forms.AddressForm(initial=initial_data)
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']

            total = 0
            if 'product_ids' in request.COOKIES and request.COOKIES['product_ids']:
                product_id_in_cart = [pid for pid in request.COOKIES['product_ids'].split('|') if pid]
                products = models.Product.objects.filter(id__in=product_id_in_cart)
                for p in products:
                    total += p.price

            coupon = request.COOKIES.get('coupon_code', '')
            discount = 0
            if coupon == 'SAVE10':
                discount = int(total * 0.10)
            elif coupon == 'WELCOME20':
                discount = int(total * 0.20)

            shipping = 0 if total >= 999 or total == 0 else 99
            final_total = max(0, total - discount + shipping)

            response = render(request, 'ecom/payment.html', {
                'total': final_total,
                'subtotal': total,
                'discount': discount,
                'shipping': shipping
            })
            response.set_cookie('email', email)
            response.set_cookie('mobile', str(mobile))
            response.set_cookie('address', address)
            return response

    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': cart_count
    })

@login_required(login_url='customerlogin')
def payment_success_view(request):
    try:
        customer = models.Customer.objects.get(user_id=request.user.id)
    except models.Customer.DoesNotExist:
        customer = None

    payment_method = request.POST.get('payment_method', 'Card / Online')
    email = request.COOKIES.get('email', request.user.email)
    mobile = request.COOKIES.get('mobile', '')
    address = request.COOKIES.get('address', '')

    new_orders = []
    if 'product_ids' in request.COOKIES and request.COOKIES['product_ids']:
        raw_ids = [pid for pid in request.COOKIES['product_ids'].split('|') if pid]
        products = models.Product.objects.filter(id__in=raw_ids)
        for prod in products:
            order = models.Orders.objects.create(
                customer=customer,
                product=prod,
                status='Order Confirmed',
                email=email,
                mobile=mobile,
                address=address,
                payment_method=payment_method,
                total_price=prod.price
            )
            new_orders.append(order)

    response = render(request, 'ecom/payment_success.html', {
        'orders': new_orders,
        'payment_method': payment_method,
        'email': email,
        'address': address
    })
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    response.delete_cookie('coupon_code')
    return response

@login_required(login_url='customerlogin')
def my_order_view(request):
    try:
        customer = models.Customer.objects.get(user_id=request.user.id)
        orders = models.Orders.objects.filter(customer_id=customer).select_related('product').order_by('-id')
    except models.Customer.DoesNotExist:
        orders = []

    cart_count = get_cart_count(request)
    ordered_products = [o.product for o in orders]

    return render(request, 'ecom/my_order.html', {
        'orders': orders,
        'data': zip(ordered_products, orders),
        'product_count_in_cart': cart_count
    })

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

@login_required(login_url='customerlogin')
def download_invoice_view(request, orderID, productID):
    order = get_object_or_404(models.Orders, id=orderID)
    product = get_object_or_404(models.Product, id=productID)
    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user.get_full_name() or request.user.username,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': order.address,
        'orderStatus': order.status,
        'paymentMethod': order.payment_method,
        'orderId': order.id,
        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,
    }
    return render_to_pdf('ecom/download_invoice.html', mydict)

@login_required(login_url='customerlogin')
def my_profile_view(request):
    try:
        customer = models.Customer.objects.get(user_id=request.user.id)
    except models.Customer.DoesNotExist:
        customer = None
    cart_count = get_cart_count(request)
    return render(request, 'ecom/my_profile.html', {'customer': customer, 'product_count_in_cart': cart_count})

@login_required(login_url='customerlogin')
def edit_profile_view(request):
    customer, _ = models.Customer.objects.get_or_create(user_id=request.user.id)
    user = request.user
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.FILES or None, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            messages.success(request, "Profile updated successfully! Please re-login.")
            return HttpResponseRedirect('my-profile')
    return render(request, 'ecom/edit_profile.html', context=mydict)

def aboutus_view(request):
    cart_count = get_cart_count(request)
    return render(request, 'ecom/aboutus.html', {'product_count_in_cart': cart_count})

def contactus_view(request):
    sub = forms.ContactusForm()
    cart_count = get_cart_count(request)
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            name = sub.cleaned_data['Name']
            email = sub.cleaned_data['Email']
            message = sub.cleaned_data['Message']
            try:
                send_mail(f"{name} || {email}", message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently=True)
            except Exception:
                pass
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form': sub, 'product_count_in_cart': cart_count})
