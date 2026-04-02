from django.urls import path

from .views import (
    RegisterView,
    test_protected,
    NationalIDLoginView
)

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [

    path('register/', RegisterView.as_view()),

    path('login/', NationalIDLoginView.as_view()),

    path('refresh/', TokenRefreshView.as_view()),

    path('test-protected/', test_protected),

]