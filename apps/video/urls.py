from django.urls import path

from apps.video.views import VideoAPIView, VideoUploadAPIView

urlpatterns = [
    path("file/", VideoUploadAPIView.as_view(), name="video-upload"),
    path("file/<uuid:id>", VideoAPIView.as_view(), name="video-edit"),
]
