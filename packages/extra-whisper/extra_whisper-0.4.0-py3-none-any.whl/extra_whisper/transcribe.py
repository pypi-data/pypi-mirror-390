import logging
import os
import shutil
from typing import Optional

import validators
from faster_whisper import WhisperModel, format_timestamp
from extra_whisper.downloader import Downloader

def extra_transcribe(
        files: list[str],
        output_dir: str,
        model: str = "large-v2",
        language: Optional[str] = None,
        task: str = "transcribe"
):
    """
    Transcripts the list of media files (audio/video), using faster-whisper.

    This function supports both local files and remote URLs (e.g., YouTube links). It handles:
    - Downloading remote media using yt-dlp
    - Performing transcription
    - Cleaning up intermediate files and keeping only the final output

    Parameters:
        files (list[str]): List of file paths or URLs pointing to audio/video files.
        output_dir (str): Path to directory where final results will be saved.
        model (str): Model to be used
        language (Optional[str]): Speech language code (e.g., "ar", "en").
                                   If None, language will be auto-detected.
        task (str): Either "transcribe" or "translate" (default: "transcribe")

    Example:
        extra_transcribe(
            files=["https://www.youtube.com/watch?v=123", "local_song.mp3"],
            media_type="audio",
            quality="medium",
            output_dir="output"
        )
    """
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)

    temp_output_dir = os.path.join(abs_output_dir, 'tmp')

    processing_files_path = []
    failed_urls = []

    # --- Preparing files for processing ---
    print("Preparing files...")

    if not files:
        raise Exception("Please provide files for processing")

    downloader = Downloader(
        output_dir=temp_output_dir,
    )
    for index, url in enumerate(files):
        if not isinstance(url, str):
            logging.warning(f"Item at index {index} is not a string, skipping.")
            continue

        is_url = validators.url(url)

        if is_url:
            downloaded_file_name = downloader.download(url=url)

            if downloaded_file_name:
                downloaded_file_path = os.path.join(temp_output_dir, downloaded_file_name)
                processing_files_path.append(downloaded_file_path)
            else:
                failed_urls.append(url)
        else:
            processing_files_path.append(os.path.abspath(url))

    if not processing_files_path:
        raise ValueError(
            f"Processing failed. No valid files or URLs were found or successfully downloaded from the {len(files)} provided inputs.")

    if failed_urls:
        logging.warning(f"Failed to download {len(failed_urls)} URLs: {failed_urls}")

    # Now you can safely continue, knowing processing_files_path is not empty
    print(f"Successfully processed {len(processing_files_path)} files.")

    # --- model inference ---
    whisper_model = WhisperModel(
            model,
            device="cuda",
            compute_type="float16",
    )

    # Process each file with batching
    for file_path in processing_files_path:
        print(f"Transcribing {file_path}...")

        segments, info = whisper_model.transcribe(
            file_path,
            beam_size=5,
            language=language,
            log_progress=True,
            task=task,
        )

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(abs_output_dir, f"{base_name}.srt")

        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, segment in enumerate(segments, start=1):
                f.write(f"{idx}\n")

                start_time = format_timestamp(segment.start, always_include_hours=True, decimal_marker=",")
                end_time = format_timestamp(segment.end, always_include_hours=True, decimal_marker=",")
                f.write(f"{start_time} --> {end_time}\n")

                f.write(f"{segment.text.strip()}\n")
                f.write("\n")

        print(f"Saved transcription to {output_file}")

    # --- Cleanup ---
    if os.path.exists(temp_output_dir):
        shutil.rmtree(temp_output_dir)
