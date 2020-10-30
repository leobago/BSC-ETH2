#! /bin/python

import os
import sys
import time
import psutil

pid = int(sys.argv[1])
print("Pid: "+str(pid))
folderStorage= str(sys.argv[2])
print("Monitoring storage of: " + str(folderStorage))

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




print("The size analyzed through the script is: ", get_size(), 'bytes')


#header_data = ['MEM [MB]', 'CPU[%]', 'NETOUT[MB]', 'NETIN[MB]', 'DiskUsage']
print("MEM [MB], CPU[%], NETOUT[MB], NETIN[MB], DiskUsage[MB]")
#print("{: >20} {: >20} {: >20} {: >20} {: >20}".format(*header_data))
while(1):
    try:
        get_size()
        diskUsageMB=int(get_size()) /int(1000000)
        process = psutil.Process(pid)
        cpuUsage= psutil.cpu_percent(interval=1)
        networkUsage = psutil.net_io_counters(pernic=True)
        #print("process memory (MB):",process.memory_info().rss/(1024*1024))  # in megabytes
        #print("CPU usage (%): ",cpuUsage)
        sent_mb = networkUsage['eth0'][0] / 1000000
        received_mb = networkUsage['eth0'][1] / 1000000
        #print("MB sent:" , bytesSent_mb)
        #print("MB received:" , bytesReceived_mb)
        
       #diskUsage=psutil.disk_usage(folderStorage)
        #filteredDiskUsage= diskUsage[1]
        #filteredDiskUsageMB = filteredDiskUsage / 1000000

        
        
        #SHOW TABLE
        table_data = [process.memory_info().rss/(1024*1024), cpuUsage, sent_mb, received_mb, diskUsageMB] 
        print(process.memory_info().rss/(1024*1024),",", cpuUsage,",", sent_mb,",", received_mb,",", diskUsageMB)
        time.sleep(1)
    except:
        print("Something went wrong")
        break
print("Process with PID " + str(pid) + " is dead.")
