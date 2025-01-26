#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：spider_demo 
@File    ：test.py
@IDE     ：PyCharm 
@Author  ：liyuda
@Date    ：2025/1/23 17:54 
'''
import base64

import cv2
import json5
import requests
import random
import time
import re
from loguru import logger
import subprocess
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs
import ddddocr

slide = ddddocr.DdddOcr(det=False, ocr=False)


def generate_uuid():
    uuid = ''.join(
        [hex(random.randint(0, 15))[2:] if c == 'x'
         else hex((random.randint(0, 15) & 0x3 | 0x8))[2:]
         for c in 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx']
    )
    return uuid


def get_w_token(lot_number, captchaId, datetime, payload, process_token):
    with open('3.js', 'r', encoding='utf-8') as f:
        js_code = f.read()
    ctx = execjs.compile(js_code).call('get_w', lot_number, captchaId, datetime, payload, process_token)
    return ctx


def get_w_token_2(lot_number, captchaId, datetime, payload, process_token, slice, bg, distance, ypos):
    with open('3.js', 'r', encoding='utf-8') as f:
        js_code = f.read()
    ctx = execjs.compile(js_code).call('get_w_2', lot_number, captchaId, datetime, payload, process_token, slice, bg,
                                       distance, ypos)
    return ctx


# 调用函数生成 UUID

def load_first():
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.gate.io/",
        "sec-ch-ua": "Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    url = "https://gcaptcha4.geetest.com/load"
    # captcha_id : 固定值，每个网站给定
    # challenge : uuid
    params = {
        "captcha_id": "f85fe6bdf28d9ee3057b126962d24b30",
        "challenge": generate_uuid(),
        "client_type": "web",
        "lang": "zho",
        "callback": "geetest_" + str(int(time.time() * 1000))
    }
    response = requests.get(url, headers=headers, params=params)
    match = re.search(r'\((.*)\)', response.text)
    if match:
        extracted_content = match.group(1)  # 提取花括号内的内容
        data = json5.loads(extracted_content)
        return data
    return None


def verify_first(lot_number, payload, process_token, w):
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.gate.io/",
        "sec-ch-ua": "Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    url = "https://gcaptcha4.geetest.com/verify"
    params = {
        "callback": "geetest_" + str(int(time.time() * 1000)),
        "captcha_id": "f85fe6bdf28d9ee3057b126962d24b30",
        "client_type": "web",
        "lot_number": lot_number,
        "payload": payload,
        "process_token": process_token,
        "payload_protocol": "1",
        "pt": "1",
        "w": w
    }
    response = requests.get(url, headers=headers, params=params)
    # logger.info(response.text)
    # 使用正则表达式提取花括号内的内容
    match = re.search(r'\((.*)\)', response.text)
    if match:
        extracted_content = match.group(1)  # 提取花括号内的内容
        data = json5.loads(extracted_content)
        return data
    return None


def load_second(payload, lot_number, process_token):
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.gate.io/",
        "sec-ch-ua": "Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    url = "https://gcaptcha4.geetest.com/load"
    params = {
        "callback": "geetest_" + str(int(time.time() * 1000)),
        "captcha_id": "f85fe6bdf28d9ee3057b126962d24b30",
        "client_type": "web",
        "lot_number": lot_number,
        "pt": "1",
        "lang": "zho",
        "payload": payload,
        "process_token": process_token,
        "payload_protocol": "1"
    }
    response = requests.get(url, headers=headers, params=params)

    match = re.search(r'\((.*)\)', response.text)
    if match:
        extracted_content = match.group(1)  # 提取花括号内的内容
        data = json5.loads(extracted_content)
        return data
    return None


def save_png(slice_path, bg_path):
    slice_url = "https://static.geetest.com/" + slice_path
    bg_url = "https://static.geetest.com/" + bg_path
    url = [slice_url, bg_url]
    headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "i",
        "referer": "https://www.gate.io/",
        "sec-ch-ua": "Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "image",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    for i in url:
        type = i.split('/')[-2]
        response = requests.get(i, headers=headers)
        if response.status_code == 200:
            # 打开本地文件并写入图片二进制数据
            with open('./image/' + type + '.png', 'wb') as file:
                file.write(response.content)
            logger.warning("图片已保存为 {}".format('./image/' + type))
        else:
            logger.warning("图片下载失败，状态码：", response.status_code)


def get_distance():
    with open('./image/slice.png', 'rb') as f:
        target_bytes = f.read()
    with open('./image/bg.png', 'rb') as f:
        background_bytes = f.read()

    res = slide.slide_match(target_bytes, background_bytes, simple_target=True)

    return res['target'][0]+16-10


def verify_second(lot_number, payload, process_token, w):
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.gate.io/",
        "sec-ch-ua": "Google",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    url = "https://gcaptcha4.geetest.com/verify"
    params = {
        "callback": "geetest_" + str(int(time.time() * 1000)),
        "captcha_id": "f85fe6bdf28d9ee3057b126962d24b30",
        "client_type": "web",
        "lot_number": lot_number,
        "payload": payload,
        "process_token": process_token,
        "payload_protocol": "1",
        "pt": "1",
        "w": w
    }
    response = requests.get(url, headers=headers, params=params)
    return response.text


if __name__ == '__main__':
    res = load_first()
    captchaId = "f85fe6bdf28d9ee3057b126962d24b30"
    lot_number = res["data"]["lot_number"]
    payload = res["data"]["payload"]
    process_token = res["data"]["process_token"]
    datetime = res["data"]["pow_detail"]["datetime"]
    logger.success("lot_number: %s" % lot_number)
    logger.success("payload: %s" % payload)
    logger.success("process_token: %s" % process_token)
    logger.success("datetime: %s" % datetime)

    w = get_w_token(lot_number, captchaId, datetime, payload, process_token)
    logger.success("w: %s" % w)
    res = verify_first(lot_number, payload, process_token, w)
    logger.info(res)
    payload = res["data"]["payload"]
    lot_number = res["data"]["lot_number"]
    process_token = res["data"]["process_token"]
    logger.success("payload: %s" % payload)
    logger.success("lot_number: %s" % lot_number)
    logger.success("process_token: %s" % process_token)
    res = load_second(payload, lot_number, process_token)
    logger.info(res)

    slice = res["data"]["slice"]
    bg = res["data"]["bg"]
    logger.success("slice: %s" % slice)
    logger.success("bg: %s" % bg)
    save_png(slice, bg)
    distance = get_distance()
    logger.success("distance: %s" % distance)
    lot_number = res["data"]["lot_number"]
    payload = res["data"]["payload"]
    process_token = res["data"]["process_token"]
    datetime = res["data"]["pow_detail"]["datetime"]
    ypos = res["data"]["ypos"]
    logger.success("datetime: %s" % datetime)
    logger.success("lot_number: %s" % lot_number)
    logger.success("payload: %s" % payload)
    logger.success("process_token: %s" % process_token)
    logger.success("ypos: %s" % ypos)
    w = get_w_token_2(lot_number, captchaId, datetime, payload, process_token, slice, bg, distance, ypos)
    logger.success("w: %s" % w)
    res = verify_second(lot_number, payload, process_token, w)
    logger.info(res)
