#!/usr/bin/env bash

PD=resources/pipeline
CONF=resources/conf

python staging/pipeline/main.py \
       --seed_file ${PD}/seeds/twitter_#sarcasm_#sarcastic_250.json \
       --users_raw_dir ${PD}/user_data/raw \
       --users_labelled_dir ${PD}/user_data/labelled \
       --stats_dir ${PD}/stats \
       --kfold_dir ${PD}/kfold \
       --k 10 \
       --split_spec 0.6 0.2 0.2 \
       --twitter_conf_file ${CONF}/twitter_conn_spec.json

