import os
from datetime import datetime
from pathlib import Path

import ffmpeg
from rest_framework.exceptions import ValidationError

from apps.video.models import Video


class VideoService:

    @staticmethod
    def change_video_resolution(video: Video, width: int, height: int) -> None:
        file = video.file.path
        temp_output = Path(file).parent / f"{video.id}_temp.mp4"

        (
            ffmpeg.input(file)
            .filter("scale", width, height)
            .filter("setsar", 1)
            .output(str(temp_output))
            .overwrite_output()
            .run()
        )

        try:
            os.remove(file)
        except FileNotFoundError:
            pass
        os.rename(temp_output, file)

    @staticmethod
    def make_copy_of_video(video: Video) -> Path:
        copy_path = Path(video.file.path).parent / f"{video.id}_{datetime.now()}.mp4"

        with open(video.file.path, "rb") as original:
            with open(copy_path, "wb") as copy:
                copy.write(original.read())

        return copy_path


class ErrorMessageService:

    @staticmethod
    def create_validation_error_message(error: ValidationError) -> str:
        errors = []

        for field, list_of_errors in error.detail.items():
            for error_message in list_of_errors:
                errors.append(f"{field}: {error_message}")

        return " \n ".join(errors)
