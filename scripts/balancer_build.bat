docker stop ocr-balancer-service
docker container rm ocr-balancer-service
docker image rm ocr-balancer
docker build -t ocr-balancer  -f Dockerfile_ocr_balancer .