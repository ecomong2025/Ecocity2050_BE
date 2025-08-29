from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from .serializers import UserSerializer
from .models import CustomUser
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairView(TokenObtainPairView):

    @swagger_auto_schema(operation_description="JWT 토큰 발급")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# 회원 정보 조회
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# JWT 로그인/로그아웃은 simplejwt 제공
