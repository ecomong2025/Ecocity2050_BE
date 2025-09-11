from django.urls import path
from . import views

urlpatterns = [
    # JWT 로그인
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 사용자 정보 조회
    path('profile/', views.UserDetailView.as_view(), name='user_detail'),

    # 웹용 카카오 로그인 처리
    path('kakao/login/', views.KakaoLoginView.as_view(), name='kakao_login_api'),

    # Unity용 카카오 로그인 처리
    path('kakao/unity/login/', views.KakaoUnityLoginView.as_view(), name='kakao_unity_login'),
    path('kakao/unity/session/', views.KakaoUnitySessionView.as_view(), name='kakao_unity_session'),

    # 카카오 콜백 (웹/Unity 공용)
    path('kakao/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback_api'),

    # 로그아웃
    path('logout/', views.LogoutView.as_view(), name='logout'),
]