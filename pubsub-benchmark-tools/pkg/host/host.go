package host

import (
	"context"
	"crypto/rand"
	"fmt"
	"os"
	"strings"
	"time"

	rpcHost "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/grpc/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host/config"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"

	ipfsaddr "github.com/ipfs/go-ipfs-addr"
	"github.com/libp2p/go-libp2p"
	connmgr "github.com/libp2p/go-libp2p-connmgr"
	lcrypto "github.com/libp2p/go-libp2p-core/crypto"
	"github.com/libp2p/go-libp2p-core/host"
	"github.com/libp2p/go-libp2p-core/peer"
	"github.com/libp2p/go-libp2p-core/routing"
	kaddht "github.com/libp2p/go-libp2p-kad-dht"
	peerstore "github.com/libp2p/go-libp2p-peerstore"
	pubsub "github.com/libp2p/go-libp2p-pubsub"
	lconfig "github.com/libp2p/go-libp2p/config"
	"github.com/libp2p/go-libp2p/p2p/discovery"
)

type mdnsNotifee struct {
	h   host.Host
	ctx context.Context
}

// HandlePeerFound...
func (m *mdnsNotifee) HandlePeerFound(pi peer.AddrInfo) {
	if err := m.h.Connect(m.ctx, pi); err != nil {
		logger.Warnf("mdns err connecting to peer with id %v:\n%v", pi.ID, err)
	}
}

// New returns a new host
// note: not passing reference to config because want it to be read only.
func New(ctx context.Context, conf config.Config) (*Host, error) {
	h := &Host{
		ctx:    ctx,
		conf:   conf,
		shtDwn: make(chan struct{}),
	}

	var lOpts []lconfig.Option

	// add private key
	if conf.Host.Priv == nil {
		var (
			priv lcrypto.PrivKey
			err  error
		)

		switch strings.ToLower(conf.Host.KeyType) {
		case "ecdsa":
			logger.Info("host priv key type is ECDSA")
			priv, _, err = lcrypto.GenerateECDSAKeyPair(rand.Reader)

		case "ed255199":
			logger.Info("host priv key type is Ed25519")
			priv, _, err = lcrypto.GenerateEd25519Key(rand.Reader)

		case "rsa":
			logger.Infof("host priv key type is RSA with %d bits", conf.Host.RSABits)
			priv, _, err = lcrypto.GenerateRSAKeyPair(conf.Host.RSABits, rand.Reader)

		case "secp256k1":
			logger.Info("host priv key type is Secp256k1")
			priv, _, err = lcrypto.GenerateSecp256k1Key(rand.Reader)

		default:
			logger.Errorf("%s is not a supported private key type", conf.Host.KeyType)
			err = config.ErrUnsupportedKeyType
		}

		if err != nil {
			logger.Errorf("err generating private key:\n%v", err)
			return nil, err
		}

		lOpts = append(lOpts, libp2p.Identity(priv))
	} else {
		lOpts = append(lOpts, libp2p.Identity(conf.Host.Priv))
	}

	// create transports
	transports, err := parseTransportOptions(conf.Host.Transports)
	if err != nil {
		logger.Errorf("err parsing transports\n%v", err)
		return nil, err
	}
	lOpts = append(lOpts, transports)

	// create muxers
	muxers, err := parseMuxerOptions(conf.Host.Muxers)
	if err != nil {
		logger.Errorf("err parsing muxers\n%v", err)
		return nil, err
	}
	lOpts = append(lOpts, muxers)

	// create security
	security, err := parseSecurityOptions(conf.Host.Security)
	if err != nil {
		logger.Errorf("err parsing security\n%v", err)
		return nil, err
	}
	lOpts = append(lOpts, security)

	// add listen addresses
	if len(conf.Host.Listens) > 0 {
		lOpts = append(lOpts, libp2p.ListenAddrStrings(conf.Host.Listens...))
	}

	// Conn manager
	if !conf.Host.OmitConnectionManager {
		cm := connmgr.NewConnManager(256, 512, 120)
		lOpts = append(lOpts, libp2p.ConnectionManager(cm))
	}

	// NAT port map
	if !conf.Host.OmitNATPortMap {
		lOpts = append(lOpts, libp2p.NATPortMap())
	}

	// create router
	if !conf.Host.OmitRouting {
		newDHT := func(hst host.Host) (routing.PeerRouting, error) {
			var err error
			dht, err := kaddht.New(ctx, hst)
			if err != nil {
				logger.Errorf("err creating new kaddht\n%v", err)
			}

			h.router = dht

			return dht, err
		}
		routing := libp2p.Routing(newDHT)
		lOpts = append(lOpts, routing)
	}

	if conf.Host.OmitRelay {
		lOpts = append(lOpts, libp2p.DisableRelay())
	}

	// build the libp2p host
	host, err := libp2p.New(ctx, lOpts...)
	if err != nil {
		logger.Errorf("err creating new libp2p host\n%v", err)
		return nil, err
	}
	h.host = host

	return h, nil
}

// ID returns the host's id
func (h *Host) ID() string {
	return h.host.ID().Pretty()
}

// Addresses returns the listening addresses of the host
func (h *Host) Addresses() []string {
	var addresses []string
	for _, addr := range h.host.Addrs() {
		addresses = append(addresses, fmt.Sprintf("%s", addr))
	}

	return addresses
}

// IPFSAddresses returns the ipfs listening addresses of the host
func (h *Host) IPFSAddresses() []string {
	var addresses []string
	for _, addr := range h.host.Addrs() {
		addresses = append(addresses, fmt.Sprintf("%s/ipfs/%s", addr, h.host.ID().Pretty()))
	}

	return addresses
}

// RPCAddress returns the host rpc address
func (h *Host) RPCAddress() string {
	return h.conf.Host.RPCAddress
}

// Connect connects the host to the list of peers
// note: it expects the peers to be in IPFS form
func (h *Host) Connect(peers []string) error {
	for _, p := range peers {
		addr, err := ipfsaddr.ParseString(p)
		if err != nil || addr == nil {
			logger.Errorf("err parsing peer: %s\n%v", p, err)
			return err
		}

		pinfo, err := peerstore.InfoFromP2pAddr(addr.Multiaddr())
		if err != nil || pinfo == nil {
			logger.Errorf("err getting info from peerstore\n%v", err)
			return err
		}

		logger.Infof("full peer addr: %s", addr.String())
		logger.Infof("peer info: %v", pinfo)

		if err := h.host.Connect(h.ctx, *pinfo); err != nil {
			logger.Errorf("connecting to peer failed\n%v", err)
			return err
		}

		logger.Infof("Connected to peer: %v", pinfo.ID)
	}

	return nil
}

// BuildPubSub returns a pubsub service
func (h *Host) BuildPubSub() (*pubsub.PubSub, error) {
	var (
		ps  *pubsub.PubSub
		err error
	)

	// build the gossip pub/sub
	switch strings.ToLower(h.conf.Host.PubsubAlgorithm) {
	case "gossip":
		logger.Info("building gossip pubsub")
		ps, err = pubsub.NewGossipSub(h.ctx, h.host)

	case "flood":
		logger.Info("building flood pubsub")
		ps, err = pubsub.NewFloodSub(h.ctx, h.host)

	case "random":
		logger.Info("building random pubsub")
		ps, err = pubsub.NewRandomSub(h.ctx, h.host)

	default:
		logger.Errorf("err, the pubsub algorithm %s is not recognized", h.conf.Host.PubsubAlgorithm)
		return nil, ErrUnknownPubsubAlgorithm
	}
	if err != nil {
		logger.Errorf("err creating new pub sub\n%v", err)
		return nil, err
	}

	// subscribe to the topic
	_, err = ps.Subscribe(pubsubTopic)
	if err != nil {
		logger.Errorf("err subscribing\n%v", err)
		return nil, err
	}

	if err = ps.RegisterTopicValidator(pubsubTopic, buildValidator(h.host.ID())); err != nil {
		logger.Errorf("err registering valudator:\n%v", err)
		return nil, err
	}

	return ps, nil
}

// BuildRPC returns an rpc service
func (h *Host) BuildRPC(ch chan error, ps *pubsub.PubSub) error {
	// Start the RPC server
	rHost := rpcHost.New(&rpcHost.Props{
		Host:        h.host,
		CH:          ch,
		PS:          ps,
		PubsubTopic: pubsubTopic,
		CTX:         h.ctx,
		Shutdown:    h.shtDwn,
	})
	go func(rh *rpcHost.Host, c chan error) {
		if err := rh.Listen(h.ctx, h.conf.Host.RPCAddress); err != nil {
			logger.Errorf("err listening on rpc:\n%v", err)
			c <- err
		}
	}(rHost, ch)

	return nil
}

// BuildDiscoveryAndRouting ...
func (h *Host) BuildDiscoveryAndRouting() error {
	// create discovery service
	if !h.conf.Host.OmitDiscoveryService {
		mdns, err := discovery.NewMdnsService(h.ctx, h.host, time.Second*10, "")
		if err != nil {
			logger.Errorf("err discovering\n%v", err)
			return err
		}
		mdns.RegisterNotifee(&mdnsNotifee{h: h.host, ctx: h.ctx})
	}

	if !h.conf.Host.OmitRouting {
		if h.router == nil {
			return ErrNilRouter
		}

		if err := h.router.Bootstrap(h.ctx); err != nil {
			logger.Errorf("err bootstrapping\n%v", err)
			return err
		}
	}

	return nil
}

// Start starts a new pubsub host
func (h *Host) Start(ch chan error, stop chan os.Signal) error {
	for i, addr := range h.host.Addrs() {
		logger.Infof("listening #%d on: %s/ipfs/%s\n", i, addr, h.host.ID().Pretty())
	}
	defer func() {
		if err := h.host.Close(); err != nil {
			logger.Errorf("err closing host:\n%v", err)
		}
	}()

	select {
	case <-stop:
		// note: I don't like '^C' showing up on the same line as the next logged line...
		fmt.Println("")
		logger.Info("Received stop signal from os. Shutting down...")

	case <-h.shtDwn:
		logger.Info("received shutdown signal on rpc")

	case err := <-ch:
		logger.Errorf("received err on rpc channel:\n%v", err)
		return err

	case <-h.ctx.Done():
		if err := h.ctx.Err(); err != nil {
			logger.Errorf("err on the context:\n%v", err)
			return err
		}
	}

	return nil
}
