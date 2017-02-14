#!/bin/bash
# Usage ./doentropy.sh 100 (x)
cnt=$1
exp=$2
filename="seed_queries.txt"
while read -r line
do
    q=$line
    echo "Current Seed: $q"
    if [ "$exp" == "x" ]; then
      python query_clarity_score.py -q "$q" -c $cnt -x >> seed_entropy.csv
    else
      python query_clarity_score.py -q "$q" -c $cnt >> seed_entropy.csv
    fi
done < "$filename"
