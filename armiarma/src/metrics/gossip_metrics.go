package metrics

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/libp2p/go-libp2p-core/peer"
	pgossip "github.com/protolambda/rumor/p2p/gossip"
	"github.com/protolambda/rumor/p2p/gossip/database"
	"github.com/protolambda/rumor/p2p/track"
	//	"github.com/protolambda/zrnt/eth2/beacon"
)

type GossipMetrics struct {
	GossipMetrics   sync.Map
	ExtraMetrics    ExtraMetrics
	MessageDatabase *database.MessageDatabase
	StartTime       int64 // milliseconds
}

func NewGossipMetrics() GossipMetrics {
	gm := GossipMetrics{
		StartTime: GetTimeMiliseconds(),
	}
	return gm
}

// Exists reports whether the named file or directory exists.
func FileExists(name string) bool {
	if _, err := os.Stat(name); err != nil {
		if os.IsNotExist(err) {
			return false
		}
	}
	return true
}

// Import an old GossipMetrics from given file
// return: - return error if there was error while reading the file
//         - return bool for existing file (true if there was a file to read, return false if there wasn't a file to read)
func (c *GossipMetrics) ImportMetrics(importFile string) (error, bool) {
	// Check if file exist
	if FileExists(importFile) { // if exists, read it
		// get the json of the file
		jsonFile, err := os.Open(importFile)
		if err != nil {
			return err, true
		}
		byteValue, err := ioutil.ReadAll(jsonFile)
		if err != nil {
			return err, true
		}
		tempMap := make(map[peer.ID]PeerMetrics, 0)
		json.Unmarshal(byteValue, &tempMap)
		// iterate to add the metrics from the json to the the GossipMetrics
		for k, v := range tempMap {
			c.GossipMetrics.Store(k, v)
		}
		return nil, true
	} else {
		return nil, false
	}
}

type GossipState struct {
	GsNode  pgossip.GossipSub
	CloseGS context.CancelFunc
	// string -> *pubsub.Topic
	Topics sync.Map
	// Validation Filter Flag
	SeenFilter bool
}

// Base Struct for the topic name and the received messages on the different topics
type PeerMetrics struct {
	PeerId     peer.ID
	NodeId     string
	ClientType string
	Pubkey     string
	Addrs      string
	Ip         string
	Country    string
	City       string
	Latency    float64

	ConnectionEvents []ConnectionEvents
	// Counters for the different topics
	BeaconBlock          MessageMetrics
	BeaconAggregateProof MessageMetrics
	VoluntaryExit        MessageMetrics
	ProposerSlashing     MessageMetrics
	AttesterSlashing     MessageMetrics
	// Variables related to the SubNets (only needed for when Shards will be implemented)
}

func NewPeerMetrics(peerId peer.ID) PeerMetrics {
	pm := PeerMetrics{
		PeerId:     peerId,
		NodeId:     "",
		ClientType: "Unknown",
		Pubkey:     "",
		Addrs:      "/ip4/127.0.0.1/0000",
		Ip:         "127.0.0.1",
		Country:    "Unknown",
		City:       "Unknown",
		Latency:    0,

		ConnectionEvents: make([]ConnectionEvents, 1),
		// Counters for the different topics
		BeaconBlock:          NewMessageMetrics(),
		BeaconAggregateProof: NewMessageMetrics(),
		VoluntaryExit:        NewMessageMetrics(),
		ProposerSlashing:     NewMessageMetrics(),
		AttesterSlashing:     NewMessageMetrics(),
	}
	return pm
}

func NewMessageMetrics() MessageMetrics {
	mm := MessageMetrics{
		Cnt:              0,
		FirstMessageTime: 0,
		LastMessageTime:  0,
	}
	return mm
}

// Connection event model
type ConnectionEvents struct {
	ConnectionType string
	TimeMili       int64
}

// Information regarding the messages received on the beacon_lock topic
type MessageMetrics struct {
	Cnt              int64
	FirstMessageTime int64
	LastMessageTime  int64
}

// Function that Wraps/Marshals the content of the sync.Map to be exported as a json
func (c *GossipMetrics) MarshalMetrics() ([]byte, error) {
	tmpMap := make(map[string]PeerMetrics)
	c.GossipMetrics.Range(func(k, v interface{}) bool {
		tmpMap[k.(peer.ID).String()] = v.(PeerMetrics)
		return true
	})
	return json.Marshal(tmpMap)
}

// Function that Wraps/Marshals the content of the Entire Peerstore into a json
func (c *GossipMetrics) MarshalPeerStore(ep track.ExtendedPeerstore) ([]byte, error) {
	var peers []peer.ID
	peers = ep.Peers()
	peerData := make(map[string]*track.PeerAllData)
	for _, p := range peers {
		peerData[p.String()] = ep.GetAllData(p)
	}
	return json.Marshal(peerData)
}

// Get the Real Ip Address from the multi Address list
// TODO: Implement the Private IP filter in a better way
func GetFullAddress(multiAddrs []string) string {
	var address string
	if len(multiAddrs) > 0 {
		for _, element := range multiAddrs {
			if strings.Contains(element, "/ip4/192.168.") || strings.Contains(element, "/ip4/127.0.") || strings.Contains(element, "/ip6/") || strings.Contains(element, "/ip4/172.") || strings.Contains(element, "0.0.0.0") {
				continue
			} else {
				address = element
				break
			}
		}
	} else {
		address = "/ip4/127.0.0.1/tcp/9000"
	}
	return address
}

// Function that iterates through the received peers and fills the missing information
func (c *GossipMetrics) FillMetrics(ep track.ExtendedPeerstore) {
	// to prevent the Filler from crashing (the url-service only accepts 45req/s)
	requestCounter := 0
	// Loop over the Peers on the GossipMetrics
	c.GossipMetrics.Range(func(key interface{}, value interface{}) bool {
		// Read the info that we have from him
		p, ok := c.GossipMetrics.Load(key)
		if ok {
			peerMetrics := p.(PeerMetrics)
			peerData := ep.GetAllData(peerMetrics.PeerId)
			//fmt.Println("Filling Metrics of Peer:", peerMetrics.PeerId.String())
			if len(peerMetrics.NodeId) == 0 {
				//fmt.Println("NodeID empty", peerMetrics.NodeId, "Adding NodeId:", peerData.NodeID.String())
				peerMetrics.NodeId = peerData.NodeID.String()
			}

			if len(peerMetrics.ClientType) == 0 || peerMetrics.ClientType == "Unknown" {
				//fmt.Println("ClientType empty", peerMetrics.ClientType, "Adding ClientType:", peerData.UserAgent)
				peerMetrics.ClientType = peerData.UserAgent
			}

			if len(peerMetrics.Pubkey) == 0 {
				//fmt.Println("Pubkey empty", peerMetrics.Pubkey, "Adding Pubkey:", peerData.Pubkey)
				peerMetrics.Pubkey = peerData.Pubkey
			}

			if len(peerMetrics.Addrs) == 0 || peerMetrics.Addrs == "/ip4/127.0.0.1/0000" {
				address := GetFullAddress(peerData.Addrs)
				//fmt.Println("Addrs empty", peerMetrics.Addrs, "Adding Addrs:", address)
				peerMetrics.Addrs = address
			}

			if len(peerMetrics.Country) == 0 || peerMetrics.Country == "Unknown" {
				if len(peerMetrics.Addrs) == 0 {
					//fmt.Println("No Addrs on the PeerMetrics to request the Location")
				} else {
					//fmt.Println("Requesting the Location based on the addrs:", peerMetrics.Addrs)
					ip, country, city := getIpAndLocationFromAddrs(peerMetrics.Addrs)
					requestCounter = requestCounter + 1
					peerMetrics.Ip = ip
					peerMetrics.Country = country
					peerMetrics.City = city
				}
			}

			// Since we want to have the latest Latency, we update it only when it is different from 0
			// latency in seconds
			if peerData.Latency != 0 {
				peerMetrics.Latency = float64(peerData.Latency/time.Millisecond) / 1000
			}

			// After check that all the info is ready, save the item back into the Sync.Map
			c.GossipMetrics.Store(key, peerMetrics)

			/*
				if requestCounter >= 40 { // Reminder 45 req/s
					time.Sleep(70 * time.Second)
					requestCounter = 0
				}
			*/
		}
		// Keep with the loop on the Range function
		return true
	})

}

// Function that Exports the entire Metrics to a .json file (lets see if in the future we can add websockets or other implementations)
func (c *GossipMetrics) ExportMetrics(filePath string, peerstorePath string, csvPath string, extraMetricsPath string, ep track.ExtendedPeerstore) error {
	metrics, err := c.MarshalMetrics()
	if err != nil {
		fmt.Println("Error Marshalling the metrics")
	}
	peerstore, err := c.MarshalPeerStore(ep)
	if err != nil {
		fmt.Println("Error Marshalling the peerstore")
	}

	err = ioutil.WriteFile(filePath, metrics, 0644)
	if err != nil {
		fmt.Println("Error opening file: ", filePath)
		return err
	}
	err = ioutil.WriteFile(peerstorePath, peerstore, 0644)
	if err != nil {
		fmt.Println("Error opening file: ", peerstorePath)
		return err
	}
	// Generate the MetricsDataFrame of the Current Metrics
	// Export the metrics to the given CSV file
	mdf := NewMetricsDataFrame(c.GossipMetrics)
	err = mdf.ExportToCSV(csvPath)
	if err != nil {
		fmt.Printf("Error:", err)
		return err
	}
	// Export the extra metrics to a csv
	err = c.ExtraMetrics.ExportCSV(extraMetricsPath)
	if err != nil {
		fmt.Printf("Error exporting the Extra metrics:", err)
		return err
	}
	return nil
}

// IP-API message structure
type IpApiMessage struct {
	Query       string `json:"query"`
	Status      string `json:"status"`
	Country     string `json:"country"`
	CountryCode string `json:"countryCode"`
	Region      string `json:"region"`
	RegionName  string `json:"regionName"`
	City        string `json:"city"`
	Zip         string `json:"zip"`
	Lat         string `json:"lat"`
	Lon         string `json:"lon"`
	Timezone    string `json:"timezone"`
	Isp         string `json:"isp"`
	Org         string `json:"org"`
	As          string `json:"as"`
}

// get IP, location country and City from the multiaddress of the peer on the peerstore
func getIpAndLocationFromAddrs(multiAddrs string) (ip string, country string, city string) {
	ip = strings.TrimPrefix(multiAddrs, "/ip4/")
	ipSlices := strings.Split(ip, "/")
	ip = ipSlices[0]
	url := "http://ip-api.com/json/" + ip
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println(err)
		country = "Unknown"
		city = "Unknown"
		return ip, country, city
	}

	attemptsLeft, _ := strconv.Atoi(resp.Header["X-Rl"][0])
	timeLeft, _ := strconv.Atoi(resp.Header["X-Ttl"][0])

	if attemptsLeft == 0 { // We have exceeded the limit of requests 45req/min
		time.Sleep(time.Duration(timeLeft) * time.Second)
		resp, err = http.Get(url)
		if err != nil {
			fmt.Println(err)
			country = "Unknown"
			city = "Unknown"
			return ip, country, city
		}
	}

	defer resp.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(resp.Body)

	// Convert response body to Todo struct
	var ipApiResp IpApiMessage
	json.Unmarshal(bodyBytes, &ipApiResp)

	// Check if the status of the request has been succesful
	if ipApiResp.Status != "success" {
		/*
			fmt.Println("Error with the received response status,", ipApiResp.Status)
			if ipApiResp.Query == ip {
				fmt.Println("The given IP of the peer is private")
			}
		*/
		country = "Unknown"
		city = "Unknown"
		return ip, country, city
	}

	country = ipApiResp.Country
	city = ipApiResp.City

	// check if country and city are correctly imported
	if len(country) == 0 || len(city) == 0 {
		country = "Unknown"
		city = "Unknown"
		return ip, country, city
	}

	// return the received values from the received message
	return ip, country, city

}

// Add new peer with all the information from the peerstore to the metrics db
// returns: Alredy (Bool)
func (c *GossipMetrics) AddNewPeer(peerId peer.ID) {
	_, ok := c.GossipMetrics.Load(peerId)
	if !ok {
		// We will just add the info that we have (the peerId)
		peerMetrics := NewPeerMetrics(peerId)
		// Include it to the Peer DB
		c.GossipMetrics.Store(peerId, peerMetrics)
		// return that wasn't already on the peerstore
	}
}

// Add a connection Event to the given peer
func (c *GossipMetrics) AddConnectionEvent(peerId peer.ID, connectionType string) {
	newConnection := ConnectionEvents{
		ConnectionType: connectionType,
		TimeMili:       GetTimeMiliseconds(),
	}
	pMetrics, ok := c.GossipMetrics.Load(peerId)
	if ok {
		peerMetrics := pMetrics.(PeerMetrics)
		peerMetrics.ConnectionEvents = append(peerMetrics.ConnectionEvents, newConnection)
		c.GossipMetrics.Store(peerId, peerMetrics)
	} else {
		// Might be possible to add
		fmt.Println("Counld't add Event, Peer is not in the list")
	}
}

// Increments the counter of the topic
func (c *MessageMetrics) IncrementCnt() int64 {
	c.Cnt++
	return c.Cnt
}

// Stamps linux_time(millis) on the FirstMessageTime/LastMessageTime from given args: time (int64), flag string("first"/"last")
func (c *MessageMetrics) StampTime(flag string) {
	unixMillis := GetTimeMiliseconds()

	switch flag {
	case "first":
		c.FirstMessageTime = unixMillis
	case "last":
		c.LastMessageTime = unixMillis
	default:
		fmt.Println("Metrics Package -> StampTime.flag wrongly parsed")
	}
}

func GetTimeMiliseconds() int64 {
	now := time.Now()
	//secs := now.Unix()
	nanos := now.UnixNano()
	millis := nanos / 1000000

	return millis
}

// Function that Manages the metrics updates for the incoming messages
func (c *GossipMetrics) IncomingMessageManager(peerId peer.ID, topicName string) error {
	pMetrics, _ := c.GossipMetrics.Load(peerId)
	//fmt.Println("the loaded", pMetrics)
	peerMetrics := pMetrics.(PeerMetrics)
	messageMetrics, err := GetMessageMetrics(&peerMetrics, topicName)
	if err != nil {
		return errors.New("Topic Name no supported")
	}
	if messageMetrics.Cnt == 0 {
		messageMetrics.StampTime("first")
	}

	messageMetrics.IncrementCnt()
	messageMetrics.StampTime("last")

	// Store back the Loaded/Modified Variable
	c.GossipMetrics.Store(peerId, peerMetrics)

	return nil
}

func GetMessageMetrics(c *PeerMetrics, topicName string) (mesMetr *MessageMetrics, err error) {
	// All this could be inside a different function
	switch topicName {
	case pgossip.BeaconBlock:
		return &c.BeaconBlock, nil
	case pgossip.BeaconAggregateProof:
		return &c.BeaconAggregateProof, nil
	case pgossip.VoluntaryExit:
		return &c.VoluntaryExit, nil
	case pgossip.ProposerSlashing:
		return &c.ProposerSlashing, nil
	case pgossip.AttesterSlashing:
		return &c.AttesterSlashing, nil
	default: //TODO: - Not returning BeaconBlock as Default
		return &c.BeaconBlock, err
	}
}
