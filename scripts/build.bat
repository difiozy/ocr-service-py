call scripts/stop.bat
docker image rm first_stage_build_ocr-parse_service
docker image rm final_stage_build_ocr-parse_service
set _pwd=%cd%
set _res=%_pwd:~-7%
if %_pwd:~-7% == scripts cd ..
docker build -t first_stage_build_ocr-parse_service -f Dockerfile .
docker build -t final_stage_build_ocr-parse_service -f Dockerfile_sec_stage .