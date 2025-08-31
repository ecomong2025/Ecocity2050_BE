from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, UserDetailView, kakao_login, kakao_callback

urlpatterns = [
    # JWT 로그인 / 토큰
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 로그인 후 사용자 정보
    path("user/", UserDetailView.as_view(), name="user_detail"),

    # 카카오 로그인
    path("users/kakao/login/", kakao_login, name="kakao_login"),
    path("users/kakao/callback/", kakao_callback, name="kakao_callback"),
]
