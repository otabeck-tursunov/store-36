from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', SalesView.as_view(), name='sales'),
    path('imports/', ImportProductsView.as_view(), name='imports'),
    path('client-debt-payments/', PayDebtsView.as_view(), name='pay-debts'),
]
