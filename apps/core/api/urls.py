from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/table/', lambda request: render(request, 'client_table.html'), name='client_table'),
    path('vip-membership/<str:token_registrazione>/', views.VipMembershipView.as_view(), name='vip_membership'),
    path('upload_vip_file/<str:token_registrazione>/', views.UploadVipFileView.as_view(), name='upload_vip_file'),
    path('vip_counts/<str:token_registrazione>/', views.VipCountsView.as_view(), name='vip_counts'),  # Fixed typo in name
    path('register/<str:token_registrazione>/', views.CustomerRegistrationView.as_view(), name='customer_registration'),
    path('regenerate_token/<int:id_negozio>/', views.RegenerateTokenView.as_view(), name='regenerate_token'),
    path('add_client/', views.AddClientView.as_view(), name='add_client'),
]
