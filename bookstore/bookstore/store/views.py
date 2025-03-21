from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Book, Cart
from .forms import SignupForm
from .models import  Comment, Rating
from .forms import CommentForm, RatingForm
import stripe
from decimal import Decimal 
from .forms import CheckoutForm
from django.conf import settings
from .models import Book, Cart, Order, OrderItem, Payment,Coupon,Category


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    discount = Decimal(0)  
    applied_coupon = None

    if request.method == "POST" and "apply_coupon" in request.POST:  
        coupon_code = request.POST.get("coupon_code")
        if coupon_code:
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                discount = (Decimal(applied_coupon.discount_percentage) / Decimal(100)) * total_price
                total_price -= discount
                request.session["applied_coupon"] = applied_coupon.code  # ✅ Save applied coupon in session
            except Coupon.DoesNotExist:
                applied_coupon = None

        return render(request, "store/checkout.html", {
            "total_price": total_price,
            "discount": discount,
            "applied_coupon": applied_coupon,
            "cart_items": cart_items
        })

    if request.method == "POST" and "proceed_payment" in request.POST:  # ✅ Process payment separately
        applied_coupon_code = request.session.get("applied_coupon", None)
        applied_coupon = Coupon.objects.filter(code=applied_coupon_code).first() if applied_coupon_code else None

        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(item.book.price * 100),  # Convert price to cents
                    'product_data': {'name': item.book.title},
                },
                'quantity': item.quantity,
            } for item in cart_items
        ]

        if not line_items:
            return render(request, "store/checkout.html", {
                "total_price": total_price,
                "discount": discount,
                "applied_coupon": applied_coupon,
                "cart_items": cart_items,
                "error": "Your cart is empty. Add books before proceeding to checkout."
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/order-success/'),
            cancel_url=request.build_absolute_uri('/checkout/'),
        )

        # ✅ Save order before payment is completed
        order = Order.objects.create(
            user=request.user,
            total_price=total_price + discount,  # Original price before discount
            discounted_price=total_price,
            coupon=applied_coupon
        )

        return redirect(session.url, code=303)

    return render(request, "store/checkout.html", {
        "total_price": total_price,
        "discount": discount,
        "applied_coupon": applied_coupon,
        "cart_items": cart_items
    })

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            discount = (coupon.discount_percentage / 100) * total_price
            total_price -= discount
        except Coupon.DoesNotExist:
            discount = 0
    return render(request, 'store/checkout.html', {'total_price': total_price, 'discount': discount})
def order_success(request):
    return render(request, "store/order_success.html")

# Home View (Show All Books)
def home(request):
    categories = Category.objects.all()  # ✅ Fetch all categories
    category_id = request.GET.get("category")  # ✅ Get selected category from URL
    search_query = request.GET.get("search")  # ✅ Get search query
    books = Book.objects.all()

    if category_id:  # ✅ If a category is selected, filter books
        books = books.filter(category_id=category_id)

    if search_query:  # ✅ If search query exists, filter books by title
        books = books.filter(title__icontains=search_query)

    return render(request, 'store/home.html', {
        'books': books,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query
    })
def order_status(request):
    orders = Order.objects.filter(user=request.user).exclude(total_price=0)  # ✅ Hide zero-price orders
    return render(request, 'store/order_status.html', {'orders': orders})

# Signup View
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "store/signup.html", {"form": form})

# Login View
def login_view(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "store/login.html", {"form": form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")

# Add Book to Cart
@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart")

# View Cart
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, "store/cart.html", {"cart_items": cart_items})
@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    comments = book.comments.all()
    average_rating = book.average_rating()
    
    if request.method == "POST":
        if "comment_submit" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.book = book
                comment.save()
                return redirect('book_detail', book_id=book.id)

        if "rating_submit" in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating, created = Rating.objects.update_or_create(
                    user=request.user, book=book, defaults={'value': rating_form.cleaned_data['value']}
                )
                return redirect('book_detail', book_id=book.id)
    
    else:
        comment_form = CommentForm()
        rating_form = RatingForm()

    return render(request, "store/book_detail.html", {
        "book": book,
        "comments": comments,
        "comment_form": comment_form,
        "rating_form": rating_form,
        "average_rating": average_rating,
    })

@login_required
def remove_from_cart(request, book_id):
    cart_item = get_object_or_404(Cart, user=request.user, book_id=book_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1  # Reduce quantity if more than 1
        cart_item.save()
    else:
        cart_item.delete()  # Remove from cart if quantity is 1
    return redirect("cart")

def search_books(request):
    query = request.GET.get("category")
    books = Book.objects.filter(category__name__icontains=query)
    return render(request, "store/book_list.html", {"books": books})


# ✅ Order Status Page (List all orders of logged-in user)
@login_required
def order_status(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_status.html', {'orders': orders})
