#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : videos
# @Time         : 2025/11/5 18:01
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from openai import AsyncOpenAI
from meutils.schemas.video_types import SoraVideoRequest, Video
from meutils.io.files_utils import to_base64, to_url_fal

"""
model
undefined · enum
Possible values: alibaba/wan2.5-i2v-preview
prompt
string · min: 1 · max: 800
The text description of the scene, subject, or action to generate in the video.

image_url
string · uri
A direct link to an online image or a Base64-encoded local image that will serve as the visual base or the first frame for the video.

resolution
string · enum
An enumeration where the short side of the video frame determines the resolution.

Default: 720p
Possible values: 480p720p1080p
duration
integer · enum
The length of the output video in seconds.

Possible values: 510
negative_prompt
string
The description of elements to avoid in the generated video.

enable_prompt_expansion
boolean
Whether to enable prompt expansion.

Default: true
seed
integer
Varying the seed integer is a way to get different results for the same other request parameters. Using the same value for an identical request will produce similar results. If unspecified, a random number is chosen.
"""


class Tasks(object):

    def __init__(self, base_url: Optional[str] = None, api_key: str = None):
        base_url = base_url or "https://api.aimlapi.com/v2"
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def create(self, request: SoraVideoRequest):
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "resolution": request.resolution,

            **(request.metadata or {})
        }
        if request.seconds:
            payload["duration"] = int(request.seconds)

        if request.ratio:
            payload["aspect_ratio"] = request.ratio

        if request.input_reference:
            payload['model'] = request.model.replace("text-to-video", "image-to-video").replace("t2v", "i2v")

            image_urls = await to_url_fal(request.input_reference, content_type="image/png")

            payload["image_url"] = image_urls[0]

            if len(image_urls) > 1:  # 首尾帧
                payload["last_image_url"] = image_urls[1]

            # https://aimlapi.com/models/veo-3-1-reference-to-video
            # 模型区分 参考图 首尾帧
        elif request.image:
            payload['model'] = request.model.replace("text-to-video", "image-to-video").replace("t2v", "i2v")

            payload["image_url"] = request.image[0]

        else:
            payload['model'] = request.model.replace("image-to-video", "text-to-video").replace("i2v", "t2v")

        logger.debug(bjson(payload))
        response = await self.client.post(
            path="/video/generations",
            body=payload,
            cast_to=object
        )
        """
        {
    "id": "9913239d-4fa8-47ea-b51d-d313e29caba5:alibaba/wan2.5-i2v-preview",
    "status": "queued",
    "meta": {
        "usage": {
            "tokens_used": 105000
        }
    }
}
        """

        logger.debug(bjson(response))

        return response

    async def get(self, task_id: str):
        response = await self.client.get(
            path=f"/video/generations?generation_id={task_id}",
            cast_to=object
        )
        """
        {
    "id": "9913239d-4fa8-47ea-b51d-d313e29caba5:alibaba/wan2.5-i2v-preview",
    "status": "completed",
    "video": {
        "url": "https://cdn.aimlapi.com/alpaca/1d/dd/20251107/30b07d9c/42740107-9913239d-4fa8-47ea-b51d-d313e29caba5.mp4?Expires=1762593280&OSSAccessKeyId=LTAI5tBLUzt9WaK89DU8aECd&Signature=Guk6apyEnKeuniLv0mcBJhkHO%2FI%3D"
    }
}

        """
        logger.debug(bjson(response))

        video = Video(id=task_id, status=response, video_url=response.get("video", {}).get("url"))
        if error := response.get("error"):
            video.error = error

        return video


if __name__ == "__main__":
    api_key = "603051fc1d7e49e19de2c67521d4a30e"

    data = {
        "model": "alibaba/wan2.5-i2v-preview",
        "prompt": '''Mona Lisa nervously puts on glasses with her hands and asks her off-screen friend to the left: ‘Do they suit me?’ She then tilts her head slightly to one side and then the other, so the unseen friend can better judge.''',
        "input_reference": "https://s2-111386.kwimgs.com/bs2/mmu-aiplatform-temp/kling/20240620/1.jpeg",
        "resolution": "480p",
        "seconds": "5",
    }

    request = SoraVideoRequest(**data)

    tasks = Tasks(api_key=api_key)
    # arun(tasks.create(request))

    task_id = "9913239d-4fa8-47ea-b51d-d313e29caba5:alibaba/wan2.5-i2v-preview"

    arun(tasks.get(task_id))
