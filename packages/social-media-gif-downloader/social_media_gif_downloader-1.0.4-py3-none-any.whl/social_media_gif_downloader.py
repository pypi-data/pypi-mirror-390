"""
Copyright (c) 2024 ax2bboud

This software is licensed under the MIT License. See LICENSE file for details.

This project uses the following third-party libraries:
- moviepy (MIT License, Copyright (c) 2015 Zulko)
- customtkinter (MIT License, Copyright (c) 2021 Tom Schimansky)
- yt-dlp (Unlicense - Public Domain)
- FFmpeg (LGPL v2.1 or later, Copyright (c) 2000-2023 the FFmpeg developers)

For full attributions and license texts, see ATTRIBUTIONS.md.
"""

__version__ = "1.0.4"

import sys
import os
import re  # For parsing the URL
import json  # For reading video metadata
import logging
import platform
import tempfile
from typing import Optional, Any

# Configure logging
if getattr(sys, 'frozen', False):
    # In bundled exe, log to a file since console may not be visible
    log_file = os.path.join(os.path.dirname(sys.executable), 'social_media_gif_downloader.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
else:
    # In development, log to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# --- PYINSTALLER FFMPEG FIX ---
# This block must be at the VERY TOP, before moviepy is imported.
# It tells the script where to find ffmpeg.exe when it's bundled.
if getattr(sys, 'frozen', False):
    if hasattr(sys, '_MEIPASS'):
        # This is the temporary path PyInstaller creates
        base_path = sys._MEIPASS
    else:
        # Fallback for some environments
        base_path = os.path.dirname(sys.executable)

    # Set the environment variable for moviepy
    ffmpeg_binary = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    ffmpeg_path = os.path.join(base_path, ffmpeg_binary)
    os.environ["FFMPEG_BINARY"] = ffmpeg_path
    logging.info(f"Frozen mode: FFMPEG_BINARY set to {ffmpeg_path}")
else:
    logging.info("Running in non-frozen mode")
# --- END OF FIX ---


# Now, when moviepy is imported, it will use the path we just set
from moviepy.video.io.VideoFileClip import VideoFileClip
import customtkinter as ctk
import tkinter.filedialog as filedialog
import threading
import subprocess
from platforms import get_platform_downloader, TwitterDownloader, PinterestDownloader, InstagramDownloader, DownloadError, NetworkError
from config import Config


# --- Constants ---
if getattr(sys, 'frozen', False):
    TEMP_VIDEO_FILE = os.path.join(tempfile.gettempdir(), "temp_video.mp4")
else:
    TEMP_VIDEO_FILE = "temp_video.mp4"
DEFAULT_GIF_FPS = 15  # Fallback if FPS detection fails


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration ---
        self.config = Config()

        # --- Window Setup ---
        self.title("Social Media GIF Downloader")
        self.geometry("600x450")
        ctk.set_appearance_mode("System")

        # --- Widgets ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # URL Entry
        self.url_label = ctk.CTkLabel(self, text="Paste Social Media Post URL:")
        self.url_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.url_entry = ctk.CTkEntry(self, placeholder_text="https://x.com/user/status/123... or https://pinterest.com/pin/123... or https://instagram.com/p/... or /reel/...")
        self.url_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Default Save Location
        self.save_location_button = ctk.CTkButton(
            self.settings_frame, text="Set Default Save Location",
            command=self.set_default_save_location, width=150
        )
        self.save_location_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Preferred Output Format
        self.format_var = ctk.StringVar(value=self.config.get_preferred_output_format())
        self.format_menu = ctk.CTkOptionMenu(
            self.settings_frame, variable=self.format_var,
            values=["gif", "mp4"],
            command=self.on_format_change
        )
        self.format_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # FPS Settings
        self.fps_label = ctk.CTkLabel(self.settings_frame, text=f"FPS: {self.config.get_fps_settings()}")
        self.fps_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.fps_slider = ctk.CTkSlider(
            self.settings_frame, from_=1, to=60,
            number_of_steps=59,
            command=self.on_fps_change
        )
        self.fps_slider.set(self.config.get_fps_settings())
        self.fps_slider.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Button Frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Download Buttons
        self.download_gif_button = ctk.CTkButton(
            self.button_frame, text="Download as GIF",
            command=lambda: self.start_download_thread(convert_to_gif=True)
        )
        self.download_gif_button.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="ew")

        self.download_video_button = ctk.CTkButton(
            self.button_frame, text="Download as Video",
            command=lambda: self.start_download_thread(convert_to_gif=False)
        )
        self.download_video_button.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="ew")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, width=400, height=15)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.progress_bar.set(0)  # Start at 0%

        # Status Label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            wraplength=550,
            justify="left"
        )
        self.status_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="ew")

        # Supported platforms info
        self.platforms_label = ctk.CTkLabel(
            self,
            text="Supports: Twitter/X, Pinterest, Instagram (videos only)",
            font=("", 10)
        )
        self.platforms_label.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="w")

    def set_default_save_location(self):
        """Set the default save location."""
        current_location = self.config.get_default_save_location()
        initial_dir = current_location if current_location and os.path.exists(current_location) else os.path.expanduser("~")
        
        directory = filedialog.askdirectory(
            title="Select Default Save Location",
            initialdir=initial_dir
        )
        
        if directory:
            self.config.set_default_save_location(directory)
            self.update_status(f"Default save location set to: {directory}", "green")
    
    def on_format_change(self, new_format: str):
        """Handle format preference change."""
        self.config.set_preferred_output_format(new_format)
        logging.info(f"Preferred output format changed to: {new_format}")
    
    def on_fps_change(self, value: float):
        """Handle FPS slider change."""
        fps = int(value)
        self.config.set_fps_settings(fps)
        self.fps_label.configure(text=f"FPS: {fps}")

    def detect_platform(self, url: str) -> str:
        """
        Detects the social media platform from the URL.
        Returns: 'twitter', 'pinterest', 'instagram', or 'unknown'
        """
        downloader = get_platform_downloader(url, TEMP_VIDEO_FILE)
        if downloader:
            if isinstance(downloader, TwitterDownloader):
                return 'twitter'
            elif isinstance(downloader, PinterestDownloader):
                return 'pinterest'
            elif isinstance(downloader, InstagramDownloader):
                return 'instagram'
        return 'unknown'

    def get_id_from_url(self, url: str) -> str:
        """
        Parses the post/pin ID from the URL to use as a filename.
        """
        downloader = get_platform_downloader(url, TEMP_VIDEO_FILE)
        return downloader.get_id_from_url(url) if downloader else "social_media_post"

    def start_download_thread(self, convert_to_gif: bool = True) -> None:
        """
        Starts a background thread to download media.
        """
        url = self.url_entry.get()
        if not url:
            self.update_status("Please paste a URL first.", "red")
            return

        downloader = get_platform_downloader(url, TEMP_VIDEO_FILE)
        if not downloader:
            self.update_status(
                "Unsupported platform detected.\n\n"
                "Troubleshooting:\n"
                "• Only Twitter/X, Pinterest, and Instagram URLs are supported\n"
                "• Make sure you copied the full URL from your browser\n"
                "• Example URLs:\n"
                "  - Twitter: https://x.com/user/status/123...\n"
                "  - Pinterest: https://pinterest.com/pin/123...\n"
                "  - Instagram: https://instagram.com/p/123... or /reel/123...",
                "red"
            )
            return

        # Disable buttons
        self.download_gif_button.configure(state="disabled")
        self.download_video_button.configure(state="disabled")

        self.progress_bar.set(0)
        self.update_status("Fetching video info...", "white")

        download_thread = threading.Thread(
            target=self.download_media,
            args=(url, downloader, convert_to_gif),
            daemon=True
        )
        download_thread.start()

    def download_media(self, url: str, downloader, convert_to_gif: bool) -> None:
        """
        (Background Thread)
        Downloads media using the appropriate platform downloader.
        """
        try:
            # Update progress
            self.after(0, lambda: self.progress_bar.set(0.2))
            self.update_status("Getting video info...", "white")

            # Get video info and default filename
            video_fps, default_name = downloader.get_video_info(url)

            # Update progress
            self.after(0, lambda: self.progress_bar.set(0.4))

            # Determine output file extension and prompt user
            if convert_to_gif:
                file_types = [("GIF files", "*.gif")]
                default_ext = ".gif"
                fps_to_use = self.config.get_fps_settings()
                status_msg = f"Downloading and converting to GIF at {fps_to_use} FPS..."
            else:
                file_types = [("MP4 files", "*.mp4")]
                default_ext = ".mp4"
                status_msg = "Downloading video..."

            self.update_status(status_msg, "white")

            # Get default save location from config
            default_save_location = self.config.get_default_save_location()
            initial_dir = default_save_location if default_save_location and os.path.exists(default_save_location) else None

            # Prompt for save location
            save_kwargs = {
                "defaultextension": default_ext,
                "filetypes": file_types,
                "title": f"Save as {default_ext.upper()}",
                "initialfile": f"{default_name}{default_ext}"
            }
            if initial_dir:
                save_kwargs["initialdir"] = initial_dir

            output_file = filedialog.asksaveasfilename(**save_kwargs)

            if not output_file:
                self.update_status("Download cancelled.", "gray")
                self.after(0, self.reset_buttons)
                return

            # Update progress
            self.after(0, lambda: self.progress_bar.set(0.6))

            # Download the media
            if convert_to_gif:
                fps_to_use = self.config.get_fps_settings()
                success = downloader.download_media(url, output_file, fps=fps_to_use)
            else:
                # For video downloads, download directly to the chosen output file
                success = downloader.download_media(url, output_file, skip_conversion=True)

            if success:
                # Update progress
                self.after(0, lambda: self.progress_bar.set(1.0))

                if convert_to_gif:
                    self.update_status(f"Success! GIF saved as {os.path.basename(output_file)}", "green")
                else:
                    self.update_status(f"Success! Video saved as {os.path.basename(output_file)}", "green")
            else:
                self.update_status(
                    "Download failed for an unknown reason.\n\n"
                    "Troubleshooting:\n"
                    "• Check the log file for more details\n"
                    "• Try restarting the application\n"
                    "• Verify the URL is correct",
                    "red"
                )

        except NetworkError as e:
            self.update_status(e.get_user_message(), "red")
            logging.error(f"Network error: {e}")
        except DownloadError as e:
            self.update_status(e.get_user_message(), "red")
            logging.error(f"Download error: {e}")
        except Exception as e:
            self.update_status(
                f"An unexpected error occurred.\n\n"
                f"Troubleshooting:\n"
                f"• Check your internet connection\n"
                f"• Try restarting the application\n"
                f"• Make sure you have enough disk space\n"
                f"• Error: {str(e)[:100]}",
                "red"
            )
            logging.error(f"Unexpected exception in download_media: {e}", exc_info=True)
        finally:
            # Cleanup
            downloader.cleanup()
            self.after(0, self.reset_buttons)


    def update_status(self, message: str, color: str) -> None:
        """Safely updates the status label from any thread."""
        def do_update():
            self.status_label.configure(text=message, text_color=color)
        self.after(0, do_update)

    def reset_buttons(self) -> None:
        """Safely re-enables the download buttons."""
        self.download_gif_button.configure(state="normal")
        self.download_video_button.configure(state="normal")
        self.progress_bar.set(0)


def main():
    """Create and run the application."""
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
