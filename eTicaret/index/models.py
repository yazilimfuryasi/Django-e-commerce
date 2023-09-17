from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.contrib.auth.models import User
from campains.models import Campaign
from decimal import Decimal

class Category(MPTTModel):
    slug = models.SlugField(null=True, allow_unicode=True, blank=True, db_index=False)
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugTR = str.maketrans("çğıöüş","cgious")
            self.slug = slugify(self.name.translate(slugTR))
        super().save(*args, **kwargs)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
    
class Product(models.Model):
    slug = models.SlugField(null=True, allow_unicode=True, blank=True, db_index=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    images = models.ManyToManyField(ProductImage, blank=True)
    brand = models.CharField(max_length=100)  # Marka bilgisi
    color = models.CharField(max_length=50)  # Renk bilgisi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Kampanyalar
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    discounted_price = models.FloatField(blank=True, null=True)

    def calculate_discounted_price(self):
        if self.campaign:
            discount_rate = Decimal(self.campaign.discount_rate) / Decimal(100)
            self.discounted_price = self.price - (self.price * discount_rate)
            self.discounted_price = self.discounted_price.quantize(Decimal('0.01'))
        else:
            self.discounted_price = None

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.calculate_discounted_price()
        if not self.slug:
            slugTR = str.maketrans("çğıöüş","cgious")
            self.slug = slugify(self.name.translate(slugTR))
        super().save(*args, **kwargs)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

# Kargo Ücreti
class ShippingFee(models.Model):
    limit = models.DecimalField("Ücretsiz Kargo Limiti", max_digits=10, decimal_places=2, default=300)
    kargo_bedeli = models.DecimalField("Kargo Ücreti", max_digits=10, decimal_places=2, default=20)
    def __str__(self) -> str:
        return "Ücretsiz Kargo Limiti"
    