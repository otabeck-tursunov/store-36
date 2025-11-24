from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import *


class SalesView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        sales = Sale.objects.filter(branch=request.user.branch).order_by('-created_at')
        products = Product.objects.filter(branch=request.user.branch).order_by('name')
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')

        context = {
            'sales': sales,
            'products': products,
            'clients': clients,
        }
        return render(request, 'sales.html', context)

    def post(self, request):
        client = get_object_or_404(Client, id=request.POST['client_id'])
        product = get_object_or_404(Product, id=request.POST['product_id'])
        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') is not None else None
        total_price = float(request.POST.get('total_price')) if request.POST.get('total_price') is not None else None
        paid = float(request.POST.get('paid_price')) if request.POST.get('paid_price') is not None else None
        debt = float(request.POST.get('debt_price')) if request.POST.get('debt_price') is not None else None

        # check product quantity
        context = self.check_enough_product(product, quantity)
        if context is not None:
            return render(request, 'warning.html', context)

        # debt & paid -> not None
        if debt and paid:
            total_price = debt + paid

        # calculate total_price
        if not total_price:
            total_price = product.price * quantity

        # paid & debt -> None
        if not paid and not debt:
            paid = total_price

        # debt -> None
        if not debt and paid:
            debt = total_price - paid

        # paid -> None
        if not paid and debt:
            paid = total_price - debt

        Sale.objects.create(
            product=product,
            client=client,
            quantity=quantity,
            total_price=total_price,
            paid_price=paid,
            debt_price=debt,
            user=request.user,
            branch=request.user.branch
        )

        # sub product quantity
        product.quantity -= quantity
        product.save()

        # add client debt
        client.debt += debt
        client.save()

        return redirect('sales')

    def check_enough_product(self, product, quantity):
        if product.quantity < quantity:
            warning_message = f"{product.name} so'ralgan miqdorda mavjud emas! Mavjud: {product.quantity} {product.unit}"
            warning_title = "Mahsulot yetarli emas!"
            back_url = 'sales'
            context = {
                'warning_message': warning_message,
                'warning_title': warning_title,
                'back_url': back_url,
            }
            return context
        return None


class ImportProductsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        import_products = ImportProduct.objects.filter(branch=request.user.branch).order_by('-created_at')

        search = request.GET.get('search')
        if search:
            import_products = import_products.filter(product__name__icontains=search)

        products = Product.objects.filter(branch=request.user.branch).order_by('name')

        context = {
            'import_products': import_products,
            'products': products,
            'search': search,
        }
        return render(request, 'import-products.html', context)

    def post(self, request):
        product = get_object_or_404(Product, id=request.POST['product_id'])
        quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') is not None else None
        ImportProduct.objects.create(
            product=product,
            quantity=quantity,
            buy_price=request.POST.get('buy_price'),
            user=request.user,
            branch=request.user.branch
        )
        product.quantity += quantity
        product.save()
        return redirect('imports')


class PayDebtsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        pay_debts = PayDebt.objects.filter(branch=request.user.branch).order_by('-created_at')
        clients = Client.objects.filter(branch=request.user.branch).order_by('name')
        context = {
            'pay_debts': pay_debts,
            'clients': clients,
        }
        return render(request, 'pay-debts.html', context)

    def post(self, request):
        client = get_object_or_404(Client, id=request.POST.get('client_id'))
        price = float(request.POST.get('price')) if request.POST.get('price') is not None else None

        if price == 0:
            return redirect('pay-debts')

        PayDebt.objects.create(
            client=client,
            price=price,
            description=request.POST.get('description'),
            user=request.user,
            branch=request.user.branch
        )

        client.debt -= price
        client.save()
        return redirect('pay-debts')
