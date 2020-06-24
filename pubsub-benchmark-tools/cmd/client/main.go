package main

import (
	"os"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/client"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

func setup() (*cobra.Command, error) {
	var (
		msgLoc, peers, loggerLoc string
		timeout                  int
		size                     uint
	)

	rootCmd := &cobra.Command{Use: "client"}

	publishCMD := &cobra.Command{
		Use:   "publish",
		Short: "Publish a message in the pubsub",
		Long:  "Request that the passed hosts publish the passed message",
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("sending message to peers for publish")
			if err := client.Publish(nil, msgLoc, peers, size, timeout); err != nil {
				logger.Fatalf("err sending messages\n%v", err)
			}
		},
	}
	publishCMD.Flags().StringVarP(&msgLoc, "message", "m", "client.message.json", "The message file to send to peers.")
	publishCMD.Flags().UintVarP(&size, "size", "s", 0, "Dynamically size the message (in bytes). Zero, or not passed will default to the size in the json.")

	closeAllPeerConnectionsCMD := &cobra.Command{
		Use:   "close-all",
		Short: "Close all peer connections",
		Long:  "Request the host to close all connected peer connections",
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting host(s) to close all connected peer connections")
			if err := client.CloseAll(peers, timeout); err != nil {
				logger.Fatalf("err closing all peer connections\n%v", err)
			}
		},
	}

	closePeerConnectionsCMD := &cobra.Command{
		Use:   "close-peers [peers to close (csv)]",
		Short: "Close connections to peers",
		Long:  "Request the host(s) to close connections to passed peers",
		Args:  cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting host(s) to close connections to passed peers")
			if err := client.ClosePeers(peers, args[0], timeout); err != nil {
				logger.Fatalf("err closing peer connections\n%v", err)
			}
		},
	}

	openPeersConnectionsCMD := &cobra.Command{
		Use:   "open-peers [peers to open (csv)]",
		Short: "Open connections to peers",
		Long:  "Request the host(s) to open connections to passed peers",
		Args:  cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting host(s) to open connections to passed peers")
			if err := client.OpenPeers(peers, args[0], timeout); err != nil {
				logger.Fatalf("err openning peer connections\n%v", err)
			}
		},
	}

	listConnectedPeersCMD := &cobra.Command{
		Use:   "list-peers",
		Short: "List connected peers",
		Long:  "Ask the host(s) to which peers it is connected",
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting list of connected peers")
			if err := client.ListPeers(peers, timeout); err != nil {
				logger.Fatalf("err listing peers\n%v", err)
			}
		},
	}

	idCMD := &cobra.Command{
		Use:   "id",
		Short: "Get peer ids",
		Long:  "Ask the host(s) for their peer ids",
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting peer ids")
			if err := client.IDs(peers, timeout); err != nil {
				logger.Fatalf("err getting ids\n%v", err)
			}
		},
	}

	shutdownCMD := &cobra.Command{
		Use:   "shutdown",
		Short: "Shutsdown the host(s)",
		Long:  "Ask the host(s) to shutdown",
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting shutdown")
			if err := client.Shutdown(peers, timeout); err != nil {
				logger.Fatalf("err shutting down\n%v", err)
			}
		},
	}

	listenAddressesCMD := &cobra.Command{
		Use:   "listens",
		Short: "Get listen addresses",
		Long:  "Ask the host(s) for their listen addresses",
		Run: func(cmd *cobra.Command, args []string) {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Fatalf("err initiating logger:\n%v", err)
			}

			logger.Infof("requesting listen addresses")
			if err := client.Listens(peers, timeout); err != nil {
				logger.Fatalf("err getting listen addresses\n%v", err)
			}
		},
	}

	rootCmd.AddCommand(
		publishCMD,
		closeAllPeerConnectionsCMD,
		closePeerConnectionsCMD,
		openPeersConnectionsCMD,
		listConnectedPeersCMD,
		idCMD,
		listenAddressesCMD,
		shutdownCMD,
	)
	rootCmd.PersistentFlags().StringVarP(&peers, "peers", "p", ":8080", "Peers to connect. Comma separated.")
	rootCmd.PersistentFlags().IntVarP(&timeout, "timeout", "t", 20, "Timeout, in seconds")
	rootCmd.PersistentFlags().StringVarP(&loggerLoc, "log", "", "", "Log file location. Defaults to standard out.")

	return rootCmd, nil
}

func main() {
	rootCmd, err := setup()
	if err != nil {
		logrus.Fatal(err)
	}

	if err := rootCmd.Execute(); err != nil {
		logger.Errorf("err executing command\n%v", err)
		os.Exit(1)
	}
}
