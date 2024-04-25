import os
import uuid
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

VIDEO_FILES_LOCATION = "media/videos/"


class VideoDeleteTests(TestCase):

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
        self.assertTrue(os.path.isfile(VIDEO_FILES_LOCATION + video_id + ".mp4"))

        response = self.client.delete(
            reverse(self.delete_reverse_name, kwargs=dict(id=video_id))
        )

        self.assertFalse(os.path.isfile(VIDEO_FILES_LOCATION + video_id + ".mp4"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertTrue(response.data["success"])

    def test_incorrect_id(self):
        incorrect_id = uuid.uuid4()
        response = self.client.delete(
            reverse(self.delete_reverse_name, kwargs=dict(id=incorrect_id))
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Incorrect id sent.")

    @patch("django.db.models.fields.files.FieldFile.delete")
    def test_deletion_failure(self, file_delete: Mock):
        file_delete.side_effect = Exception("error")

        response = self.client.post(
            self.upload_url,
            data=encode_multipart(BOUNDARY, dict(video=self.video)),
            content_type=MULTIPART_CONTENT,
        )

        video_id = response.data["id"]

        response = self.client.delete(
            reverse(self.delete_reverse_name, kwargs=dict(id=video_id))
        )

        self.assertTrue(os.path.isfile(VIDEO_FILES_LOCATION + video_id + ".mp4"))
        self.assertFalse(response.data["success"])
