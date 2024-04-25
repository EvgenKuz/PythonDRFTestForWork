import uuid

from apps.video.models import Video


def create_video():
    id = uuid.uuid4()
    video = Video(id=id, name="test_video.mp4")

    test_video_path = "test_binary_files/SampleVideo_1280x720_1mb.mp4"
    file_copy_path = f"videos/{id}.mp4"

    with open(test_video_path, "rb") as original:
        with open("media/" + file_copy_path, "wb") as copy:
            copy.write(original.read())

    video.file = file_copy_path
    video.save()

    return video
