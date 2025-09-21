import os
import re
import logging
import subprocess
from typing import Optional

from .basics import parse_anime_info
from .remove_duplicates import DuplicateRemover


def check_cuda_availability(logger=None):
    if logger is None:
        logger = logging.getLogger()
    try:
        output = subprocess.check_output(
            ["ffmpeg", "-hwaccels"], universal_newlines=True
        )
        return "cuda" in output
    except Exception as e:
        logging.warning(f"Error checking CUDA availability: {e}")
        return False


def get_ffmpeg_command(file, file_pattern, extract_key, extract_all_frames=False, fps: Optional[int] = None, logger=None):
    if logger is None:
        logger = logging.getLogger()
    cuda_available = check_cuda_availability(logger)
    command = ["ffmpeg"]

    if cuda_available:
        command.extend(["-hwaccel", "cuda"])
    else:
        logger.warning("CUDA is not available. Proceeding without CUDA.")

    command.extend(["-i", file])

    # ### CHANGED: 필터 체인을 동적으로 구성 ###
    filter_chain = []

    # .vob 파일인 경우 yadif 필터를 가장 먼저 추가
    if file.lower().endswith(".vob"):
        filter_chain.append("yadif")
        logger.info(f"VOB file detected. Applying 'yadif' deinterlacing filter for: {file}")

    # 기존 프레임 추출 로직을 필터 체인에 추가
    if extract_key:
        filter_chain.append("select='eq(pict_type,I)'")
        command.extend(["-vsync", "vfr"])
    elif extract_all_frames:
        if fps is not None:
            filter_chain.append(f"fps={fps}")
    else:
        # 기본값: mpdecimate 필터 사용
        filter_chain.append("mpdecimate=hi=64*200:lo=64*50:frac=0.33,setpts=N/FRAME_RATE/TB")

    # 구성된 필터 체인이 있는 경우, ffmpeg 명령어에 추가
    if filter_chain:
        command.extend(["-vf", ",".join(filter_chain)])

    command.extend(["-qscale:v", "1", "-qmin", "1", "-c:a", "copy", file_pattern])

    return command


def extract_and_remove_similar(
    src_dir: str,
    dst_dir: str,
    prefix: Optional[str] = None,
    ep_init: Optional[int] = None,
    extract_key: bool = False,
    extract_all_frames: bool = False,
    fps: Optional[int] = None,
    duplicate_remover: Optional[DuplicateRemover] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    (Docstring은 기존과 동일)
    """
    if logger is None:
        logger = logging.getLogger()
    # ### CHANGED: 지원하는 비디오 확장자에 .vob 추가 ###
    video_extensions = [".mp4", ".mkv", ".avi", ".flv", ".mov", ".wmv", ".vob"]

    files = [
        os.path.join(root, file)
        for root, dirs, files in os.walk(src_dir)
        for file in files
        if os.path.splitext(file)[1].lower() in video_extensions # .lower() 추가하여 대소문자 구분 없이 처리
    ]

    for i, file in enumerate(sorted(files)):
        filename_without_ext = os.path.splitext(os.path.basename(file))[0]

        anime_name, ep_num = parse_anime_info(filename_without_ext)
        anime_name = "_".join(re.split(r"\s+", anime_name))
        prefix_anime = f"{prefix if isinstance(prefix, str) else anime_name}_"
        if isinstance(ep_init, int):
            ep_num = i + ep_init
        elif ep_num is None:
            ep_num = i

        dst_ep_dir = os.path.join(dst_dir, filename_without_ext)
        os.makedirs(dst_ep_dir, exist_ok=True)
        file_pattern = os.path.join(dst_ep_dir, f"{prefix_anime}EP{ep_num}_%d.png")

        ffmpeg_command = get_ffmpeg_command(file, file_pattern, extract_key, extract_all_frames, fps, logger)
        logger.info(f"Executing FFmpeg command: {' '.join(ffmpeg_command)}") # 로그 가독성 향상
        subprocess.run(ffmpeg_command, check=True)

        if duplicate_remover is not None:
            duplicate_remover.remove_similar_from_dir(dst_ep_dir)

    if duplicate_remover is not None:
        duplicate_remover.remove_similar_from_dir(dst_dir, portion="first")
        duplicate_remover.remove_similar_from_dir(dst_dir, portion="last")