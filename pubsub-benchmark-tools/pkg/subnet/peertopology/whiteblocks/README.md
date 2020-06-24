# Whiteblocks Peering Algorithm

The Whiteblocks peering algorithm can be found in the readme of their [test suite](https://github.com/whiteblock/p2p-tests/blob/master/README.md), and has been included below for convenience.


## Network Topology 
![Network Topology](/topology.png)

For demonstrative purposes, the above illustration provides a high-level view into the peering algorithm defined in the following section. Within most topologies, peering with every other node within the network is ineffective and likely impossible. Within a live, global network, we can assume that
nodes will be organized according to the defined topology. 

For example, a (cluster specific) node within Cluster 1 may be peered with N number of nodes within its own cluster, however, based on proximity, certain nodes on the edge of this cluster may also be peered with nodes within Cluster 2 (inter cluster nodes). If Node X within Cluster 1 would like to transmit a message to Node Y within Cluster 4, these messages must propogate through each consecutive cluster in order to reach its destination. 

While this topology may present an oversimplification, within most cases, we can expect the results to be reflective of real-world performance. As we establish an appropriate dataset that is indicative of baseline performance, we can develop additional test series' and cases for future test phases. 

Since peer discovery is outside the scope of work for this test phase, peering within the client implementation presented within this repository is handled statically. 

## Peering Algorithm

```
Let n be the number of nodes in the network
Let c be the max peer list size
Let out be the list of peers for each node, such that out[n] is the list of peers for n
Let rand(i) be the function which gives a random value R, where R∈[0,i)
Let e be the next peer to ensure existence in the network

e := 0
∀ i ∈ [0, n):
  ∀ j ∈ [1, min(c, i)]:
    while:
       p := rand(j) 
       iff e < i, then  p := e,  e := e + 1.
       iff ¬ p ∈ out[i] and p ≠ i, then out[i][|out[i]| - 1] := p, else goto while.
```


This algorithm is designed to provide 3 guarantees. 

1) There will exist a path between all nodes in the network, so that no nodes are isolated from the network. 
2) Bootstrap safety in order to reduce the propability of race conditions. Given that all of the nodes start up in order, a node will not have a peer inside of its 
peer list which hasn’t yet been bootstrapped within the network. 
3) A node will not peer with itself. Within these constraints, it will attempt to fill its peer list to the given value for _c_ – first using the previous node 
and then using a random peer which meets the requirements. It is worth noting that nodes with an index <_c_ will not have a peer list of size _c_, as the pool of 
peers they can choose from is smaller than _c_.
