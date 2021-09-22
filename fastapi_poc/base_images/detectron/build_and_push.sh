#!/bin/bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 607182506347.dkr.ecr.us-east-1.amazonaws.com
docker build -t model_server .
docker tag model_server:latest 607182506347.dkr.ecr.us-east-1.amazonaws.com/model_server:detectron_base
docker push 607182506347.dkr.ecr.us-east-1.amazonaws.com/model_server:detectron_base
