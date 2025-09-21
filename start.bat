@echo off

call .\venv\Scripts\activate

python automatic_pipeline.py ^
    --src_dir "D:\AI\training\source\#video" ^
    --dst_dir "D:\AI\training\source\#capture" ^
    --crop_with_head ^
    --start_stage 1 ^
    --end_stage 1 ^
    --extract_all_frames ^
    --no_remove_similar^
    --config_file configs/pipelines/base.toml

pause