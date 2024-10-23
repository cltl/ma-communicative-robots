#!/bin/bash

# ASR implementation writes this files for some unknown reason
rm -f *.wav

rm -f storage/event_log/*.json

rm -f storage/audio/*.wav
rm -f storage/audio/*.json

rm -f storage/image/*.png
rm -f storage/image/*.json
rm -f storage/image/*.pkl

rm -rf storage/brain/**/*
rmdir storage/brain/*
rm -rf storage/rdf/**/*
rmdir storage/rdf/*

rm -rf storage/emissor/**/*
rmdir storage/emissor/*

rm -rf storage/vector_id/*