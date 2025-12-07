from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Sum, Avg, Count, F
from datetime import timedelta
from django.utils.timezone import now
from shop.models import Order, OrderItem, Product, Category, Review


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('shop:product_list')


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    User = get_user_model()
    q = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('-date_joined')
    if q:
        users = users.filter(username__icontains=q) | users.filter(email__icontains=q)
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__gte=now() - timedelta(days=7)).count()

    orders_count = Order.objects.count()
    revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
    avg_order = Order.objects.aggregate(avg=Avg('total'))['avg'] or 0
    recent_orders = Order.objects.select_related('user').order_by('-placed_at')[:10]

    top_products = (
        OrderItem.objects.values('product__id', 'product__name')
        .annotate(qty=Sum('quantity'), revenue=Sum(F('price') * F('quantity')))
        .order_by('-qty')[:5]
    )

    products_count = Product.objects.count()
    categories_count = Category.objects.count()
    reviews_count = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0

    return render(request, 'accounts/admin_dashboard.html', {
        'users': users,
        'q': q,
        'total_users': total_users,
        'new_users': new_users,
        'orders_count': orders_count,
        'revenue': revenue,
        'avg_order': avg_order,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'products_count': products_count,
        'categories_count': categories_count,
        'reviews_count': reviews_count,
        'avg_rating': avg_rating,
    })
