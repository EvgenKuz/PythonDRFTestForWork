from os import PathLike

import ffmpeg


def get_video_resolution(video: PathLike) -> (int, int):
    output = ffmpeg.probe(
        video, v="error", select_streams="v", show_entries="stream=width,height"
    )
    width = output["streams"][0]["width"]
    height = output["streams"][0]["height"]

    return width, height
