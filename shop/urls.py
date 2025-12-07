from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.category_page, name='category'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('review/<int:pk>/', views.add_review, name='add_review'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.orders, name='orders'),
    path('wishlist/', views.wishlist_list, name='wishlist'),
    path('wishlist/add/<int:pk>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:pk>/', views.wishlist_remove, name='wishlist_remove'),
    path('api/products/', views.products_json, name='products_json'),
    path('api/products/<int:pk>/', views.product_json, name='product_json'),
    path('api/categories/', views.categories_json, name='categories_json'),
]
