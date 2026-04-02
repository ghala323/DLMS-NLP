from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.MemberAssetListView.as_view(), name='asset-list'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset-detail'),
    path('assets/<int:pk>/edit/', views.AssetEditView.as_view(), name='asset-edit'),
    path('assets/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset-delete'),
    path('assets/<int:pk>/beneficiary-access/', views.BeneficiaryAssetAccessView.as_view(), name='beneficiary-asset-access'),
    path('members/<int:pk>/process-death/', views.TriggerPostDeathWorkflowView.as_view(), name='process-death'),
]