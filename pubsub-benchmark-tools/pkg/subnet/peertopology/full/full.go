package full

import (
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
)

// Build connects the hosts using the full topology
func Build(hosts []*host.Host) error {
	var err error

	for i := range hosts {
		for j := i + 1; j < len(hosts); j++ {
			if err = hosts[i].Connect(hosts[j].IPFSAddresses()); err != nil {
				logger.Errorf("err connecting %s with %s:\n%v", hosts[i].ID(), hosts[j].ID(), err)
				return err
			}
		}
	}

	return nil
}
