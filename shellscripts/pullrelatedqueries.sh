#!/bin/bash
# Usage ./pullrelatedqueries.sh 150 (noamt|amt) (nocomp|comp)
cnt=$1
amt=$2
comp=$3
if [ "$amt" == "amt" ]; then
  filename="seed_queries_amt.txt"
elif [ "$amt" == "noamt" ]; then
  filename="seed_queries_index.txt"
fi

while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    if [ "$comp" == "comp" ]; then
      SEED_FILE="./surveyQueries/grouped_by_seed/${SEED// /_}_approved.csv"
      python google_related_queries.py -s "$SEED" -k $cnt -f $SEED_FILE -comp >> amt_index_recall.csv
    elif [ "$comp" == "nocomp" ]; then
      python google_related_queries.py -s "$SEED" -k $cnt >> pull_related_queries_log.txt
    fi    
done < "$filename"
