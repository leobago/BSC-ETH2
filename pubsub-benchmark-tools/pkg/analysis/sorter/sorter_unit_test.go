// +build unit

package sorter

import (
	"fmt"
	"testing"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/analysis/types"
)

func TestLen(t *testing.T) {
	for i, tt := range []struct {
		in  *MessageLogsSorter
		out int
	}{
		{
			in: &MessageLogsSorter{
				messageLogs: []*types.MessageLog{},
			},
			out: 0,
		},
		{
			in: &MessageLogsSorter{
				messageLogs: []*types.MessageLog{
					&types.MessageLog{},
				},
			},
			out: 1,
		},
		{
			in: &MessageLogsSorter{
				messageLogs: []*types.MessageLog{
					&types.MessageLog{},
					&types.MessageLog{},
					&types.MessageLog{},
					&types.MessageLog{},
					&types.MessageLog{},
				},
			},
			out: 5,
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result := tt.in.Len()
			if result != tt.out {
				t.Errorf("want %v; got %v", tt.out, result)
			}
		})
	}
}

type testSwapIn struct {
	sorter *MessageLogsSorter
	i, j   int
}

func TestSwap(t *testing.T) {
	for i, tt := range []struct {
		in *testSwapIn
	}{
		{
			in: &testSwapIn{
				sorter: &MessageLogsSorter{
					messageLogs: []*types.MessageLog{
						&types.MessageLog{},
						&types.MessageLog{},
					},
				},
				i: 0,
				j: 1,
			},
		},
		{
			in: &testSwapIn{
				sorter: &MessageLogsSorter{
					messageLogs: []*types.MessageLog{
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
					},
				},
				i: 0,
				j: 2,
			},
		},
		{
			in: &testSwapIn{
				sorter: &MessageLogsSorter{
					messageLogs: []*types.MessageLog{
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
					},
				},
				i: 1,
				j: 2,
			},
		},
		{
			in: &testSwapIn{
				sorter: &MessageLogsSorter{
					messageLogs: []*types.MessageLog{
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
						&types.MessageLog{},
					},
				},
				i: 4,
				j: 1,
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			originalI := tt.in.sorter.messageLogs[tt.in.i]
			originalJ := tt.in.sorter.messageLogs[tt.in.j]

			tt.in.sorter.Swap(tt.in.i, tt.in.j)

			if originalI != tt.in.sorter.messageLogs[tt.in.j] || originalJ != tt.in.sorter.messageLogs[tt.in.i] {
				t.Error("expected swap")
			}
		})
	}
}

type testLessIn struct {
	m1, m2 *types.MessageLog
}

func TestLess(t *testing.T) {
	// Closures that order the messageLog structure.
	unixNanoTimestamp := func(m1, m2 *types.MessageLog) bool {
		return m1.NanoTime < m2.NanoTime
	}

	sorter := &MessageLogsSorter{
		by: unixNanoTimestamp,
	}

	for i, tt := range []struct {
		in  *testLessIn
		out bool
	}{
		{
			in: &testLessIn{
				m1: &types.MessageLog{
					NanoTime: 0,
				},
				m2: &types.MessageLog{
					NanoTime: 1,
				},
			},
			out: true,
		},
		{
			in: &testLessIn{
				m1: &types.MessageLog{
					NanoTime: 1,
				},
				m2: &types.MessageLog{
					NanoTime: 0,
				},
			},
			out: false,
		},
		{
			in: &testLessIn{
				m1: &types.MessageLog{
					NanoTime: 0,
				},
				m2: &types.MessageLog{
					NanoTime: 0,
				},
			},
			out: false,
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			sorter.messageLogs = []*types.MessageLog{
				tt.in.m1,
				tt.in.m2,
			}

			result := sorter.Less(0, 1)

			if result != tt.out {
				t.Errorf("expected %v, received: %v", tt.out, result)
			}
		})
	}
}

func TestSort(t *testing.T) {
	// Closures that order the messageLog structure.
	unixNanoTimestamp := func(m1, m2 *types.MessageLog) bool {
		return m1.NanoTime < m2.NanoTime
	}

	var original []*types.MessageLog

	for i, tt := range []struct {
		in  [3]*types.MessageLog
		out [3]int
	}{
		{
			in: [3]*types.MessageLog{
				&types.MessageLog{
					NanoTime: 2,
				},
				&types.MessageLog{
					NanoTime: 1,
				},
				&types.MessageLog{
					NanoTime: 0,
				},
			},
			out: [3]int{2, 1, 0},
		},
		{
			in: [3]*types.MessageLog{
				&types.MessageLog{
					NanoTime: 0,
				},
				&types.MessageLog{
					NanoTime: 1,
				},
				&types.MessageLog{
					NanoTime: 2,
				},
			},
			out: [3]int{0, 1, 2},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			original = []*types.MessageLog{
				tt.in[0],
				tt.in[1],
				tt.in[2],
			}

			By(unixNanoTimestamp).Sort(tt.in[:])

			if tt.in[0] != original[tt.out[0]] || tt.in[1] != original[tt.out[1]] || tt.in[2] != original[tt.out[2]] {
				t.Error("did not sort")
			}
		})
	}
}
