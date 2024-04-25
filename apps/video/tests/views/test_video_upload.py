import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.video.models import Video
from apps.video.tests.views.test_video_delete import VIDEO_FILES_LOCATION


class VideoUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.upload_url = reverse("video-upload")
        with open("test_binary_files/SampleVideo_1280x720_1mb.mp4", "rb") as video:
            self.video = SimpleUploadedFile(
                "video.mp4", video.read(), content_type="video/mp4"
            )
        with open("test_binary_files/SampleAudio_0.4mb.mp3", "rb") as audio:
            self.audio = SimpleUploadedFile(
                "audio.mp3", audio.read(), content_type="video/mpeg"
            )

        self.uploaded_videos = []

    def tearDown(self):
        for video in self.uploaded_videos:
            os.remove(VIDEO_FILES_LOCATION / f"{video}.mp4")

    def test_file_upload(self):
        response = self.client.post(
            self.upload_url,
            data=encode_multipart(BOUNDARY, dict(video=self.video)),
            content_type=MULTIPART_CONTENT,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        video_id = response.data["id"]
        self.uploaded_videos.append(video_id)
        video_in_db = Video.objects.get(id=video_id)

        self.assertEqual(video_in_db.name, self.video.name)
        self.assertIn(video_id, video_in_db.file.path)

    def test_sending_no_file(self):
        response = self.client.post(self.upload_url, content_type=MULTIPART_CONTENT)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_sending_incorrect_file(self):
        response = self.client.post(
            self.upload_url,
            data=encode_multipart(BOUNDARY, dict(video=self.audio)),
            content_type=MULTIPART_CONTENT,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "video: Video has to be in mp4 format")

    def test_sending_incorrect_mime(self):
        copy_location = "test_binary_files/test_file.mp4"
        with self.audio.open("rb") as file:
            with open(copy_location, "wb") as copy:
                copy.write(file.read())

        with open(copy_location, "rb") as copy:
            copy_file = SimpleUploadedFile(
                "test_file.mp4", copy.read(), content_type="video/mp4"
            )

        response = self.client.post(
            self.upload_url,
            data=encode_multipart(BOUNDARY, dict(video=copy_file)),
            content_type=MULTIPART_CONTENT,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "video: Video has to be in mp4 format")

        os.remove(copy_location)
