import logging
import uuid

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from apps.video.models import Video
from apps.video.serializers import UploadVideo, VideoIdSerializer

logger = logging.getLogger(__name__)


class VideoUpload(views.APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = UploadVideo

    @swagger_auto_schema(
        operation_description="Upload mp4 video file",
        request_body=UploadVideo,
        responses={
            200: openapi.Response(
                description="Video uploaded", schema=VideoIdSerializer
            ),
            400: "Incorrect file sent",
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as v:
            logging.warning("Incorrect video was not uploaded")
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": v.detail["video"][0]}
            )

        uploaded_video = serializer.validated_data["video"]

        video = Video(id=uuid.uuid4(), name=uploaded_video.name)
        video.video.save(name=str(video.id) + ".mp4", content=uploaded_video)
        video.save()

        return Response(
            status=status.HTTP_200_OK, data=VideoIdSerializer(instance=video).data
        )
