from django.db.models import ExpressionWrapper, F, FloatField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import *


class SectionsView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        return render(request, 'sections.html')


class ProductsView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        products = Product.objects.filter(branch=request.user.branch).annotate(
            total=ExpressionWrapper(
                F('quantity') * F('price'),
                output_field=FloatField()
            )
        ).order_by('-total')

        editedProductID = request.GET.get('editedProductID')
        if editedProductID:
            editedProduct = get_object_or_404(Product, pk=int(editedProductID))
        else:
            editedProduct = None

        context = {
            'products': products,
            'editedProduct': editedProduct,
            'branch': request.user.branch,
        }

        return render(request, 'products.html', context)

    def post(self, request):
        if request.user.branch is None:
            return redirect('products')
        Product.objects.create(
            name=request.POST.get('name'),
            brand=request.POST.get('brand'),
            price=request.POST.get('price'),
            quantity=request.POST.get('quantity'),
            unit=request.POST.get('unit'),
            branch=request.user.branch,
        )
        return redirect('products')


class ProductUpdateView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        context = {
            'product': product,
        }
        return render(request, 'product-update.html', context)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.unit = request.POST.get('unit')
        product.save()
        return redirect('products')
