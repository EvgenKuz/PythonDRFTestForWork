from django.urls import path

from apps.video.views import VideoUpload

urlpatterns = [path("file/", VideoUpload.as_view(), name="video-upload")]
