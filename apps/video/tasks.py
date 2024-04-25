import logging
import uuid
from time import sleep

import ffmpeg
from celery.app import shared_task

from apps.video.models import Video
from apps.video.services import VideoService

logger = logging.getLogger(__name__)


@shared_task
def change_resolution_of_video(video_id: uuid.UUID, width: int, height: int):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        logger.warning(
            f"Failed to change resolution of video({video_id}). Video deleted."
        )
        return

    while video.is_processing:
        sleep(2)
        try:
            video.refresh_from_db()
        except Video.DoesNotExist:
            logger.warning(
                f"Failed to change resolution of video({video_id}). Video deleted."
            )
            return

    video.is_processing = True
    video.save()

    try:
        VideoService.make_copy_of_video(video)
    except IOError as e:
        logger.error(f"Failed to make copy of video({video.id}).", exc_info=e)
        set_failed_status_to_video(video)
        return

    try:
        VideoService.change_video_resolution(video, width, height)
    except ffmpeg.Error as e:
        logger.error(
            f"Failed to change resolution of video"
            f"({video.id}) to (w: {width}, h: {height})",
            exc_info=e,
        )

        set_failed_status_to_video(video)
        return

    logger.info(f"Changed resolution of video({video.id}) to (w: {width}, h: {height})")
    video.last_processed_success = True
    video.is_processing = False
    video.save()


def set_failed_status_to_video(video: Video):
    video.is_processing = False
    video.last_processed_success = False
    video.save()
