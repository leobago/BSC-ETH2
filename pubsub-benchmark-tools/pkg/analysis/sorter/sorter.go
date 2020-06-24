package sorter

import (
	"sort"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/analysis/types"
)

// By is the type of a "less" function that defines the ordering of its Planet arguments.
type By func(m1, m2 *types.MessageLog) bool

// Sort is a method on the function type, By, that sorts the argument slice according to the function.
func (by By) Sort(messageLogs []*types.MessageLog) {
	ms := &MessageLogsSorter{
		messageLogs: messageLogs,
		by:          by, // The Sort method's receiver is the function (closure) that defines the sort order.
	}
	sort.Sort(ms)
}

// MessageLogsSorter joins a By function and a slice of messageLogs to be sorted.
type MessageLogsSorter struct {
	messageLogs []*types.MessageLog
	by          func(m1, m2 *types.MessageLog) bool // Closure used in the Less method.
}

// Len is part of sort.Interface.
func (s *MessageLogsSorter) Len() int {
	return len(s.messageLogs)
}

// Swap is part of sort.Interface.
// note: this could panic!
func (s *MessageLogsSorter) Swap(i, j int) {
	s.messageLogs[i], s.messageLogs[j] = s.messageLogs[j], s.messageLogs[i]
}

// less is part of sort.Interface. It is implemented by calling the "by" closure in the sorter.
func (s *MessageLogsSorter) Less(i, j int) bool {
	return s.by(s.messageLogs[i], s.messageLogs[j])
}
