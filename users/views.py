import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from allauth.socialaccount.models import SocialApp
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
class KakaoLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="카카오 로그인 시작 URL 반환",
        responses={200: openapi.Response("OK", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"auth_url": openapi.Schema(type=openapi.TYPE_STRING)}
        ))},
    )
    def get(self, request):
        try:
            social_app = SocialApp.objects.get(provider='kakao')
        except SocialApp.DoesNotExist:
            return Response(
                {"error": "카카오 소셜 앱이 등록되지 않았습니다. Django admin에서 SocialApp을 등록하세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # redirect uri: 프론트/백엔드 설정에 맞게 변경하세요.
        callback_url = request.build_absolute_uri('/accounts/kakao/login/callback/')

        # 카카오 인가 URL 생성
        # 필요한 scope는 서비스에 맞게 확장하세요 (profile_nickname, account_email 등)
        auth_url = (
            "https://kauth.kakao.com/oauth/authorize"
            f"?response_type=code"
            f"&client_id={social_app.client_id}"
            f"&redirect_uri={callback_url}"
            f"&scope=profile_nickname"
        )

        return Response({"auth_url": auth_url})


# 카카오 콜백: code로 JWT 발급 (카카오 토큰 교환 + 사용자 정보 조회)
class KakaoCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="카카오 OAuth 콜백 (code로 JWT 발급)",
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_QUERY,
                description="카카오 OAuth 인가 코드",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
    )
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "code가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            social_app = SocialApp.objects.get(provider='kakao')
        except SocialApp.DoesNotExist:
            return Response(
                {"error": "카카오 소셜 앱이 등록되지 않았습니다. Django admin에서 SocialApp을 등록하세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # callback url은 로그인 시작 때와 동일해야 합니다
        callback_url = request.build_absolute_uri('/accounts/kakao/login/callback/')

        # 1) 코드 -> 액세스 토큰 교환
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": social_app.client_id,
            "redirect_uri": callback_url,
            "code": code,
        }
        # client_secret이 설정되어 있으면 포함
        if getattr(social_app, "secret", None):
            token_data["client_secret"] = social_app.secret

        try:
            token_resp = requests.post(token_url, data=token_data, timeout=10)
            token_resp.raise_for_status()
            token_json = token_resp.json()
        except requests.RequestException as e:
            return Response(
                {"error": f"카카오 토큰 교환 실패: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = token_json.get("access_token")
        if not access_token:
            return Response(
                {"error": "카카오에서 access_token을 받지 못했습니다.", "detail": token_json},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) 사용자 정보 조회
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            user_resp = requests.get(user_info_url, headers=headers, timeout=10)
            user_resp.raise_for_status()
            user_json = user_resp.json()
        except requests.RequestException as e:
            return Response(
                {"error": f"카카오 사용자 정보 조회 실패: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        kakao_id = user_json.get("id")
        # nickname 위치는 카카오 응답 구조에 따라 다를 수 있으므로 안전하게 추출
        kakao_account = user_json.get("kakao_account", {})
        profile = kakao_account.get("profile", {}) if isinstance(kakao_account, dict) else {}
        nickname = profile.get("nickname") or ""

        if not kakao_id:
            return Response({"error": "카카오 ID를 가져오지 못했습니다.", "detail": user_json},
                            status=status.HTTP_400_BAD_REQUEST)

        # 사용자 생성 또는 조회
        username = f"kakao_{kakao_id}"  # 숫자만 있는 username 충돌/문제 방지
        try:
            user = User.objects.get(username=username)
            message = "login success"
        except User.DoesNotExist:
            # 필요한 필드에 따라 create_user 호출을 조정하세요 (email 필드가 required면 추가 처리)
            user = User.objects.create_user(username=username)
            # 닉네임을 first_name에 넣거나 프로필 모델이 따로 있다면 거기에 저장
            user.first_name = nickname or ""
            user.save()
            message = "register success"

        # JWT 발급
        refresh = RefreshToken.for_user(user)
        access_token_jwt = str(refresh.access_token)
        refresh_token_jwt = str(refresh)

        data = {
            "user": UserSerializer(user).data,
            "message": message,
            "token": {"access": access_token_jwt, "refresh": refresh_token_jwt},
        }

        resp = Response(data, status=status.HTTP_200_OK)

        # 개발환경에서 https가 아닐 수 있으니 settings.DEBUG 기반으로 secure 옵션 설정
        secure_cookie = not getattr(settings, "DEBUG", False)

        # 쿠키 저장 (프론트와의 정책에 맞게 name/path/domain/samesite 조정하세요)
        resp.set_cookie("accessToken", access_token_jwt, httponly=True, secure=secure_cookie, samesite="None")
        resp.set_cookie("refreshToken", refresh_token_jwt, httponly=True, secure=secure_cookie, samesite="None")

        return resp


# 로그아웃
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="로그아웃 (JWT 토큰 블랙리스트 처리)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh Token")
            },
            required=["refresh"]
        ),
        responses={
            200: openapi.Response(
                "로그아웃 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response("잘못된 요청")
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                refresh_token = request.COOKIES.get("refreshToken")

            if not refresh_token:
                return Response(
                    {"error": "refresh token이 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            # blacklisting app이 활성화되어 있어야 함 (rest_framework_simplejwt.token_blacklist)
            token.blacklist()

            resp = Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)

            # 쿠키 삭제 (samesite는 클라이언트 정책에 따라 조정)
            resp.delete_cookie("accessToken", samesite="None")
            resp.delete_cookie("refreshToken", samesite="None")

            return resp

        except Exception as e:
            return Response(
                {"error": f"로그아웃 처리 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
