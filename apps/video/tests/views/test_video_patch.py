import os
import uuid
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.video.tests.utils import create_video


class VideoPatchTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.edit_reverse_name = "video-edit"

        self.saved_videos = []

    def tearDown(self):
        for video in self.saved_videos:
            os.remove(video)

    @patch("apps.video.tasks.change_resolution_of_video.delay")
    def test_video_changing_resolution_started(self, task: Mock):
        video = create_video()
        self.saved_videos.append(video.file.path)

        expected_width = 100
        expected_height = 100
        response = self.client.patch(
            reverse(self.edit_reverse_name, kwargs=dict(id=video.id)),
            data=dict(width=expected_width, height=expected_height),
        )

        self.assertEqual(task.call_count, 1)

        video_sent_to_task, width, height = task.call_args[0]
        self.assertEqual(video_sent_to_task, video.id)
        self.assertEqual(expected_width, width)
        self.assertEqual(expected_height, height)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertTrue(response.data["success"])

    @patch("apps.video.tasks.change_resolution_of_video.delay")
    def test_invalid_resolution(self, task):
        params = [("aa", "bb"), (20, 40), ("null", "null")]
        for width, height in params:
            self.subtest_invalid_resolution(width, height)

        self.assertFalse(task.called)

    def subtest_invalid_resolution(self, width, height):
        video = create_video()
        self.saved_videos.append(video.file.path)

        response = self.client.patch(
            reverse(self.edit_reverse_name, kwargs=dict(id=video.id)),
            data=dict(width=width, height=height),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("apps.video.tasks.change_resolution_of_video.delay")
    def test_patch_invalid_video_id(self, task):
        invalid_id = uuid.uuid4()
        response = self.client.patch(
            reverse(self.edit_reverse_name, kwargs=dict(id=invalid_id)),
            data=dict(width=22, height=22),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual("Incorrect id sent.", response.data["error"])
        self.assertFalse(task.called)

    @patch("apps.video.tasks.change_resolution_of_video.delay")
    def test_video_changing_resolution_failed(self, task: Mock):
        video = create_video()
        self.saved_videos.append(video.file.path)

        task.side_effect = Exception("exeption")

        response = self.client.patch(
            reverse(self.edit_reverse_name, kwargs=dict(id=video.id)),
            data=dict(width=100, height=100),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertFalse(response.data["success"])
