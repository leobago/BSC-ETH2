> libp2p/go-libp2p-pubsub benchmark tools

# go-libp2p-pubsub-benchmark-tools
[![Build Status](https://travis-ci.org/agencyenterprise/go-libp2p-pubsub-benchmark-tools.svg?branch=develop)](https://travis-ci.org/agencyenterprise/go-libp2p-pubsub-benchmark-tools) [![Coverage Status](https://coveralls.io/repos/github/agencyenterprise/go-libp2p-pubsub-benchmark-tools/badge.svg?branch=develop)](https://coveralls.io/github/agencyenterprise/go-libp2p-pubsub-benchmark-tools?branch=develop) [![Go Report Card](https://goreportcard.com/badge/github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools)](https://goreportcard.com/report/github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools) [![GoDoc](https://godoc.org/github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools?status.svg)](https://godoc.org/github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools)

This module provides tools for benchmarking the [go-libp2p pubsub protocols](https://github.com/libp2p/go-libp2p-pubsub); however, it can be easily extended to other pubsub protocols or even beyond pubsub.


## Architecture

Hosts are connected to each other via the protocols defined in the config file. Each host also runs an rpc host and can receive messages from clients. Via rpc, clients can request hosts connect and disconnect with peers, publish a message, shutdown, and more.


## Usage

The simplest way to use the tool is via `cmd/subnet/main.go`:

1. Spin up a subnet of hosts: `$ go run ./cmd/subnet/main.go`
2. In another terminal, pass a message into the subnet and watch the hosts start publishing: `$ go run ./cmd/client/main.go publish`

If you'd like to manually spin up hosts, do the following:
1. `$ go run ./cmd/host/main.go`
2. In another terminal, spin up a second host and connect it to the first: `$ go run ./cmd/host/main.go -l /ip4/127.0.0.2/tcp/3002,/ip4/127.0.0.2/tcp/3003/ws -r :8081 -p <prev. host listen addrs>`. 
   * Note, the `-l` flag are the listen addresses. Notice how we've incremented standard local host from `127.0.0.1` to `127.0.0.2`. We could have also simply changed the port address.
    * Further note that `-r` is the rpc listen address and needs to be different for this host than the default `:8080`.
3. In a third terminal, pass a message into the subnet and watch the hosts start publishing: `$ go run ./cmd/client/main.go publish`


## Commands

Five command line programs are available in this module and are located in the `cmd/` directory:
1. **Analysis** - this command is used to analyze log files and compute metrics.
2. **Client** - this command is used to interact with hosts via the rpc.
3. **Host** - this command is used to start a libp2p host.
4. **Orchestra** - this command spins up an "orchestra" of clients and optionally a subnet and and sends the hosts messages at the specified interval.
5. **Subnet** - this command is used to start multiple libp2p hosts in one process.

### Analysis

The analysis tool computes performance metrics. These metrics were taken from the research paper:

```
Leito, J., Pereira, J., Rodrigues, L.: Epidemic broadcast trees.
In: Proceedings of the 26th IEEE International Symposium on Reliable Distributed Systems (SRDS’2007),
Beijing, China (2007) 301 – 310
```

The metrics computed are:
1. **TotalNanoTime** - the time (in nano seconds) for the message to propogate the network
2. **LastDeliveryHop** - the hop count of the last message that is delivered by a [pubsub] protocol or, in other words, is the maximum number of hops that a message must be forwarded in the overlay before it is delivered.
3. **RelativeMessageRedundancy** - RelativeMessageRedundancy (RMR) this metric measures the messages overhead in a [pubsub] protocol. It is defined as: (m / (n - 1)) - 1. where m is the total number of payload messages exchanged during the broadcast procedure and n is the total number of nodes that received that broadcast. This metric is only applicable when at least 2 nodes receive the message. A RMR value of zero means that there is exactly one payload message exchange for each node in the system, which is clearly the optimal value. By opposition, high values of RMR are indicative of a broadcast strategy that promotes a poor network usage. Note that it is possible to achieve a very low RMR by failing to be reliable. Thus the aim is to combine low RMR values with high reliability. Furthermore, RMR values are only comparable for protocols that exhibit similar reliability. Finally, note that in pure [pubsub] approaches, RMR is closely related with the protocol fanout, as it tends to fanout−1.

The commands availabe are:

```bash
$ go run ./cmd/analysis/main.go --help
Analyzes a log file and outputs the metrics to standard out or the specified log file

Usage:
  analyze [log file] [flags]

Flags:
  -h, --help         help for analyze
  -o, --out  string  Output json location. Defaults to standard out.
```

An example output is:

```bash
$ go run ./cmd/analysis/main.go log.txt

INFO[0000] analyzing log file at log.txt         source="main.go:29:main.setup.func1"
INFO[0000] [
  {
    "totalNanoTime": 2426076,
    "lastDeliveryHop": 1,
    "relativeMessageRedundancy": 0.111111164
  }
]  source="main.go:61:main.setup.func1"
INFO[0000] done
```

### Client

The client command is used to interact with hosts via the rpc. Multiple hosts can be messaged in a single command by separating each listen address with a comma using the `-p` flag. 

The output of `--help` is shown, below. Each command has its own `--help` as well.

```bash
$ go run ./cmd/client/main.go --help
Usage:
  client [command]

Available Commands:
  close-all   Close all peer connections
  close-peers Close connections to peers
  publish     Publish a message in the pubsub
  help        Help about any command
  id          Get peer ids
  list-peers  List connected peers
  listens     Get listen addresses
  open-peers  Open connections to peers
  shutdown    Shutsdown the host(s)

Flags:
  -h, --help            help for client
      --log     string  Log file location. Defaults to standard out.
  -p, --peers   string  Peers to connect. Comma separated. (default ":8080")
  -t, --timeout int     Timeout, in seconds (default 20)

  Use "client [command] --help" for more information about a command.
```

### Host

The host command spins up a libp2p host, an RPC host and opens a pubsub channel. The host command only has one command, `start`, which starts the server.

```bash
$ go run ./cmd/host/main.go --help
Starts the go-libp2p pub/sub host

Usage:
  start [flags]

Flags:
  -c, --config     string   The configuration file. (default "configs/host/config.json")
  -h, --help                help for start
  -l, --listens    string   Addresses on which to listen. Comma separated. Overides config.json.
      --log        string   Log file location. Defaults to standard out.
      --pem        string   PEM file location. Overrides the config.json.
  -p, --peers      string   Peers to connect. Comma separated. Overides config.json.
  -r, --rpc-listen string   RPC listen address. Overides config.json.
```

#### Configuration

The host has many configuration options which can be set between a combination of flags and config file options. The default config file location is `configs/host/config.json` but can be set with the `-c` flag. The default config file is shown, below. If any option is not present in the passed config file, the host will default to the below.

```json
{
  "host": {
    "privPEM": "",
    "transports": ["tcp", "ws"],
    "listens": ["/ip4/127.0.0.1/tcp/3000","/ip4/127.0.0.1/tcp/3001/ws"],
    "rpcAddress": "127.0.0.1:8080",
    "peers": [],
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
    "loggerLocation": "",
    "debug": true
  }
}
```


### Orchestra

Orchestra is a command which spins up a client, and optionally a subnet, and pings the hosts at regularly defined intervals. The client creates a new message id for each new message that it sends.

The available commands and flags are shown below.

```bash
$ go run ./cmd/orchestra/main.go --help
Spins up clients and optionally hosts and sends the hosts messages at the specified interval.

Usage:
  start [flags]

Flags:
  -c, --config  string   The configuration file. (default "configs/orchestra/config.json")
  -h, --help             help for start
      --log     string   Log file location. Defaults to standard out.
  -m, --message string   The message file to send to peers. (default "client.message.json")
```

#### Configuration

The orchestration can be configured via a json file. The default configuration location is `configs/orchestra/config.json` but can be modified with the `-c` flag. The default config file is shown, below. If any option is not present in the passed config file, the subnet will default to the below.

```json
{
  "orchestra": {
    "omitSubnet": false,
    "hostsIfOmitSubnet": [],
    "messageNanoSecondInterval": 10000000,
    "clientTimeoutSeconds": 20,
    "messageLocation": "client.message.json",
    "messageByteSize": 1000,
    "testDurationSeconds": 900,
    "testWarmupSeconds": 60,
    "testCooldownSeconds": 60
  },
  "subnet": {
    "numHosts": 10,
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
    "loggerLocation": "",
    "debug": true
  }
}

```

### Subnet

Subnet is a command which simplifies the creation and peering of hosts. Using this command, dozens, hundreds or possibly even thousands of hosts can been started and peered on a single machine in a single process. In order to start a large number of hosts, you may need to increase the max open files limit on your machine.

The available commands and flags are shown below.

```bash
$ go run ./cmd/subnet/main.go --help
Start a subnet of interconnected libp2p pubsub hosts

 Usage:
   start [flags]

Flags:
  -c, --config  string   The configuration file. (default "configs/subnet/config.json")
  -h, --help             help for start
      --log     string   Log file location. Defaults to standard out.
```

#### Configuration

The subnet can be configured via a json file. The default configuration location is `configs/subnet/config.json` but can be modified with the `-c` flag. The default config file is shown, below. If any option is not present in the passed config file, the subnet will default to the below.

```json
{
  "subnet": {
    "numHosts": 10,
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
    "loggerLocation": "",
    "debug": true
  }
}
```

#### Peering Topologies

Three peering topologies have been provided; however, new ones can easily by added by implementing the `PeerTopology` interface:

```go
// PeerTopology is a peering algorithm that connects hosts
type PeerTopology interface {
	Build(hosts []*host.Host) error
}
```

The three provided topologies are:
1. Whiteblocks
   * This is the peering topology from the original Whiteblocks [gossip sub tests](https://github.com/whiteblock/p2p-tests). Essentially, each peer is randomly connected to a previously started peer. A more detailed description can be found in the topology [readme](./pkg/subnet/peertopology/whiteblocks/README.md).
2. Linear
   *  Each Nth host is connected to the N-1 host, starting with N=1.
3. Full
   * Each host is connected to each other host.


## Protobufs

Clients can communicate with hosts via RPC. The RPC messages and services are defined in the protobuf file. In order to make the protobufs, you will need to first follow the installation instructions, [here](https://github.com/golang/protobuf), and then run `$ make -C ./pkg/pb/`. The protobuf definition can be found in the [proto file](./pkg/pb/publisher/publisher.proto) and is shown, below.

```proto
syntax = "proto3";

package pb;

option java_multiple_files = true;
option java_package = "io.grpc.pubsub.benchmark";
option java_outer_classname = "PubsubBenchmark";

import "google/protobuf/empty.proto";

message Message {
  string id = 1;
  int32 sequence = 2;
  bytes data = 3;
}

message PublishReply {
  string msgId = 1;
  bool success = 2;
}

message CloseAllPeerConnectionsReply {
  bool success = 1;
}

message ShutdownReply {
  bool success = 1;
}

message PeersList {
  repeated string peers = 1;
}

message ClosePeerConnectionsReply {
  bool success = 1;
}

message OpenPeerConnectionReply {
  bool success = 1;
  string peer = 2;
}

message OpenPeersConnectionsReplies {
  repeated OpenPeerConnectionReply PeerConnections = 1;
}

message IDReply {
  string ID = 1;
}

message ListenAddressesReply {
  repeated string Addresses = 1;
}

// The publisher service definition.
service Publisher {
  // Publishes a message on the pubsub channel
  rpc PublishMessage(Message) returns (PublishReply) {}
  // Closes all connections
  rpc CloseAllPeerConnections(google.protobuf.Empty) returns (CloseAllPeerConnectionsReply) {}
  // Closes connections to listed peers
  rpc ClosePeerConnections(PeersList) returns (ClosePeerConnectionsReply) {}
  // Opens connections to listed peers
  rpc OpenPeersConnections(PeersList) returns (OpenPeersConnectionsReplies) {}
  // Lists the host's connected peers
  rpc ListConnectedPeers(google.protobuf.Empty) returns (PeersList) {}
  // Shuts the host down
  rpc Shutdown(google.protobuf.Empty) returns (ShutdownReply) {}
  // ID returns the host's id
  rpc ID(google.protobuf.Empty) returns (IDReply) {}
  // ListenAddresses returns the host's listen addresses  
  rpc ListenAddresses(google.protobuf.Empty) returns (ListenAddressesReply) {}
}
```

## License

[**MIT**](LICENSE).

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fagencyenterprise%2Fgo-libp2p-pubsub-benchmark-tools.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fagencyenterprise%2Fgo-libp2p-pubsub-benchmark-tools?ref=badge_large)

```
MIT License

Copyright (c) 2019 AE Studio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
