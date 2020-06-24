# Benchmark Tests

This example benchmark test was carried out on 17 Oct. 2019 on an Amazon AWS EC2 t2.xlarge instance running Red Hat Enterprise Linux.

The benchmark consisted of roughly two and one half hours of publishing messages of 1kb between fifty nodes. Nodes were started sequentiall, and were randomly peered with previously started nodes. Nodes in the subnet were then randomly selected every 100ms and told to publish a message on their pubsub channel.

Three libp2p pubsub protocols tested were: gossip, flood and random.

These tests were performed without any routing, peer discovery or relays.

Compiled versions of `orchestra` and `analysis` were used.

The shell script used in these tests were the same in all three tests:

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

### Gossip

The [config](./data/gossip/orchestra.config.json) file used in this test is:

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
Total Nano Times - mean: 26263571.375944443, median: 5174269.0, std: 224268172.2281729
Last Delivery Hop - mean: 9.067222222222222, median: 9.0, std: 1.788448444743704
Relative Message Redundancy - mean: 0.020408154000000008, median: 0.020408154, std: 6.938893903907228e-18
```

### Flood

The [config](./data/flood/orchestra.config.json) file used in this test is:

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
    "pubsubAlgorithm": "flood",
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
Total Nano Times - mean: 5401697.526744445, median: 5063028.5, std: 1606625.824702993
Last Delivery Hop - mean: 9.058477777777778, median: 9.0, std: 1.7084015643465469
Relative Message Redundancy - mean: 0.020408154000000008, median: 0.020408154, std: 6.938893903907228e-18
```

### Random

The [config](./data/random/orchestra.config.json) file used in this test is:

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
    "pubsubAlgorithm": "random",
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
Total Nano Times - mean: 5345632.971422222, median: 5041622.5, std: 1618816.94873532
Last Delivery Hop - mean: 9.105344444444444, median: 9.0, std: 1.745120910558674
Relative Message Redundancy - mean: 0.021059074959888895, median: 0.020408154, std: 0.0044073976014634845
```
