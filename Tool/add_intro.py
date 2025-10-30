import json
import os
import shutil
import subprocess

from Movie.management.commands.step_function import StepFunction
from Movie.models import Subtitle as MovieSubtitle, Video
from Movie.values import get_movie_root
from Tool.get_soft_subtitle import SoftSubtitle


def get_video_duration(path):
    """
    This function will get the duration of the video
    Args:
        path: video path
    """
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', path
    ]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(process.stdout.strip()) if process.returncode == 0 else 0


def get_sar(video_path: str) -> str:
    """
    Returns the sample aspect ratio (SAR) of the first video stream,
    in the form "num:den". Falls back to "1:1" if we can’t read it.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=sample_aspect_ratio",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        sar = subprocess.check_output(cmd).decode().strip()
        # Some files report “0:1” for square pixels—normalize that:
        if not sar or sar.startswith("0"):
            return "1:1"
        return sar
    except subprocess.CalledProcessError:
        return "1:1"


class AddIntro:
    def __init__(self, video: Video):
        self.steps = []
        self.video = video
        self.original_intro = os.path.join(os.getcwd(), 'media', 'env', 'intro.mp4')
        self.temp_intro = None
        self.temp_video = None
        self.merged = None
        self.final_video = None
        self.calculate_steps()

    def calculate_steps(self):
        resize = StepFunction(name='Resizing intro', function=self.resizing_intro)
        self.steps.append(resize)
        if self.video.file.name.split('.')[-1] == 'mp4':
            convert_mkv = StepFunction(name='Converting to mkv', function=self.convert_to_mkv)
            self.steps.append(convert_mkv)
        concatenating = StepFunction(name="Concatenating videos", function=self.concatenating)
        self.steps.append(concatenating)
        if self.video.subbed:
            adjust_sub = StepFunction(name="Adjusting subtitle timing", function=self.adjust_subtitle_timing)
            adding_subtitle = StepFunction(name="Adding subtitle to video", function=self.adding_subtitle)
            self.steps.append(adjust_sub)
            self.steps.append(adding_subtitle)
        shift_censors = StepFunction(name="Shift censors and credits", function=self.adjust_censors_timing)
        self.steps.append(shift_censors)
        cleanup = StepFunction(name="Cleanup", function=self.cleanup)
        self.steps.append(cleanup)

    def get_video_resolution(self):
        """Get video resolution with proper Windows path handling
        return:
            width*height
        """
        video_path = os.path.normpath(self.video.file.path)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of',
             'csv=s=x:p=0', video_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=10
        )

        resolution = result.stdout.decode().strip()
        if 'x' not in resolution:
            raise ValueError(f"Invalid resolution format: {resolution}")
        return resolution

    def resizing_intro(self):
        resolution = self.get_video_resolution()
        width, height = resolution.split('x') if 'x' in resolution else (1920, 1080)
        main_sar = get_sar(self.video.file.path)
        temp_intro = os.path.join(os.getcwd(), get_movie_root(self.video.movie, use_media=True,
                                                              filepath=f"temp_intro_{self.video.uuid}.mkv"))
        self.temp_intro = temp_intro
        cmd = [
            'ffmpeg', '-y',
            '-i', f'"{self.original_intro}"',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
            '-vf',
            f'scale=w={width}:h={height}:force_original_aspect_ratio=decrease,'
            f'pad=w={width}:h={height}:x=(ow-iw)/2:y=(oh-ih)/2:color=black,'
            f'setsar={main_sar},format=yuv420p',
            '-c:a', 'aac', '-b:a', '128k', '-ac', '2',
            '-threads', '0', '-profile:v', 'high', '-tune', 'film',
            f'"{self.temp_intro}"'

        ]

        return [subprocess.Popen(
            ' '.join(cmd),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True,
            text=True
        )], [None]

    def convert_to_mkv(self):
        """
            This function will convert video file from mp4 to mkv
        """
        temp_video = os.path.join(os.getcwd(), get_movie_root(self.video.movie, use_media=True,
                                                              filepath=f"temp_video_{self.video.uuid}.mkv"))
        self.temp_video = temp_video
        cmd = [
            'ffmpeg', '-y',
            '-i', f'"{self.video.file.path}"',
            '-c', 'copy',
            f'"{self.temp_video}"'
        ]
        return [subprocess.Popen(
            ' '.join(cmd),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True,
            text=True
        )], [None]

    def adjust_subtitle_timing(self):
        subs = MovieSubtitle.objects.filter(video=self.video)
        intro_duration = get_video_duration(self.original_intro)
        for sub in subs:
            SoftSubtitle([]).adjust_srt_timing(input_file=sub.srt.path, shift_seconds=intro_duration,
                                               vtt_path=sub.vtt.path)
        return [None], [None]

    def adjust_censors_timing(self):
        """
        Shift all censor and credit timestamps by the intro’s duration.
        """
        d = get_video_duration(self.original_intro)

        def _shift(json_str: str) -> str:
            return json.dumps([
                {'start': float(seg['start']) + d, 'end': float(seg['end']) + d}
                for seg in json.loads(json_str)
            ])

        c, cr = map(_shift, (self.video.censors, self.video.credits))
        self.video.censors, self.video.credits = c, cr
        self.video.save(update_fields=['censors', 'credits'])
        return [None], [None]

    def concatenating(self):
        """
        This function will concatenate video file to the intro file
        """
        main_video = self.temp_video if self.temp_video is not None else self.video.file.path
        self.merged = os.path.join(os.getcwd(), get_movie_root(self.video.movie, use_media=True,
                                                               filepath=f"merged_video_{self.video.uuid}.mkv"))
        print("Im the call back from concatenating")
        cmd = [
            'ffmpeg', '-y',
            '-i', f'"{self.temp_intro}"',
            '-i', f'"{main_video}"',
            '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-threads', '0', '-profile:v', 'high', '-tune', 'film',
            f'"{self.merged}"'
        ]

        print("concatenating command: {}".format(" ".join(cmd)))

        self.final_video = self.merged

        return [subprocess.Popen(
            ' '.join(cmd),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True,
            text=True
        )], [None]

    def adding_subtitle(self):
        """
        This function will add all the subtitles to the new concatenated video
        """
        subs = MovieSubtitle.objects.filter(video=self.video)
        soft_ins = SoftSubtitle([self.video.uuid])
        temp_video = os.path.join(os.getcwd(), get_movie_root(self.video.movie, use_media=True,
                                                              filepath=f"temp_video_{self.video.uuid}.mkv"))
        self.temp_video = temp_video
        processes, context = soft_ins.add_soft_to_video(subs_path=[sub.srt.path for sub in subs],
                                                        input_path=self.merged, output_path=self.temp_video)

        self.final_video = self.temp_video
        return processes, context

    def cleanup(self):
        print("cleaning up")
        if self.final_video is not None and os.path.isfile(self.final_video):
            shutil.move(self.final_video, self.video.file.path)
        if self.temp_intro is not None and os.path.isfile(self.temp_intro):
            os.remove(self.temp_intro)
        if self.temp_video is not None and os.path.isfile(self.temp_video):
            shutil.move(self.temp_video, self.video.file.path)
        if self.merged is not None and os.path.isfile(self.merged):
            os.remove(self.merged)
        return [None], [None]
