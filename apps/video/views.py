import logging
import uuid

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from apps.video.models import Video
from apps.video.serializers import (
    UploadVideo,
    VideoIdSerializer,
    VideoResolution,
    VideoStatusSerializer,
)
from apps.video.services import ErrorMessageService
from apps.video.tasks import change_resolution_of_video

logger = logging.getLogger(__name__)


OPENAPI_ID_PARAM_SCHEME = openapi.Parameter(
    name="id",
    description="Video's id",
    type=openapi.TYPE_STRING,
    in_=openapi.IN_PATH,
    format=openapi.FORMAT_UUID,
)


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
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as v:
            logging.warning("Incorrect video was not uploaded")
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": ErrorMessageService.create_validation_error_message(v)},
            )

        uploaded_video = serializer.validated_data["video"]

        video = Video(id=uuid.uuid4(), name=uploaded_video.name)
        video.file.save(name=str(video.id) + ".mp4", content=uploaded_video)
        video.save()

        return Response(
            status=status.HTTP_200_OK, data=VideoIdSerializer(instance=video).data
        )


class VideoAPIView(views.APIView):
    @swagger_auto_schema(
        operation_description="Delete video file",
        manual_parameters=[OPENAPI_ID_PARAM_SCHEME],
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
            video.file.delete()
            video.delete()
        except Exception as e:
            logger.error("Failed to delete video with id: " + str(id), exc_info=e)
            return Response(status=status.HTTP_200_OK, data={"success": False})

        return Response(status=status.HTTP_200_OK, data={"success": True})

    @swagger_auto_schema(
        operation_description="Change video's resolution.",
        manual_parameters=[OPENAPI_ID_PARAM_SCHEME],
        request_body=VideoResolution,
        responses={
            200: openapi.Response(
                description="Attempted to start procedure "
                "to change video's resolution.",
                schema=openapi.Schema(
                    title="Was procedure started?",
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                ),
            ),
            400: "Incorrect id or video resolution sent.",
        },
    )
    def patch(self, request: views.Request, id: uuid.UUID):
        resolution = VideoResolution(data=request.data)
        try:
            resolution.is_valid(raise_exception=True)
        except ValidationError as v:
            logger.warning("Incorrect video resolution was sent")
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": ErrorMessageService.create_validation_error_message(v)},
            )

        try:
            video = Video.objects.get(id=id)
        except Video.DoesNotExist:
            logger.warning("Incorrect id sent.")
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": "Incorrect id sent."}
            )

        width = resolution.validated_data["width"]
        height = resolution.validated_data["height"]

        try:
            change_resolution_of_video.delay(video.id, width, height)
        except Exception as e:
            logger.error(
                f"Failed to create task of changing video"
                f"({video.id}) to resolution ({width}, {height})",
                exc_info=e,
            )
            return Response(status=status.HTTP_200_OK, data={"success": False})

        return Response(status=status.HTTP_200_OK, data={"success": True})

    @swagger_auto_schema(
        operation_description="Get video's information and processing status.",
        manual_parameters=[OPENAPI_ID_PARAM_SCHEME],
        responses={
            200: openapi.Response(
                description="Video's info and status.", schema=VideoStatusSerializer
            ),
            400: "Incorrect id sent",
        },
    )
    def get(self, request: views.Request, id: uuid.UUID):
        try:
            video = Video.objects.get(id=id)
        except Video.DoesNotExist:
            logger.warning("Incorrect id sent.")
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": "Incorrect id sent."}
            )

        data = VideoStatusSerializer(instance=video).data

        return Response(status=status.HTTP_200_OK, data=data)
