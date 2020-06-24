package host

import (
	"context"
	"encoding/binary"
	"time"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"

	pb "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/pb/publisher"
	"github.com/davecgh/go-spew/spew"
	peer "github.com/libp2p/go-libp2p-peer"
	pubsub "github.com/libp2p/go-libp2p-pubsub"
)

func pubsubHandler(ctx context.Context, hostID peer.ID, sub *pubsub.Subscription) {
	for {
		nxt, err := sub.Next(ctx)
		if err != nil {
			logger.Errorf("err reading next:\n%v", err)
			continue
		}
		logger.Info("msg received on pubsub channel")

		msg := pb.Message{}
		if err = msg.XXX_Unmarshal(nxt.GetData()); err != nil {
			logger.Errorf("err unmarshaling next message:\n%v", err)
			continue
		}
		spew.Dump(msg)

		// TODO: how to increment sequence before sending out?
		logger.Infof("Pubsub message received: %v,%v,%v,%v,%d,%d", hostID, nxt.GetFrom(), msg.GetId(), binary.BigEndian.Uint64(nxt.GetSeqno()), time.Now().UnixNano(), msg.GetSequence())
	}
}
