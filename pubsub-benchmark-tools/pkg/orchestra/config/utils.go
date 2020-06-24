package config

import (
	"encoding/json"
	"path/filepath"
	"strings"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	sconf "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/config"
	"github.com/gobuffalo/packr/v2"

	"github.com/spf13/viper"
)

func trimExtension(filename string) string {
	return strings.TrimSuffix(filename, filepath.Ext(filename))
}

// BuildSubnetConfig builds the subnet configuration from the orchestra configuration
func BuildSubnetConfig(conf Config) sconf.Config {
	var sConf sconf.Config

	sConf.Subnet.NumHosts = conf.Subnet.NumHosts
	sConf.Subnet.PubsubCIDR = conf.Subnet.PubsubCIDR
	sConf.Subnet.PubsubPortRange = conf.Subnet.PubsubPortRange
	sConf.Subnet.RPCCIDR = conf.Subnet.RPCCIDR
	sConf.Subnet.RPCPortRange = conf.Subnet.RPCPortRange
	sConf.Subnet.PeerTopology = conf.Subnet.PeerTopology

	sConf.Host.KeyType = conf.Host.KeyType
	sConf.Host.RSABits = conf.Host.RSABits
	sConf.Host.Transports = conf.Host.Transports
	sConf.Host.Muxers = conf.Host.Muxers
	sConf.Host.Security = conf.Host.Security
	sConf.Host.PubsubAlgorithm = conf.Host.PubsubAlgorithm
	sConf.Host.OmitRelay = conf.Host.OmitRelay
	sConf.Host.OmitConnectionManager = conf.Host.OmitConnectionManager
	sConf.Host.OmitNATPortMap = conf.Host.OmitNATPortMap
	sConf.Host.OmitRPCServer = conf.Host.OmitRPCServer
	sConf.Host.OmitDiscoveryService = conf.Host.OmitDiscoveryService
	sConf.Host.OmitBootstrapPeers = conf.Host.OmitBootstrapPeers
	sConf.Host.OmitRouting = conf.Host.OmitRouting

	sConf.General.LoggerLocation = conf.General.LoggerLocation
	sConf.General.Debug = conf.General.Debug

	return sConf
}

func parseConfigFile(conf *Config, confLoc string) error {
	var err error

	v := viper.New()

	v.SetConfigName(trimExtension(confLoc))
	v.AddConfigPath(".")

	if err = v.ReadInConfig(); err != nil {
		logger.Errorf("err reading configuration file: %s\n%v", confLoc, err)
		return err
	}

	if err = v.Unmarshal(conf); err != nil {
		logger.Errorf("err unmarshaling config\n%v", err)
		return err
	}

	return nil
}

func loadDefaultBox() *packr.Box {
	return packr.New("defaults", defaultsLoc)
}

func loadDefaultConfig(box *packr.Box) ([]byte, error) {
	// Get the string representation of a file, or an error if it doesn't exist:
	return box.Find(defaultConfigName)
}

func parseDefaults(conf *Config) error {
	box := loadDefaultBox()

	defaultConfig, err := loadDefaultConfig(box)
	if err != nil {
		logger.Errorf("err loading default config:\n%v", err)
		return err
	}

	if err := json.Unmarshal(defaultConfig, conf); err != nil {
		logger.Errorf("err unmarshaling config\n%v", err)
		return err
	}

	return nil
}

// note: this could panic!
func mergeDefaults(conf, defaults *Config) {
	// orchestra
	if len(conf.Orchestra.HostRPCAddressesIfOmitSubnet) == 0 {
		conf.Orchestra.HostRPCAddressesIfOmitSubnet = defaults.Orchestra.HostRPCAddressesIfOmitSubnet
	}
	if conf.Orchestra.MessageNanoSecondInterval == 0 {
		conf.Orchestra.MessageNanoSecondInterval = defaults.Orchestra.MessageNanoSecondInterval
	}
	if conf.Orchestra.ClientTimeoutSeconds == 0 {
		conf.Orchestra.ClientTimeoutSeconds = defaults.Orchestra.ClientTimeoutSeconds
	}
	if conf.Orchestra.MessageLocation == "" {
		conf.Orchestra.MessageLocation = defaults.Orchestra.MessageLocation
	}
	if conf.Orchestra.MessageByteSize == 0 {
		conf.Orchestra.MessageByteSize = defaults.Orchestra.MessageByteSize
	}
	if conf.Orchestra.TestDurationSeconds == 0 {
		conf.Orchestra.TestDurationSeconds = defaults.Orchestra.TestDurationSeconds
	}
	if conf.Orchestra.TestWarmUpSeconds == 0 {
		conf.Orchestra.TestWarmUpSeconds = defaults.Orchestra.TestWarmUpSeconds
	}
	if conf.Orchestra.TestCoolDownSeconds == 0 {
		conf.Orchestra.TestCoolDownSeconds = defaults.Orchestra.TestCoolDownSeconds
	}

	// subnet
	if conf.Subnet.NumHosts == 0 {
		conf.Subnet.NumHosts = defaults.Subnet.NumHosts
	}
	if conf.Subnet.PubsubCIDR == "" {
		conf.Subnet.PubsubCIDR = defaults.Subnet.PubsubCIDR
	}
	if len(conf.Subnet.PubsubPortRange) == 0 {
		conf.Subnet.PubsubPortRange = defaults.Subnet.PubsubPortRange
	}
	if conf.Subnet.RPCCIDR == "" {
		conf.Subnet.RPCCIDR = defaults.Subnet.RPCCIDR
	}
	if len(conf.Subnet.RPCPortRange) == 0 {
		conf.Subnet.RPCPortRange = defaults.Subnet.RPCPortRange
	}
	if conf.Subnet.PeerTopology == "" {
		conf.Subnet.PeerTopology = defaults.Subnet.PeerTopology
	}

	// host
	if conf.Host.KeyType == "" {
		conf.Host.KeyType = defaults.Host.KeyType
	}
	if conf.Host.RSABits <= 0 {
		conf.Host.RSABits = defaults.Host.RSABits
	}
	if len(conf.Host.Transports) == 0 {
		conf.Host.Transports = defaults.Host.Transports
	}
	if len(conf.Host.Muxers) == 0 {
		conf.Host.Muxers = defaults.Host.Muxers
	}
	if conf.Host.Security == "" {
		conf.Host.Security = defaults.Host.Security
	}
	if conf.Host.PubsubAlgorithm == "" {
		conf.Host.PubsubAlgorithm = defaults.Host.PubsubAlgorithm
	}
}
