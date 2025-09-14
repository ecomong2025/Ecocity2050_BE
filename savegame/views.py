from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import SavedGameData
from .serializers import SavedGameDataSerializer
import json

User = get_user_model()


@api_view(["POST"])
def save_game_data(request):
    """
    게임 데이터를 저장하는 API
    """
    # 사용자 인증 확인 (카카오 로그인된 사용자)
    user_id = request.data.get("userId")
    if not user_id:
        return Response(
            {"error": "사용자 인증이 필요합니다."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        user = User.objects.get(kakao_id=user_id)  # 카카오 ID로 사용자 찾기
    except User.DoesNotExist:
        return Response(
            {"error": "사용자를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 게임 데이터 추출
    co2_tons = request.data.get("co2Tons", 0)
    citizen_satisfaction = request.data.get("citizenSatisfaction", "")
    budget = request.data.get("budget", 0)
    top_tags = request.data.get("topTags", []) or []
    ai_city_name = request.data.get("aiCityName", "")

    # 기존 저장된 데이터가 있으면 업데이트, 없으면 새로 생성
    saved_data, created = SavedGameData.objects.update_or_create(
        user=user,
        defaults={
            'co2_tons': co2_tons,
            'citizen_satisfaction': citizen_satisfaction,
            'budget': budget,
            'top_tags': json.dumps(top_tags),
            'ai_city_name': ai_city_name,
        }
    )

    return Response({
        "message": "게임 데이터가 저장되었습니다.",
        "created": created
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def load_game_data(request):
    """
    저장된 게임 데이터를 불러오는 API
    """
    user_id = request.query_params.get("userId")
    if not user_id:
        return Response(
            {"error": "사용자 인증이 필요합니다."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        user = User.objects.get(kakao_id=user_id)
        saved_data = SavedGameData.objects.get(user=user)

        # JSON 형태로 저장된 top_tags를 리스트로 변환
        top_tags = json.loads(saved_data.top_tags) if saved_data.top_tags else []

        return Response({
            "co2Tons": saved_data.co2_tons,
            "citizenSatisfaction": saved_data.citizen_satisfaction,
            "budget": saved_data.budget,
            "topTags": top_tags,
            "aiCityName": saved_data.ai_city_name,
            "lastSaved": saved_data.updated_at.isoformat()
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "사용자를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    except SavedGameData.DoesNotExist:
        return Response(
            {"error": "저장된 게임 데이터가 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
def check_saved_data_exists(request):
    """
    저장된 데이터가 존재하는지 확인하는 API
    """
    user_id = request.query_params.get("userId")
    if not user_id:
        return Response(
            {"exists": False, "error": "사용자 인증이 필요합니다."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        user = User.objects.get(kakao_id=user_id)
        exists = SavedGameData.objects.filter(user=user).exists()

        return Response({
            "exists": exists
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"exists": False, "error": "사용자를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )