from rest_framework import generics

from django.contrib.auth import get_user_model

from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated


from .serializers import (
    RegisterSerializer,
    UserSerializer,
    NationalIDTokenSerializer
)


User = get_user_model()


class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = RegisterSerializer


    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({

            "user": UserSerializer(user).data,

            "refresh": str(refresh),

            "access": str(refresh.access_token),

        })


class NationalIDLoginView(TokenObtainPairView):

    serializer_class = NationalIDTokenSerializer


@api_view(['GET'])

@permission_classes([IsAuthenticated])

def test_protected(request):

    return Response({

        "message":"You are authenticated",

        "user":request.user.national_id

    })