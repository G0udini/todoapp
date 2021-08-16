from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("home/", include("base.urls")),
    path("admin/", admin.site.urls),
]
urlpatterns += [path(r"^silk/", include("silk.urls", namespace="silk"))]
