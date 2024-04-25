import filecmp
import os

from django.test import TestCase

from apps.video.services import VideoService
from apps.video.tests.utils import create_video
from apps.video.utils import get_video_resolution


class FFMPEGTest(TestCase):

    def setUp(self):
        self.created_videos = []

    def tearDown(self):
        for video in self.created_videos:
            os.remove(video)

    def test_make_copy(self):
        video = create_video()
        self.created_videos.append(video.file.path)

        copy_path = VideoService.make_copy_of_video(video)
        self.created_videos.append(copy_path)

        self.assertTrue(os.path.isfile(copy_path))
        self.assertIn(str(video.id), str(copy_path))
        self.assertTrue(filecmp.cmp(video.file.path, copy_path, shallow=False))

    def test_change_resolution(self):
        video = create_video()
        self.created_videos.append(video.file.path)
        original_width, original_height = get_video_resolution(video.file.path)

        width_change_to = 100
        height_change_to = 500
        VideoService.change_video_resolution(video, width_change_to, height_change_to)

        new_width, new_height = get_video_resolution(video.file.path)
        self.assertNotEqual(original_width, new_width)
        self.assertNotEqual(original_height, new_height)
        self.assertEqual(width_change_to, new_width)
        self.assertEqual(height_change_to, new_height)
