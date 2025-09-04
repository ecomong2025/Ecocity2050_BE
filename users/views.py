import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import UserSerializer

User = get_user_model()

# JWT 로그인 (username/password)
class MyTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(operation_description="JWT 토큰 발급 (username/password 로그인)")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# 회원 정보 조회 (JWT)
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(operation_description="현재 로그인한 사용자 정보 조회")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

# 카카오 로그인 시작: 인증 URL 반환
@swagger_auto_schema(
    method="get",
    operation_description="카카오 로그인 시작 URL 반환",
    responses={200: openapi.Response("OK", schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"auth_url": openapi.Schema(type=openapi.TYPE_STRING)}
    ))},
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def kakao_login(request):
    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?response_type=code&client_id={settings.KAKAO_REST_API_KEY}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
    )
    return Response({"auth_url": kakao_auth_url})

# 카카오 콜백: code로 JWT 발급 + 사용자 생성/로그인
code_param = openapi.Parameter(
    "code",
    openapi.IN_QUERY,
    description="카카오 OAuth 인가 코드",
    type=openapi.TYPE_STRING,
    required=True,
)

@swagger_auto_schema(
    method="get",
    operation_description="카카오 OAuth 콜백 (code로 JWT 발급)",
    manual_parameters=[code_param],
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def kakao_callback(request):
    code = request.GET.get("code")
    if not code:
        return Response({"error": "code가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 카카오 Access Token 요청
    token_req = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
        headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        timeout=10,
    )
    token_json = token_req.json()
    if token_req.status_code != 200 or token_json.get("error"):
        return Response({"error": token_json}, status=status.HTTP_400_BAD_REQUEST)

    kakao_access_token = token_json["access_token"]

    # 카카오 사용자 정보 요청
    profile_req = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {kakao_access_token}"},
        timeout=10,
    )
    if profile_req.status_code != 200:
        return Response({"error": "카카오 프로필 요청 실패"}, status=status.HTTP_400_BAD_REQUEST)

    profile = profile_req.json()
    kakao_id = profile.get("id")
    kakao_account = profile.get("kakao_account", {})
    nickname = (kakao_account.get("profile") or {}).get("nickname", "")

    if not kakao_id:
        return Response({"error": "카카오 ID 없음"}, status=status.HTTP_400_BAD_REQUEST)

    # 사용자 생성 또는 로그인
    try:
        user = User.objects.get(username=kakao_id)
        message = "login success"
    except User.DoesNotExist:
        user = User.objects.create_user(username=kakao_id)
        user.first_name = nickname or ""
        user.save()
        message = "register success"

    # JWT 발급
    token = TokenObtainPairSerializer.get_token(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    data = {
        "user": UserSerializer(user).data,
        "message": message,
        "token": {"access": access_token, "refresh": refresh_token},
    }
    resp = Response(data, status=status.HTTP_200_OK)

    # 쿠키 저장
    resp.set_cookie("accessToken", access_token, httponly=True, secure=True, samesite="None")
    resp.set_cookie("refreshToken", refresh_token, httponly=True, secure=True, samesite="None")
    return resp

# JWT 인증 기반 카카오 유저 인포 API
@swagger_auto_schema(
    method="get",
    operation_description="JWT 인증된 카카오 로그인 사용자 정보 반환",
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def kakao_userinfo(request):
    user = request.user
    return Response({"nickname": user.first_name})
