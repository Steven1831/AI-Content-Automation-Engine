import subprocess
import tempfile
from pathlib import Path
from typing import List

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class FFmpegTool(BaseModelTool):
    """
    Tool for basic video editing operations using FFmpeg.
    """

    def _run(self, cmd: List[str]) -> None:
        # shell=False is better for Windows with list of args
        p = subprocess.run(cmd, shell=False)
        if p.returncode != 0:
            raise RuntimeError(f"FFmpeg falló: {' '.join(cmd)}")

    def split_audio(
        self,
        audio_in: Path,
        audio_out: Path,
        start_time: float,
        duration: float
    ) -> None:
        """
        Splits an audio file into a segment starting at start_time with duration.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", str(audio_in),
            "-ss", str(start_time),
            "-t", str(duration),
            "-v", "error",
            str(audio_out)
        ]
        self._run(cmd)

    def make_transition_video(
        self,
        img_a: Path,
        img_b: Path,
        out_path: Path,
        seconds: int = 4
    ) -> None:
        offset = max(0, seconds - 1)
        xfade_filter = f"[0:v][1:v]xfade=transition=fade:duration=1:offset={offset},format=yuv420p"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(seconds), "-i", str(img_a),
            "-loop", "1", "-t", str(seconds), "-i", str(img_b),
            "-filter_complex", xfade_filter,
            "-t", str(seconds), str(out_path)
        ]
        self._run(cmd)

    def concat_videos(
        self,
        video_list: List[Path],
        out_path: Path,
    ) -> None:
        with tempfile.TemporaryDirectory() as td_str:
            td = Path(td_str)
            list_path = td / "files.txt"
            with open(list_path, "w", encoding="utf-8") as f:
                for v in video_list:
                    abs_v = v.absolute()
                    # FFmpeg concat file expects single quotes escaped or double quotes? 
                    # Usually it's: file 'path' (with backslashes escaped or forward slashes)
                    safe_v = str(abs_v).replace("'", "'\\''")
                    f.write(f"file '{safe_v}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                str(out_path)
            ]
            self._run(cmd)

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Retrieves the duration of an audio file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        output = subprocess.check_output(cmd, shell=False).decode("utf-8").strip()
        return float(output)

    def get_video_duration(self, video_path: Path) -> float:
        """
        Retrieves the duration of a video file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, shell=False).decode("utf-8").strip()
        return float(output)

    def sync_video_and_audio(
        self,
        video_in: Path,
        audio_in: Path,
        video_out: Path
    ) -> None:
        """
        Synchronizes a video file to an audio file's duration.
        """
        audio_dur = self.get_audio_duration(audio_in)
        video_dur = self.get_video_duration(video_in)

        if video_dur <= 0:
            raise RuntimeError(f"Invalid video duration: {video_dur} for {video_in}")

        scale = audio_dur / video_dur

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-i", str(audio_in),
            "-filter_complex", f"[0:v]setpts={scale:.6f}*PTS[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
            "-v", "error",
            str(video_out)
        ]
        self._run(cmd)

    def get_video_height(self, video_path: Path) -> int:
        """
        Retrieves the height of a video file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=height",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, shell=False).decode("utf-8").strip()
        return int(output)

    def get_video_width(self, video_path: Path) -> int:
        """
        Retrieves the width of a video file using ffprobe.
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        output = subprocess.check_output(cmd, shell=False).decode("utf-8").strip()
        return int(output)

    def create_composite_scene_video(
        self,
        img_path: Path,
        audio_path: Path,
        out_path: Path
    ) -> None:
        """
        Creates a video with a 3-part dynamic sequence.
        """
        duration = self.get_audio_duration(audio_path)
        fps = 25
        total_frames = int(duration * fps)
        f1 = total_frames * 0.3
        f2 = total_frames * 0.7

        width = self.get_video_width(img_path)
        height = self.get_video_height(img_path)

        z_expr = (
            f"if(lt(on,{f1}), 1.0+0.2*(on/{f1}), "
            f"if(lt(on,{f2}), 1.2, "
            f"1.2-0.2*((on-{f2})/({total_frames}-{f2}))))"
        )
        pos_filter = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        zoom_filter = f"zoompan=z='{z_expr}':d=1:{pos_filter}:s={width}x{height},format=yuv420p"
        
        # Handheld Jitter (random small movements)
        jitter_filter = "vignette,noise=alls=10:allf=t+u,curves=vintage"
        
        # Jitter via random crop or rotate
        # Let's use a simpler approach: slightly varying rotation and zoom
        rotate_expr = "rotate='1*PI/180*sin(2*PI*t/3) + 0.1*sin(2*PI*t*5)'" # Added high freq jitter
        
        # Flicker (random brightness changes)
        flicker_filter = "drawbox=y=ih-1:color=black@0.1,eq=brightness='0.02*sin(2*PI*t*10)':contrast=1.1"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img_path),
            "-i", str(audio_path),
            "-vf", f"{zoom_filter},{rotate_expr},{jitter_filter},{flicker_filter}",
            "-shortest",
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
            str(out_path)
        ]
        self._run(cmd)

    def extract_audio(self, video_in: Path, audio_out: Path) -> None:
        """
        Extracts audio from a video file.
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-vn", "-ac", "1", "-ar", "16000",
            str(audio_out)
        ]
        self._run(cmd)

    def add_subtitles_to_video(
        self,
        video_in: Path,
        srt_path: Path,
        video_out: Path,
        font_size: int = 64
    ) -> None:
        """
        Adds subtitles to a video.
        """
        width = self.get_video_width(video_in)
        height = self.get_video_height(video_in)
        margin_v = int(height * 0.15)

        # FFmpeg subtitles filter needs escaped path for Windows
        safe_srt = str(srt_path).replace("\\", "/").replace(":", "\\:")
        
        style = (
            f"PlayResX={width},PlayResY={height},"
            f"FontName=Impact,FontSize={font_size},PrimaryColour=&H00FFFF,"
            f"OutlineColour=&H000000,BorderStyle=1,Outline=2,"
            f"Alignment=2,MarginV={margin_v}"
        )
        sub_filter = f"subtitles={safe_srt}:force_style='{style}'"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-vf", sub_filter,
            "-c:a", "copy",
            str(video_out)
        ]
        self._run(cmd)

    def add_background_music(
        self,
        video_in: Path,
        audio_bg: Path,
        video_out: Path,
        bg_volume: float = 0.15
    ) -> None:
        """
        Mixes a background audio track into a video.
        """
        filter_complex = (
            f"[0:a]volume=1.0[v_a]; "
            f"[1:a]volume={bg_volume}[bg_a]; "
            "[v_a][bg_a]amix=inputs=2:duration=first[fixed_a]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-stream_loop", "-1", "-i", str(audio_bg),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[fixed_a]",
            "-c:v", "copy", "-c:a", "aac",
            str(video_out)
        ]
        self._run(cmd)
