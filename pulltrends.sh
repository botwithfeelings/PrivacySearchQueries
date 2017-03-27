#!/bin/bash
# Usage ./pulltrends.sh 200 (cmp|scale) amt
cnt=$1
cs=$2
amt=$3
if [ "$amt" == "amt" ]; then
  filename="seed_queries_amt.txt"
else
  filename="seed_queries.txt"
fi

while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    if [ "$amt" == "amt" ]; then
      SEED_FILE="./surveyQueries/grouped_by_seed/${SEED// /_}_approved.csv"
    else
      SEED_FILE="./googledata/${SEED// /_}_approved.csv"
    fi
    if [ "$cs" == "scale" ]; then
      python google_trends.py -s "$SEED" -k $cnt -scale >> log.txt
    elif [ "$cs" == "cmp" ]; then
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt -cmp >> log.txt
    else
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt >> log.txt
    fi
done < "$filename"
