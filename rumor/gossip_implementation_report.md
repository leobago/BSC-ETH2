# Gossip implementation on the Rumor debugging tool
As Rumor is getting popularity on the ETH2 community for debugging the Eth2 clients, more problems and bugs appear with the time. On this report, we will take a look at a small bug related to the GossipSub implementation that Rumor does to log the messages and gossips on the network.

## Spoted Issue
Debug the real GossipSub implementation on the medalla testnet for a later analysis has achieved a high priority for the BSC-ETH2 team. Since Rumor offers a prebuilt tool to debug it, we have been pushing the boundaries of Rumor until we have faced an unexpected behaviour on the `gossip` command. 

We have been trying to debug one of the main topics on the Eth2 network, the "beacon_block" topic. As it is explained on the [p2p-interface](https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/p2p-interface.md#encodings), the structure to generate the GossipSub topics is "/eth2" + "/fork digest" + "name of the topic" + "encoding". 
e.g: `/eth2/0xe7a75d5a/beacon_block/ssz_snappy` (0xe7a75d5a is the fork digest of the medalla testnet)

As a result of this trial we have experienced that, despite having 7-10 peers connected to our node and more than 300 peers on the peerstore, the Rumor implementation fo GossipSub isn't able to get any peer on the given topic.

Note: the peers are real nodes on the medalla testnet, received from the medalla bootnodes.

After talking with the main developer @Protolambda, he mentioned that it could hapend due to a bad order on the followed steps. He suggested that the commands to start debugging the topic have to executed before the peers are connected.

Even though we followed his suggestions, the received result was the same, 0 peers on the topic. 

As little testing, to see if the command was working fine, we developed a small script called [gossip test](https://github.com/Cortze/rumor-playground/blob/master/gossip-test/gossip-test.rumor). Following the instructions given by @Protolambda, we can see that the peers get connected to each other on the test topic, and while trying to publish a message all the peers receive it. 

## Check of the GossipSub Code Implementation
For a better understanding of what the code really does, we took a look at the GossipSub code. 

On the `join.go`, we find the implementation of the cmd `gossip join` [link to the code](https://github.com/protolambda/rumor/blob/802060022e3d052ec558da9be2196886e8a57fdb/control/actor/gossip/join.go#L19). Here we can see that after parsing the comand `gossip join` the function does:
1. Check if the host is already on the topic.
2. Joins the topic using the funtion `Join` provided by the [PubSub implementation](https://github.com/libp2p/go-libp2p-pubsub/blob/f7f33e10cc18b4a20542d0208aeaccb91ad64f99/pubsub.go#L1063)
3. Store the topic.

There are a few questions about this implementation:
1. Why are we just joining the topic and not subscribing to it.
(check the documentation of the function [PubSub.Subscrib](https://github.com/libp2p/go-libp2p-pubsub/blob/f7f33e10cc18b4a20542d0208aeaccb91ad64f99/pubsub.go#L1124)) Shouldn't we aslo add (code bellow) as the PubSub.Subscribe() suggests?
```
sub, err = top.Subscribe()
	if err != nil {
		return err
	}
```


2. If we are not Subscribed to the topic, and it doesn't look like it is doing any specific request of the received metadata message (didn't have time to check this properly, for what I saw doesn't really looks like), why are we receiving the entire message on the log of the little test we did?

3. Why are we using the PubSub.Join() implementation and not the GossipSub.Join() one? Can this be the problem? are both implementations equivalent?

4. Why after connecting to 7-10 peers while being joined to the topic we can not log any single gossip? 
As libp2p claim on the website, the protocol itself doesn't offer any peer discovery, it rellies on the peer discovery of the application. Why is it not working?

5. Would be a nice idea to have 2 separate commands for Joining and Subscribing the topic. We could then log the metadata and full messages (might be a bit stupid since we can already have the entire message, but I'm not sure if it can be interesting for checking how many gossips are we listening)

## Tried things
1. We already tried to include the subscribing step to the Join command. Having the same results as before.
2. (I'm going to try tomorrow to use the GossipSub.Join() function as the Subscribe one) 

