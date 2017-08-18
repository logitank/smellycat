#!/usr/bin/env bash

image_name=smellycat

# Build a fresh smellycat container
docker rmi -f $image_name
docker build -t $image_name .

# Make sure all old smellycats are killed
for box in $(docker ps -q --filter="ancestor=$image_name"); do
  docker kill $box;
done

# Start a new smellycat
docker run --restart=always -t $image_name
