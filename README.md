# BSC-ETH2
This repository compiles the work that the BSC team does on Eth2.0.

##Overview
This study attempts to test the performance of the GossipSub version 1.1.0 protocol implementation in go-libp2p-pubsub, with the aim of comparing the GossipSub version 1.1.0 to GossipSub version 1.0.0, testing its robustness in terms of scalability and its resilience against potential attacks. It, ultimately, seeks to analyze the performance of go-libp2p-pubsub within the constraints and rules of Ethereum 2.0. 

##Objective
1. Comparison between GossipSub 1.1.0 and GossipSub 1.0.0 to identify the characteristics of the new version.
2. Testing Scalability in GossipSub 1.1.0.
3. Examine GossipSub 1.1.0 parameters stretchability. 
4. Assessing the resilience of GossibSub to potential attacks.

##Methodology 
This study will be divided into a number of phases. In each phase the collected data will be analyzed and visualized in order to obtain a comprehensive view.

###Phase 1:
Establish a stable GossipSub network for each version of GossipSub (1.1.0 and 1.0.0). In doing so, we should be able to characterize the performance of each network and identify their differences as well as their pros and cons.

###Phase 2:
Taking advantage of the resources available at Barcelona Supercomputing Center, In this phase we will focus on the scalability of the GossipSub version 1.1.0 by deploying various networks with different numbers of nodes. The objective of this phase is to test the performance and robustness of the protocol in terms of scalability trying to go beyond the tested number of nodes in relevant up to date studies. Concurrently, we will examine go-libp2p-pubsub’s parameter stretchability of each network established for each scale of experimentation.

###Phase 3:
Emulation of different types of attack with the purpose of assessing GossipSub 1.1.0 resilience, by looking at aspects of liveliness of nodes and the redundancy of publications and subscriptions, among others.

###Phase 4:
Applying the measures used in the previous phases especially for analyzing scalability, stretchability and resilience of GossipSub 1.1.0 within the constraints and parameter specifications adopted by Ethereum 2.0, to assess the overall performance of GossibSub 1.1.0.


