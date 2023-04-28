call scripts/stop.bat
docker image rm final_stage_build_ocr-parse_service
docker build -t final_stage_build_ocr-parse_service  -f Dockerfile_sec_stage .