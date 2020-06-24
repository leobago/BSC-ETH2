package logger

import (
	"os"

	"github.com/sirupsen/logrus"
)

// Fatalf ...
func Fatalf(s string, i ...interface{}) {
	logrus.Fatalf(s, i...)
}

// Fatal ...
func Fatal(s string) {
	logrus.Fatal(s)
}

// Errorf ...
func Errorf(s string, i ...interface{}) {
	logrus.Errorf(s, i...)
}

// Error ...
func Error(s string) {
	logrus.Errorf(s)
}

// Infof ...
func Infof(s string, i ...interface{}) {
	logrus.Infof(s, i...)
}

// Info ...
func Info(s string) {
	logrus.Infof(s)
}

// Printf ...
func Printf(s string, i ...interface{}) {
	logrus.Infof(s, i...)
}

// Print ...
func Print(s string) {
	logrus.Infof(s)
}

// Println ...
func Println(i ...interface{}) {
	logrus.Infoln(i...)
}

// Warnf ...
func Warnf(s string, i ...interface{}) {
	logrus.Warnf(s, i...)
}

// Warn ...
func Warn(s string) {
	logrus.Warnf(s)
}

// Set modifies the logger
func Set(hook ContextHook, fileLoc string, debug bool, setReport bool) error {
	logrus.SetReportCaller(setReport)
	if !debug {
		logrus.SetLevel(logrus.WarnLevel)
	}
	logrus.AddHook(hook)
	if fileLoc != "" {
		// note: need to pass back some way to file.Close()?
		file, err := os.OpenFile(fileLoc, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
		if err != nil {
			logrus.Errorf("err opening file %s:\n%v", fileLoc, err)
			return err
		}

		// note: writing to this from multiple writers is threadsafe?
		// https://stackoverflow.com/a/29981337/3512709
		logrus.SetOutput(file)
	}

	return nil
}

// SetLoggerLoc sets the file location of the logger
func SetLoggerLoc(loc string) error {
	if loc != "" {
		// note: need to pass back some way to file.Close()?
		file, err := os.OpenFile(loc, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
		if err != nil {
			logrus.Errorf("err opening file %s:\n%v", loc, err)
			return err
		}

		// note: threadsafe?
		// https://stackoverflow.com/a/29981337/3512709
		logrus.SetOutput(file)
	}

	return nil
}

// SetLoggerLevel sets the logger level
func SetLoggerLevel(debug bool) {
	logrus.Info("setting log level to warn")
	if !debug {
		logrus.SetLevel(logrus.WarnLevel)
	}
}
