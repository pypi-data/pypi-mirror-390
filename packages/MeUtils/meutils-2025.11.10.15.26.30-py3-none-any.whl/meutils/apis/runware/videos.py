#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : videos
# @Time         : 2025/10/13 13:46
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from meutils.pipe import *
from meutils.db.redis_db import redis_aclient
from meutils.llm.clients import AsyncClient
from meutils.io.files_utils import to_url, to_url_fal
from meutils.schemas.video_types import SoraVideoRequest, Video

from openai import APIStatusError

MODELS_MAPPING = {

    "minimax-hailuo-02": "minimax:3@1",
    "minimax-hailuo-2.3": "minimax:4@1",
    "minimax-hailuo-2.3-fast": "minimax:4@2",

    "kling-2.5": "klingai:6@0",  # Kling 2.5 Turbo Standard model only supports image-to-video generation
    "kling-2.5-pro": "klingai:6@1",

    "viduq2-pro": "vidu:3@1",
    "viduq2-turbo": "vidu:3@2",

    "sora-2": "openai:3@1",
    "sora-2-pro": "openai:3@2",

    "veo3.1": "google:3@2",
    "veo3.1-fast": "google:3@3",

}

# https://runware.ai/docs/en/video-inference/api-reference#request-providersettings
provider_settings_mapping = {
    'vidu': {
        "providerSettings": {
            "vidu": {
                "movementAmplitude": "auto",
                "bgm": True,
                "style": "anime"
            }
        }
    },

    'minimax': {"providerSettings": {
        "minimax": {
            "promptOptimizer": True
        }
    }}

}


async def create_task(request: SoraVideoRequest, api_key: str, base_url: Optional[str] = None):
    # 模型路由
    if request.model.startswith("minimax"):
        mapping = {
            "512p": "512x512",
            "768p": "1366x768",
            "1080p": "1920x1080",
        }
        request.size = mapping.get(request.resolution) or request.size or "1366x768"

    elif request.model.startswith("vidu"):  # todo 视频模型 分辨率 映射
        mapping = {
            "512p": "512x512",
            "768p": "1366x768",
            "1080p": "1920x1080",
        }
        request.size = mapping.get(request.resolution) or request.size or "512x512"

    payload = [
        {
            "taskType": "videoInference",

            "taskUUID": str(uuid.uuid4()),

            "model": MODELS_MAPPING.get(request.model, request.model),
            "positivePrompt": request.prompt,

            "numberResults": 1,

            "duration": request.seconds and int(request.seconds) or 5,

            "includeCost": True,

            "webhookURL": "https://openai-dev.chatfire.cn/sys/webhook/runware?expr=%24..taskUUID",  # task_id
        },
    ]

    if provider_settings := provider_settings_mapping.get(request.model):
        payload[0]['providerSettings'] = provider_settings

    if request.model not in {"kling-2.5"}:
        payload[0]["width"], payload[0]["height"] = map(int, request.size.split("x"))

    if request.input_reference:  # todo 多图

        urls = await to_url_fal(request.input_reference, content_type="image/png")
        if request.model.startswith(("vidu",)):
            payload[0]["referenceImages"] = urls
        else:
            payload[0]["frameImages"] = [
                {
                    "inputImage": url
                }
                for url in urls
            ]
    elif request.image:
        urls = request.image
        if request.model.startswith(("vidu",)):
            payload[0]["referenceImages"] = urls
        else:
            payload[0]["frameImages"] = [
                {
                    "inputImage": url
                }
                for url in urls
            ]

    logger.debug(bjson(payload))

    try:
        client = AsyncClient(base_url="https://api.runware.ai/v1", api_key=api_key, timeout=300)
        response = await client.post(
            "/",
            body=payload,
            cast_to=object
        )

        video = Video(
            id=response["data"][0]["taskUUID"],
            model=request.model,
            seconds=request.seconds,
        )

        await redis_aclient.set(video.id, api_key)  # 回调接口即可

        return video

    except APIStatusError as e:
        if (errors := e.response.json().get("errors")):
            logger.debug(bjson(errors))

        raise e


async def get_task(task_id):
    if not await redis_aclient.get(task_id):
        raise ValueError(f"task_id not found")

    video = Video(id=task_id)
    webhook_id = f"webhook:runware:{task_id}"
    if (data := await redis_aclient.lrange(webhook_id, 0, -1)) and (runware_response := json.loads(data[0])):
        if errors := runware_response.get("errors"):
            logger.debug(bjson(errors))
            video.status = "failed"
            video.error = errors
            return video

        if data := runware_response.get("data"):
            if video_url := data[0].get("videoURL"):
                video.status = "completed"
                video.progress = 100
                video.video_url = video_url

    return video


if __name__ == '__main__':
    model = "openai:3@1"
    # model = "viduq2-turbo"
    model = "bytedance:2@2"
    # model = "kling-2.5"

    request = SoraVideoRequest(model=model, prompt="裸体女孩", seconds="5",

                               size="864x480",

                               )

    logger.info(request)

    # arun(create_task(request, api_key="TdgJuoP9VEyeBBtzuF5q6E1ibdioHAyV"))

    # https://openai-dev.chatfire.cn/sys/webhook/runware?expr=%24..taskUUID

    task_id = "72f0462b-bc54-4941-bb97-918fa0e49167"
    arun(get_task(task_id))

    # {
    #     "data": [
    #         {
    #             "taskType": "videoInference",
    #             "taskUUID": "8a5a1c09-d0a5-4b1b-9b67-8943cacc935f"
    #         }
    #     ]
    # }

"""
curl --request POST \
--url 'https://api.runware.ai/v1' \
--header "Authorization: Bearer Fk3Clsgcwc3faIvbsjDajGFATJLfaWpE" \
--header "Content-Type: application/json" \
--data-raw '[
  {
    "taskType": "videoInference",
    "duration": 4,
    "fps": 30,
    "height": 720,
    "width": 1280,
    "model": "openai:3@1",
    "numberResults": 1,
    "positivePrompt": "a cat",
    "taskUUID": "3f7fcfc4-e257-4cb7-bf97-439bceaa7cc3",
    "webhookURL": "https://openai-dev.chatfire.cn/sys/webhook/runware?expr=%24..taskUUID"
  }
]'
"""
