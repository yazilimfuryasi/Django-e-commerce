from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Category, Product, Cart, CartItem, ShippingFee
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
import json
from urllib.parse import unquote

def index(request):
    parametre = request.GET.get("search")
    q = unquote(parametre) if parametre else ''
    result = Product.objects.filter(Q(name__icontains=q) | Q(description__icontains=q))
    products_with_images = []
    for i in result:
        images = i.images.filter(product=i)[:1]
        products_with_images.append({
            'product': i,
            'images': images,
        })
    
    DATA = {
        "product": products_with_images
    }
    return render(request, 'index.html', DATA)

def get_category_tree(node, slug=None):
    children = list(node.get_children())
    if not children:
        return {
            'id': node.slug,
            'name': node.name,
            'is_active': slug == node.name, # geçerli yoldaysak
        }
    return {
        'id': node.slug,
        'name': node.name,
        'children': [get_category_tree(child, slug) for child in children],
    }

def details(request, slug, id):
    product_ = Product.objects.get(slug=id)
    home_category = Category.objects.get(id=product_.category_id, slug=slug)
    # Kategori ağacını oluşturun
    category_tree = home_category.get_ancestors(include_self=True)
    # Ürün Resimleri
    images = product_.images.all()
    DATA = {
            "category":category_tree,
            "product": product_,
            "images": images,
        }
    return render(request, "product-details.html", DATA)

def sepet(request):
    item = []
    total_amount = 0

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart__user=request.user)
        
        for i in cart_items:
            product = i.product
            product_image = product.images.first()
            urunFiyat = product.discounted_price if product.discounted_price else product.price
            urunFiyat *= i.quantity
            total_amount += float(urunFiyat)
            item.append({
                "id": product.id,
                "name": product.name,
                "price": urunFiyat,
                "image": product_image.image if product_image else None,
                "quantity": i.quantity,
                "slug": product.slug,
                "category": product.category.slug,
            })

    else:
        cart_data = request.COOKIES.get('cart')
        if cart_data:
            cart = json.loads(cart_data)
            for product_id, quantity in cart.items():
                product = Product.objects.get(pk=product_id)
                urunFiyat = product.discounted_price if product.discounted_price else product.price
                urunFiyat *= quantity
                total_amount += float(urunFiyat)
                item.append({
                    "id": product.id,
                    "name": product.name,
                    "price": urunFiyat,
                    "image": product.images.first().image if product.images.exists() else None,
                    "quantity": int(quantity),
                    "slug": product.slug,
                    "category": product.category.slug,
                })

    # Kargo Ücreti
    kargo = 0
    ucretsizKargo = ShippingFee.objects.get()
    if int(total_amount) >= ucretsizKargo.limit: kargo = 0
    else: kargo = ucretsizKargo.kargo_bedeli
    toplam = float(total_amount) + float(kargo)

    return render(request, "sepet.html", {"item": item, "total": total_amount, "kargo":kargo, "toplam": toplam})

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        if not quantity: quantity = 1
        product = Product.objects.get(pk=product_id)

        cart_data = request.COOKIES.get('cart')
        if cart_data:
            cart = json.loads(cart_data)
        else:
            cart = {}
        if request.user.is_authenticated:
            # Kullanıcı oturum açmışsa
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        else:
            # Kullanıcı oturum açmamışsa çerezlerden sepet bilgisini al
            cart[str(product_id)] = cart.get(str(product_id), 0) + int(quantity)
            response = JsonResponse({'status': 'success', 'cart_item_count': len(cart)})
            response.set_cookie('cart', json.dumps(cart))
            return response
        try:
            if int(cart_item.quantity) < 1 or int(quantity) > 1000000:
                cart_item.quantity = 1
        except:
            cart_item.quantity = 1
        if not item_created: cart_item.quantity += int(quantity)
        else: cart_item.quantity = int(quantity)
        # cart_item.quantity += int(quantity)
        cart_item.save()
        cart_item_count = CartItem.objects.filter(cart=cart).count()
        response = JsonResponse({'status': 'success', 'cart_item_count': cart_item_count})
        
        if not request.user.is_authenticated:
            # Kullanıcı oturum açmamışsa çerezlere sepet bilgisini kaydet
            cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
            response.set_cookie('cart', json.dumps(cart))
        return response
    else: return JsonResponse({'status': 'error'})

def shop(request, slug=None):
    try: default = Category.objects.all()[1]
    except: default = Category.objects.first()
    if slug: current_category = Category.objects.get(slug=slug)
    else: current_category = default
    
    tree = get_category_tree(default, current_category.name)
    
    sort_option = request.GET.get('sirala')
    if sort_option == 'Sıralı':
        urunler = Product.objects.filter(category_id=current_category.id).order_by("id")
    elif sort_option == 'Artan':
        urunler = Product.objects.filter(category_id=current_category.id).order_by("price")
    elif sort_option == 'Azalan':
        urunler = Product.objects.filter(category_id=current_category.id).order_by("-price")
    else:
        urunler = Product.objects.filter(category_id=current_category.id).order_by("id")
    
    # Fiyat filtresi için değerleri alın
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        urunler = urunler.filter(price__gte=min_price, price__lte=max_price)
    elif min_price:
        urunler = urunler.filter(price__gte=min_price)
    elif max_price:
        urunler = urunler.filter(price__lte=max_price)

    paginator = Paginator(urunler, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    page_range = paginator.page_range
    products_with_images = []
    for i in page_obj:
        images = i.images.filter(product=i)[:2]
        products_with_images.append({
            'product': i,
            'images': images,
        })
    DATA = {
        'tree': tree,
        "urunler": products_with_images,
        "current_path": current_category.slug,
        "page_obj": page_obj,
        'page_range': page_range,
        'sort': "Sıralı" if sort_option == None else sort_option,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop.html', DATA)

def sepetUrunSil(request, id):
    if request.user.is_authenticated:
        urun = CartItem.objects.filter(cart__user=request.user, product_id=id).first()
    
        if urun.quantity > 1:
            urun.quantity -= 1
            urun.save()
        else: urun.delete()
    else:
        data = request.COOKIES.get("cart")
        urun = json.loads(data) if data else {}
        if str(id) in urun:
            adet = int(urun[str(id)])
            if adet > 1:
                urun[str(id)] = adet - 1
            else: del urun[str(id)]

            response = JsonResponse({'status': 'success', "cart": urun})
            response.set_cookie("cart", json.dumps(urun))
            return response
    return JsonResponse({"status":"success"})

def email_verify(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, 'E-posta adresiniz zaten onaylı.')
            return redirect(signin)

        user.is_active = True
        user.save()
        messages.success(request, "E-posta adresiniz onaylandı! Giriş yapabilirsiniz.")
        return redirect(signin)
    else:
        messages.error(request, "Onaylanırken bir sorun oluştu.")
        return redirect('index')

def send_email_verify(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    domain = current_site.domain
    email_subject = 'E-posta Onayı'
    email_body = render_to_string('login/mail_onay.html', {
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token,
    })
    send_mail(email_subject, email_body, 'user@example.com', [user.email])
    print("Mail Gönderildi")

def signin(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("login")
        password = request.POST.get("password")
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        messages.error(request, "Username or Password Not Correct")
        return redirect(signin)
    return render(request, "login/login.html")

def register(request):
    if request.user.is_authenticated: 
        return redirect(index)

    if request.method == "POST":
        post = request.POST
        if post.get("password1") == post.get("password2") and post.get("username") and post.get("email"):
            username = post.get("username")
            password = post.get("password1")
            user = User.objects.create_user(username=username, email=post.get("email"), password=password)
            user.is_active = False
            user.save()
            send_email_verify(request, user)
            return redirect(signin)
        return redirect("register")
    return render(request, "login/register.html")

# Oturumu sonlandırma
@login_required(login_url="login")
def logoutPage(request):
    logout(request)
    return redirect(index)

# Özel Şifre Sıfırlama Maili Şablonu Göndermek

# from django.shortcuts import render, get_object_or_404
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.urls import reverse
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes

# def send_custom_password_reset_email(request):
#     if request.method == 'POST':
#         user = get_object_or_404(User, email=request.POST.get('email'))

#         # Şifre sıfırlama token'ını oluşturma
#         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         # Özel e-posta şablonu oluşturma
#         subject = 'Şifre Sıfırlama'
#         reset_link = f"{request.scheme}://{request.get_host()}{reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})}"
#         html_message = render_to_string('registration/password_reset_email.html', {
#             'user': user,
#             'reset_link': reset_link
#         })
#         plain_message = strip_tags(html_message)
#         # E-postayı gönderme
#         send_mail(subject, plain_message, 'user@example.com', [user.email], html_message=html_message)
#         return render(request, 'login/password_reset.html', {"success":True})
#     return render(request, 'login/password_reset.html')

