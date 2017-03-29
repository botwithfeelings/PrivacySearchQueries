#!/bin/bash
# Usage ./pulltrends.sh 150 (cmp|scale|nocmp) (noamt|amt)
cnt=$1
cs=$2
amt=$3
if [ "$amt" == "amt" ]; then
  filename="seed_queries_amt.txt"
elif [ "$amt" == "noamt" ]; then
  filename="seed_queries.txt"
fi

while read -r line
do
    SEED=$line
    echo "Current Seed: $SEED"
    if [ "$amt" == "amt" ]; then
      SEED_FILE="./surveyQueries/grouped_by_seed/${SEED// /_}_approved.csv"
    elif [ "$amt" == "noamt" ]; then
      SEED_FILE="./googledata/${SEED// /_}_approved.csv"
    fi

    if [ "$cs" == "scale" ]; then
      if [ "$amt" == "amt" ]; then
        python google_trends.py -s "$SEED" -k $cnt -scale -amt >> log.txt
      elif [ "$amt" == "noamt" ]; then
        python google_trends.py -s "$SEED" -k $cnt -scale >> log.txt
      fi
    elif [ "$cs" == "cmp" ]; then
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt -cmp >> log.txt
    elif [ "$cs" == "nocmp" ]; then
      python google_trends.py -f "$SEED_FILE" -s "$SEED" -k $cnt >> log.txt
    fi
done < "$filename"
