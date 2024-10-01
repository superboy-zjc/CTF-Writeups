#!/bin/bash
docker rm -f secret_door
docker build --tag=secret_door .
docker run -p 1337:1337 -p 2338:3306 --rm --name=secret_door secret_door -d