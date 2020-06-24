package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/orchestra"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/orchestra/config"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

func setup() *cobra.Command {
	var (
		confLoc, msgLoc, loggerLoc string
	)

	rootCmd := &cobra.Command{
		Use:   "start",
		Short: "Orchestrate a test run of clients and optionally a subnet",
		Long:  `Spins up clients and optionally a subnet and sends the hosts messages at the specified interval.`,
		RunE: func(cmd *cobra.Command, args []string) error {
			if err := logger.Set(logger.ContextHook{}, loggerLoc, true, false); err != nil {
				logrus.Errorf("err initiating logger:\n%v", err)
				return err
			}

			logger.Infof("Loading config: %s", confLoc)
			conf, err := config.Load(confLoc)
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

			// capture the ctrl+c signal
			stop := make(chan os.Signal, 1)
			signal.Notify(stop, syscall.SIGINT)

			// create a context
			ctx, cancel := context.WithCancel(context.Background())
			defer cancel()

			orch, err := orchestra.New(orchestra.Props{
				Conf: conf,
				CTX:  ctx,
			})
			if err != nil {
				logger.Errorf("err building new test orchestra:\n%v", err)
				return err
			}

			if err = orch.Orchestrate(stop); err != nil {
				logger.Errorf("err running test orchestration:\n%v", err)
				return err
			}

			return nil
		},
	}

	rootCmd.PersistentFlags().StringVarP(&confLoc, "config", "c", "configs/orchestra/config.json", "The configuration file.")
	rootCmd.PersistentFlags().StringVarP(&loggerLoc, "log", "", "", "Log file location. Defaults to standard out.")
	rootCmd.Flags().StringVarP(&msgLoc, "message", "m", "client.message.json", "The message file to send to peers.")

	return rootCmd
}

func main() {
	rootCmd := setup()

	if err := rootCmd.Execute(); err != nil {
		logrus.Fatalf("err executing command\n%v", err)
	}

	logger.Info("done")
}
