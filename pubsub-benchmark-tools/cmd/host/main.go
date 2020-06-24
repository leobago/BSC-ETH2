package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/host/config"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

func setup() *cobra.Command {
	var (
		confLoc, listens, rpcListen, peers, loggerLoc, pemLoc string
	)

	rootCmd := &cobra.Command{
		Use:   "start",
		Short: "Start node",
		Long:  `Starts the go-libp2p pub/sub host`,
		RunE: func(cmd *cobra.Command, args []string) error {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Errorf("err initiating logger:\n%v", err)
				return err
			}

			logger.Infof("Loading config: %s", confLoc)
			conf, err := config.Load(confLoc, listens, rpcListen, peers, pemLoc)
			if err != nil {
				logger.Errorf("error loading config\n%v", err)
				return err
			}
			logger.Infof("Loaded configuration. Starting host.\n%v", conf)

			// check the logger location in the conf file
			if conf.General.LoggerLocation != "" {
				switch loggerLoc {
				case conf.General.LoggerLocation:
					break

				case "":
					logger.Warnf("logs will now be written to %s", conf.General.LoggerLocation)
					if err = logger.SetLoggerLoc(conf.General.LoggerLocation); err != nil {
						logger.Errorf("err setting log location to %s:\n%v", conf.General.LoggerLocation, err)
						return err
					}

					break

				default:
					logger.Warnf("log location confliction between flag (%s) and config file (%s); defering to flag (%s)", loggerLoc, conf.General.LoggerLocation, loggerLoc)
				}
			}

			logger.SetLoggerLevel(conf.General.Debug)

			// create a context
			ctx, cancel := context.WithCancel(context.Background())
			defer cancel()

			// create the host
			h, err := host.New(ctx, conf)
			if err != nil {
				logger.Errorf("err creating new host:\n%v", err)
				return err
			}

			// build pubsub
			ps, err := h.BuildPubSub()
			if err != nil || ps == nil {
				logger.Errorf("err building pubsub:\n%v", err)
				return err
			}

			// build rpc
			ch := make(chan error)
			if err = h.BuildRPC(ch, ps); err != nil {
				logger.Errorf("err building rpc:\n%v", err)
				return err
			}

			// connect to peers
			if err = h.Connect(conf.Host.Peers); err != nil {
				logger.Errorf("err connecting to peers:\n%v", err)
				return err
			}

			// add the router
			if err = h.BuildDiscoveryAndRouting(); err != nil {
				logger.Errorf("err building router:\n%v", err)
				return err
			}

			// capture the ctrl+c signal
			stop := make(chan os.Signal, 1)
			signal.Notify(stop, syscall.SIGINT)

			// start the server
			// note: this is blocking
			if err = h.Start(ch, stop); err != nil {
				logger.Errorf("err starting host\n%v", err)
				return err
			}

			return nil
		},
	}

	rootCmd.PersistentFlags().StringVarP(&confLoc, "config", "c", "configs/host/config.json", "The configuration file.")
	rootCmd.PersistentFlags().StringVarP(&listens, "listens", "l", "", "Addresses on which to listen. Comma separated. Overides config.json.")
	rootCmd.PersistentFlags().StringVarP(&peers, "peers", "p", "", "Peers to connect. Comma separated. Overides config.json.")
	rootCmd.PersistentFlags().StringVarP(&rpcListen, "rpc-listen", "r", "", "RPC listen address. Overides config.json.")
	rootCmd.PersistentFlags().StringVarP(&loggerLoc, "log", "", "", "Log file location. Defaults to standard out.")
	rootCmd.PersistentFlags().StringVarP(&pemLoc, "pem", "", "", "PEM file location. Overrides the config.json.")

	return rootCmd
}

func main() {
	rootCmd := setup()

	if err := rootCmd.Execute(); err != nil {
		logrus.Fatalf("err executing command\n%v", err)
	}

	logger.Info("done")
}
