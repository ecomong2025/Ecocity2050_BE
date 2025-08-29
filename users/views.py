from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from .serializers import UserSerializer
from .models import CustomUser

# 회원 정보 조회
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# JWT 로그인/로그아웃은 simplejwt 제공
