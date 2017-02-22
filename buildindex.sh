#!/bin/bash
# Usage ./buildindex.sh ./gtrends/with_seed_cmp/ ./indextrends/
tdir=$1
rdir=$2
filename="seed_queries.txt"
while read -r line
do
    seed=$line
    python create_index_from_trends.py -s "$seed" -t $tdir -r $rdir
done < "$filename"
