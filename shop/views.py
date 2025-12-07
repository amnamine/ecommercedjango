from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Product, Category, Review, Order, OrderItem, Coupon


def product_list(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('category')
    sort = request.GET.get('sort', 'new')
    base = Product.objects.all()
    if q:
        base = base.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if cat:
        base = base.filter(category__slug=cat)
    base = base.annotate(avg_rating=Avg('reviews__rating'))
    if sort == 'price_asc':
        base = base.order_by('price')
    elif sort == 'price_desc':
        base = base.order_by('-price')
    else:
        base = base.order_by('-created_at')
    paginator = Paginator(base, 8)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    categories = Category.objects.all()
    featured = Product.objects.filter(featured=True).order_by('-created_at')[:6]
    rv_ids = request.session.get('recently_viewed', [])
    recently = Product.objects.filter(id__in=rv_ids)
    return render(request, 'shop/product_list.html', {
        'products': products,
        'q': q,
        'categories': categories,
        'active_category': cat,
        'sort': sort,
        'featured': featured,
        'recently': recently,
    })


def category_page(request, slug):
    request.GET = request.GET.copy()
    request.GET['category'] = slug
    return product_list(request)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    avg = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    reviews = product.reviews.select_related('user')
    rv = request.session.setdefault('recently_viewed', [])
    if pk not in rv:
        rv.insert(0, pk)
        request.session['recently_viewed'] = rv[:10]
        request.session.modified = True
    return render(request, 'shop/product_detail.html', {'product': product, 'avg': avg, 'reviews': reviews})


def _get_cart(session):
    return session.setdefault('cart', {})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = _get_cart(request.session)
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session.modified = True
    return redirect('shop:view_cart')


def remove_from_cart(request, pk):
    cart = _get_cart(request.session)
    key = str(pk)
    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            del cart[key]
        request.session.modified = True
    return redirect('shop:view_cart')


def view_cart(request):
    cart = _get_cart(request.session)
    items = []
    total = 0
    for key, qty in cart.items():
        product = get_object_or_404(Product, pk=int(key))
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    return render(request, 'shop/cart.html', {'items': items, 'total': total})


def update_cart(request, pk):
    cart = _get_cart(request.session)
    qty = int(request.POST.get('qty', '1'))
    key = str(pk)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    request.session.modified = True
    return redirect('shop:view_cart')


def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('shop:view_cart')


@login_required
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        return redirect('shop:product_list')
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zipc = request.POST.get('zip')
        items = []
        total = 0
        for key, qty in cart.items():
            product = get_object_or_404(Product, pk=int(key))
            price = product.price
            total += price * qty
            items.append((product, qty, price))
        coupon_code = request.POST.get('coupon', '').strip()
        discount_amount = 0
        if coupon_code:
            cp = Coupon.objects.filter(code__iexact=coupon_code, active=True).first()
            if cp:
                discount_amount = (total * cp.discount_percent) / 100
        grand_total = total - discount_amount
        order = Order.objects.create(user=request.user, full_name=full_name, address=address, city=city, zip=zipc, total=grand_total, coupon_code=coupon_code, discount_amount=discount_amount)
        for product, qty, price in items:
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
            product.stock = max(0, product.stock - qty)
            product.save()
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('shop:order_success', order.id)
    return render(request, 'shop/checkout.html')


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})


@login_required
def orders(request):
    qs = Order.objects.filter(user=request.user).order_by('-placed_at')
    return render(request, 'shop/orders.html', {'orders': qs})


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', '5'))
        text = request.POST.get('text', '')
        Review.objects.create(product=product, user=request.user, rating=rating, text=text)
    return redirect('shop:product_detail', pk=pk)


def wishlist_list(request):
    ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=ids)
    return render(request, 'shop/wishlist.html', {'products': products})


def wishlist_add(request, pk):
    wl = request.session.setdefault('wishlist', [])
    if pk not in wl:
        wl.append(pk)
        request.session.modified = True
    return redirect('shop:wishlist')


def wishlist_remove(request, pk):
    wl = request.session.setdefault('wishlist', [])
    if pk in wl:
        wl.remove(pk)
        request.session.modified = True
    return redirect('shop:wishlist')


def products_json(request):
    products = Product.objects.all()
    data = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price),
            'image_url': p.image_url,
            'stock': p.stock,
        }
        for p in products
    ]
    return JsonResponse({'products': data})


def product_json(request, pk):
    p = get_object_or_404(Product, pk=pk)
    data = {
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': float(p.price),
        'image_url': p.image_url,
        'stock': p.stock,
    }
    return JsonResponse(data)


def categories_json(request):
    cats = Category.objects.all().values('id', 'name', 'slug')
    return JsonResponse({'categories': list(cats)})
