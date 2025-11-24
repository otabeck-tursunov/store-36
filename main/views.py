from django.db.models import ExpressionWrapper, F, FloatField, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import *


def home(request):
    return redirect('sections')


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

        search = request.GET.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search)
            )

        context = {
            'products': products,
            'branch': request.user.branch,
            'search': search,
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


class ClientsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        clients = Client.objects.filter(branch=request.user.branch)

        context = {
            'clients': clients,
        }
        return render(request, 'clients.html', context)

    def post(self, request):
        Client.objects.create(
            name=request.POST.get('name'),
            shop_name=request.POST.get('shop_name'),
            phone_number=request.POST.get('phone_number'),
            address=request.POST.get('address'),
            debt=request.POST.get('debt'),
            branch=request.user.branch,
        )
        return redirect('clients')

