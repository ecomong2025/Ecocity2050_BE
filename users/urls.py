from django.urls import path
from . import views

urlpatterns = [
    # JWT 로그인
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 사용자 정보 조회
    path('profile/', views.UserDetailView.as_view(), name='user_detail'),

    # allauth 기반 카카오 로그인 처리
    path('kakao/login/', views.KakaoLoginView.as_view(), name='kakao_login_api'),


    path('kakao/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback_api'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]