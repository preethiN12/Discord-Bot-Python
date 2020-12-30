#!/bin/sh
#Navigates to the folder the script is in
cd "${0%/*}"
echo "Building..."
cd ..
echo "Removing Old Version..."
docker-compose kill > /dev/null 2&>1 
docker-compose rm -f > /dev/null 2&>1 
echo "Starting New Version..."
docker-compose up -d --no-deps --build --no-color |& sed 's/\x1b\[.*m//g'
echo "New Version Started."
