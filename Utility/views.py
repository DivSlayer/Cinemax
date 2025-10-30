import json
import math
import os
import re
import cv2
from django.core.validators import FileExtensionValidator
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.utils.text import slugify

Image_Validator = [FileExtensionValidator(allowed_extensions=["png", "jpg"])]
Video_Validator = [
    FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"])
]

"""
    This file should not be used in Models or Serializers
"""


def get_safe_words(string):
    list_words = []
    for word in string.strip().split(" "):
        check = re.match(r"[0-9A-Za-z]", word)
        if check is not None:
            list_words.append(check.string.lower())
    input_string = " ".join(list_words)
    input_string = input_string.encode("latin", "ignore")
    input_string = input_string.decode("utf-8", "ignore")
    input_string = input_string.replace("'", "")
    input_string = input_string.replace(",", "")
    input_string = input_string.replace(":", "").lower()
    input_string = " ".join(slugify(input_string).split('-'))
    slugged = slugify(input_string)
    reorder = slugged.replace('-', ' ')
    list_words = list(string)
    current = 0
    ordered_list = list(reorder)
    for word in list_words:
        if word == "-":
            ordered_list[current] = word
        current += 1
    return "".join(ordered_list)


def get_uuid():
    return get_random_string(10)


def get_duration(file_path):
    try:
        v = cv2.VideoCapture(file_path)
        frames = v.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = v.get(cv2.CAP_PROP_FPS)
        seconds = round(frames / fps)
        duration = math.ceil(seconds / 60)
        return duration
    except:
        return None


def get_size(file_path, bytes=False):
    try:
        size_bytes = os.path.getsize(file_path)
        size = size_bytes / 1024 / 1024 / 1024
        if size >= 1:
            size_str = str(math.ceil(size * 100) / 100) + " گیگابایت "
        else:
            size = size_bytes / 1024 / 1024
            if size >= 1:
                size_str = str(math.ceil(size * 10) / 10) + " مگابایت "
            else:
                size = size_bytes / 1024
                size_str = str(math.ceil(size * 10) / 10) + " کیلوبایت "
        return size_bytes if bytes else size_str
    except:
        return None


def get_resolution(file_path):
    try:
        vcap = cv2.VideoCapture(file_path)
        width = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
        res = ''
        print(int(width))
        if 700 < int(width) < 1200:
            res = '480p'
        if 1200 < int(width) < 1480:
            res = '720p'
        if 1900 < int(width) <= 1920:
            res = '1080p'
        if int(width) == 3840:
            res = '2160p'
        return res
    except Exception as e:
        print(e)
        return None


def get_sub_audio_nums(video_path, root_folder):
    sub_nums = 0
    audio_nums = 1
    metadata_path = root_folder + "/metadata.json"
    meta_data_command = f'ffprobe -loglevel 0 -print_format json -show_format -show_streams "{video_path}" > "{metadata_path}"'
    value = os.system(meta_data_command)
    if value == 0:
        content = ""
        with open(metadata_path, "r", encoding="utf8") as f:
            content = json.loads(f.read())
        if content["streams"]:
            for stream in content["streams"]:
                if stream["codec_type"] and stream["codec_type"] == "subtitle":
                    sub_nums += 1
                if stream["codec_type"] and stream["codec_type"] == "audio":
                    audio_nums += 1
        if os.path.isfile(metadata_path):
            os.remove(metadata_path)
        return sub_nums, audio_nums
    else:
        
        if os.path.isfile(metadata_path):
            os.remove(metadata_path)
        return 0, 1
