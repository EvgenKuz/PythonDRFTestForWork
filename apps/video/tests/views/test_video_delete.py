import os
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

VIDEO_FILES_LOCATION = "media/videos/"


class VideoUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.upload_url = reverse("video-upload")
        self.delete_reverse_name = "video-edit"

        with open("test_binary_files/SampleVideo_1280x720_1mb.mp4", "rb") as video:
            self.video = SimpleUploadedFile(
                "video.mp4", video.read(), content_type="video/mp4"
            )

    def test_video_delete(self):
        response = self.client.post(
            self.upload_url,
            data=encode_multipart(BOUNDARY, dict(video=self.video)),
            content_type=MULTIPART_CONTENT,
        )

        video_id = response.data["id"]
        assert os.path.isfile(VIDEO_FILES_LOCATION + video_id + ".mp4")

        response = self.client.delete(
            reverse(self.delete_reverse_name, kwargs=dict(id=video_id))
        )

        assert not os.path.isfile(VIDEO_FILES_LOCATION + video_id + ".mp4")
        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.data
        assert response.data["success"]

    def test_incorrect_id(self):
        incorrect_id = uuid.uuid4()
        response = self.client.delete(
            reverse(self.delete_reverse_name, kwargs=dict(id=incorrect_id))
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"] == "Incorrect id sent."

    # There's should be a test for deletion failure, but I can't think of one
