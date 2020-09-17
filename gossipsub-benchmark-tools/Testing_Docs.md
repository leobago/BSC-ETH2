#TESTS TO RUN

Tests are run with the parameters used in the Gossipsub-v1.1 Evaluation Report made by Protocol Labs.
The objective of the testing is the replication of the results obtained in the Gossipsub-v1.1 Evaluation Report, as well as extending the scope of those tests, both in magnitude and variety of attack vectors.
Most of the parameters will have the same value for most of the tests, but the value of several parameters will change in every test.
For this reason, here there are some standard parameters used for all the test.
Depending on the test some of them will need to be changed accordingly to the specific documentation provided in the test.
Some parameters are not defined yet, and their value is set to “TBD” (To Be Defined).

##Gossipsub-v1.1 Mesh Parameters

**Time:**
TestSetupTime: TBD TestRuntime: TBD WarmupTime : TBD CooldownTime: TBD
Node Counts:
N_PUBLISHERS = 100
N_LURKERS = 900
N_ATTACKER_NODES = 4000 N_HONEST_PEERS_FOR_CONTAINER = TBD N_ATTACKER_PEERS_FOR_CONTAINER = TBD

**Pubsub:**
HeartBeatInterval = 1s IntitialHeartbeatDelay = TBD SizeOfValidationQueue= TBD SizeOfOutboundRPC_Queue = TBD IntervalToDumpPeerScores= TBD
OVERLAY_D = 8 OVERLAY_DLO = 6
OVERLAY_DHI = 12 OVERLAY_DSCORE = 6 OVERLAY_DLAZY = 12
D_OUT = TBD
GossipFactor = 0.25
Heartbeat = 1s OpportunisticGraftHeartbeatTicks = TBD

**Network:**
MIN_LATENCY = TBD MAX_LATENCY = TBD LATENCY JITTER = 10% BANDWIDTH = 10240 N_DEGREE = 20 N_SYBILS = 4000 ATTACK_DEGREE = 100
Honest Behaviour:
FloodPublishing = Yes JitterHonestConnectDelay = TBD HonestPeerConnectionDelay = TBD
Attack Behaviour:
AttackType = Sybil
CensorTargetNode = ... (value depends on specific TEST) TargetSingleNode = ... (value depend on specific TEST) AttackPublishersOnly = ... (value depend on specific TEST) JitterForAttackerDelay = TBD
SybilDropProbability = TBD
SybilAttackDelay = TBD
RegraftDelay = TBD

RegraftBackoff = TBD SeenCacheDuration = TBD

**PeerScore:**
GossipThreshold = -4000.0 [unattainable without invalid message deliveries or app signal] PublishThreshold = -5000.0
GraylistThreshold = -10000.0
AcceptPXThreshold = 0.0 [PX is not enabled as there is no peer routing system] OpportunisticGraftThreshold = 0.0 [this effectively disables by default – it is enabled in certain tests] IP_ColocationFactorWeight = TBD
IP_ColocationFactorThresold = TBD ScoreDecayInterval = TBD DecayZeroThresold = TBD TimeToRetainScore = TBD

**Topic Config:**
TopicName = blocks MessageRate = 120/s MessageSize = 2KB
Peer Score Parameters:
TopicWeight = 0.25
TimeinMeshWeight = 0.0027 TimeinMeshQuantum = "1s" TimeinMeshCap = 3600.0 FirstMessageDeliveriesWeight = 0.664 FirstMessageDeliveriesDecay = 0.9916 FirstMessageDeliveriesCap = 1500.0 MeshMessageDeliveriesWeight = -0.25 MeshMessageDeliveriesDecay = 0.997 MeshMessageDeliveriesCap = 400.0 MeshMessageDeliveriesThreshold = 10.0 MeshMessageDeliveriesActivation = "1m" MeshMessageDeliveryWindow = "5ms" MeshFailurePenaltyWeight = -0.25 MeshFailurePenaltyDecay = 0.997
InvalidMessageDeliveriesWeight = -99.0 InvalidMessageDeliveriesDecay = 0.9994

##TESTS

**TEST 1 -Delivery Latency Gossipsub-v1.1 - Baseline Scenario ​(No attackers)**
N_PUBLISHERS = 100 N_LURKERS = 900 N_ATTACKER_NODES = 0

**TEST 2 - Eclipse Attack Against a Single Target**
N_PUBLISHERS = 100
N_LURKERS = 900
N_ATTACKER_NODES = 1000
AttackBehaviour = target a single node
the attack nodes are introduced 1 min into the test WarmupTime : 30s

**TEST 3 - ​Eclipse Attack Against the Entire Network N_PUBLISHERS = 100**
N_LURKERS = 900
N_ATTACKER_NODES = 4000
AttackBehaviour: target every node
Sybils establishing 100 honest connections each WarmupTime : 30s

**TEST 4 - ​Eclipse Attack Against all Publishers N_PUBLISHERS = 100**
N_LURKERS = 900
N_ATTACKER_NODES = 4000
AttackBehaviour = Target Publishers Only
Sybils establishing 100 honest connections each WarmupTime : 30s

**TEST 5 - ​Censor Attack Against a Single Target N_PUBLISHERS = 100**
N_LURKERS = 900
N_ATTACKER_NODES = 2000
Sybils establishing 100 honest connections each warm-up period is 30 sec
AttackBehaviour = Censor Target Node

**TEST 6 - ​Network Degradation Attack N_PUBLISHERS = 100**
N_LURKERS = 900 N_ATTACKER_NODES = 2000
warm-up period is 30 sec
attack nodes are introduced 1min into the test

**TEST 7 - Cold Boot Attack**
N_PUBLISHERS = 100
N_LURKERS = 900
N_ATTACKER_NODES = 4000
Nodes join all together at time 0
Publishers start publishing at the 30s mark in the test run. (is this a consequence or a test parameter?)
opportunistic grafting period is set to 10 sec,in order to get meaningful results out of this test, whereas this parameter is set to 1 min in real deployments.
(which parameter is it?)
Increasing the gossip factor to 0.4 results in a p99 latency of 1.177 sec without opportunistic grafting and 1.027 with opportunistic grafting

**TEST 8 - ​Covert Flash Attack**
 N_PUBLISHERS = 100 N_LURKERS = 900 N_ATTACKER_NODES = 4000 Sybils join at time 0
Publishers start publishing at the 30s mark
SybilAttackDelay = 120s (Sybil behaves properly for 2 minutes before attacking)
TestRuntime = 5min
opportunistic grafting period is set to 10 sec whereas this parameter is set to 1 min in real deployments.

**TEST 9 -Attack at Dawn**
N_PUBLISHERS = 100
N_LURKERS = 900
N_ATTACKER_NODES = 4000
Sybils starts at time 0
opportunistic grafting period is set to 10 sec ​whereas this parameter is set to 1 min in real deployments. honest peers and the Sybils connect concurrently at time 0 N_ATTACKER_PEERS_FOR_CONTAINER = 160
Publishers begin publishing messages after 30s.
Exclusively for this test, we set a value of -100 for the 𝑃​6 ​parameter weight; the parameter was disabled in the previous tests in order to allow us to pack multiple Sybils per container and achieve high sybil:honest connection ratios.

###Questions about general parameters:
1)​ Is overlayD=D?
2) ​If Opportunistic grafting takes place every minute: does it mean that O​ pportunisticGraftHeartbeatTicks= 60? Or there should be another parameter to set?
3)​ ​“The attack nodes are introduced 1 min into the test” : Does it mean that ​AttackerConnectionDelay = 60s ? 4) ​“Sybils establishing 100 honest connections each” : does it mean that AttackDegree=100 ?
5)​ Does “Nodes join all together at time 0” mean that ​AttackerConnectionDelay = 0s and HonestPeerConnectionDelay=0s?
6) ​“Publishers start publishing at the 30s mark in the test run”: which parameter should represent this? 7)​ To which parameter does the “𝑃​6 p​ arameter weight” actually corresponds?
8) ​Is the following information useful to understand how some of the “TBD” parameters need to be set? 

>The primary load is 2.5k to 25k attestations ( 250 B per message) per minute (sent in bursts every 12
>seconds, split across 16-64 topics). Expected somewhere between 1/256 to 1/64 nodes on each topic. – Additional loads are larger blocks (10 KB to 100 KB). 5 per minute on a single global topic
>– The attestation broadcasting full propagation can likely take in the 3-sec range, followed by a (large) 1-sec buffer with the aggregates being broadcast at 4 sec.
>Block rate: 10 blocks/min (5 blocks per round with round duration 30 sec) • Transaction rate: 2-4 transactions/second

9) ​Is there any other considerations that makes us able to deduct what are the values of “TBD” parameters?
