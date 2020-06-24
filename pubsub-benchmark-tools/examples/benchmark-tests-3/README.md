# Benchmark Tests v3

These tests are the same as v1 and v2, except they were performed on an Amazon AWS c5.24xlarge instance.

This example benchmark test was carried out on 19 Oct. 2019 and 20 Oct. 2019 on an Amazon AWS EC2 c5.24xlarge instance running Red Hat Enterprise Linux. The c5 instance was chosen in order to increase the hardware available to each go-routine running the pubsub host. The c5 instance is equipped with 96 cpu's, 375 ecu's and 192 GB of ram.

The benchmark consisted of roughly two and one half hours of publishing messages of 1kb between fifty nodes. Nodes were started sequentially, and were randomly peered with previously started nodes. Nodes in the subnet were then randomly selected every 100ms and told to publish a message on their pubsub channel.

Only the gossip pubsub algorithm was tested.

These tests were performed both with and without routing, peer discovery and relays.

Compiled versions of `orchestra` and `analysis` were used.

The shell script used in these tests were the same in both tests:

```sh
#!/bin/sh
for i in {1..100} 
do 
	echo $i; 
	./orchestra -c orchestra.config.json --log log-$i.txt
	./analysis log-$i.txt -o=analysis-$i.json
	rm log-$i.txt
done
```

## Usage

### Dependancies

```
$ python3 -m venv ./.venv
$ . ./.venv/bin/activate
$ pip3 install -r requirements.txt
$ jupyter notebook
```

### Data

The data files need to be un-tarred and un-gzipped. Navigate into each data directory and find the `.tar.gz` and run the following command `$ tar -zxvf <filename>.tar.gz -C analyses --strip-components 2`

## Results

### Discovery

The [config](./data/gossip/discovery/orchestra.config.json) file used in this test is:

```
{
  "orchestra": {
    "omitSubnet": false,
    "hostRPCAddressesIfOmitSubnet": [],
    "messageNanoSecondInterval": 100000000,
    "clientTimeoutSeconds": 20,
    "messageLocation": "client.message.json",
    "messageByteSize": 1000,
    "testDurationSeconds": 90,
    "testWarmupSeconds": 10,
    "testCooldownSeconds": 10
  },
  "subnet": {
    "numHosts": 50,
    "pubsubCIDR": "127.0.0.1/8",
    "pubsubPortRange": [3000, 4000],
    "rpcCIDR": "127.0.0.1/8",
    "rpcPortRange": [8080, 9080],
    "peerTopology": "whiteblocks"
  },
  "host": {
    "transports": ["tcp", "ws"],
    "muxers": [["yamux", "/yamux/1.0.0"], ["mplex", "/mplex/6.7.0"]],
    "security": "secio",
    "pubsubAlgorithm": "gossip",
    "omitRelay": false,
    "omitConnectionManager": false,
    "omitNATPortMap": false,
    "omitRPCServer": false,
    "omitDiscoveryService": false,
    "omitRouting": false
  },
  "general": {
    "loggerLocation": ""
  }
}
```

The results of these tests are:

```
Messages published: 89999
Total Nano Times - mean: 4804331.925110279, median: 4206965.0, std: 4581137.130196488
Last Delivery Hop - mean: 4.935543728263648, median: 5.0, std: 0.6992502184365876
Relative Message Redundancy - mean: 0.020408154000000008, median: 0.020408154, std: 6.938893903907228e-18
```

### No-Discovery

The [config](./data/gossip/no-discovery/orchestra.config.json) file used in this test is:

```
{
  "orchestra": {
    "omitSubnet": false,
    "hostRPCAddressesIfOmitSubnet": [],
    "messageNanoSecondInterval": 100000000,
    "clientTimeoutSeconds": 20,
    "messageLocation": "client.message.json",
    "messageByteSize": 1000,
    "testDurationSeconds": 90,
    "testWarmupSeconds": 10,
    "testCooldownSeconds": 10
  },
  "subnet": {
    "numHosts": 50,
    "pubsubCIDR": "127.0.0.1/8",
    "pubsubPortRange": [3000, 4000],
    "rpcCIDR": "127.0.0.1/8",
    "rpcPortRange": [8080, 9080],
    "peerTopology": "whiteblocks"
  },
  "host": {
    "transports": ["tcp", "ws"],
    "muxers": [["yamux", "/yamux/1.0.0"], ["mplex", "/mplex/6.7.0"]],
    "security": "secio",
    "pubsubAlgorithm": "gossip",
    "omitRelay": true,
    "omitConnectionManager": false,
    "omitNATPortMap": false,
    "omitRPCServer": false,
    "omitDiscoveryService": true,
    "omitRouting": true
  },
  "general": {
    "loggerLocation": ""
  }
}
```

The results of these tests are:

```
Messages published: 90000
Total Nano Times - mean: 4991700.221977778, median: 4305307.0, std: 3330589.107232732
Last Delivery Hop - mean: 9.017844444444444, median: 9.0, std: 1.7406044346791407
Relative Message Redundancy - mean: 0.020408154000000008, median: 0.020408154, std: 6.938893903907228e-18
```

## c5.24xlarge vs t2.xlarge

A comparison of gossip protocols of fifty nodes on the c5.24xlarge to the t2.xlarge is shown in the tables, below. All values shown are median.

### With Discovery

|           | Nano Time | LDH | RMR     |
|-----------|-----------|-----|---------|
| t2.xlarge | 7,424,747 | 5   | 0.0204  |
| c5.24xlarge | 4,206,965 | 5   | 0.0204  |


The t2 instance median message delivery time in nano seconds was nearly double that of the c5 instance, indicating that the nodes may have been resource constrained on CPU resources.

### Without Discovery

|           | Nano Time | LDH | RMR     |
|-----------|-----------|-----|---------|
| t2.xlarge | 5,174,269 | 9   | 0.0204  |
| c5.24xlarge | 4,305,307 | 9   | 0.0204  |

Interestingly, performance without discovery was nearly identical. These results suggest that there may be some computationally intensive tasks being performed in the protocol when discovery is enabled.
