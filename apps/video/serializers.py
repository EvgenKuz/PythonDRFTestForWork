import filetype
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from apps.video.models import Video


class UploadVideo(serializers.Serializer):
    video = serializers.FileField()

    class Meta:
        fields = ["video"]

    def validate_video(self, value: UploadedFile):
        allowed_video_format = "mp4"
        allowed_video_mime = "video/mp4"
        kind = filetype.guess(value.read())

        if kind.extension != allowed_video_format or kind.mime != allowed_video_mime:
            raise ValidationError(
                detail="Video has to be in mp4 format", code=status.HTTP_400_BAD_REQUEST
            )

        return value


class VideoIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id"]
        read_only_fields = ["id"]


STARTING_WIDTH_AND_HEIGHT = 22


class VideoResolution(serializers.Serializer):
    width = serializers.IntegerField(min_value=STARTING_WIDTH_AND_HEIGHT)
    height = serializers.IntegerField(min_value=STARTING_WIDTH_AND_HEIGHT)

    class Meta:
        fields = ["width", "height"]

    def validate_width(self, value: int):
        if value % 2 != 0:
            raise ValidationError(
                detail="Width has to be even.", code=status.HTTP_400_BAD_REQUEST
            )

        return value

    def validate_height(self, value: int):
        if value % 2 != 0:
            raise ValidationError(
                detail="Height has to be even.", code=status.HTTP_400_BAD_REQUEST
            )

        return value


class VideoStatusSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source="name", read_only=True)
    processing = serializers.BooleanField(source="is_processing", read_only=True)
    processingSuccess = serializers.BooleanField(
        source="last_processed_success", read_only=True, allow_null=True
    )

    class Meta:
        model = Video
        fields = ["id", "filename", "processing", "processingSuccess"]
        read_only_fields = ["id"]
