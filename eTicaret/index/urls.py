from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sepet/", views.sepet, name="sepet"),
    path('sepet/remove/<int:id>/', views.sepetUrunSil, name='remove'),
    path("shop/", views.shop, name="shop"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("shop/<str:slug>/", views.shop, name="shop2"),
    path("shop/<str:slug>/<str:id>", views.details, name="details"),

    path("admin/", admin.site.urls),
    path("accounts/login/", views.signin, name="login"),
    path("accounts/signup/", views.register, name="register"),
    path('accounts/', include('allauth.urls')),
    path('logout', views.logoutPage, name="logout"),

    # Django'nun sunduğu standart şifre sıfırlama fonksiyonları
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('email-verify/<str:uidb64>/<str:token>/', views.email_verify, name='email-verify'),

]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
