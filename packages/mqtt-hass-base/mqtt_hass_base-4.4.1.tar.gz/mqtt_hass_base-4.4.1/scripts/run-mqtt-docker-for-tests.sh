#!/bin/bash

docker run --rm -it \
	-p 1883:1883 \
	eclipse-mosquitto:2.0.11 sh -c "cp mosquitto-no-auth.conf /mosquitto/config/mosquitto.conf && cat /mosquitto/config/mosquitto.conf && /docker-entrypoint.sh mosquitto -c /mosquitto/config/mosquitto.conf"
