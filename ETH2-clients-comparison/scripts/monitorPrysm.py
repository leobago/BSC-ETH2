#! /bin/python

import os
import sys
import time
import psutil
import datetime
from datetime import datetime as dt

print("Welcome to the monitor .py")
pid = int(sys.argv[1])
folderStorage= str(sys.argv[2])
print(pid, folderStorage)

#GET SIZE OF ARGUMENT FOLDER
def get_size(start_path = folderStorage):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

print("TIME [month dd hh:mm:ss:ms], MEM [MB], CPU[%], NETOUT[MB], NETIN[MB], DiskUsage[MB]")

while(1):
    try:
        currentTime = datetime.datetime.now()
        diskUsageMB=int(get_size()) /int(1000000)
        process = psutil.Process(pid)
        cpuUsage= psutil.cpu_percent(interval=1)
        networkUsage = psutil.net_io_counters(pernic=True)
        sent_mb = networkUsage['eth0'][0] / 1000000
        received_mb = networkUsage['eth0'][1] / 1000000
        timestamp = datetime.datetime.now()
        currentTime= timestamp.strftime('%Y-%b-%d %H:%M:%S')
        print(currentTime, ",", process.memory_info().rss/(1024*1024),",", cpuUsage,",", sent_mb,",", received_mb,",", diskUsageMB)
        time.sleep(1)
    except:
        print(currentTime, "Error")
        #break
print("Process with PID " + str(pid) + " is dead.")
