from django.contrib import admin
from .models import Book, Order, OrderItem, Payment,Coupon
from .models import  Category
import random


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status']
    list_editable = ['status']  # ✅ Allows admin to change order status

# ✅ Check if already registered before registering
if not admin.site.is_registered(Order):
    admin.site.register(Order, OrderAdmin)
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active')  # ✅ Show in admin list
    search_fields = ('code',)  # ✅ Allow searching by coupon code
    list_filter = ('is_active',)  # ✅ Filter active/inactive coupons




# ✅ Bulk Add 50 Books Function
def bulk_add_books(modeladmin, request, queryset):
    sample_books = [
        "Django for Beginners", "Advanced Django", "Python Crash Course",
        "Deep Learning with Python", "Fluent Python", "Automate the Boring Stuff",
        "Clean Code", "The Pragmatic Programmer", "Design Patterns",
        "Data Science from Scratch", "Machine Learning with Python",
        "Python Data Analysis", "JavaScript: The Good Parts",
        "Eloquent JavaScript", "You Don't Know JS", "HTML & CSS Design",
        "React for Beginners", "Node.js Design Patterns",
        "Full Stack Development with Django", "The Mythical Man-Month"
    ]

    categories = list(Category.objects.all())  # ✅ Fetch existing categories

    if not categories:
        modeladmin.message_user(request, "No categories found! Please add categories first.", level='ERROR')
        return

    book_instances = []
    for i in range(50):
        book = Book(
            title=random.choice(sample_books) + f" #{i+1}",  # ✅ Make unique titles
            author=f"Author {i+1}",
            price=random.uniform(10, 50),  # ✅ Random price between 10-50
            category=random.choice(categories)  # ✅ Assign to a random existing category
        )
        book_instances.append(book)

    Book.objects.bulk_create(book_instances)  # ✅ Bulk insert 50 books
    modeladmin.message_user(request, "50 books added successfully!")

bulk_add_books.short_description = "🔄 Bulk Add 50 Books"  # ✅ Ensure it's registered in admin panel

# ✅ Register Book Admin
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'category')
    list_filter = ('category',)
    search_fields = ('title', 'author')
    ordering = ('title',)
    actions = [bulk_add_books]  # ✅ Add bulk action here

admin.site.register(Category)  # ✅ Register categories
admin.site.register(Book, BookAdmin)  # ✅ Register books
