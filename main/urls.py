from django.urls import path
from .views import *

urlpatterns = [
    path('sections/', SectionsView.as_view(), name='sections'),
    path('products/', ProductsView.as_view(), name='products'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
]
