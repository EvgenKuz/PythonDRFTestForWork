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


class VideoUploadAPIView(views.APIView):
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


class VideoAPIView(views.APIView):
    @swagger_auto_schema(
        operation_description="Delete video file",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                description="Video's id",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_PATH,
                format=openapi.FORMAT_UUID,
            )
        ],
        responses={
            200: openapi.Response(
                description="Video deletion attempted",
                schema=openapi.Schema(
                    title="Was video deleted?",
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                ),
            ),
            400: "Incorrect id sent",
        },
    )
    def delete(self, request: views.Request, id: uuid.UUID):
        try:
            video = Video.objects.get(id=id)
        except Video.DoesNotExist:
            logging.warning("Incorrect id sent.")
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": "Incorrect id sent."}
            )

        try:
            video.video.delete()
            video.delete()
        except Exception as e:
            logger.error("Failed to delete video with id: " + str(id), exc_info=e)
            return Response(status=status.HTTP_200_OK, data={"success": False})

        return Response(status=status.HTTP_200_OK, data={"success": True})
