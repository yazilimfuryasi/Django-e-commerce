import json
from .models import Product, Cart, CartItem

class CartDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Kullanıcı oturum açtıysa çerezlerdeki verileri veritabanına kaydet
            data = request.COOKIES.get("cart")
            if data:
                cart_data = json.loads(data)

                # Sepet verilerini veritabanına kaydet
                for product_id, quantity in cart_data.items():
                    product = Product.objects.get(pk=product_id)
                    cart, _ = Cart.objects.get_or_create(user=request.user)
                    cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
                    cart_item.quantity = quantity
                    cart_item.save()

                # Çerezleri temizle
                response = self.get_response(request)
                response.delete_cookie('cart')
                return response

        # Kullanıcı oturum açmadıysa normal işlem devam etsin
        response = self.get_response(request)
        return response
