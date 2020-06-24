package config

import (
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/cerr"

	lcrypto "github.com/libp2p/go-libp2p-core/crypto"
)

const (
	defaultsLoc       string = "./defaults"
	defaultConfigName string = "config.default.json"
)

// Config is a struct to hold the config options
type Config struct {
	Host    Host    `json:"host,omitempty"`
	General General `json:"general,omitempty"`
}

// Host contains configs for the host
type Host struct {
	// PrivPEM is the host's private key location in PKCS#8, ASN.1 DER PEM format
	PrivPEM string `json:"privPEM,omitempty"`
	// Priv is the parsed, host's private key
	Priv lcrypto.PrivKey
	// KeyType sets the key from one of the following supported types: ecdsa, ed25519, rsa and secp256k1
	KeyType string `json:"keyType,omitempty"`
	// RSABits is used to set the entropy level only when KeyType == "RSA"
	RSABits int `json:"rsaBits,omitempty"`
	// Listen are addresses on which to listen
	Listens []string `json:"listens,omitempty"`
	// RPCAddress is the address to listen on for RPC
	RPCAddress string `json:"rcpAddress,omitempty"`
	// Peers are peers to be bootstrapped (e.g. /ip4/127.0.0.1/tcp/63785/ipfs/QmWjz6xb8v9K4KnYEwP5Yk75k5mMBCehzWFLCvvQpYxF3d)
	// note: peers are expected to be in IPFS format
	Peers []string `json:"peers,omitempty"`
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

// ErrNilConfig is returned when a config is expected but none is given
const ErrNilConfig = cerr.Error("unknown nil config")

// ErrIncorrectKeyType is returned when the private key is not of the correct type
const ErrIncorrectKeyType = cerr.Error("incorrect private key type")

// ErrUnsupportedKeyType is returned when the specified private key type is not supported
const ErrUnsupportedKeyType = cerr.Error("unsupported key type")
