package main

import (
	"encoding/json"
	"os"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/analysis"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

func setup() *cobra.Command {
	var (
		out string
	)

	rootCmd := &cobra.Command{
		Use:   "analyze [log file]",
		Short: "Analyze a log file",
		Long:  `Analyzes a log file and outputs the metrics to standard out or the specified output json file`,
		Args:  cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			var (
				f   *os.File
				err error
			)

			// set the logger
			if err := logger.Set(logger.ContextHook{}, "", true, false); err != nil {
				logrus.Errorf("err initiating logger:\n%v", err)
				return err
			}

			// get the output ready if writing to file
			if out != "" {
				f, err = os.OpenFile(out, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
				if err != nil {
					logger.Errorf("err creating file at %s:\n%v", out, err)
					return err
				}
				defer f.Close()
			}

			// run the analyzer
			logger.Infof("analyzing log file at %s", args[0])
			metrics, err := analysis.Analyze(args[0])
			if err != nil {
				logger.Errorf("err analyzing log file %s:\n%v", args[1], err)
				return err
			}

			// json marshal the metrics and print
			js, err := json.MarshalIndent(metrics, "", "\t")
			if err != nil {
				logger.Errorf("err marshalling metric json:\n%v", err)
				return err
			}
			if out == "" {
				logger.Info(string(js))
			} else {
				logger.Infof("writing results to %s", out)
				_, err = f.Write(js)
				if err != nil {
					logger.Errorf("err writing result to file at %s:\n%v", out, err)
					return err
				}
			}

			return nil
		},
	}

	rootCmd.PersistentFlags().StringVarP(&out, "out", "o", "", "Output json location. Defaults to standard out.")

	return rootCmd
}

func main() {
	rootCmd := setup()

	if err := rootCmd.Execute(); err != nil {
		logrus.Fatalf("err executing command\n%v", err)
	}

	logger.Info("done")
}
