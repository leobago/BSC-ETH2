// +build unit

package analysis

import (
	"fmt"
	"reflect"
	"strings"
	"testing"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/analysis/types"
)

func TestBuildMessageLogFromStrings(t *testing.T) {
	for i, tt := range []struct {
		in  []string
		out *types.MessageLog
	}{
		{
			in: []string{
				"QmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1",
				"QmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU",
				"foo",
				"1570505610507484693",
				"1570505615043912938",
				"1",
			},
			out: &types.MessageLog{
				HostID:    "QmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1",
				SenderID:  "QmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU",
				MessageID: "foo",
				SeqNo:     1570505610507484693,
				NanoTime:  1570505615043912938,
				Seq:       1,
			},
		},
		{
			in: []string{
				"AmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1",
				"AmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU",
				"Aoo",
				"2570505610507484693",
				"2570505615043912938",
				"2",
			},
			out: &types.MessageLog{
				HostID:    "AmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1",
				SenderID:  "AmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU",
				MessageID: "Aoo",
				SeqNo:     2570505610507484693,
				NanoTime:  2570505615043912938,
				Seq:       2,
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result, err := buildMessageLogFromStrings(tt.in)
			if err != nil {
				t.Fatal(err)
			}

			if !reflect.DeepEqual(result, tt.out) {
				t.Errorf("want %v; got %v", *tt.out, *result)
			}
		})
	}
}

func TestSortMessageLogs(t *testing.T) {
	var originals [][]*types.MessageLog

	// note: requires [2][3] for both in an out
	for i, tt := range []struct {
		in  [][]*types.MessageLog
		out [][]int
	}{
		{
			in: [][]*types.MessageLog{
				[]*types.MessageLog{
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
				[]*types.MessageLog{
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
			},
			out: [][]int{
				[]int{2, 1, 0},
				[]int{0, 1, 2},
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			originals = [][]*types.MessageLog{
				[]*types.MessageLog{
					tt.in[0][0],
					tt.in[0][1],
					tt.in[0][2],
				},
				[]*types.MessageLog{
					tt.in[1][0],
					tt.in[1][1],
					tt.in[1][2],
				},
			}

			sortMessageLogs(tt.in)

			if tt.in[0][0] != originals[0][tt.out[0][0]] ||
				tt.in[0][1] != originals[0][tt.out[0][1]] ||
				tt.in[0][2] != originals[0][tt.out[0][2]] ||
				tt.in[1][0] != originals[1][tt.out[1][0]] ||
				tt.in[1][1] != originals[1][tt.out[1][1]] ||
				tt.in[1][2] != originals[1][tt.out[1][2]] {
				t.Error("did not sort")
			}
		})
	}
}

func TestGroupMessageLogsByID(t *testing.T) {
	var (
		result  [][]*types.MessageLog
		group   []*types.MessageLog
		log     *types.MessageLog
		groupID string
	)

	for i, tt := range []struct {
		in []*types.MessageLog
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "1",
				},
				&types.MessageLog{
					MessageID: "1",
				},
				&types.MessageLog{
					MessageID: "1",
				},
				&types.MessageLog{
					MessageID: "2",
				},
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "1",
				},
				&types.MessageLog{
					MessageID: "2",
				},
				&types.MessageLog{
					MessageID: "3",
				},
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "3",
				},
				&types.MessageLog{
					MessageID: "3",
				},
				&types.MessageLog{
					MessageID: "3",
				},
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "5",
				},
				&types.MessageLog{
					MessageID: "7",
				},
				&types.MessageLog{
					MessageID: "5",
				},
				&types.MessageLog{
					MessageID: "2",
				},
				&types.MessageLog{
					MessageID: "3",
				},
				&types.MessageLog{
					MessageID: "1",
				},
				&types.MessageLog{
					MessageID: "3",
				},
				&types.MessageLog{
					MessageID: "1",
				},
				&types.MessageLog{
					MessageID: "7",
				},
				&types.MessageLog{
					MessageID: "5",
				},
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result = groupMessageLogsByID(tt.in)

			for _, group = range result {
				if len(group) == 0 {
					continue
				}

				groupID = group[0].MessageID

				for _, log = range group {
					if groupID != log.MessageID {
						t.Errorf("want %v; got %v", groupID, log.MessageID)
					}
				}
			}
		})
	}
}

func TestCountUniqueHosts(t *testing.T) {
	var result uint

	for i, tt := range []struct {
		in  []*types.MessageLog
		out uint
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
			},
			out: 1,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "2",
				},
			},
			out: 2,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "2",
				},
				&types.MessageLog{
					HostID:   "3",
					SenderID: "4",
				},
				&types.MessageLog{
					HostID:   "5",
					SenderID: "6",
				},
				&types.MessageLog{
					HostID:   "7",
					SenderID: "8",
				},
			},
			out: 8,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "2",
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "3",
				},
				&types.MessageLog{
					HostID:   "3",
					SenderID: "4",
				},
				&types.MessageLog{
					HostID:   "4",
					SenderID: "2",
				},
			},
			out: 4,
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result = countUniqueHosts(tt.in)

			if result != tt.out {
				t.Errorf("want %v; got %v", tt.out, result)
			}
		})
	}
}

type testPrependStringIn struct {
	s   string
	arr []string
}

func TestPrependString(t *testing.T) {
	var (
		original, result []string
	)

	for i, tt := range []struct {
		in *testPrependStringIn
	}{
		{
			in: &testPrependStringIn{
				s:   "1",
				arr: []string{},
			},
		},
		{
			in: &testPrependStringIn{
				s:   "1",
				arr: []string{"2", "3"},
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			original = make([]string, len(tt.in.arr))
			copy(original, tt.in.arr)

			result = prependString(tt.in.s, tt.in.arr)

			if len(result) != len(original)+1 {
				t.Errorf("want %v; got %v", len(original)+1, len(result))
			}

			if result[0] != tt.in.s {
				t.Errorf("want %v; got %v", tt.in.s, result[0])
			}

			if !reflect.DeepEqual(result[1:], original) {
				t.Errorf("want %v; got %v", original, result[1:])
			}
		})
	}
}

type testCalcRMRAndTotalCountOut struct {
	rmr   float32
	count uint
}

func TestCalcRMRAndTotalCount(t *testing.T) {
	var (
		rmr   float32
		count uint
		err   error
	)

	for i, tt := range []struct {
		in    []*types.MessageLog
		toErr bool
		out   testCalcRMRAndTotalCountOut
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
			},
			toErr: true,
			out: testCalcRMRAndTotalCountOut{
				rmr:   0,
				count: 1,
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
				&types.MessageLog{
					HostID:   "2",
					SenderID: "2",
				},
			},
			toErr: false,
			out: testCalcRMRAndTotalCountOut{
				rmr:   1.0,
				count: 2,
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
				},
				&types.MessageLog{
					HostID:   "2",
					SenderID: "2",
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "2",
				},
				&types.MessageLog{
					HostID:   "2",
					SenderID: "1",
				},
			},
			toErr: false,
			out: testCalcRMRAndTotalCountOut{
				rmr:   3.0,
				count: 2,
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			rmr, count, err = calcRMRAndTotalCount(tt.in)

			if err != nil {
				if !tt.toErr {
					t.Fatalf("received %v but expected no err", err)
				}
			} else {
				if tt.toErr {
					t.Fatal("expected err but received none")
				} else {
					if rmr != tt.out.rmr {
						t.Errorf("want rmr %v; got %v", tt.out.rmr, rmr)
					}
					if count != tt.out.count {
						t.Errorf("want count %v; got %v", tt.out.count, count)
					}
				}
			}
		})
	}
}

func TestCalcTotalNanoTime(t *testing.T) {
	var (
		result uint64
		err    error
	)

	for i, tt := range []struct {
		in    []*types.MessageLog
		toErr bool
		out   uint64
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					NanoTime: 1,
				},
			},
			toErr: false,
			out:   0,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					NanoTime: 1,
				},
				&types.MessageLog{
					NanoTime: 1,
				},
			},
			toErr: false,
			out:   0,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					NanoTime: 1,
				},
				&types.MessageLog{
					NanoTime: 1,
				},
			},
			toErr: false,
			out:   0,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					NanoTime: 1,
				},
				&types.MessageLog{
					NanoTime: 3,
				},
			},
			toErr: false,
			out:   2,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					NanoTime: 3,
				},
				&types.MessageLog{
					NanoTime: 1,
				},
			},
			toErr: true,
			out:   0,
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result, err = calcTotalNanoTime(tt.in)

			if err != nil {
				if !tt.toErr {
					t.Fatalf("received %v but expected no err", err)
				}
			} else {
				if tt.toErr {
					t.Fatal("expected err but received none")
				}
			}

			if result != tt.out {
				t.Errorf("want %v; got %v", tt.out, result)
			}
		})
	}
}

func TestParseLogLine(t *testing.T) {
	var (
		result *types.MessageLog
		err    error
	)

	for i, tt := range []struct {
		in    []byte
		toErr bool
		out   *types.MessageLog
	}{
		{
			in:    []byte("not a relevant line"),
			toErr: false,
			out:   nil,
		},
		{
			in:    []byte(`time="2019-10-08T03:33:35Z" level=info msg="Pubsub message received: QmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1,QmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU,foo,1570505610507484693,1570505615043912938,1,bad" source="pubsub.go:33:host.pubsubHandler"`),
			toErr: true,
			out:   nil,
		},
		{
			in:    []byte(`time="2019-10-08T03:33:35Z" level=info msg="Pubsub message received: QmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1,QmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU,foo,1570505610507484693,1570505615043912938,1" source="pubsub.go:33:host.pubsubHandler"`),
			toErr: false,
			out: &types.MessageLog{
				HostID:    "QmYBvjm9qTc1bYkm6KsrprraVA4Y8NiBVjK751dijyS4t1",
				SenderID:  "QmW5V3oyFASqxobsmY3vyYsL1kSu7B6nDbVAUAivC5rXmU",
				MessageID: "foo",
				SeqNo:     1570505610507484693,
				NanoTime:  1570505615043912938,
				Seq:       1,
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result, err = parseLogLine(tt.in)
			if err != nil {
				if !tt.toErr {
					t.Fatalf("received %v but expected no err", err)
				}
			} else {
				if tt.toErr {
					t.Fatal("expected err but received none")
				}
			}

			if !reflect.DeepEqual(result, tt.out) {
				t.Errorf("want %v; got %v", tt.out, result)
			}
		})
	}
}

type buildPathsForSenderIDIn struct {
	senderID, originalSender string
	ts                       int64
	m                        map[string]map[string][]*types.MessageLog
}

func TestBuildPathsForSenderID(t *testing.T) {
	var (
		result            [][]string
		path, resultPath  []string
		tmpOut, tmpResult string
	)

	for i, tt := range []struct {
		in  *buildPathsForSenderIDIn
		out [][]string
	}{
		{
			in: &buildPathsForSenderIDIn{
				senderID:       "1",
				originalSender: "1",
				ts:             0,
				m: map[string]map[string][]*types.MessageLog{
					"1": map[string][]*types.MessageLog{
						"1": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 1,
							},
						},
					},
				},
			},
			out: [][]string{},
		},
		{
			in: &buildPathsForSenderIDIn{
				senderID:       "1",
				originalSender: "1",
				ts:             0,
				m: map[string]map[string][]*types.MessageLog{
					"1": map[string][]*types.MessageLog{
						"2": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 1,
							},
						},
					},
				},
			},
			out: [][]string{
				[]string{"1", "2"},
			},
		},
		{
			in: &buildPathsForSenderIDIn{
				senderID:       "1",
				originalSender: "1",
				ts:             0,
				m: map[string]map[string][]*types.MessageLog{
					"1": map[string][]*types.MessageLog{
						"2": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 1,
							},
						},
						"1": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 5,
							},
						},
					},
					"2": map[string][]*types.MessageLog{
						"3": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 2,
							},
						},
					},
					"3": map[string][]*types.MessageLog{
						"4": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 3,
							},
						},
					},
					"4": map[string][]*types.MessageLog{
						"5": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 4,
							},
						},
					},
				},
			},
			out: [][]string{
				[]string{"1", "2", "3", "4", "5"},
			},
		},
		{
			in: &buildPathsForSenderIDIn{
				senderID:       "1",
				originalSender: "1",
				ts:             0,
				m: map[string]map[string][]*types.MessageLog{
					"1": map[string][]*types.MessageLog{
						"2": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 1,
							},
						},
						"9": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 1,
							},
						},
						"1": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 100,
							},
						},
					},
					"2": map[string][]*types.MessageLog{
						"3": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 2,
							},
						},
						"4": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 3,
							},
						},
					},
					"3": map[string][]*types.MessageLog{
						"5": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 4,
							},
						},
					},
					"5": map[string][]*types.MessageLog{
						"6": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 5,
							},
						},
					},
					"6": map[string][]*types.MessageLog{
						"7": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 6,
							},
						},
					},
					"4": map[string][]*types.MessageLog{
						"8": []*types.MessageLog{
							&types.MessageLog{
								NanoTime: 7,
							},
						},
					},
				},
			},
			out: [][]string{
				[]string{"1", "2", "3", "5", "6", "7"},
				[]string{"1", "2", "4", "8"},
				[]string{"1", "9"},
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result = buildPathsForSenderID(tt.in.senderID, tt.in.originalSender, tt.in.ts, tt.in.m)

			if len(tt.out) != len(result) {
				t.Errorf("want len %v; got len %v", len(tt.out), len(result))
			}

			// TODO: improve this...
		OUTER:
			for _, path = range tt.out {
				tmpOut = strings.Join(path, ",")
				for _, resultPath = range result {
					tmpResult = strings.Join(resultPath, ",")
					if tmpOut == tmpResult {
						continue OUTER
					}
				}

				t.Fatalf("%v not found in %v", path, result)
			}
		})
	}
}

func TestCalcLastDeliveryHop(t *testing.T) {
	var (
		result uint
	)

	for i, tt := range []struct {
		in  []*types.MessageLog
		out uint
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "2",
					SenderID: "1",
					NanoTime: 1,
				},
			},
			out: 1,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "2",
					SenderID: "1",
					NanoTime: 1,
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
					NanoTime: 5,
				},
				&types.MessageLog{
					HostID:   "3",
					SenderID: "2",
					NanoTime: 2,
				},
				&types.MessageLog{
					HostID:   "4",
					SenderID: "3",
					NanoTime: 3,
				},
				&types.MessageLog{
					HostID:   "5",
					SenderID: "4",
					NanoTime: 4,
				},
			},
			out: 4,
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					HostID:   "2",
					SenderID: "1",
					NanoTime: 1,
				},
				&types.MessageLog{
					HostID:   "9",
					SenderID: "1",
					NanoTime: 1,
				},
				&types.MessageLog{
					HostID:   "1",
					SenderID: "1",
					NanoTime: 100,
				},
				&types.MessageLog{
					HostID:   "3",
					SenderID: "2",
					NanoTime: 2,
				},
				&types.MessageLog{
					HostID:   "4",
					SenderID: "2",
					NanoTime: 3,
				},
				&types.MessageLog{
					HostID:   "5",
					SenderID: "3",
					NanoTime: 4,
				},
				&types.MessageLog{
					HostID:   "6",
					SenderID: "5",
					NanoTime: 5,
				},
				&types.MessageLog{
					HostID:   "7",
					SenderID: "6",
					NanoTime: 6,
				},
				&types.MessageLog{
					HostID:   "8",
					SenderID: "4",
					NanoTime: 7,
				},
			},
			out: 5,
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result = calcLastDeliveryHop(tt.in)

			if result != tt.out {
				t.Errorf("want %v; got %v", tt.out, result)
			}
		})
	}
}

func TestBuildMetricsFromSortedMessageLogs(t *testing.T) {
	var (
		result *types.Metric
		err    error
	)

	for i, tt := range []struct {
		in    []*types.MessageLog
		toErr bool
		out   *types.Metric
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "2",
					SenderID:  "1",
					NanoTime:  1,
				},
			},
			toErr: false,
			out: &types.Metric{
				MessageID:                 "foo",
				OriginatorHostID:          "1",
				TotalHostCount:            2,
				TotalNanoTime:             0,
				LastDeliveryHop:           1,
				RelativeMessageRedundancy: 0,
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "2",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "3",
					SenderID:  "2",
					NanoTime:  2,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "4",
					SenderID:  "3",
					NanoTime:  3,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "5",
					SenderID:  "4",
					NanoTime:  4,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "1",
					SenderID:  "1",
					NanoTime:  5,
				},
			},
			toErr: false,
			out: &types.Metric{
				MessageID:                 "foo",
				OriginatorHostID:          "1",
				TotalHostCount:            5,
				TotalNanoTime:             4,
				LastDeliveryHop:           4,
				RelativeMessageRedundancy: (5.0 / (5.0 - 1.0)) - 1.0,
			},
		},
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "2",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "9",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "3",
					SenderID:  "2",
					NanoTime:  2,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "4",
					SenderID:  "2",
					NanoTime:  3,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "5",
					SenderID:  "3",
					NanoTime:  4,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "6",
					SenderID:  "5",
					NanoTime:  5,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "7",
					SenderID:  "6",
					NanoTime:  6,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "8",
					SenderID:  "4",
					NanoTime:  7,
				},
				&types.MessageLog{
					MessageID: "foo",
					HostID:    "1",
					SenderID:  "1",
					NanoTime:  8,
				},
			},
			toErr: false,
			out: &types.Metric{
				MessageID:                 "foo",
				OriginatorHostID:          "1",
				TotalNanoTime:             7,
				LastDeliveryHop:           5,
				TotalHostCount:            9,
				RelativeMessageRedundancy: (9.0 / (9.0 - 1.0)) - 1.0,
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result, err = buildMetricsFromSortedMessageLogs(tt.in)
			if err != nil {
				if !tt.toErr {
					t.Fatalf("received %v but expected no err", err)
				}
			} else {
				if tt.toErr {
					t.Fatal("expected err but received none")
				}
			}

			if !reflect.DeepEqual(result, tt.out) {
				t.Errorf("want %v; got %v", tt.out, result)
			}
		})
	}
}

func TestBuildMetricsFromMessageLogs(t *testing.T) {
	var (
		results []*types.Metric
		result  *types.Metric
		idx     int
		err     error
	)

	for i, tt := range []struct {
		in    []*types.MessageLog
		toErr []bool
		out   []*types.Metric
	}{
		{
			in: []*types.MessageLog{
				&types.MessageLog{
					MessageID: "1",
					HostID:    "2",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "2",
					HostID:    "4",
					SenderID:  "3",
					NanoTime:  3,
				},
				&types.MessageLog{
					MessageID: "2",
					HostID:    "3",
					SenderID:  "2",
					NanoTime:  2,
				},
				&types.MessageLog{
					MessageID: "2",
					HostID:    "5",
					SenderID:  "4",
					NanoTime:  4,
				},
				&types.MessageLog{
					MessageID: "2",
					HostID:    "1",
					SenderID:  "1",
					NanoTime:  5,
				},
				&types.MessageLog{
					MessageID: "2",
					HostID:    "2",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "9",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "2",
					SenderID:  "1",
					NanoTime:  1,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "4",
					SenderID:  "2",
					NanoTime:  3,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "1",
					SenderID:  "1",
					NanoTime:  8,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "5",
					SenderID:  "3",
					NanoTime:  4,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "6",
					SenderID:  "5",
					NanoTime:  5,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "7",
					SenderID:  "6",
					NanoTime:  6,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "3",
					SenderID:  "2",
					NanoTime:  2,
				},
				&types.MessageLog{
					MessageID: "3",
					HostID:    "8",
					SenderID:  "4",
					NanoTime:  7,
				},
			},
			toErr: []bool{
				false,
				false,
				false,
			},
			out: []*types.Metric{
				&types.Metric{
					TotalHostCount:            2,
					MessageID:                 "1",
					OriginatorHostID:          "1",
					TotalNanoTime:             0,
					LastDeliveryHop:           1,
					RelativeMessageRedundancy: 0,
				},
				&types.Metric{
					TotalHostCount:            5,
					MessageID:                 "2",
					OriginatorHostID:          "1",
					TotalNanoTime:             4,
					LastDeliveryHop:           4,
					RelativeMessageRedundancy: (5.0 / (5.0 - 1.0)) - 1.0,
				},
				&types.Metric{
					TotalHostCount:            9,
					MessageID:                 "3",
					OriginatorHostID:          "1",
					TotalNanoTime:             7,
					LastDeliveryHop:           5,
					RelativeMessageRedundancy: (9.0 / (9.0 - 1.0)) - 1.0,
				},
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			results, err = buildMetricsFromMessageLogs(tt.in)

			for idx, result = range results {
				if err != nil {
					if !tt.toErr[idx] {
						t.Fatalf("received %v but expected no err", err)
					}
				} else {
					if tt.toErr[idx] {
						t.Fatal("expected err but received none")
					}
				}

				var expected *types.Metric
				for _, metric := range tt.out {
					if result.MessageID == metric.MessageID {
						expected = metric
						break
					}
				}

				if !reflect.DeepEqual(result, expected) {
					t.Errorf("want %v; got %v", expected, result)
				}
			}
		})
	}
}

func TestBuildMetricsFromMessageLogsGroups(t *testing.T) {
	var (
		results []*types.Metric
		result  *types.Metric
		idx     int
		err     error
	)

	for i, tt := range []struct {
		in    [][]*types.MessageLog
		toErr []bool
		out   []*types.Metric
	}{
		{
			in: [][]*types.MessageLog{
				[]*types.MessageLog{
					&types.MessageLog{
						MessageID: "1",
						HostID:    "2",
						SenderID:  "1",
						NanoTime:  1,
					},
				},
				[]*types.MessageLog{
					&types.MessageLog{
						MessageID: "2",
						HostID:    "2",
						SenderID:  "1",
						NanoTime:  1,
					},
					&types.MessageLog{
						MessageID: "2",
						HostID:    "3",
						SenderID:  "2",
						NanoTime:  2,
					},
					&types.MessageLog{
						MessageID: "2",
						HostID:    "4",
						SenderID:  "3",
						NanoTime:  3,
					},
					&types.MessageLog{
						MessageID: "2",
						HostID:    "5",
						SenderID:  "4",
						NanoTime:  4,
					},
					&types.MessageLog{
						MessageID: "2",
						HostID:    "1",
						SenderID:  "1",
						NanoTime:  5,
					},
				},
				[]*types.MessageLog{
					&types.MessageLog{
						MessageID: "3",
						HostID:    "9",
						SenderID:  "1",
						NanoTime:  1,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "2",
						SenderID:  "1",
						NanoTime:  1,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "3",
						SenderID:  "2",
						NanoTime:  2,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "4",
						SenderID:  "2",
						NanoTime:  3,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "5",
						SenderID:  "3",
						NanoTime:  4,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "6",
						SenderID:  "5",
						NanoTime:  5,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "7",
						SenderID:  "6",
						NanoTime:  6,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "8",
						SenderID:  "4",
						NanoTime:  7,
					},
					&types.MessageLog{
						MessageID: "3",
						HostID:    "1",
						SenderID:  "1",
						NanoTime:  8,
					},
				},
			},
			toErr: []bool{
				false,
				false,
				false,
			},
			out: []*types.Metric{
				&types.Metric{
					MessageID:                 "1",
					OriginatorHostID:          "1",
					TotalNanoTime:             0,
					LastDeliveryHop:           1,
					TotalHostCount:            2,
					RelativeMessageRedundancy: 0,
				},
				&types.Metric{
					TotalHostCount:            5,
					MessageID:                 "2",
					OriginatorHostID:          "1",
					TotalNanoTime:             4,
					LastDeliveryHop:           4,
					RelativeMessageRedundancy: (5.0 / (5.0 - 1.0)) - 1.0,
				},
				&types.Metric{
					TotalHostCount:            9,
					MessageID:                 "3",
					OriginatorHostID:          "1",
					TotalNanoTime:             7,
					LastDeliveryHop:           5,
					RelativeMessageRedundancy: (9.0 / (9.0 - 1.0)) - 1.0,
				},
			},
		},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			results, err = buildMetricsFromSortedMessageLogsGroups(tt.in)

			for idx, result = range results {
				if err != nil {
					if !tt.toErr[idx] {
						t.Fatalf("received %v but expected no err", err)
					}
				} else {
					if tt.toErr[idx] {
						t.Fatal("expected err but received none")
					}
				}
				var expected *types.Metric
				for _, metric := range tt.out {
					if result.MessageID == metric.MessageID {
						expected = metric
						break
					}
				}

				if !reflect.DeepEqual(result, expected) {
					t.Errorf("want %v; got %v", expected, result)
				}
			}
		})
	}
}
