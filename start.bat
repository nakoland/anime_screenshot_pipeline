@echo off

call .\venv\Scripts\activate

python automatic_pipeline.py ^
    --anime_name "Urotsukidoji_ep1.avi" ^
    --src_dir "F:\f\ani\aaa\ona\test" ^
    --dst_dir "O:\Ai\training\source\#capture" ^
    --crop_with_head ^
    --start_stage 1 ^
    --end_stage 4 ^
    --config_file configs/pipelines/base.toml

pause