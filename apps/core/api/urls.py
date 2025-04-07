from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/table/', lambda request: render(request, 'client_table.html'), name='client_table'),  # Updated path
]
