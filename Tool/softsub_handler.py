import asyncio
import json
import os
import shutil
import subprocess

from asgiref.sync import sync_to_async

from Movie.models import Movie, Video, Subtitle as MovieSubtitle
from Movie.values import get_movie_root
from Serial.models import Episode, EpisodeSubtitle
from Serial.values import get_serial_root
from Tool.mark_sub import MarkSub
from Tool.views import convert_vtt
from Utility.no_serializer import get_object
from Utility.translator import translate_text
from Utility.views import get_sub_audio_nums


class SoftSubtitle:
    def __init__(self, uuids: list, mark=True):
        """
        Args:
            uuids (str): The UUIDs of the Movies, Videos or Episodes that you want to change
            mark (bool): Whether the subtitle should be marked or not
        """
        self.uuids = uuids
        self.objects = []
        self.done_subs = []
        self.set_objects()
        self.mark = mark

    def set_objects(self):
        for uuid in self.uuids:
            obj = get_object(uuid, use_imdb=False)
            self.objects.append(obj)

    def get_subs_folder(self, obj):
        if obj is not None:
            if type(obj) == Movie:
                subs_folder = get_movie_root(obj, filepath="subs", use_media=True)
                if not os.path.isdir(subs_folder):
                    os.makedirs(subs_folder, exist_ok=True)
                return subs_folder
            if type(obj) == Video:
                subs_folder = get_movie_root(obj.movie, filepath="subs", use_media=True)
                if not os.path.isdir(subs_folder):
                    os.makedirs(subs_folder, exist_ok=True)
                return subs_folder
            elif type(obj) == Episode:
                subs_folder = get_serial_root(
                    obj.serial,
                    filepath=f"episodes/season-{obj.season.number}/subs",
                    use_media=True,
                )

                if not os.path.isdir(subs_folder):
                    os.makedirs(subs_folder, exist_ok=True)
                return subs_folder

    def get_video_path(self, obj):
        if type(obj) == Movie:
            videos = Video.objects.filter(movie=obj)
            video = videos.first()
            return video.file.path
        elif type(obj) == Episode:
            return obj.video.path
        elif type(obj) == Video:
            return obj.file.path

    def save_instance(self, srt_path, obj, language="Persian"):
        sub_instance = None
        if type(obj) == Movie:
            sub_instance = MovieSubtitle.objects.create(video=obj)
        if type(obj) == Episode:
            sub_instance = EpisodeSubtitle.objects.create(episode=obj)
        if type(obj) == Video:
            sub_instance = MovieSubtitle.objects.create(video=obj)
        sub_instance.srt.name = str(srt_path).replace("media/", "")
        try:
            sub_instance.language = asyncio.run(translate_text(language))
        except:
            sub_instance.language = 'فارسی'
        sub_instance.vtt.name = (
            str(srt_path).replace("media/", "").replace(".srt", ".vtt")
        )
        sub_instance.save()
        self.done_subs.append(sub_instance)

    def get_root_folder(self, obj):
        if type(obj) == Movie:
            return get_movie_root(obj, use_media=True, )
        elif type(obj) == Video:
            return get_movie_root(obj.movie, use_media=True, )
        elif type(obj) == Episode:
            return get_serial_root(obj.serial, use_media=True, )

    def action(self):
        """
        It will extract the subtitles from the video
        """
        processes = []
        contexts = []
        for obj in self.objects:
            subs_folder = self.get_subs_folder(obj)
            video_path = self.get_video_path(obj)
            root_folder = self.get_root_folder(obj)
            sub_file_name = (
                f"soft-sub-s{obj.season.number}e{obj.number}"
                if type(obj) == Episode
                else f"soft-sub-{obj.uuid}"
            )
            subs_num, audio_num = get_sub_audio_nums(video_path, root_folder)
            for i in range(0, subs_num):
                # Extracting subtitle from video
                cmd = [
                    'ffmpeg', '-y',
                    '-i', f'"{video_path}"',
                    '-map', f'0:s:{i}',
                    '-f', 'matroska copy',
                    f'"{subs_folder}/{sub_file_name}-{i}.srt"'

                ]
                language_c = f'ffprobe -loglevel error -select_streams s:{i} -show_entries stream_tags=language -of csv=p=0 "{video_path}"'
                language = subprocess.check_output(language_c, shell=True)
                language = str(language.decode().strip())
                language = "English" if language == "eng" else "Persian"
                process = subprocess.Popen(
                    ' '.join(cmd),
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    shell=True,
                    text=True
                )
                processes.append(process)
                contexts.append((subs_folder, sub_file_name, i, obj, language))
        return processes, contexts

    def post_extracting(self, context):
        subs_folder, sub_file_name, i, obj, language = context
        sub_path = f"{subs_folder}/{sub_file_name}-{i}.srt"
        if os.path.isfile(sub_path):
            if self.mark:
                MarkSub(sub_path).save_file(sub_path)
            convert = convert_vtt(sub_path)
            if convert:
                self.save_instance(sub_path, obj, language)
            else:
                os.remove(sub_path)

    def remove_sub(self):
        """
        This function will remove subtitle from a video

        """
        processes = []
        contexts = []
        for obj in self.objects:
            video_path = self.get_video_path(obj)
            old_video_name = video_path.split("\\")[-1]
            ext = old_video_name.split(".")[-1]
            root_folder = self.get_root_folder(obj)
            no_subs_vid_path = f"{root_folder}video-no-subs.{ext}"  # The path of the video that has no subs

            cmd = [
                'ffmpeg', '-y',
                '-i', f'"{video_path}"',
                '-vcodec', 'copy',
                '-acodec', 'copy',
                '-sn', f'"{no_subs_vid_path}"'
            ]
            process = subprocess.Popen(
                ' '.join(cmd),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True,
                text=True
            )
            processes.append(process)
            contexts.append((obj, video_path, no_subs_vid_path, old_video_name, ext, root_folder))
        return processes, contexts

    def hasSoftSub(self, name):
        """
        This function will check if the video is softsub
        """
        if str(name).lower().find("softsub") != -1:
            return True
        if str(name).lower().find("subbed") != -1:
            return True
        if str(name).lower().find("soft-sub") != -1:
            return True
        return False

    def add_soft_to_video(self, subs_path: list, language="Persian", output_path=None, input_path=None):
        """
        This function will add soft subtitles to the video

        Args:
            subs_path: a list of the subtitles path that are going to be added to the video
            language: the language of the subtitles
            output_path: the output path of the video
            input_path: the input path of the video
        """
        processes = []
        contexts = []
        for obj in self.objects:
            for sub_path in subs_path:
                video_path = input_path if input_path is not None else self.get_video_path(obj)
                ext = os.path.splitext(video_path)[1]
                root_folder = self.get_root_folder(obj)
                out_put_vid = output_path if output_path is not None else f"{root_folder}output.{ext}"
                old_video_name = video_path.split("\\")[-1]
                ext = old_video_name.split(".")[-1]
                cmd = [
                    'ffmpeg', '-y',
                    '-i', f'"{video_path}"',
                    '-sub_charenc', 'UTF-8',
                    '-f', 'srt',
                    '-i', f'"{sub_path}"',
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    '-c:s', 'copy',
                    '-map', '0',
                    '-map', '1:s',
                    '-metadata:s:s:0', f'language={"fa" if language == "Persian" else "en"}',
                    '-metadata:s:s:0', f'title="{language} - Cinemax.com"',
                    f'"{out_put_vid}"'
                ]
                process = subprocess.Popen(
                    ' '.join(cmd),
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    shell=True,
                    text=True
                )
                processes.append(process)
                contexts.append((obj, sub_path, video_path, out_put_vid, old_video_name, ext, root_folder))
        return processes, contexts

    def post_add_processing(self, context):
        obj, sub_path, video_path, out_put_vid, old_video_name, ext, root_folder = context
        if os.path.isfile(out_put_vid):
            os.remove(video_path)
        video_name = old_video_name
        if not self.hasSoftSub(old_video_name):
            video_name = video_name.replace(".Cinemax", ".SoftSub.Cinemax")
            video_path = video_path.replace(".Cinemax", ".SoftSub.Cinemax")
        shutil.move(out_put_vid, video_path)
        asyncio.run(self._update_video_path(obj, video_name, ext))
        obj.subbed = True
        obj.save()
        return obj


    def get_sub_nums(self, video_path, root_folder):
        sub_nums = 0
        metadata_path = root_folder + "metadata.json"
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
            return sub_nums
        else:
            return 0

    def adjust_srt_timing(self, input_file, shift_seconds=5, vtt_path=None):
        """
        Shift all subtitles in an SRT file forward by specified seconds.

        Args:
            input_file (str): Path to input SRT file
            vtt_path (str|None): Path to input VTT file
            shift_seconds (float): Number of seconds to shift (positive for forward, negative for backward)
        """

        def time_to_ms(time_str):
            parts = time_str.replace(',', ':').split(':')
            h, m, s, ms = map(int, parts)
            return h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + ms

        def ms_to_time(ms):
            hours, ms = divmod(ms, 3600 * 1000)
            minutes, ms = divmod(ms, 60 * 1000)
            seconds, ms = divmod(ms, 1000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

        shift_ms = int(shift_seconds * 1000)
        outlines = []
        if self.mark:
            MarkSub(input_file).save_file(input_file)
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                if '-->' in line:
                    parts = line.strip().split(' --> ')
                    if len(parts) == 2:
                        start, end = parts
                        # Convert times to milliseconds and apply shift
                        start_ms = time_to_ms(start) + shift_ms
                        end_ms = time_to_ms(end) + shift_ms
                        # Convert back to time strings
                        new_start = ms_to_time(start_ms)
                        new_end = ms_to_time(end_ms)
                        # Write adjusted time line
                        outlines.append(f"{new_start} --> {new_end}\n")
                    else:
                        outlines.append(line)
                else:
                    outlines.append(line)
        with open(input_file, 'w', encoding='utf-8') as outfile:
            for line in outlines:
                outfile.write(line)
        if vtt_path is not None and os.path.isfile(vtt_path):
            os.remove(vtt_path)
        convert = convert_vtt(input_file)

    def post_remove_processing(self, context):
        obj, video_path, no_subs_vid_path, old_video_name, ext, root_folder = context
        if os.path.isfile(no_subs_vid_path):
            os.remove(video_path)
        video_name = old_video_name
        if self.hasSoftSub(video_path):
            video_path = self._clean_sub_name(video_path)
            video_name = self._clean_sub_name(old_video_name)
        if os.path.isfile(no_subs_vid_path):
            shutil.move(no_subs_vid_path, video_path)
        self._update_video_path(obj, video_name, ext)
        return obj


    def _clean_sub_name(self, name):
        patterns = [".SoftSub", ".softsub", ".soft-sub", ".Soft-Sub", ".subbed"]
        for pattern in patterns:
            name = name.replace(pattern, "")
        return name

    @sync_to_async
    def _update_video_path(self, obj, video_name, ext):
        print(f'updating name of: {type(obj)}')
        print(video_name)
        if type(obj) == Video:
            new_name = get_movie_root(
                obj.movie, filepath=video_name, use_media=False
            )
            print("new_name: ", new_name)
            obj.file.name = new_name
            obj.save()
            print("Video name updated")
        if type(obj) == Episode:
            obj.video.name = get_serial_root(
                obj.serial,
                filepath=f"episodes/season-{obj.season.number}/{video_name}",
                use_media=False,
            )
            obj.save()
        obj.save()
