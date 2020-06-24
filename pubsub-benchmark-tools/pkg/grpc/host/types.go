package host

import (
	"context"

	"github.com/libp2p/go-libp2p-core/host"

	pubsub "github.com/libp2p/go-libp2p-pubsub"
)

// Props are passed to New
type Props struct {
	Host        host.Host
	CH          chan error
	PS          *pubsub.PubSub
	PubsubTopic string
	CTX         context.Context
	Shutdown    chan struct{}
}

// Host listens on grpc
type Host struct {
	props *Props
}
