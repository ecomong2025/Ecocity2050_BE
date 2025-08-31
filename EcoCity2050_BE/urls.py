from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    path("api/", include("users.urls")),

    # Swagger & ReDoc
    path("swagger(<format>\.json|\.yaml)", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name="swagger-ui"),
    path("redoc/", schema_view.with_ui('redoc', cache_timeout=0), name="redoc"),
]
