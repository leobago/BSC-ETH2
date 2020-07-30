# BSC-ETH2 Altona Validator
This README file includes all the needed information and guides to run four ETH2 Beacon-Nodes and Validators on the Altona testnet from the four main clients.

## Overview
The information and guides that will be attached to the document were the ones used to run the [Lighthouse Ethereum 2.0 Client](https://lighthouse-book.sigmaprime.io/become-a-validator.html), [Prysm Client](https://kb.beaconcha.in/tutorial-eth2-multiclient/prysm-client/macos-prysm/docker-beaconnode-and-validator-macos#start-the-beaconnode), [Nimbus Client](https://status-im.github.io/nim-beacon-chain/intro.html) and [Teku Client](https://docs.teku.pegasys.tech/en/latest/) on the [Altona Testnet](https://github.com/goerli/altona). All of the validators are running on a laptop with an Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz.

## Hardware
- Asus Laptop with an Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz (8GB RAM) (In our case running [Ubuntu 20.04 LTS](https://releases.ubuntu.com/20.04/))
- SSD 250GB
- 802.11ac WIFI card

## Setup of the beacon-node and the validator
For sending the validator deposit you will need to have at least 32ETH from the Goerli testnet (non real money. Please be sure you DON'T USE real ETH) on your Goerli Metamask wallet. In case you don't have the 32ETH you can easily get them from the community asking for them on the [Prysmatic Labs Discord](https://discord.com/invite/cyAszAh). You can easily get them typing !send ETH_ADDRESS on the #request-goerli-eth channel.

Wait until the beacon-node is synced with the head of the beacon-chain to make the deposit, otherwise your validator will not be able to start making the attestations and will be slashed.

### Lighthouse
As it is shown on the [Lighthouse website](https://lighthouse-book.sigmaprime.io/become-a-validator.html) there are two ways of running a lighthouse validator:

- [Dockers](https://lighthouse-book.sigmaprime.io/become-a-validator-docker.html)
- [Buildig from source](https://lighthouse-book.sigmaprime.io/become-a-validator-source.html)

In our case, we decided to run the validator on dockers following the official [guide](https://www.coincashew.com/coins/overview-eth/guide-how-to-stake-on-eth-2.0-altona-testnet-with-lighthouse-on-ubuntu). All the needed files can be found on the [git repository](https://github.com/sigp/lighthouse-docker) and on [docker hub](https://hub.docker.com/r/sigp/lighthouse).

Notes: 
    - Before launching the 'docker-compose up' on the lighthouse-docker repository, swap the images for the beacon-node and validator.
        From: sigp/lighthouse:latest -> To: sigp/lighthouse:medalla

    This is the latest stable version offered by lighthouse (29-07-2020). 
    The Genesis block will be released in a few days so don't panic if your validator is not working or shows an error while running.

### Prysmatic labs
There are three ways of running the beacon-node and the validator from [Prysmatic Labs](https://kb.beaconcha.in/tutorial-eth2-multiclient/prysm-client/macos-prysm/docker-beaconnode-and-validator-macos#start-the-beaconnode):

- [Installation Script](https://docs.prylabs.network/docs/install/linux)
- [Dockers](https://docs.prylabs.network/docs/install/lin/docker)
- [Bazel](https://docs.prylabs.network/docs/install/lin/bazel)

We decided to run them on dockers with [this guide](https://kb.beaconcha.in/tutorial-eth2-multiclient/prysm-client/macos-prysm/docker-beaconnode-and-validator-macos#start-the-beaconnode). 

Notes:
    - If you try to run the four different beacon-nodes and validators on the same machine, might happen that they report errors because they try to use the same ports. 

### Nimbus
For the Nimbus option, as they claim that "At the moment, Nimbus has to be built from source." so there was no other option than build the validator from source. All the needed information and files can be found in the official [git repository](https://github.com/status-im/nim-beacon-chain) and the [docu website](https://status-im.github.io/nim-beacon-chain/intro.html)

### Teku
To install the Teku version of the altona validator, PegaSys offers three possible options:
- [Binary distribution](https://docs.teku.pegasys.tech/en/latest/HowTo/Get-Started/Install-Binaries/)
- [From source](https://docs.teku.pegasys.tech/en/latest/HowTo/Get-Started/Build-From-Source/)
- [Docker image](https://docs.teku.pegasys.tech/en/latest/HowTo/Get-Started/Run-Docker-Image/)

We decided to choose to build the Teku validator from source. For the setup of the validator, [this guide](https://medium.com/@steve.berryman/installing-and-running-an-ethereum-2-pegasys-teku-validator-on-the-altona-testnet-e3b9a0989a52) was followed.

## Additional Information

#### Monitoring
Monitoring the status of your validator will be essential to check if all the processes were properly done, as the proper operation of the block Attestation and Proposition processes. Once the validator is working, you can easily find it on the [beaconcha.in](https://altona.beaconcha.in/).

#### Problems or doubts
If you experience problems while setting up or while running the Beacon-Node or the Validator you can openly expose your concerns in the discord and gitter channels showed below:
- [Lighthouse Discord](https://discord.com/invite/cyAszAh).
- [Prysmatic Labs Discord](https://discord.com/invite/cyAszAh).
- [Nimbus Discord](https://discord.gg/XRxWahP).
- [Teku Discord](https://discord.com/invite/7hPv2T6)

- [Goerli Testnet Gitter](https://gitter.im/goerli/testnet).
- [Eth R&D Discord Server](https://discord.com/invite/VmG7Uxc).

#### Validator is missing attestations or missing block proposal
[Link](https://www.reddit.com/r/ethstaker/comments/g9dbug/what_causes_missed_attestations/) to the reddit discussion where the possible causes are explained.

#### Edit validator name
1. Go to your Validator overview page on beaconcha.in ([Our page](https://altona.beaconcha.in/validator/4384#overview) as example).
2. Click on the NAME field.
3. Type custom name.
4. Go to [MyCrypto](https://www.mycrypto.com/sign-and-verify-message/sign). On the "Sign Message" tab, select Web3 and allow Metamask extension to connect MyCrypto.
5. Write "beaconcha.in" in the message field.
6. Click Sign Message on MyCrypto and on Metamask wallet.
7. Copy the json format signature and paste it on the pop up message on the beaconcha.io.

## Future Work
As next steps on the BSC-ETH2 project, the team aims to test the robustness of the network, emulating attacks on the libp2p Gossipsub protocol and on the Altona testnet if possible. 

## Related Information
- [Small Ethereum 2.0 overview](https://ethos.dev/beacon-chain/).
- Lighthouse [RESTful JSON HTTP API](https://lighthouse-book.sigmaprime.io/http.html).
- [Metamask Website](https://metamask.io/) for the ETH wallet.

