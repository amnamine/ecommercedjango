def cart_summary(request):
    cart = request.session.get('cart', {})
    wishlist = request.session.get('wishlist', [])
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
    return {
        'cart_count': cart_count,
        'wishlist_count': len(wishlist) if isinstance(wishlist, list) else 0,
    }
