"""
Platform-specific downloaders for Social Media GIF Downloader.
Each platform implements its own download logic while inheriting common functionality.
"""

import os
import re
import json
import logging
import platform
import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any


class PlatformDownloader(ABC):
    """Abstract base class for platform-specific downloaders."""

    def __init__(self, temp_file: str = "temp_video.mp4"):
        self.temp_file = temp_file
        self.yt_dlp_executable = 'yt-dlp.exe' if platform.system() == "Windows" else 'yt-dlp'

    @abstractmethod
    def detect_platform(self, url: str) -> bool:
        """Check if this downloader can handle the given URL."""
        pass

    @abstractmethod
    def get_download_formats(self) -> list:
        """Return yt-dlp format selection for this platform."""
        pass

    @abstractmethod
    def get_id_from_url(self, url: str) -> str:
        """Extract post/pin ID from URL for filename generation."""
        pass

    def get_video_info(self, url: str) -> Tuple[int, str]:
        """
        Get video FPS and default filename using yt-dlp.
        Returns: (fps, default_filename)
        """
        yt_dlp_command_info = [
            self.yt_dlp_executable,
            '--print-json',
            '-f', 'bestvideo[ext=mp4]',
            '--skip-download',
            url
        ]

        result_info = subprocess.run(
            yt_dlp_command_info,
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=(subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0)
        )

        video_fps = 15  # Default FPS
        if result_info.returncode == 0 and result_info.stdout:
            try:
                video_info = json.loads(result_info.stdout)
                video_fps = video_info.get('fps', 15)
            except json.JSONDecodeError:
                pass  # Use default FPS

        default_name = self.get_id_from_url(url)
        return video_fps, default_name

    def download_media(self, url: str, output_file: str, progress_callback=None, skip_conversion=False) -> bool:
        """
        Download media from the platform.
        Returns True if successful, False otherwise.
        """
        try:
            # For video downloads, download directly to output file
            if skip_conversion:
                download_target = output_file
            else:
                # Clean up any existing temp file
                if os.path.exists(self.temp_file):
                    os.remove(self.temp_file)
                download_target = self.temp_file

            formats = self.get_download_formats()
            yt_dlp_command_dl = [
                self.yt_dlp_executable,
                '-o', download_target,
                '--force-overwrites',
                url
            ]

            # Add format selection if specified
            if formats:
                yt_dlp_command_dl.insert(1, '-f')
                yt_dlp_command_dl.insert(2, formats)

            result_dl = subprocess.run(
                yt_dlp_command_dl,
                capture_output=True,
                text=True,
                creationflags=(subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0)
            )

            if result_dl.returncode != 0:
                logging.error(f"yt-dlp Error: {result_dl.stderr}")
                return False

            if not os.path.exists(download_target):
                logging.error("Downloaded file not found")
                return False

            # If we downloaded directly to output (video download), we're done
            if skip_conversion:
                return True

            # Otherwise, check if it's already a GIF
            if self.temp_file.lower().endswith('.gif'):
                # Just copy the GIF file
                import shutil
                shutil.copy2(self.temp_file, output_file)
                return True

            # Convert video to GIF
            return self.convert_to_gif(self.temp_file, output_file, progress_callback)

        except Exception as e:
            logging.error(f"Download error: {e}")
            return False

    def convert_to_gif(self, input_file: str, output_file: str, progress_callback=None) -> bool:
        """Convert video file to GIF format."""
        try:
            from moviepy.video.io.VideoFileClip import VideoFileClip

            logging.info("Creating VideoFileClip...")
            clip = VideoFileClip(input_file)
            logging.info(f"VideoFileClip created: {clip is not None}, duration: {clip.duration if clip else 'N/A'}")

            if clip is None:
                raise ValueError("VideoFileClip returned None")

            # Disable moviepy's default logger to prevent tqdm issues in bundled apps
            try:
                from moviepy import logger
                original_logger = logger.get_logger()
                logger.set_logger(None)  # Disable logging to avoid tqdm issues
                logger_restored = True
            except ImportError:
                logger_restored = False
                logging.warning("Could not import moviepy logger, proceeding without logger management")

            try:
                clip.write_gif(output_file, fps=15, logger=None)  # Default 15 FPS
                logging.info("write_gif completed")
                return True
            finally:
                # Restore original logger if it was successfully imported
                if logger_restored:
                    try:
                        logger.set_logger(original_logger)
                    except Exception as e:
                        logging.warning(f"Could not restore moviepy logger: {e}")

        except Exception as e:
            logging.error(f"GIF conversion error: {e}")
            return False
        finally:
            # Ensure clip is closed
            try:
                if 'clip' in locals() and clip is not None:
                    clip.close()
                    logging.info("VideoFileClip closed")
            except Exception as e:
                logging.warning(f"Error closing clip: {e}")

    def cleanup(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
                logging.info("Temporary file removed")
            except PermissionError:
                logging.warning("PermissionError removing temp file - file may still be in use")


class TwitterDownloader(PlatformDownloader):
    """Downloader for Twitter/X videos."""

    def detect_platform(self, url: str) -> bool:
        return 'twitter.com' in url or 'x.com' in url

    def get_download_formats(self) -> str:
        return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    def get_id_from_url(self, url: str) -> str:
        match = re.search(r"status/(\d+)", url)
        return match.group(1) if match else "tweet_video"


class PinterestDownloader(PlatformDownloader):
    """Downloader for Pinterest videos and GIFs."""

    def detect_platform(self, url: str) -> bool:
        return 'pinterest.com' in url

    def get_download_formats(self) -> Optional[str]:
        # Let yt-dlp choose the best format (it handles GIFs vs videos automatically)
        return None

    def get_id_from_url(self, url: str) -> str:
        match = re.search(r"pin/(\d+)/?", url)
        return match.group(1) if match else "pinterest_pin"


class InstagramDownloader(PlatformDownloader):
    """Downloader for Instagram videos (posts and reels only)."""

    def detect_platform(self, url: str) -> bool:
        return 'instagram.com' in url

    def get_download_formats(self) -> str:
        return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    def get_id_from_url(self, url: str) -> str:
        # Handle both posts (/p/) and reels (/reel/)
        match = re.search(r"(?:p|reel)/([A-Za-z0-9_-]+)", url)
        return match.group(1) if match else "instagram_post"


def get_platform_downloader(url: str, temp_file: str) -> Optional[PlatformDownloader]:
    """Factory function to get the appropriate downloader for a URL."""
    downloaders = [
        TwitterDownloader(temp_file=temp_file),
        PinterestDownloader(temp_file=temp_file),
        InstagramDownloader(temp_file=temp_file)
    ]

    for downloader in downloaders:
        if downloader.detect_platform(url):
            return downloader

    return None