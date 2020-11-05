echo "Ploting the metrics"
python3 plotMetrics.py logs ../../client-metrics/light-metrics.txt  ../../client-metrics/teku-metrics.txt ../../client-metrics/nimbus-metrics.txt ../../client-metrics/prysm-metrics.txt
echo "Finish"
