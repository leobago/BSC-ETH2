package peertopology

import (
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/cerr"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
)

const (
	// ErrUnknownTopology is thrown when a passed topology is not known
	ErrUnknownTopology = cerr.Error("unknown peering topology")
)

// PeerTopology is a peering algorithm that connects hosts
type PeerTopology interface {
	Build(hosts []*host.Host) error
}
