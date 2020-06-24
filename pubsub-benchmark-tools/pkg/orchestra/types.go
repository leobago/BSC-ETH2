package orchestra

import (
	"context"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/cerr"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/orchestra/config"
)

const (
	// ErrNoHostRPCAddresses is returned when no rpc host addresses were returned from the subnet
	ErrNoHostRPCAddresses = cerr.Error("no host rpc addresses")
)

// Orchestra runs a full test of clients and optionally a subnet
type Orchestra struct {
	props Props
}

// Props are passed to New
type Props struct {
	Conf config.Config
	CTX  context.Context
}
