package config

import (
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
)

// Load reads the passed config file location and parses it into a config struct.
func Load(confLoc string) (Config, error) {
	var (
		conf, defaults Config
		err            error
	)

	if err = parseDefaults(&defaults); err != nil {
		logger.Errorf("err parsing defaults:\n%v", err)
	}

	if err = parseConfigFile(&conf, confLoc); err != nil {
		logger.Errorf("err parsing config file:\n%v", err)
		return conf, err
	}

	mergeDefaults(&conf, &defaults)

	return conf, nil
}
