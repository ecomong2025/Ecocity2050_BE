import os, re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI

@api_view(["POST"])
def name_city(request):
    co2 = request.data.get("co2Tons", 0)
    satis = request.data.get("citizenSatisfaction", "")
    budget = request.data.get("budget", 0)
    tags = request.data.get("topTags", []) or []

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return Response(
            {"cityName": "에러", "detail": "OPENAI_API_KEY not found in environment"},
            status=500
        )

    messages = [
        {
            "role": "system",
            "content": "너는 게임 도시 이름 네이머다. "
                       "한국어, 2~4음절, 한 단어, 공백/특수문자 없이."
        },
        {
            "role": "user",
            "content": (
                f"지표: CO2={co2}t, 시민만족도={satis}, 예산={budget}\n"
                f"도시 특징 태그: {', '.join(tags)}\n"
                f"도시 이름 1개만 답하라."
            )
        }
    ]

    try:
        client = OpenAI(api_key=api_key)

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=messages
        )

        text = (r.choices[0].message.content or "").strip()
        name = re.sub(r'[\"\'‘’“”\s]', "", text) or "이름생성실패"

        return Response({"cityName": name})

    except Exception as e:
        return Response(
            {"cityName": "에러", "detail": str(e)},
            status=500
        )
