#!/bin/bash
# Usage ./pulltrends.sh 200 (cmp|scale)
cnt=$1
cs=$2
if [ "$cs" == "cmp" ]; then
  filename="seed_queries.txt"
else
  filename="seed_queries_amt.txt"
fi

while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    SEED_FILE="./googledata/${SEED// /_}_approved.csv"
    if [ "$cs" == "scale" ]; then
      python google_trends.py -s "$SEED" -k $cnt -scale >> log.txt
    elif [ "$cs" == "cmp" ]; then
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt -cmp >> log.txt
    else
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt >> log.txt
    fi
done < "$filename"
