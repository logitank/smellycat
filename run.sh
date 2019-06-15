#!/usr/bin/env bash

image_name=smellycat

# Build a fresh smellycat container
docker build -t $image_name .
# Make sure all old smellycats are killed
docker kill $(docker ps -q --filter="ancestor=$image_name")
# Start a new smellycat
docker run --restart=always -t $image_name
