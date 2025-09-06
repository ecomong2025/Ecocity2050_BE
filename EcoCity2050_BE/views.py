# EcoCity2050_BE/views.py
import os, json, re
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

def get_client():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        # 여기서 친절한 에러로 반환하게 해도 됨
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=key)

@csrf_exempt
def name_city(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        body = {}

    co2 = body.get("co2Tons", 0)
    satis = body.get("citizenSatisfaction", "")
    budget = body.get("budget", 0)
    tags = body.get("topTags", []) or []

    # 키 체크 (사용자에게 명확히 알려주기)
    if not os.environ.get("OPENAI_API_KEY"):
        return JsonResponse({"cityName": "에러", "detail": "OPENAI_API_KEY not set"}, status=500)

    messages = [
        {"role":"system","content":"너는 게임 도시 이름 네이머다. 한국어, 2~4음절, 한 단어, 공백/특수문자 없이."},
        {"role":"user","content": f"지표: CO2={co2}t, 시민만족도={satis}, 예산={budget}\n도시 특징 태그: {', '.join(tags)}\n도시 이름 1개만 답하라."}
    ]

    try:
        client = get_client()  # ← 여기서 생성
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=messagespython manage.py runserver
        )
        text = (r.choices[0].message.content or "").strip()
        name = re.sub(r'[\"\'‘’“”\s]', "", text) or "이름생성실패"
        return JsonResponse({"cityName": name})
    except Exception as e:
        return JsonResponse({"cityName": "에러", "detail": str(e)}, status=500)
