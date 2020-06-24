package types

import "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/cerr"

const (
	// ErrImproperlyFormattedLogLine is returned when the log line is not in the expected format
	ErrImproperlyFormattedLogLine = cerr.Error("improperly formated log line")
	// LogLineLeader is the first string in the relevant log line
	LogLineLeader string = "Pubsub message received: "
)

// Metric contains performance metrics
// These metrics were taken from the research paper:
// Leito, J., Pereira, J., Rodrigues, L.: Epidemic broadcast trees. In: Proceedings of the
// 26th IEEE International Symposium on Reliable Distributed Systems (SRDS’2007),
// Beijing, China (2007) 301 – 310
// https://drive.google.com/file/d/1_evRQujY28K7LBqhuiefiml3QgmWafe-/view
type Metric struct {
	// MessageID is the message id associated with this metric
	MessageID string `json:"messageID,omitempty"`
	// OriginatorHostID is the firsth host who received the message
	OriginatorHostID string `json:"originatorHostID,omitempty"`
	// TotalNanoTime is the time (in nano seconds) for the message to propagate the network
	TotalNanoTime uint64 `json:"totalNanoTime,omitempty"`
	// LastDeliveryHop is the hop count of the last message that is delivered by a gossip protocol or,\
	// in other words, is the maximum number of hops that a message must be forwarded in the overlay before it is delivered.
	LastDeliveryHop uint `json:"lastDeliveryHop,omitempty"`
	// Reliability is defined as the percentage of active nodes that deliver a gossip broadcast.\
	// A reliability of 100% (i.e. 1.0) means that the protocol was able to deliver a given message to all active nodes or, in other \
	// words, that the message resulted in an atomic broadcast
	// note: how to calculate this???
	//Reliability float32
	// RelativeMessageRedundancy (RMR) this metric measures the messages overhead in a gossip protocol. It is defined as: \
	// (m / (n - 1)) - 1. where m is the total number of payload messages exchanged during the broadcast procedure and n is the total \
	// number of nodes that received that broadcast. This metric is only applicable when at least 2 nodes receive the \
	// message.
	//
	// A RMR value of zero means that there is exactly one payload message exchange for each node in the system, \
	// which is clearly the optimal value. By opposition, high values of RMR are indicative of a broadcast strategy that \
	// promotes a poor network usage. Note that it is possible to achieve a very low RMR by failing to be reliable. Thus \
	// the aim is to combine low RMR values with high reliability. Furthermore, RMR values are only comparable for \
	// protocols that exhibit similar reliability. Finally, note that in pure gossip approaches, RMR is closely related with \
	// the protocol fanout, as it tends to fanout−1.
	RelativeMessageRedundancy float32 `json:"relativeMessageRedundancy,omitempty"`
	// TotalHostCount is the toal count of hosts who received this message
	TotalHostCount uint `json:"totalCount,omitempty"`
}

// MessageLog is a log output by the host that contains important pubsub metric data
type MessageLog struct {
	// HostID is the host that received a message on the pubsub channel
	HostID string
	// SenderID is the host who sent the pubsub message
	SenderID string
	// MessageID is the id of the message that the host received
	MessageID string
	// SeqNo is the pubsub sequence number
	SeqNo uint64
	// NanoTime is the unix nano timestamp that the message was received
	NanoTime int64
	// Seq is the message sequence
	Seq int
}
