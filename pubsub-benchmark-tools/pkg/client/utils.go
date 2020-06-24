package client

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"strings"

	"github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/logger"
	pb "github.com/agencyenterprise/go-libp2p-pubsub-benchmark-tools/pkg/pb/publisher"
)

func parseMessageFile(loc string) (*pb.Message, error) {
	b, err := ioutil.ReadFile(loc)
	if err != nil {
		logger.Errorf("err reading file %s:\n%v", loc, err)
		return nil, err
	}

	var msg pb.Message
	if err = json.Unmarshal(b, &msg); err != nil {
		logger.Errorf("err unmarshaling message:\n%v", err)
		return nil, err
	}

	return &msg, nil
}

func parsePeers(peers string) []string {
	peersArr := strings.Split(peers, ",")
	for idx := range peersArr {
		peersArr[idx] = strings.TrimSpace(peersArr[idx])
	}
	return peersArr
}

func sizeMessage(msg *pb.Message, size uint) error {
	if err := checkMsgSize(msg, size); err != nil {
		logger.Errorf("err checking message size:\n%v", err)
		return err
	}

	resizeMessage(msg, size)

	return nil
}

func checkMsgSize(msg *pb.Message, size uint) error {
	if msg == nil {
		logger.Error("nil message")
		return errors.New("message cannot be nil")
	}

	msgSize := msg.XXX_Size()
	diff := int(size) - msgSize

	if diff < 0 {
		logger.Errorf("cannot create message of size %v bytes; have %v bytes", size, msgSize)
		return errors.New("cannot size message")
	}

	return nil
}

func resizeMessage(msg *pb.Message, size uint) {
	msgSize := msg.XXX_Size()
	diff := int(size) - msgSize

	for idx := 0; idx < diff; idx++ {
		msg.Data = append(msg.Data, 0)
	}
}
