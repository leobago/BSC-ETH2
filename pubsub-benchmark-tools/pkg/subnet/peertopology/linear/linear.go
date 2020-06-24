package linear

import (
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
)

// Build connects the hosts using the linear topology
func Build(hosts []*host.Host) error {
	var err error

	for i := 1; i < len(hosts); i++ {
		selectedHostIdx := i - 1
		if err = hosts[i].Connect(hosts[selectedHostIdx].IPFSAddresses()); err != nil {
			logger.Errorf("err connecting %s with %s:\n%v", hosts[i].ID(), hosts[selectedHostIdx].ID(), err)
			return err
		}
	}

	return nil
}
