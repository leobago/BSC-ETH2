package subnet

import (
	"context"
	"crypto/rand"
	"fmt"
	"net"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	hconf "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host/config"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/subnet/config"
	lcrypto "github.com/libp2p/go-libp2p-core/crypto"
)

func buildHosts(ctx context.Context, conf config.Config, pubsubIP, rpcIP net.IP, pubsubNet, rpcNet *net.IPNet, pubsubPorts, rpcPorts [2]int) ([]*host.Host, error) {
	var (
		currPubsubIP   net.IP = pubsubIP
		currRPCIP      net.IP = rpcIP
		currPubsubPort int    = pubsubPorts[0]
		currRPCPort    int    = rpcPorts[0]
		hostConf       hconf.Config
		hosts          []*host.Host
		err            error
	)

	for i := 0; i < conf.Subnet.NumHosts; i++ {
		hostConf, err = buildHostConf(conf, currPubsubIP, currRPCIP, pubsubNet, rpcNet, &currPubsubPort, &currRPCPort, pubsubPorts, rpcPorts)
		if err != nil {
			logger.Errorf("err building host #%d:\n%v", i+1, err)
			return nil, err
		}
		logger.Infof("host conf #%d: %v", i+1, hostConf)

		h, err := host.New(ctx, hostConf)
		if err != nil {
			logger.Errorf("err building host #%d:\n%v", i+1, err)
			return nil, err
		}

		hosts = append(hosts, h)
	}

	return hosts, nil
}

func buildHostConf(conf config.Config, currPubsubIP, currRPCIP net.IP, pubsubNet, rpcNet *net.IPNet, currPubsubPort, currRPCPort *int, pubsubPorts, rpcPorts [2]int) (hconf.Config, error) {
	hostConfig := parseSubnetConfig(conf)

	nextRPCAddress, err := nextRPCAddress(currRPCIP, rpcNet, currRPCPort, rpcPorts)
	if err != nil {
		logger.Errorf("err getting next rpc address:\n%v", err)
		return hostConfig, err
	}
	hostConfig.Host.RPCAddress = nextRPCAddress

	nextListenAddresses, err := nextListenAddresses(conf, currPubsubIP, pubsubNet, currPubsubPort, pubsubPorts)
	if err != nil {
		logger.Errorf("err getting next listen addresses:\n%v", err)
		return hostConfig, err
	}
	hostConfig.Host.Listens = nextListenAddresses

	hostConfig.Host.Priv, _, err = lcrypto.GenerateECDSAKeyPair(rand.Reader)
	if err != nil {
		logger.Errorf("err generating private key:\n%v", err)
		return hostConfig, err
	}

	return hostConfig, nil
}

// note: rpcPorts is []int{minRPCPort, maxRPCPort}, inclusive
// TODO: should probably use a struct so it's more self documenting...
func nextRPCAddress(currRPCIP net.IP, rpcNet *net.IPNet, currRPCPort *int, rpcPorts [2]int) (string, error) {
	if rpcNet == nil {
		return "", ErrNilIPNet
	}
	if currRPCPort == nil {
		return "", ErrNilPort
	}

	var addr string

	if *currRPCPort < rpcPorts[1] {
		addr = fmt.Sprintf("%s:%d", currRPCIP.String(), *currRPCPort)
		*currRPCPort++
		return addr, nil
	}

	// note: currRPCPort is above limit; need to inc ip
	*currRPCPort = rpcPorts[0]
	incIP(currRPCIP)
	if !rpcNet.Contains(currRPCIP) {
		// out of ip addresses given CIDR constraints
		logger.Errorf("ip %s is not in CIDR: %s", currRPCIP.String(), rpcNet.String())
		return "", ErrIPOutOfCIDRRange
	}

	addr = fmt.Sprintf("%s:%d", currRPCIP, *currRPCPort)
	*currRPCPort++
	return addr, nil
}

func nextListenAddresses(conf config.Config, currPubsubIP net.IP, pubsubNet *net.IPNet, currPubsubPort *int, pubsubPorts [2]int) ([]string, error) {
	if pubsubNet == nil {
		return nil, ErrNilIPNet
	}
	if currPubsubPort == nil {
		return nil, ErrNilPort
	}

	var addresses []string

	for _, transport := range conf.Host.Transports {
		var t string
		if transport != "tcp" {
			t = transport
		}

		if *currPubsubPort < pubsubPorts[1] {
			// TODO: fixme; assumes tcp
			addresses = append(addresses, fmt.Sprintf("/ip4/%s/tcp/%d/%s", currPubsubIP.String(), *currPubsubPort, t))
			*currPubsubPort++
			continue
		}

		// note: currRPCPort is above limit; need to inc ip
		*currPubsubPort = pubsubPorts[0]
		incIP(currPubsubIP)
		if !pubsubNet.Contains(currPubsubIP) {
			// out of ip addresses given CIDR constraints
			logger.Errorf("ip %s is not in CIDR: %s", currPubsubIP.String(), pubsubNet.String())
			return nil, ErrIPOutOfCIDRRange
		}

		// TODO: fixme; assumes tcp
		addresses = append(addresses, fmt.Sprintf("/ip4/%s/tcp/%d/%s", currPubsubIP.String(), *currPubsubPort, t))
		*currPubsubPort++
	}

	return addresses, nil
}

func parseSubnetConfig(conf config.Config) hconf.Config {
	var hostConfig hconf.Config

	hostConfig.Host.KeyType = conf.Host.KeyType
	hostConfig.Host.RSABits = conf.Host.RSABits
	hostConfig.Host.Peers = []string{}
	hostConfig.Host.Transports = conf.Host.Transports
	hostConfig.Host.Muxers = conf.Host.Muxers
	hostConfig.Host.Security = conf.Host.Security
	hostConfig.Host.PubsubAlgorithm = conf.Host.PubsubAlgorithm
	hostConfig.Host.OmitRelay = conf.Host.OmitRelay
	hostConfig.Host.OmitConnectionManager = conf.Host.OmitConnectionManager
	hostConfig.Host.OmitNATPortMap = conf.Host.OmitNATPortMap
	hostConfig.Host.OmitRPCServer = conf.Host.OmitRPCServer
	hostConfig.Host.OmitDiscoveryService = conf.Host.OmitDiscoveryService
	hostConfig.Host.OmitBootstrapPeers = conf.Host.OmitBootstrapPeers
	hostConfig.Host.OmitRouting = conf.Host.OmitRouting

	return hostConfig
}

// note: range through IP's from CIDR.
func all(cidr string) ([]net.IP, error) {
	ip, ipnet, err := net.ParseCIDR(cidr)
	if err != nil {
		return nil, err
	}

	var ips []net.IP
	for ip := ip.Mask(ipnet.Mask); ipnet.Contains(ip); incIP(ip) {
		ips = append(ips, ip)
	}

	// remove network address and broadcast address
	lenIPs := len(ips)
	switch {
	case lenIPs < 2:
		return ips, nil

	default:
		return ips[1 : len(ips)-1], nil
	}
}

func incIP(ip net.IP) {
	for j := len(ip) - 1; j >= 0; j-- {
		ip[j]++
		if ip[j] > 0 {
			break
		}
	}
}

func buildPubsubAndRPC(ch chan error, hosts []*host.Host) error {
	for _, h := range hosts {
		// build pubsub
		ps, err := h.BuildPubSub()
		if err != nil || ps == nil {
			logger.Errorf("err building pubsub:\n%v", err)
			return err
		}

		// build rpc
		if err = h.BuildRPC(ch, ps); err != nil {
			logger.Errorf("err building rpc:\n%v", err)
			return err
		}
	}

	return nil
}

func buildDiscovery(hosts []*host.Host) error {
	var err error

	for _, h := range hosts {
		if err = h.BuildDiscoveryAndRouting(); err != nil {
			logger.Errorf("err building router:\n%v", err)
			return err
		}
	}

	return nil
}
