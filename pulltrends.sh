#!/bin/bash
# Usage ./pulltrends.sh 200 (cmp)
cnt=$1
cmp=$2
filename="seed_queries_refs.txt"
while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    SEED_FILE="./googledata/${SEED// /_}_approved.csv"
    if [ "$cmp" == "cmp" ]; then
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt -cmp >> log.txt
    else
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt >> log.txt
    fi
done < "$filename"
