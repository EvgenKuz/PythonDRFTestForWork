import os
import uuid
from unittest.mock import Mock, patch

import ffmpeg
from django.test import TestCase

from apps.video.models import Video
from apps.video.tasks import change_resolution_of_video
from apps.video.tests.utils import create_video


class ChangeResolutionOfVideoTaskTests(TestCase):
    def setUp(self):
        self.created_videos = []

    def tearDown(self):
        for video in self.created_videos:
            os.remove(video)

    def test_task_change_resolution_of_video(self):
        video = create_video()
        self.created_videos.append(video.file.path)

        self.assertIsNone(video.last_processed_success)
        self.assertFalse(video.is_processing)

        width = 500
        height = 500

        change_resolution_of_video(video.id, width, height)

        video.refresh_from_db()
        self.assertTrue(video.last_processed_success)
        self.assertFalse(video.is_processing)

    @patch("apps.video.models.Video.refresh_from_db")
    @patch("apps.video.services.VideoService.change_video_resolution")
    def test_video_deleted(self, change_resolution: Mock, refresh: Mock):
        video = create_video()
        video.is_processing = True
        video.save()
        self.created_videos.append(video.file.path)

        width = 500
        height = 500
        refresh.side_effect = Video.DoesNotExist

        change_resolution_of_video(video.id, width, height)
        self.assertFalse(change_resolution.called)

    @patch("apps.video.services.VideoService.change_video_resolution")
    def test_video_does_not_exist(self, change_resolution: Mock):
        width = 500
        height = 500

        change_resolution_of_video(uuid.uuid4(), width, height)
        self.assertFalse(change_resolution.called)

    @patch("apps.video.services.VideoService.change_video_resolution")
    def test_ffmpeg_error(self, change_resolution: Mock):
        video = create_video()
        self.created_videos.append(video.file.path)
        self.assertIsNone(video.last_processed_success)

        change_resolution.side_effect = ffmpeg.Error("", "", "")
        width = 500
        height = 500

        change_resolution_of_video(video.id, width, height)

        video.refresh_from_db()
        self.assertFalse(video.last_processed_success)
        self.assertFalse(video.is_processing)
