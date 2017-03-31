#!/bin/bash
# Usage ./pullrelatedqueries.sh 150 (noamt|amt)
cnt=$1
amt=$2
if [ "$amt" == "amt" ]; then
  filename="seed_queries_amt.txt"
elif [ "$amt" == "noamt" ]; then
  filename="seed_queries_index.txt"
fi

while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    python google_related_queries.py -s "$SEED" -k $cnt >> pull_related_queries_log.txt
done < "$filename"
