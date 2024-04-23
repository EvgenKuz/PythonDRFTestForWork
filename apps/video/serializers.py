from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from apps.video.models import Video


class UploadVideo(serializers.Serializer):
    video = serializers.FileField()

    class Meta:
        fields = ["video"]

    def validate_video(self, value: UploadedFile):
        if value.name.split(".")[-1] != "mp4":
            raise ValidationError(
                detail="Video has to be in mp4 format", code=status.HTTP_400_BAD_REQUEST
            )

        return value


class VideoIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id"]
