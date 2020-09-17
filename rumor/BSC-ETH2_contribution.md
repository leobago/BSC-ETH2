# BSC-ETH2 contribution to Rumor
This file compiles the work and contributions that the BSC-ETH2 team did and aims to do on Rumor. This work includes:
- Found and reported bugs
- Links to guides and demos
- Ideas that could be implemented
- Contributions to the current development of Rumor
 
 ## The list (Chronological track/record of the events)
 - [x] Suggested adding a command that allows copying the stdout on the given file. Protolambda added the command `grab`. [Link to the commit](https://github.com/protolambda/rumor/commit/10fa08fe1459db3011999ec0d5ad90fe26daadf9)
 - [x] Reported a bug that was causing a panic runtime error while trying to find the status received from the poll command. Protolambda fixed the bug. [Link to the commit](https://github.com/protolambda/rumor/commit/ae4c53209f705bc4b6b1533c5919d4ebed577c4f)
 - [x] Reported a bug that was causing a panic runtime error while trying to poll the status received from the poll command. Protolambda fixed the bug. [Link to the commit](https://github.com/protolambda/rumor/commit/https://github.com/protolambda/rumor/commit/79e277783f0b629a60084377c2f6ea5b2606684b)
 - [x] Spotted a node deadlock on the scripts/dv5.rumor example. Protolambda fixed the bug. [Link to the commit](https://github.com/protolambda/rumor/commit/https://github.com/protolambda/rumor/commit/a50572e6cb7c569fa57845cdcc66ceea2f5becec)
 - [x] Suggested adding a feature to the `dv5 random` command that automatically adds the founded peers to the peerstore without needing the `next` command. Protolambda added the feature with the `-stepwise` and `--interval` flags on the `dv5 random` command. [Link to the commit](https://github.com/protolambda/rumor/commit/https://github.com/protolambda/rumor/commit/0df828c07e9f70ab7060699c919fe687ba8fc4fa)
 - [ ] Spotted misbehaviour on the libp2p host, it wasn't automatically peering peers from the peerstore following the `--lo-peers` and `--hi-peers` flags.
 - [x] Spotted a terminal block/freeze while running the command `gossip log`. Protolambda fixed the bug. [Link to the commit](https://github.com/protolambda/rumor/commit/https://github.com/protolambda/rumor/commit/a944296401a05cdb0895709a6cd3aee54d750d15)
 - [ ] Spotted misbehaviour on the `gossip` implementation. The `gossip` command doesn't connect on the given topic to any of the peers. Making it unable to log the messages/gossips.
 - [ ] Suggested adding the functionality of following the head of the chain (getting the blocks and states) so that we could keep the connections for a longer time. Basically adding the "Full node" functionality.
 
 