package subnet

import (
	"context"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/cerr"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/config"
)

const (
	// ErrIPOutOfCIDRRange is returned when an IP is incremented but out of CIDR range
	ErrIPOutOfCIDRRange = cerr.Error("ip out of CIDR range")
	// ErrNilIPNet is thrown when an IPNet pointer is nil
	ErrNilIPNet = cerr.Error("ip net is nil")
	// ErrNilPort is thrown when a port pointer is nil
	ErrNilPort = cerr.Error("port is nil")
)

// Props is passed to new to build a new subnet
type Props struct {
	CTX  context.Context
	Conf config.Config
}

// Subnet implements the subment methods
type Subnet struct {
	props *Props
	hosts []*host.Host
}
