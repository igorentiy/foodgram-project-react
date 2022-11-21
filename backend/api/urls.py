from django.urls import include, path
from rest_framework import routers

from .views import TagViewSet, ObtainToken, UsersViewSet, set_password

app_name = "api"

router = routers.DefaultRouter()
router.register("tags", TagViewSet, basename="tags")
router.register("users", UsersViewSet, basename="users")

urlpatterns = [
    path("auth/token/login/", ObtainToken.as_view(), name="obtain_token"),
    path("users/set_password/", set_password, name="set_password"),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
