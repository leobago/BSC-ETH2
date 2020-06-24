#!/bin/sh
for i in {1..100} 
do 
	echo $i; 
	./orchestra -c orchestra.config.json --log log-$i.txt
	./analysis log-$i.txt -o=analysis-$i.json
	rm log-$i.txt
done
