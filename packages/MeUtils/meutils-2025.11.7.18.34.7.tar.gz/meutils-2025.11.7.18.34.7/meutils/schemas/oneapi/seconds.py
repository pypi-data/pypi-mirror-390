#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : seconds
# @Time         : 2025/10/31 19:15
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

data = {
    "minimax-hailuo-2.3_768p": 0.22,
    "minimax-hailuo-2.3_1080p": 0.32,
    "minimax-hailuo-2.3-fast_768p": 0.128,
    "minimax-hailuo-2.3-fast_1080p": 0.22,
    "viduq2-turbo_720p": 0.2,
    "viduq2-turbo_1080p": 0.8,
    "viduq2-pro_720p": 0.2,
    "viduq2-pro_1080p": 0.8,

    "doubao-seedance-1-0-pro-fast-251015_480p": 0.025,
    "doubao-seedance-1-0-pro-fast-251015_720p": 0.05,
    "doubao-seedance-1-0-pro-fast-251015_1080p": 0.1
}




if __name__ == '__main__':

     _ = ','.join([k for k, v in data.items() if k.startswith("doubao")])

     print(_)
