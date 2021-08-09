#!/bin/bash
cd ./frontend/arbol-curso
./build.sh | grep -v "Found another file with the destination path"
cd -
