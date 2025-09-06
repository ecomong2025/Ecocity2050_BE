from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views   # ✅ 추가: 같은 패키지의 views 임포트

schema_view = get_schema_view(
   openapi.Info(
      title="EcoCity2050 API",
      default_version='v1',
      description="EcoCity2050 프로젝트 API 문서",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),

    # Swagger & ReDoc  (경고 제거: raw string 사용)
    path(r"swagger(?P<format>\.json|\.yaml)", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name="swagger-ui"),
    path("redoc/", schema_view.with_ui('redoc', cache_timeout=0), name="redoc"),

    path("test/", TemplateView.as_view(template_name="kakao_test.html"), name="kakao_test"),
    
    path("name-city", views.name_city, name="name-city"),
    path("name-city/", views.name_city, name="name-city"),  # ✅ 추가: 엔드포인트 등록(슬래시 포함)
]
