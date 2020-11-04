echo "Geting metrics from Logs"
python3 lightLogAnalyzer.py logFolder/light-bn-logs.txt csvs/light-logs.csv
python3 tekuLogAnalyzer.py logFolder/teku-bn-logs.txt csvs/teku-logs.csv
echo "Ploting Logs"
python3 clientsPlot.py csvs/light-logs.csv csvs/teku-logs.csv
