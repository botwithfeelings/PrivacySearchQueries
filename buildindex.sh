#!/bin/bash
# Usage ./buildindex.sh ./gtrends/with_seed_cmp/ ./indextrends/ amt|noamt
tdir=$1
rdir=$2
amt=$3
if [ "$amt" == "amt" ]; then
  filename="seed_queries_amt.txt"
elif [ "$amt" == "noamt" ]; then
  filename="seed_queries.txt"
fi

while read -r line
do
    seed=$line
    python create_index_from_trends.py -s "$seed" -t $tdir -r $rdir
done < "$filename"
