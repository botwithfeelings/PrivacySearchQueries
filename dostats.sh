#!/bin/bash
# Usage ./dostats.sh ./gtrends/without_seed_cmp/ 2013-06-01 ./stats/
tdir=$1
split=$2
rdir=$3
filename="seed_queries.txt"
while read -r line
do
    seed=$line
    echo "Current Seed: $seed"
    python google_trends_analysis.py -s "$seed" -d $tdir -i $split -r $rdir
done < "$filename"
