package whiteblocks

import (
	"math/rand"
	"time"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
)

// Build connects the hosts using the whiteblocks topology
func Build(hosts []*host.Host) error {
	var err error

	rand.Seed(time.Now().UnixNano())
	for i := 1; i < len(hosts); i++ {
		selectedHostIdx := randBetween(0, i-1)
		logger.Warnf("selectedHostIdx: %d", selectedHostIdx)
		if err = hosts[i].Connect(hosts[selectedHostIdx].IPFSAddresses()); err != nil {
			logger.Errorf("err connecting %s with %s:\n%v", hosts[i].ID(), hosts[selectedHostIdx].ID(), err)
			return err
		}
	}

	return nil
}
