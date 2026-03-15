from django.urls import path
from documents import views

urlpatterns = [
    # Asset endpoints
    path('', views.list_assets, name='list_assets'),
    path('upload/', views.upload_asset, name='upload_asset'),
    path('<uuid:asset_id>/', views.get_asset, name='get_asset'),
    path('<uuid:asset_id>/delete/', views.delete_asset, name='delete_asset'),

    # Death certificate (Absher — not activated)
    path(
        'death-certificate/',
        views.upload_death_certificate,
        name='upload_death_certificate'
    ),

    # Beneficiary endpoints
    path(
        'beneficiary/add/',
        views.add_beneficiary,
        name='add_beneficiary'
    ),
    path(
        'beneficiary/assign/',
        views.assign_asset_to_beneficiary,
        name='assign_asset_to_beneficiary'
    ),
]