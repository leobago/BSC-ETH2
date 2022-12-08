module github.com/protolambda/rumor

go 1.14

replace github.com/libp2p/go-libp2p-pubsub v0.3.3 => github.com/cortze/go-libp2p-pubsub v0.3.4-0.20210318120057-ca6e67cdec42

require (
	github.com/anmitsu/go-shlex v0.0.0-20200514113438-38f4b401e2be // indirect
	github.com/btcsuite/btcd v0.22.0-beta
	github.com/chzyer/readline v0.0.0-20180603132655-2972be24d48e
	github.com/cortze/go-eth2-beacon-nodes v0.0.0-20210226135425-ab05ba562a6f
	github.com/ethereum/go-ethereum v1.10.1
	github.com/gliderlabs/ssh v0.3.0
	github.com/golang/snappy v0.0.3-0.20201103224600-674baa8c7fc3
	github.com/gorilla/websocket v1.4.2
	github.com/herumi/bls-eth-go-binary v0.0.0-20200722032157-41fc56eba7b4 // indirect
	github.com/ipfs/go-datastore v0.5.0
	github.com/ipfs/go-ds-badger v0.3.0
	github.com/ipfs/go-ds-leveldb v0.5.0
	github.com/ipfs/go-log v1.0.5
	github.com/klauspost/cpuid v1.2.3 // indirect
	github.com/libp2p/go-addr-util v0.1.0
	github.com/libp2p/go-conn-security-multistream v0.3.0
	github.com/libp2p/go-eventbus v0.2.1
	github.com/libp2p/go-libp2p v0.18.0
	github.com/libp2p/go-libp2p-autonat v0.3.2
	github.com/libp2p/go-libp2p-connmgr v0.2.4
	github.com/libp2p/go-libp2p-core v0.14.0
	github.com/libp2p/go-libp2p-mplex v0.6.0
	github.com/libp2p/go-libp2p-nat v0.1.0
	github.com/libp2p/go-libp2p-noise v0.3.0
	github.com/libp2p/go-libp2p-peerstore v0.6.0
	github.com/libp2p/go-libp2p-pubsub v0.3.3
	github.com/libp2p/go-libp2p-secio v0.2.2
	github.com/libp2p/go-libp2p-swarm v0.10.2
	github.com/libp2p/go-libp2p-tls v0.3.1
	github.com/libp2p/go-libp2p-transport-upgrader v0.7.1
	github.com/libp2p/go-libp2p-yamux v0.8.2
	github.com/libp2p/go-netroute v0.2.0
	github.com/libp2p/go-stream-muxer-multistream v0.4.0
	github.com/libp2p/go-tcp-transport v0.5.1
	github.com/libp2p/go-ws-transport v0.6.0
	github.com/minio/sha256-simd v1.0.0
	github.com/multiformats/go-base32 v0.0.3
	github.com/multiformats/go-multiaddr v0.5.0
	github.com/multiformats/go-multiaddr-dns v0.3.1
	github.com/multiformats/go-multiaddr-net v0.2.0
	github.com/multiformats/go-multistream v0.2.2
	github.com/olekukonko/tablewriter v0.0.2-0.20190409134802-7e037d187b0c
	github.com/protolambda/ask v0.0.5
	github.com/protolambda/zrnt v0.13.2
	github.com/protolambda/ztyp v0.1.2
	github.com/sirupsen/logrus v1.7.0
	github.com/spf13/cobra v1.1.1
	mvdan.cc/sh/v3 v3.1.2
)
