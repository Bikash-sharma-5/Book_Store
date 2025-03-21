from django.urls import path
from .views import (
    home, book_detail, signup_view, login_view, logout_view, 
    add_to_cart, view_cart, remove_from_cart,checkout,order_success, apply_coupon, order_status, search_books
)

urlpatterns = [
    path("", home, name="home"),
    path("book/<int:book_id>/", book_detail, name="book_detail"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("cart/", view_cart, name="cart"),
    path("cart/add/<int:book_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:book_id>/", remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout, name="checkout"),
    path('apply-coupon/', apply_coupon, name='apply_coupon'),  # ✅ Apply Discount Coupon
    path('order-status/', order_status, name='order_status'),  # ✅ Track Order Status
    path('search/', search_books, name='search_books'),
    path("order-success/", order_success, name="order_success"),
]
