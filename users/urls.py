from django.urls import path
from . import views

urlpatterns = [
    # JWT 로그인
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 사용자 정보 조회
    path('profile/', views.UserDetailView.as_view(), name='user_detail'),

    # 카카오 로그인 관련
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('kakao/userinfo/', views.kakao_userinfo, name='kakao_userinfo'),
    path('kakao/logout/', views.kakao_logout, name='kakao_logout'),
]