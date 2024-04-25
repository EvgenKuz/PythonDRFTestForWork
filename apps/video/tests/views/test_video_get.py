import os
import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.video.tests.utils import create_video


class GetVideoInfoTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.get_video_reversed = "video-edit"

        self.created_videos = []

    def tearDown(self):
        for video in self.created_videos:
            os.remove(video)

    def test_get_video_info(self):
        video = create_video()
        self.created_videos.append(video.file.path)

        response = self.client.get(
            reverse(self.get_video_reversed, kwargs=dict(id=video.id))
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_should_be = dict(
            id=str(video.id),
            filename=video.name,
            processing=video.is_processing,
            processingSuccess=video.last_processed_success,
        )

        self.assertEqual(response.data, response_should_be)

    def test_get_incorrect_id(self):
        response = self.client.get(
            reverse(self.get_video_reversed, kwargs=dict(id=uuid.uuid4()))
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual("Incorrect id sent.", response.data["error"])
