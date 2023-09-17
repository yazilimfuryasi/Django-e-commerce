from .models import CartItem, Cart
import json

def cart_item_count(request):
    urunSayisi = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        urunSayisi = CartItem.objects.filter(cart=cart).count()
    else:
        try:
            data = request.COOKIES.get('cart')
            urunler = json.loads(data)
            urunSayisi = len(urunler)
        except:
            urunSayisi = 0
    DATA = {
        "cart_item_count": urunSayisi,
    }
    return DATA
