#!/bin/bash
cnt=$1
filename="seed_queries.txt"
while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    SEED_FILE="./gtrends/${l// /_}_approved.csv"
    python google_trends.py -f "$SEED_FILE" -s "SEED" -k $cnt >> log.txt
done < "$filename"
