package client

import (
	"context"
	"errors"
	"time"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	pb "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/pb/publisher"
	"github.com/golang/protobuf/ptypes/empty"

	grpc "google.golang.org/grpc"
)

// Publish requests the passed peers to publish the passed message
func Publish(msgID []byte, msgLoc, peers string, size uint, timeout int) error {
	msg, err := parseMessageFile(msgLoc)
	if err != nil || msg == nil {
		logger.Errorf("err parsing message file:\n%v", err)
		return err
	}
	logger.Infof("message is %s", msg.String())

	if size != 0 {
		oldSize := msg.XXX_Size()
		if err = sizeMessage(msg, size); err != nil {
			logger.Errorf("err sizing message to %v:\n%v", size, err)
			return err
		}

		logger.Infof("old message size: %v (bytes); new size: %v (bytes)", oldSize, msg.XXX_Size())
	}

	if msgID != nil {
		msg.Id = string(msgID)
	}

	peersArr := parsePeers(peers)
	var failed = false
	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.PublishMessage(ctx, msg)
		if err != nil {
			logger.Errorf("could not publish message to %s:\n %v", peer, err)
			failed = true
			conn.Close()
			cancel()
			continue
		}

		logger.Infof("ok for %s: %v", peer, r.GetSuccess())
		if !r.GetSuccess() {
			failed = true
		}

		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("publish failed")
	}

	return nil
}

// CloseAll requests the passed peers close all peer connections
func CloseAll(peers string, timeout int) error {
	peersArr := parsePeers(peers)
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.CloseAllPeerConnections(ctx, &empty.Empty{})
		if err != nil {
			logger.Errorf("err closing all peer connections for %s:\n%v", peer, err)
			failed = true
			conn.Close()
			cancel()
			continue
		}

		logger.Infof("ok for %s: %v", peer, r.GetSuccess())
		if !r.GetSuccess() {
			failed = true
		}

		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("close all connections failed")
	}

	return nil
}

// ClosePeers requests the passed hosts to close connections to passed peers
func ClosePeers(peers string, closePeers string, timeout int) error {
	peersArr := parsePeers(peers)
	closePeersList := parsePeers(closePeers)
	peersList := &pb.PeersList{
		Peers: closePeersList,
	}
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.ClosePeerConnections(ctx, peersList)
		if err != nil {
			logger.Errorf("err closing all peer connections for %s:\n%v", peer, err)
			failed = true
			conn.Close()
			cancel()
			continue
		}

		logger.Infof("ok for %s: %v", peer, r.GetSuccess())
		if !r.GetSuccess() {
			failed = true
		}

		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("close peer connections failed")
	}

	return nil
}

// OpenPeers requests the passed peers to open connections to passed peers
func OpenPeers(peers string, openPeers string, timeout int) error {
	peersArr := parsePeers(peers)
	openPeersList := parsePeers(openPeers)
	peersList := &pb.PeersList{
		Peers: openPeersList,
	}
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.OpenPeersConnections(ctx, peersList)
		if err != nil {
			logger.Errorf("err opening peer connections for %s to %v:\n%v", peer, openPeers, err)
			failed = true
			conn.Close()
			cancel()
			continue
		}

		for _, peerConn := range r.GetPeerConnections() {
			if !peerConn.GetSuccess() {
				logger.Errorf("peer %v failed to connect to peer %v", peer, peerConn.GetPeer())
				failed = true
			}
		}

		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("open peers failed")
	}

	return nil
}

// ListPeers requests the passed peers to list their connected peers
func ListPeers(peers string, timeout int) error {
	peersArr := parsePeers(peers)
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			return err
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.ListConnectedPeers(ctx, &empty.Empty{})
		if err != nil {
			logger.Errorf("err closing all peer connections for peer %s:\n%v", peer, err)
			conn.Close()
			cancel()
			failed = true
			continue
		}

		for _, connPeers := range r.GetPeers() {
			logger.Infof("peers for %s:\n%v", peer, connPeers)
		}

		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("list peers failed")
	}

	return nil
}

// IDs requests the passed peers to return their IDs
func IDs(peers string, timeout int) error {
	peersArr := parsePeers(peers)
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.ID(ctx, &empty.Empty{})
		if err != nil {
			logger.Errorf("err getting id for %s:\n%v", peer, err)
			conn.Close()
			cancel()
			failed = true
			continue
		}

		logger.Infof("id for %s is %s", peer, r.GetID())
		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("get id failed")
	}

	return nil
}

// Listens requests the listen addresses of the passed peers
func Listens(peers string, timeout int) error {
	peersArr := parsePeers(peers)
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		r, err := c.ListenAddresses(ctx, &empty.Empty{})
		if err != nil {
			logger.Errorf("err getting listens for %s:\n%v", peer, err)
			conn.Close()
			cancel()
			failed = true
			continue
		}

		logger.Infof("listens addresses for %s is %v", peer, r.GetAddresses())
		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("get listens failed")
	}

	return nil
}

// Shutdown requests that past peers be shutdown
func Shutdown(peers string, timeout int) error {
	peersArr := parsePeers(peers)
	var failed = false

	for _, peer := range peersArr {
		// Set up a connection to the server.
		conn, err := grpc.Dial(peer, grpc.WithInsecure())
		if err != nil {
			logger.Errorf("did not connect to %s:\n%v", peer, err)
			failed = true
			continue
		}

		c := pb.NewPublisherClient(conn)

		// Contact the server and print out its response.
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)

		_, err = c.Shutdown(ctx, &empty.Empty{})
		if err != nil {
			logger.Errorf("err shutting down for %s:\n%v", peer, err)
			conn.Close()
			cancel()
			failed = true
			continue
		}

		conn.Close()
		cancel()
	}

	if failed {
		return errors.New("shutting down failed")
	}

	return nil
}
