package peertopology

import (
	"strings"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/peertopology/full"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/peertopology/linear"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/peertopology/whiteblocks"
)

// ConnectPeersForTopology builds the specified topology
func ConnectPeersForTopology(topology string, hosts []*host.Host) error {
	switch strings.ToLower(topology) {
	case "whiteblocks":
		return whiteblocks.Build(hosts)

	case "linear":
		return linear.Build(hosts)

	case "full":
		return full.Build(hosts)

	default:
		logger.Errorf("unknown peering topology %s", topology)
		return ErrUnknownTopology
	}
}
