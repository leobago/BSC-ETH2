package host

import (
	"context"
	"fmt"
	"net"
	"time"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	pb "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/pb/publisher"

	"github.com/golang/protobuf/ptypes/empty"
	ipfsaddr "github.com/ipfs/go-ipfs-addr"
	peerstore "github.com/libp2p/go-libp2p-peerstore"
	"google.golang.org/grpc"
)

// New returns a new grpc host
func New(props *Props) *Host {
	return &Host{
		props: props,
	}
}

// Listen starts the grpc host
func (h *Host) Listen(ctx context.Context, addr string) error {
	var lstnCfg net.ListenConfig
	lis, err := lstnCfg.Listen(ctx, "tcp", addr)
	if err != nil {
		logger.Errorf("failed to listen: %v", err)
		return err
	}
	defer lis.Close()

	s := grpc.NewServer()
	pb.RegisterPublisherServer(s, h)
	if err := s.Serve(lis); err != nil {
		logger.Errorf("failed to serve: %v", err)
		return err
	}

	return nil
}

// PublishMessage implements
func (h *Host) PublishMessage(ctx context.Context, in *pb.Message) (*pb.PublishReply, error) {
	logger.Info("received rpc message; will now publish to subscribers")
	//spew.Dump(in)

	bs, err := in.XXX_Marshal(nil, true)
	if err != nil {
		logger.Errorf("err marshaling message:\n%v", err)
		h.props.CH <- err
		return nil, err
	}

	if err = h.props.PS.Publish(h.props.PubsubTopic, bs); err != nil {
		logger.Errorf("err publishing message:\n%v", err)
		h.props.CH <- err
		return nil, err
	}

	return &pb.PublishReply{
		MsgId:   in.Id,
		Success: err == nil,
	}, nil
}

// CloseAllPeerConnections closes all connections
// note: is this working correctly?
func (h *Host) CloseAllPeerConnections(ctx context.Context, _ *empty.Empty) (*pb.CloseAllPeerConnectionsReply, error) {
	logger.Info("received close peers all connection signal on rpc")
	peerIDs := h.props.Host.Network().Peers()
	for _, peerID := range peerIDs {
		if err := h.props.Host.Network().ClosePeer(peerID); err != nil {
			logger.Errorf("err closing connection to %s\n%v", peerID, err)
			h.props.CH <- err
			return nil, err
		}
	}

	return &pb.CloseAllPeerConnectionsReply{
		Success: true,
	}, nil
}

// ClosePeerConnections closes connections to listed peers
func (h *Host) ClosePeerConnections(ctx context.Context, peersList *pb.PeersList) (*pb.ClosePeerConnectionsReply, error) {
	logger.Info("received close peers connection signal on rpc")
	// TODO: ...
	//var results []*pb.OpenPeerConnectionReply
	for _, peer := range peersList.Peers {
		addr, err := ipfsaddr.ParseString(peer)
		if err != nil || addr == nil {
			logger.Errorf("err parsing peer: %s\n%v", peer, err)
			h.props.CH <- err
			return nil, err
		}

		pinfo, err := peerstore.InfoFromP2pAddr(addr.Multiaddr())
		if err != nil || pinfo == nil {
			logger.Errorf("err getting info from peerstore\n%v", err)
			h.props.CH <- err
			return nil, err
		}
		if err = h.props.Host.Network().ClosePeer(pinfo.ID); err != nil {
			logger.Errorf("err closing connection to %s\n%v", pinfo.ID, err)
			h.props.CH <- err
			return nil, err
		}
	}

	return &pb.ClosePeerConnectionsReply{
		Success: true,
	}, nil
}

// OpenPeersConnections opens connections to listed peers
func (h *Host) OpenPeersConnections(ctx context.Context, peersList *pb.PeersList) (*pb.OpenPeersConnectionsReplies, error) {
	logger.Info("received open peers connection signal on rpc")
	var results []*pb.OpenPeerConnectionReply

	for _, p := range peersList.Peers {
		addr, err := ipfsaddr.ParseString(p)
		if err != nil || addr == nil {
			logger.Errorf("err parsing peer: %s\n%v", p, err)
			results = append(results, &pb.OpenPeerConnectionReply{
				Success: false,
				Peer:    p,
			})
			return nil, err
		}

		pinfo, err := peerstore.InfoFromP2pAddr(addr.Multiaddr())
		if err != nil || pinfo == nil {
			logger.Errorf("err getting info from peerstore\n%v", err)
			results = append(results, &pb.OpenPeerConnectionReply{
				Success: false,
				Peer:    p,
			})
			return nil, err
		}

		logger.Infof("full peer addr: %s", addr.String())
		logger.Infof("peer info: %v", pinfo)

		if err := h.props.Host.Connect(h.props.CTX, *pinfo); err != nil {
			logger.Errorf("connecting to peer failed\n%v", err)
			results = append(results, &pb.OpenPeerConnectionReply{
				Success: false,
				Peer:    p,
			})
			return nil, err
		}

		logger.Infof("Connected to peer: %v", pinfo.ID)
		results = append(results, &pb.OpenPeerConnectionReply{
			Success: true,
			Peer:    p,
		})
	}

	return &pb.OpenPeersConnectionsReplies{
		PeerConnections: results,
	}, nil
}

// ListConnectedPeers lists the host's connected peers
func (h *Host) ListConnectedPeers(ctx context.Context, _ *empty.Empty) (*pb.PeersList, error) {
	logger.Info("received list connected peers signal on rpc")
	var peers []string

	// note: is this the correct method?
	peerIDs := h.props.Host.Network().Peers()
	for _, peerID := range peerIDs {
		multiAddrs := h.props.Host.Peerstore().Addrs(peerID)
		for _, multiAddr := range multiAddrs {
			peers = append(peers, multiAddr.String())
		}
	}

	return &pb.PeersList{
		Peers: peers,
	}, nil
}

// Shutdown shuts the host down
func (h *Host) Shutdown(ctx context.Context, _ *empty.Empty) (*pb.ShutdownReply, error) {
	logger.Info("received shutdown signal on rpc")
	if err := h.props.Host.Close(); err != nil {
		logger.Errorf("err shutting down server:\n%v", err)
		h.props.CH <- err
		return nil, err
	}

	defer func() {
		// note: hacky...
		time.Sleep(2 * time.Second)
		h.props.Shutdown <- struct{}{}
	}()

	return &pb.ShutdownReply{
		Success: true,
	}, nil
}

// ID returns the libp2p host id
func (h *Host) ID(ctx context.Context, _ *empty.Empty) (*pb.IDReply, error) {
	return &pb.IDReply{
		ID: fmt.Sprintf("%s", h.props.Host.ID()),
	}, nil
}

// ListenAddresses returns the addresses on which the libp2p is listening
func (h *Host) ListenAddresses(ctx context.Context, _ *empty.Empty) (*pb.ListenAddressesReply, error) {
	var addresses []string

	multiAddrs := h.props.Host.Addrs()
	for _, multiAddr := range multiAddrs {
		addresses = append(addresses, multiAddr.String())
	}

	return &pb.ListenAddressesReply{
		Addresses: addresses,
	}, nil
}
