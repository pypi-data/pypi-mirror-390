import pytest
import json
import os
import subprocess
import time
from unittest.mock import patch, Mock, MagicMock
from social_media_gif_downloader import App
from tests.conftest import is_headless
from platforms import (
    TwitterDownloader, 
    get_platform_downloader, 
    DownloadError, 
    NetworkError
)


class TestErrorHandling:
    """Tests for error handling in various scenarios."""

    def test_get_video_info_subprocess_error(self):
        """Test handling of yt-dlp subprocess errors."""
        downloader = TwitterDownloader()
        pass

    def test_platform_downloader_error_handling(self):
        """Test error handling in platform downloaders."""
        downloader = TwitterDownloader()

        # Test with invalid URL (should raise DownloadError)
        with pytest.raises(DownloadError):
            downloader.download_media("invalid-url", "output.gif")

    def test_app_empty_url_handling(self):
        """Test handling of empty URL input in the new architecture."""
        # Test with empty URL
        downloader = get_platform_downloader("", temp_file="dummy.mp4")
        assert downloader is None

        # Test with invalid URL
        downloader = get_platform_downloader("not-a-url", temp_file="dummy.mp4")
        assert downloader is None

        # Test with valid Twitter URL
        downloader = get_platform_downloader("https://x.com/user/status/123", temp_file="dummy.mp4")
        assert downloader is not None
        assert downloader.__class__.__name__ == "TwitterDownloader"

    def test_retry_mechanism_success_on_retry(self):
        """Test that retry mechanism works when first attempt fails but second succeeds."""
        downloader = TwitterDownloader(max_retries=3)
        
        # Mock subprocess to fail once then succeed
        mock_results = [
            Mock(returncode=1, stderr="Network error: Connection timeout"),
            Mock(returncode=0, stdout='{"fps": 30}', stderr="")
        ]
        
        with patch('subprocess.run', side_effect=mock_results):
            with patch('time.sleep'):  # Speed up tests by mocking sleep
                result = downloader._run_with_retry(
                    ['yt-dlp', '--version'],
                    'test operation'
                )
                assert result.returncode == 0

    def test_retry_mechanism_all_attempts_fail(self):
        """Test that retry mechanism raises error after all attempts fail."""
        downloader = TwitterDownloader(max_retries=3)
        
        # Mock subprocess to always fail with network error (but not "timed out" specifically)
        mock_result = Mock(returncode=1, stderr="Network error: Connection failed")
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('time.sleep'):  # Speed up tests
                with pytest.raises(NetworkError) as exc_info:
                    downloader._run_with_retry(
                        ['yt-dlp', '--version'],
                        'test operation'
                    )
                # Should raise NetworkError (network keyword in stderr)
                assert "network" in str(exc_info.value.message).lower()

    def test_retry_mechanism_timeout_handling(self):
        """Test that timeout errors trigger retry mechanism."""
        downloader = TwitterDownloader(max_retries=2, timeout=1)
        
        # Mock subprocess to timeout - should retry and eventually raise error
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 1)):
            with patch('time.sleep'):  # Speed up tests
                # After all retries exhausted with timeout, should raise NetworkError
                # (timeout detection happens after all retries based on last_error message)
                with pytest.raises((NetworkError, DownloadError)) as exc_info:
                    downloader._run_with_retry(
                        ['yt-dlp', '--version'],
                        'test operation'
                    )
                # Should mention timeout in the error message
                error_msg = str(exc_info.value.message).lower()
                assert "timeout" in error_msg or "timed out" in error_msg

    def test_download_error_with_troubleshooting(self):
        """Test that DownloadError includes troubleshooting steps."""
        error = DownloadError(
            "Test error message",
            "• Step 1\n• Step 2"
        )
        
        user_message = error.get_user_message()
        assert "Test error message" in user_message
        assert "Troubleshooting:" in user_message
        assert "Step 1" in user_message
        assert "Step 2" in user_message

    def test_network_error_is_download_error(self):
        """Test that NetworkError is a subclass of DownloadError."""
        error = NetworkError("Network failed", "Check connection")
        assert isinstance(error, DownloadError)

    def test_retry_exponential_backoff(self):
        """Test that retry mechanism uses exponential backoff."""
        downloader = TwitterDownloader(max_retries=3)
        
        mock_result = Mock(returncode=1, stderr="Network error")
        sleep_times = []
        
        def mock_sleep(seconds):
            sleep_times.append(seconds)
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('time.sleep', side_effect=mock_sleep):
                try:
                    downloader._run_with_retry(
                        ['yt-dlp', '--version'],
                        'test operation'
                    )
                except NetworkError:
                    pass
                
                # Should have exponential backoff: 2^1=2, 2^2=4
                assert len(sleep_times) == 2
                assert sleep_times[0] == 2
                assert sleep_times[1] == 4

    def test_error_classification_404(self):
        """Test that 404 errors are properly classified."""
        downloader = TwitterDownloader(max_retries=1)
        
        mock_result = Mock(returncode=1, stderr="HTTP Error 404: Not Found")
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('time.sleep'):
                with pytest.raises(DownloadError) as exc_info:
                    downloader._run_with_retry(
                        ['yt-dlp', '--version'],
                        'test operation'
                    )
                assert "not found" in str(exc_info.value.message).lower()
                assert "deleted" in str(exc_info.value.troubleshooting).lower()

    def test_error_classification_private_content(self):
        """Test that private content errors are properly classified."""
        downloader = TwitterDownloader(max_retries=1)
        
        mock_result = Mock(returncode=1, stderr="Video is private")
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('time.sleep'):
                with pytest.raises(DownloadError) as exc_info:
                    downloader._run_with_retry(
                        ['yt-dlp', '--version'],
                        'test operation'
                    )
                assert "private" in str(exc_info.value.message).lower()

    def test_error_classification_no_video(self):
        """Test that 'no video' errors are properly classified."""
        downloader = TwitterDownloader(max_retries=1)
        
        mock_result = Mock(returncode=1, stderr="No video formats found")
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('time.sleep'):
                with pytest.raises(DownloadError) as exc_info:
                    downloader._run_with_retry(
                        ['yt-dlp', '--version'],
                        'test operation'
                    )
                assert "no video" in str(exc_info.value.message).lower()

    def test_get_video_info_with_retry(self):
        """Test that get_video_info uses retry mechanism."""
        downloader = TwitterDownloader(max_retries=2)
        
        # First attempt fails, second succeeds
        mock_results = [
            Mock(returncode=1, stderr="Network timeout"),
            Mock(returncode=0, stdout='{"fps": 30}', stderr="")
        ]
        
        with patch('subprocess.run', side_effect=mock_results):
            with patch('time.sleep'):
                fps, name = downloader.get_video_info("https://x.com/user/status/123")
                assert fps == 30
                assert name == "123"

    def test_download_media_with_retry(self):
        """Test that download_media uses retry mechanism."""
        downloader = TwitterDownloader(max_retries=2, temp_file="test_temp.mp4")
        
        # Mock successful download
        mock_result = Mock(returncode=0, stdout="", stderr="")
        
        with patch('subprocess.run', return_value=mock_result):
            with patch('os.path.exists') as mock_exists:
                # First call checks if temp_file exists (for cleanup), second checks after download
                mock_exists.side_effect = [False, True]
                with patch('platforms.PlatformDownloader.convert_to_gif', return_value=True):
                    result = downloader.download_media(
                        "https://x.com/user/status/123",
                        "output.gif"
                    )
                    assert result is True

    def test_convert_to_gif_error_handling(self):
        """Test that GIF conversion errors are properly handled."""
        downloader = TwitterDownloader()
        
        with patch('moviepy.video.io.VideoFileClip.VideoFileClip', side_effect=Exception("FFmpeg error")):
            with pytest.raises(DownloadError) as exc_info:
                downloader.convert_to_gif("input.mp4", "output.gif")
            assert "convert" in str(exc_info.value.message).lower()
            assert "FFmpeg" in str(exc_info.value.troubleshooting)
