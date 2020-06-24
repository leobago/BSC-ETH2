package config

const (
	defaultsLoc       string = "./defaults"
	defaultConfigName string = "config.default.json"
)

// Config is a struct to hold the config options
type Config struct {
	Subnet  Subnet  `json:"subnet,omitempty"`
	Host    Host    `json:"host,omitempty"`
	General General `json:"general,omitempty"`
}

// Subnet holds the configs for the subnet
type Subnet struct {
	// NumHosts is the number of hosts to spin up
	NumHosts int `json:"numHosts,omitempty"`
	// PubsubCIDR is the range of ip addrs for the pubsub to listen. Ports are incremented before IP
	PubsubCIDR string `json:"pubsubCIDR,omitempty"`
	// PubsubPortRange is the range of ports of pubsub to listen. Range is inclusive. Ports are incremented before IP
	PubsubPortRange [2]int `json:"pubsubPortRange,omitempty"`
	// RPCCIDR is the range of ip addrs for the rpc host to listen. Ports are incremented before IP
	RPCCIDR string `json:"rpcCIDR,omitempty"`
	// RPCPortRange is the range of ports for the rpc to listen. Range is inclusive. Ports are incremented before IP
	RPCPortRange [2]int `json:"rpcPortRange,omitempty"`
	// PeerTopology is the named peering topology
	PeerTopology string `json:"peerTopology,omitempty"`
}

// Host holds the configs for the hosts
type Host struct {
	// KeyType sets the key from one of the following supported types: ecdsa, ed25519, rsa and secp256k1
	KeyType string `json:"keyType,omitempty"`
	// RSABits is used to set the entropy level only when KeyType == "RSA"
	RSABits int `json:"rsaBits,omitempty"`
	// Transports are the transport protocols which the host is to use (e.g. "tcp", "ws", etc)
	Transports []string `json:"transports,omitempty"`
	// Muxers are the transport muxers (e.g. yamux, mplex, etc.)
	Muxers [][]string `json:"muxers,omitempty"`
	// Security specifies the security to use
	Security string `json:"security,omitempty"`
	// PubsubAlgorithm is the pubsub method to use; available are: gossip, flood and random
	PubsubAlgorithm string `json:"pubsubAlgorith,omitempty"`
	// OmitRelay disables the relay
	OmitRelay bool `json:"omitRelay,omitempty"`
	// OmitConnectionManager disables the connection manager
	OmitConnectionManager bool `json:"omitConnectionManager,omitempty"`
	// OmitNatPortMap disables the nat port map
	OmitNATPortMap bool `json:"omitNATPortMap,omitempty"`
	// OmitRPCServer disables the rpc server
	OmitRPCServer bool `json:"omitRPCServer,omitempty"`
	// OmitDiscoveryService disables the discovery service
	OmitDiscoveryService bool `json:"omitDiscoveryService,omitempty"`
	// OmitBootstrapPeers disables bootstrapping of peers
	OmitBootstrapPeers bool `json:"omitBootstrapPeers,omitempty"`
	// OmitRouting disables ipfs routing (e.g. dht);
	// note: DHT is the only router supported, for now...
	OmitRouting bool `json:"omitRouting,omitempty"`
}

// General store general config directives
type General struct {
	// LogerLocation points to the log file. One will be create if not exists. Default is std out.
	LoggerLocation string `json:"loggerLocation,omitempty"`
	// Debug sets the log level; true logs everything; false sets logger to warn, error and fatal
	Debug bool `json:"debug,omitempty"`
}
