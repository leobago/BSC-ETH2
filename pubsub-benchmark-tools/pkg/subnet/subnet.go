package subnet

import (
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/peertopology"
)

// New returns a subnet
func New(props *Props) (*Subnet, error) {
	return &Subnet{
		props: props,
	}, nil
}

// Start begins the subnet
func (s *Subnet) Start(started chan struct{}) error {
	// parse pubsub cidr
	pubsubIP, pubsubNet, err := net.ParseCIDR(s.props.Conf.Subnet.PubsubCIDR)
	if err != nil {
		logger.Errorf("err parsing pubsub CIDRs %s:\n%v", s.props.Conf.Subnet.PubsubCIDR, err)
		return err
	}

	// parse RPC cidr
	rpcIP, rpcNet, err := net.ParseCIDR(s.props.Conf.Subnet.RPCCIDR)
	if err != nil {
		logger.Errorf("err parsing rpc CIDRs %s:\n%v", s.props.Conf.Subnet.RPCCIDR, err)
		return err
	}

	// build hosts
	hosts, err := buildHosts(s.props.CTX, s.props.Conf, pubsubIP, rpcIP, pubsubNet, rpcNet, s.props.Conf.Subnet.PubsubPortRange, s.props.Conf.Subnet.RPCPortRange)
	if err != nil {
		logger.Errorf("err bulding hosts:\n%v", err)
		return err
	}
	s.hosts = hosts

	// build the host pubsubs and rpc
	ch := make(chan error)
	if err = buildPubsubAndRPC(ch, hosts); err != nil {
		logger.Errorf("err bulding pubsub and rpc:\n%v", err)
		return err
	}

	// build network topology
	if err = peertopology.ConnectPeersForTopology(s.props.Conf.Subnet.PeerTopology, hosts); err != nil {
		logger.Errorf("err building topology for %s:\n%v", s.props.Conf.Subnet.PeerTopology, err)
		return err
	}

	// build router/discover
	if err = buildDiscovery(hosts); err != nil {
		logger.Errorf("err building discovery:\n%v", err)
		return err
	}

	// capture the ctrl+c signal
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT)

	for _, h := range hosts {
		// TODO: need to add ready signal when host has started
		go func(ch chan error, stop chan os.Signal, hst *host.Host) {
			if err = hst.Start(ch, stop); err != nil {
				logger.Errorf("host id %s err:\n%v", hst.ID(), err)
			}
		}(ch, stop, h)
	}

	started <- struct{}{}
	select {
	case <-stop:
		// note: I don't like '^C' showing up on the same line as the next logged line...
		fmt.Println("")
		logger.Info("Received stop signal from os. Shutting down...")

	case err := <-ch:
		logger.Errorf("received err on rpc channel:\n%v", err)
		return err

	case <-s.props.CTX.Done():
		if err := s.props.CTX.Err(); err != nil {
			logger.Errorf("err on the context:\n%v", err)
			return err
		}
	}

	return nil
}

// Addresses returns the host addresses
func (s *Subnet) Addresses() []string {
	var addresses []string

	for _, host := range s.hosts {
		addresses = append(addresses, host.IPFSAddresses()...)
	}

	return addresses
}

// RPCAddresses returns the host rpc addresses
func (s *Subnet) RPCAddresses() []string {
	var addresses []string

	for _, host := range s.hosts {
		addresses = append(addresses, host.RPCAddress())
	}

	return addresses
}
