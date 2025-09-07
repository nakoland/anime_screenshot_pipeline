@echo off

call .\venv\Scripts\activate

python automatic_pipeline.py ^
    --anime_name "[M-UNC] Choujin Densetsu Urotsukidouji" ^
    --src_dir "D:\temp\uro" ^
    --dst_dir "O:\Ai\training\source\#capture" ^
    --crop_with_head ^
    --start_stage 1 ^
    --end_stage 1 ^
    --extract_all_frames ^
    --config_file configs/pipelines/base.toml

pause