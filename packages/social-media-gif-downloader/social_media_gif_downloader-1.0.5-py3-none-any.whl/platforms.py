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
import time
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any


class DownloadError(Exception):
    """Base exception for download errors with user-friendly messages."""
    
    def __init__(self, message: str, troubleshooting: str = ""):
        self.message = message
        self.troubleshooting = troubleshooting
        super().__init__(self.message)
    
    def get_user_message(self) -> str:
        """Get formatted message for display to user."""
        if self.troubleshooting:
            return f"{self.message}\n\nTroubleshooting:\n{self.troubleshooting}"
        return self.message


class NetworkError(DownloadError):
    """Network-related errors."""
    pass


class PlatformDownloader(ABC):
    """Abstract base class for platform-specific downloaders."""

    def __init__(self, temp_file: str = "temp_video.mp4", max_retries: int = 3, timeout: int = 60):
        self.temp_file = temp_file
        self.yt_dlp_executable = 'yt-dlp.exe' if platform.system() == "Windows" else 'yt-dlp'
        self.max_retries = max_retries
        self.timeout = timeout

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

    def _run_with_retry(self, command: list, operation: str) -> subprocess.CompletedProcess:
        """
        Run a subprocess command with automatic retry on failure.
        
        Args:
            command: Command list to execute
            operation: Human-readable operation name for error messages
            
        Returns:
            CompletedProcess result
            
        Raises:
            NetworkError: On network-related failures
            DownloadError: On other failures
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logging.info(f"Attempt {attempt}/{self.max_retries} for {operation}")
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=self.timeout,
                    creationflags=(subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0)
                )
                
                if result.returncode == 0:
                    logging.info(f"{operation} succeeded on attempt {attempt}")
                    return result
                
                # Check for network-related errors in stderr
                stderr_lower = result.stderr.lower()
                is_network_error = any(keyword in stderr_lower for keyword in [
                    'network', 'timeout', 'connection', 'timed out', 'unreachable',
                    'dns', 'unable to download', 'http error 5', 'errno'
                ])
                
                last_error = result.stderr
                
                if is_network_error and attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                    logging.warning(f"Network error on attempt {attempt}, retrying in {wait_time}s: {result.stderr[:200]}")
                    time.sleep(wait_time)
                    continue
                
                # Non-retryable error or last attempt
                break
                
            except subprocess.TimeoutExpired:
                logging.warning(f"Timeout on attempt {attempt}/{self.max_retries} for {operation}")
                last_error = f"Operation timed out after {self.timeout} seconds"
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logging.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt, break to raise error
                    break
                    
            except Exception as e:
                logging.error(f"Unexpected error on attempt {attempt}: {e}")
                last_error = str(e)
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt, break to raise error
                    break
                    
        # All retries exhausted
        if last_error and 'timed out' in str(last_error).lower():
            raise NetworkError(
                "Connection timed out - the download took too long to complete.",
                "• Check your internet connection\n"
                "• Try again in a few moments\n"
                "• The video might be too large or the server might be slow"
            )
        elif last_error and any(keyword in str(last_error).lower() for keyword in ['network', 'connection', 'unreachable', 'dns']):
            raise NetworkError(
                "Network connection error - couldn't reach the server.",
                "• Check your internet connection\n"
                "• Verify the URL is correct and the post is still available\n"
                "• Try disabling VPN/proxy if enabled\n"
                "• Your firewall might be blocking the connection"
            )
        elif last_error and ('private' in str(last_error).lower() or 'not available' in str(last_error).lower()):
            raise DownloadError(
                "Content not accessible - the post might be private or deleted.",
                "• Verify the post URL is correct\n"
                "• Check if the post is public (not private or deleted)\n"
                "• For private accounts, the content cannot be downloaded"
            )
        elif last_error and 'http error 404' in str(last_error).lower():
            raise DownloadError(
                "Content not found - the post doesn't exist or has been deleted.",
                "• Double-check the URL\n"
                "• The post may have been deleted by the author\n"
                "• Try copying the URL again from your browser"
            )
        elif last_error and ('format' in str(last_error).lower() or 'no video' in str(last_error).lower()):
            raise DownloadError(
                "No video found - this post doesn't contain downloadable video content.",
                "• Make sure the post contains a video (not just images)\n"
                "• Some content types (like Instagram stories) are not supported\n"
                "• Try a different post URL"
            )
        else:
            raise DownloadError(
                f"Download failed after {self.max_retries} attempts.",
                "• Check your internet connection\n"
                "• Verify the URL is correct\n"
                "• Try again in a few moments\n"
                f"• Error details: {last_error[:150]}"
            )

    def get_video_info(self, url: str) -> Tuple[int, str]:
        """
        Get video FPS and default filename using yt-dlp.
        Returns: (fps, default_filename)
        
        Raises:
            DownloadError: If unable to fetch video info
        """
        yt_dlp_command_info = [
            self.yt_dlp_executable,
            '--print-json',
            '-f', 'bestvideo[ext=mp4]',
            '--skip-download',
            url
        ]

        try:
            result_info = self._run_with_retry(yt_dlp_command_info, "fetch video info")
            
            video_fps = 15  # Default FPS
            if result_info.stdout:
                try:
                    video_info = json.loads(result_info.stdout)
                    video_fps = video_info.get('fps', 15)
                except json.JSONDecodeError:
                    logging.warning("Could not parse video info JSON, using default FPS")

            default_name = self.get_id_from_url(url)
            return video_fps, default_name
            
        except (NetworkError, DownloadError):
            raise
        except Exception as e:
            logging.error(f"Error getting video info: {e}")
            raise DownloadError(
                "Failed to retrieve video information.",
                "• Check if the URL is valid\n"
                "• Make sure the post is public and contains a video\n"
                f"• Error: {str(e)[:100]}"
            )

    def download_media(self, url: str, output_file: str, progress_callback=None, skip_conversion=False, fps: int = 15) -> bool:
        """
        Download media from the platform.
        Returns True if successful, False otherwise.
        
        Raises:
            DownloadError: On download failures with user-friendly messages
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

            # Download with retry mechanism
            self._run_with_retry(yt_dlp_command_dl, "download media")

            if not os.path.exists(download_target):
                raise DownloadError(
                    "Download completed but file not found.",
                    "• Try downloading again\n"
                    "• Check if you have write permissions to the output folder\n"
                    "• Your antivirus might be blocking the file"
                )

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
            return self.convert_to_gif(self.temp_file, output_file, progress_callback, fps)

        except (NetworkError, DownloadError):
            raise
        except Exception as e:
            logging.error(f"Download error: {e}")
            raise DownloadError(
                f"An unexpected error occurred during download.",
                "• Check your internet connection\n"
                "• Make sure you have enough disk space\n"
                "• Try restarting the application\n"
                f"• Error: {str(e)[:100]}"
            )

    def convert_to_gif(self, input_file: str, output_file: str, progress_callback=None, fps: int = 15) -> bool:
        """
        Convert video file to GIF format.
        
        Raises:
            DownloadError: If conversion fails
        """
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
                clip.write_gif(output_file, fps=fps, logger=None)
                logging.info(f"write_gif completed at {fps} FPS")
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
            raise DownloadError(
                "Failed to convert video to GIF format.",
                "• The video file might be corrupted\n"
                "• Try downloading as video (MP4) instead\n"
                "• Make sure you have enough disk space\n"
                "• FFmpeg might not be installed correctly"
            )
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
