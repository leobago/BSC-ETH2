# Report of the Port Collision Issue running Gossipsub-Hardening on Testground
 On an attempt of reproducing the tests executed on the report "Gossipsub-v1.1 Evaluation Report" done by Protocol Labs, the code compiled on the GitHub repository [gossipsub-hardening](https://github.com/libp2p/gossipsub-hardening) failed at setting up the necessary docker containers.

 ## The Testground Crash
 The code offered on the [gossipsub-hardening](https://github.com/libp2p/gossipsub-hardening) repository is the test plan used for testing the GossipSub protocol on the [Testground](https://github.com/testground/testground) platform. 

 For setting up the Testground, the official guide provided on the [Testground repository](https://github.com/testground/testground#getting-started) was followed. 

 For running the gossipsub-hardening test plan on the Testground platform, the guide provided on the [gossipsub-hardening](https://github.com/libp2p/gossipsub-hardening/#testground) repository was followed. 

 Local versions of the commands:
 ```
 Gossipsub-hardening Commit: 05e0e18
 Processor Architecture: x86_64
 go version: go1.14.4 linux/amd64
 docker version: 19.03.11
 testground version: 0.5.3
 ```

 After setting up all the simulation parameters on the jupyter notebook `Runner.ipynb` and while the Testground daemon was running on a terminal, the test was started. At one point of the test setup, the process failed reporting:

 ```
Aug 11 09:55:56.169607 INFO created container {"req_id": "aa3ff200", "container_name": "testground-sidecar", "id": "1441f98d0535a06a84176ea9879903e96cd8542663c58329833613e275d5e762"}
Aug 11 09:55:56.169664 INFO starting container {"req_id": "aa3ff200", "container_name": "testground-sidecar", "id": "1441f98d0535a06a84176ea9879903e96cd8542663c58329833613e275d5e762"}
Aug 11 09:55:56.649180 INFO started container {"req_id": "aa3ff200", "container_name": "testground-sidecar", "id": "1441f98d0535a06a84176ea9879903e96cd8542663c58329833613e275d5e762"}
Aug 11 09:55:56.649899 WARN engine run error: healthcheck fixes failed; aborting:
Checks:

local-outputs-dir: ok; directory exists.
control-network: ok; network exists.
local-grafana: failed; container not found.
local-redis: failed; container not found.
local-influxdb: failed; container not found.
sidecar-container: failed; container not found.
Fixes:
local-outputs-dir: unnecessary;
control-network: unnecessary;
local-grafana: failed; failed to start container.
local-redis: ok; container started
local-influxdb: ok; container started
sidecar-container: ok; container started
{"req_id": "aa3ff200"}
Error:

engine run error: healthcheck fixes failed; aborting:
Checks:

local-outputs-dir: ok; directory exists.
control-network: ok; network exists.
local-grafana: failed; container not found.
local-redis: failed; container not found.
local-influxdb: failed; container not found.
sidecar-container: failed; container not found.
Fixes:
local-outputs-dir: unnecessary;
control-network: unnecessary;
local-grafana: failed; failed to start container.
local-redis: ok; container started
local-influxdb: ok; container started
sidecar-container: ok; container started
 ```

Since no information or issues that could help to solve the problem were found, a [GitHub Issue](https://github.com/libp2p/gossipsub-hardening/issues/14) was opened (Aug 11 2020)

After exchanging some messages with the developers of Testground, we could find the problem causing the error. The grafana docker container was failing at the start even though the image was there.
Logs of the error that Testground was reporting:
```
Aug 18 13:55:44.593724 WARN engine run error: healthcheck fixes failed;
aborting:
Checks:

local-outputs-dir: ok; directory exists.
control-network: ok; network exists.
local-grafana: failed; container not found.
local-redis: ok; container state: running
local-influxdb: ok; container state: running
sidecar-container: ok; container state: running
Fixes:
local-outputs-dir: unnecessary;
control-network: unnecessary;
local-grafana: failed; failed to start container.
local-redis: unnecessary;
local-influxdb: unnecessary;
sidecar-container: unnecessary;
{"req_id": "bc421857"}
```
Results of making `docker image ls`
```
REPOSITORY TAG IMAGE ID CREATED SIZE

16a94e12f2c9 latest 07597608d153 26 minutes ago 31.3MB
c46a249bb94b latest 07597608d153 26 minutes ago 31.3MB
d3e6461cbb3a latest 07597608d153 26 minutes ago 31.3MB
tg-plan-pubsub 07597608d153 07597608d153 26 minutes ago 31.3MB
sigp/lighthouse latest 9d837981a9fa 28 hours ago 157MB
bitnami/grafana latest 694a7c1715a4 2 days ago 465MB <<-- Image of Grafana 
12b7ad10ed5a latest d1e2767dfc7c 7 days ago 31.3MB
2b8f93a7a770 latest d1e2767dfc7c 7 days ago 31.3MB
c75eca9fab6b latest d1e2767dfc7c 7 days ago 31.3MB
tg-plan-pubsub d1e2767dfc7c d1e2767dfc7c 7 days ago 31.3MB
85427a09bcad latest 84f5a24276c8 7 days ago 31.3MB
tg-plan-pubsub 84f5a24276c8 84f5a24276c8 7 days ago 31.3MB
8f6f0386a1c6 latest 3bc2e263619c 8 days ago 31.3MB
c37ef8929229 latest 3bc2e263619c 8 days ago 31.3MB
tg-plan-pubsub 3bc2e263619c 3bc2e263619c 8 days ago 31.3MB
3e11f1cb54a9 latest 3bc2e263619c 8 days ago 31.3MB
78f01cd821f5 latest 3bc2e263619c 8 days ago 31.3MB
811dae235b1c latest 3bc2e263619c 8 days ago 31.3MB
26d0decd7b1a latest 7ffb3b6faeee 11 days ago 31.3MB
d92c090b869e latest 7ffb3b6faeee 11 days ago 31.3MB
e8bcc2da0bf5 latest 7ffb3b6faeee 11 days ago 31.3MB
tg-plan-pubsub 7ffb3b6faeee 7ffb3b6faeee 11 days ago 31.3MB
iptestground/sidecar edge 86d7a216e5bd 11 days ago 198MB
iptestground/testground edge 62a89121c0bf 11 days ago 870MB
influxdb 1.8 376a04c5c7e5 12 days ago 304MB
golang 1.14-buster 132b2ef94b55 13 days ago 810MB
redis latest 1319b1eaa0b7 13 days ago 104MB
debian buster ee11c54e6bb7 13 days ago 114MB
golang 1.14.4-buster 00d970a31ef2 7 weeks ago 810MB
ubuntu latest 74435f89ab78 2 months ago 73.9MB
busybox 1.31.1-glibc 7a2331af2292 2 months ago 5.2MB
goproxy/goproxy latest e5878c746779 3 months ago 532MB
hello-world latest bf756fb1ae65 7 months ago 13.3kB

```
As @nonsense pointed in one of the replies on the GitHub Issue, the problem could be caused by a port collision on the port 3000. After checking the if the port was used with `sudo lsof -i -P -n | grep 3000` , we could confirm that the issue was that port collision. 

The processes that were using the 3000 port: 
```
nghttpx     979            root    5u  IPv4  31551      0t0  TCP 127.0.0.1:3000 (LISTEN)
nghttpx    1025            root    5u  IPv4  31551      0t0  TCP 127.0.0.1:3000 (LISTEN)
```

After reporting the details to the Testground team, they are working on a fix for the issue. 

## Temporary Fix to the problem
After finding the issue and while the Testground team works on a fix, the only fix found so far has been freeing that port by uninstalling the nghttpx program. (Sep 17 2020) 
Right now, no way of running nghttpx and the gossipsub-hardening test at the same time has been found.    


