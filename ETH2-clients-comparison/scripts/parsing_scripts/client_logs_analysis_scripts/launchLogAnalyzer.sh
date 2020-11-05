echo "Geting metrics from Logs"
python3 lightLogAnalyzer.py ../../../client-logs/light-bn-logs.txt ../../../data/Lighthouse/light-logs.csv
python3 tekuLogAnalyzer.py ../../../client-logs/teku-bn-logs.txt ../../../data/Teku/teku-logs.csv
python3 nimbusLogAnalyzer.py ../../../client-logs/nimbus-bn-logs.txt ../../../data/Nimbus/nimbus-logs.csv
python3 prysmLogAnalyzer.py ../../../client-logs/prysm-bn-logs.txt ../../../data/Prysm/prysm-logs.csv
echo "Done"
