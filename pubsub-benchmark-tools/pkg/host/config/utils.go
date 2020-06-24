package config

import (
	"bufio"
	"crypto/rand"
	"crypto/x509"
	"encoding/json"
	"encoding/pem"
	"errors"
	"os"
	"path/filepath"
	"strings"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"

	"github.com/gobuffalo/packr/v2"
	lcrypto "github.com/libp2p/go-libp2p-core/crypto"
	"github.com/spf13/viper"
)

func trimExtension(filename string) string {
	return strings.TrimSuffix(filename, filepath.Ext(filename))
}

func parseListens(conf *Config, listens string) {
	if listens != "" {
		listensArr := strings.Split(listens, ",")
		for idx := range listensArr {
			listensArr[idx] = strings.TrimSpace(listensArr[idx])
		}
		conf.Host.Listens = listensArr
	}
}

func parsePeers(conf *Config, peers string) {
	if peers != "" {
		peersArr := strings.Split(peers, ",")
		for idx := range peersArr {
			peersArr[idx] = strings.TrimSpace(peersArr[idx])
		}
		conf.Host.Peers = peersArr
	}
}

func parseConfigFile(conf *Config, confLoc, pemLoc string) error {
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

	if pemLoc != "" {
		conf.Host.PrivPEM = pemLoc
	}

	if conf.Host.PrivPEM != "" {
		if err = loadAndSavePriv(conf); err != nil {
			logger.Errorf("could not load private key:\n%v", err)
			return err
		}
	} else {
		conf.Host.Priv, _, err = lcrypto.GenerateECDSAKeyPair(rand.Reader)
		if err != nil {
			logger.Errorf("err generating private key:\n%v", err)
			return err
		}
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

func loadAndSavePriv(conf *Config) error {
	privB, err := loadPriv(conf.Host.PrivPEM)
	if err != nil {
		logger.Errorf("err loading private key file:\n%v", err)
		return err
	}

	priv, err := parsePrivateKey(privB)
	if err != nil {
		logger.Errorf("err parsing private key:\n%v", err)
		return err
	}

	conf.Host.Priv = priv

	return nil
}

func loadPriv(loc string) ([]byte, error) {
	privateKeyFile, err := os.Open(loc)
	if err != nil {
		logger.Errorf("err loading private key pem file: %s\n%v", loc, err)
		return nil, err
	}
	defer privateKeyFile.Close()

	pemfileinfo, err := privateKeyFile.Stat()
	if err != nil {
		logger.Errorf("err statting private key file:\n%v", err)
		return nil, err
	}
	var size int64 = pemfileinfo.Size()
	pembytes := make([]byte, size)

	buffer := bufio.NewReader(privateKeyFile)
	_, err = buffer.Read(pembytes)
	return []byte(pembytes), err
}

func parsePrivateKey(privB []byte) (lcrypto.PrivKey, error) {
	data, _ := pem.Decode(privB)
	if data == nil {
		logger.Error("err decoding default PEM file. Nil data block")
		return nil, errors.New("err decoding default PEM file")
	}

	cPriv, err := x509.ParsePKCS8PrivateKey(data.Bytes)
	if err != nil {
		logger.Errorf("err parsing private key bytes:\n%v", err)
		return nil, err
	}

	priv, _, err := lcrypto.KeyPairFromStdKey(cPriv)
	if err != nil {
		logger.Errorf("err generating lcrypto priv key:\n%v", err)
		return nil, err
	}

	return priv, nil
}

// note: this could panic!
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
	if conf.Host.KeyType == "" {
		conf.Host.KeyType = defaults.Host.KeyType
	}
	if conf.Host.RSABits <= 0 {
		conf.Host.RSABits = defaults.Host.RSABits
	}
	if len(conf.Host.Listens) == 0 {
		conf.Host.Listens = defaults.Host.Listens
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
	if conf.Host.RPCAddress == "" {
		conf.Host.RPCAddress = defaults.Host.RPCAddress
	}
	if conf.General.LoggerLocation == "" {
		conf.General.LoggerLocation = defaults.General.LoggerLocation
	}
}
