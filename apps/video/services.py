from django.core.files import File
from rest_framework.exceptions import ValidationError


class FFMPEGService:

    @staticmethod
    def change_video_resolution(video: File, width: int, height: int):
        pass


class ErrorMessageService:

    @staticmethod
    def create_validation_error_message(error: ValidationError) -> str:
        errors = []

        for field, list_of_errors in error.detail:
            for error_message in list_of_errors:
                errors.append(f"{field}: {error_message}")

        return "\n".join(errors)
