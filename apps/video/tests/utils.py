import os.path
import uuid

from django.conf import settings

from apps.video.models import Video


def create_video():
    id = uuid.uuid4()
    video = Video(id=id, name="test_video.mp4")

    test_video_path = "test_binary_files/SampleVideo_1280x720_1mb.mp4"
    file_copy_path = f"videos/{id}.mp4"
    if not os.path.isdir(settings.MEDIA_ROOT):
        os.mkdir(settings.MEDIA_ROOT)
    if not os.path.isdir(settings.MEDIA_ROOT / "videos"):
        os.mkdir(settings.MEDIA_ROOT / "videos")

    with open(test_video_path, "rb") as original:
        with open(settings.MEDIA_ROOT / file_copy_path, "wb") as copy:
            copy.write(original.read())

    video.file = file_copy_path
    video.save()

    return video
