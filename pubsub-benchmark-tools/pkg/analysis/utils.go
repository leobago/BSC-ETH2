package analysis

import (
	"bufio"
	"errors"
	"math"
	"os"
	"strconv"
	"strings"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/analysis/sorter"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/analysis/types"
	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
)

// TODO @adam-hanna: to test
func loadLogFile(logLoc string) (*bufio.Scanner, func() error, error) {
	file, err := os.Open(logLoc)
	if err != nil {
		logger.Errorf("err opening log file at %s:\n%v", logLoc, err)
		return nil, nil, err
	}

	return bufio.NewScanner(file), file.Close, nil
}

// TODO @adam-hanna: to test
func buildMetricsFromScanner(scanner *bufio.Scanner) ([]*types.Metric, error) {
	messageLogs, err := buildMessageLogsFromScanner(scanner)
	if err != nil {
		logger.Errorf("err building message logs:\n%v", err)
		return nil, err
	}

	return buildMetricsFromMessageLogs(messageLogs)
}

// TODO @adam-hanna: to test
func buildMessageLogsFromScanner(scanner *bufio.Scanner) ([]*types.MessageLog, error) {
	var messageLogs []*types.MessageLog

	// note: this may fail for lines longer than 65536 characters. I'm just going to assume we won't encounter that...
	// https://stackoverflow.com/a/16615559/3512709
	for scanner.Scan() {
		// note: is there a way to prevent allocation of these each loop?
		msgLog, err := parseLogLine(scanner.Bytes())
		if err != nil {
			logger.Errorf("err parsing log line %s:\n%v", scanner.Text(), err)
			return nil, err
		}

		// note: if msgLog is nil, then it means this line isn't a relevant log line
		if msgLog == nil {
			continue
		}

		messageLogs = append(messageLogs, msgLog)
	}

	if err := scanner.Err(); err != nil {
		logger.Errorf("scanner error:\n%v", err)
		return nil, err
	}

	return messageLogs, nil
}

// note: nil struct return indicates the line is not relevant
func parseLogLine(logLine []byte) (*types.MessageLog, error) {
	if !strings.Contains(string(logLine), types.LogLineLeader) {
		// note: nil struct indicates this line is not relevant
		return nil, nil
	}

	beginningOfLine := strings.Index(string(logLine), types.LogLineLeader)
	if beginningOfLine == -1 {
		logger.Errorf("could not find log line leader in log line %s", string(logLine))
		return nil, errors.New("log line leader not in line")
	}
	line := string(logLine)[beginningOfLine+len(types.LogLineLeader):]

	endOfData := strings.Index(line, `" `)
	if endOfData != -1 {
		line = line[:endOfData]
	}
	line = strings.TrimSpace(line)

	data := strings.Split(line, ",")
	if len(data) != 6 {
		logger.Errorf("improperly formatted log line %s; expected length == 6, received %d", line, len(data))
		return nil, types.ErrImproperlyFormattedLogLine
	}

	return buildMessageLogFromStrings(data)
}

func buildMetricsFromMessageLogs(messageLogs []*types.MessageLog) ([]*types.Metric, error) {
	messageLogsGroups := groupMessageLogsByID(messageLogs)

	sortMessageLogs(messageLogsGroups)

	return buildMetricsFromSortedMessageLogsGroups(messageLogsGroups)
}

func buildMetricsFromSortedMessageLogsGroups(messageLogsGroups [][]*types.MessageLog) ([]*types.Metric, error) {
	var metrics []*types.Metric
	for _, sortedMessageLogs := range messageLogsGroups {
		metric, err := buildMetricsFromSortedMessageLogs(sortedMessageLogs)
		if err != nil {
			logger.Errorf("err building metrics:\n%v", err)
			continue
			//return nil, err
		}

		metrics = append(metrics, metric)
	}

	return metrics, nil
}

func buildMetricsFromSortedMessageLogs(sortedMessageLogs []*types.MessageLog) (*types.Metric, error) {
	var (
		metric types.Metric
		err    error
	)

	if len(sortedMessageLogs) == 0 {
		return nil, errors.New("no message logs")
	}

	metric.MessageID = sortedMessageLogs[0].MessageID
	metric.OriginatorHostID = sortedMessageLogs[0].SenderID

	metric.TotalNanoTime, err = calcTotalNanoTime(sortedMessageLogs)
	if err != nil {
		logger.Errorf("err calculating nano time fro msg %s:\n%v", metric.MessageID, err)
		return nil, err
	}

	metric.RelativeMessageRedundancy, metric.TotalHostCount, err = calcRMRAndTotalCount(sortedMessageLogs)
	if err != nil {
		logger.Errorf("err calculating rmr for msg %s:\n%v", metric.MessageID, err)
		return nil, err
	}

	metric.LastDeliveryHop = calcLastDeliveryHop(sortedMessageLogs)

	return &metric, nil
}

func calcTotalNanoTime(sortedMessageLogs []*types.MessageLog) (uint64, error) {
	if sortedMessageLogs[len(sortedMessageLogs)-1].NanoTime < sortedMessageLogs[0].NanoTime {
		return 0, errors.New("message logs are not sorted ascending")
	}

	return uint64(sortedMessageLogs[len(sortedMessageLogs)-1].NanoTime - sortedMessageLogs[0].NanoTime), nil
}

func calcRMRAndTotalCount(sortedMessageLogs []*types.MessageLog) (float32, uint, error) {
	uniqueHosts := countUniqueHosts(sortedMessageLogs)
	if uniqueHosts == 0 || uniqueHosts == 1 {
		return 0.0, 0, errors.New("cannot calculate RMR with none or one host")
	}

	return (float32(len(sortedMessageLogs)) / (float32(uniqueHosts - 1))) - 1.0, uniqueHosts, nil
}

func calcLastDeliveryHop(sortedMessageLogs []*types.MessageLog) uint {
	// note: map is senderID => recipientID
	// note: assumes a host only ever sends a message to a recipient once!
	// TODO: put this into a seprate function for easier unit testing
	m := make(map[string]map[string][]*types.MessageLog)
	for _, msg := range sortedMessageLogs {
		if _, ok := m[msg.SenderID]; !ok {
			m[msg.SenderID] = make(map[string][]*types.MessageLog)
		}

		m[msg.SenderID][msg.HostID] = append(m[msg.SenderID][msg.HostID], msg)
	}

	// note: array length has already been checked, previously so this shouldn't panic... I hope :D
	firstGossiperID := sortedMessageLogs[0].SenderID
	firstGossipTime := sortedMessageLogs[0].NanoTime

	// note: this assumes that a host never receives a message that it doesn't already have
	paths := buildPathsForSenderID(firstGossiperID, firstGossiperID, firstGossipTime, m)

	// find the longest path
	lastDeliveryHop := 0.0
	for _, path := range paths {
		lastDeliveryHop = math.Max(lastDeliveryHop, float64(len(path))-1.0)
	}

	return uint(lastDeliveryHop)
}

// note: map is senderID => recipientID
// note: return is a chain of recipient IDs starting with the original senderID
func buildPathsForSenderID(senderID, originalSender string, ts int64, m map[string]map[string][]*types.MessageLog) [][]string {
	var ret [][]string

	for recipient, msgs := range m[senderID] {
		if recipient == originalSender {
			continue
		}

		var tmpTs int64
		for _, msg := range msgs {
			if msg.NanoTime < ts {
				continue
			}

			tmpTs = msg.NanoTime
			paths := buildPathsForSenderID(recipient, originalSender, tmpTs, m)
			for _, path := range paths {
				path = prependString(senderID, path)
				ret = append(ret, path)
			}

			if len(paths) == 0 {
				ret = append(ret, []string{senderID, recipient})
			}
		}
	}

	return ret
}

func prependString(s string, arr []string) []string {
	return append([]string{s}, arr...)
}

func countUniqueHosts(sortedMessageLogs []*types.MessageLog) uint {
	m := make(map[string]struct{})
	for _, msg := range sortedMessageLogs {
		m[msg.HostID] = struct{}{}
		m[msg.SenderID] = struct{}{}
	}

	return uint(len(m))
}

func groupMessageLogsByID(messageLogs []*types.MessageLog) [][]*types.MessageLog {
	var messageLogGroups [][]*types.MessageLog
	messageLogMap := make(map[string][]*types.MessageLog)

	for _, messageLog := range messageLogs {
		messageLogMap[messageLog.MessageID] = append(messageLogMap[messageLog.MessageID], messageLog)
	}

	for _, messageLogGroup := range messageLogMap {
		messageLogGroups = append(messageLogGroups, messageLogGroup)
	}

	return messageLogGroups
}

func sortMessageLogs(messageLogsGroups [][]*types.MessageLog) {
	// Closures that order the messageLog structure.
	unixNanoTimestamp := func(m1, m2 *types.MessageLog) bool {
		return m1.NanoTime < m2.NanoTime
	}

	for _, messageLogs := range messageLogsGroups {
		sorter.By(unixNanoTimestamp).Sort(messageLogs)
	}
}

func buildMessageLogFromStrings(data []string) (*types.MessageLog, error) {
	// note: have already checked data length
	seqNo, err := strconv.ParseUint(data[3], 10, 64)
	if err != nil {
		logger.Errorf("expected seqNo typeof Uint64 but got %s", data[3])
		return nil, types.ErrImproperlyFormattedLogLine
	}

	unixNano, err := strconv.ParseInt(data[4], 10, 64)
	if err != nil {
		logger.Errorf("expected unixNano typeof Int64 but got %s", data[4])
		return nil, types.ErrImproperlyFormattedLogLine
	}

	seq, err := strconv.Atoi(data[5])
	if err != nil {
		logger.Errorf("expected seq typeof Int32 but got %s", data[5])
		return nil, types.ErrImproperlyFormattedLogLine
	}

	return &types.MessageLog{
		HostID:    data[0],
		SenderID:  data[1],
		MessageID: data[2],
		SeqNo:     seqNo,
		NanoTime:  unixNano,
		Seq:       seq,
	}, nil
}
