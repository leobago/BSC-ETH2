# BSC-ETH2 Altona Validator
This README file includes all the needed information and guides to run an ETH2  Beacon-Node and Validator on the Altona testnet.

## Overview
The information and guides that will be attached to the document were the ones used to run the [Lighthouse Ethereum 2.0 Client](https://lighthouse-book.sigmaprime.io/become-a-validator.html) on a Raspberry pi 4 4GB on the [Altona Testnet](https://github.com/goerli/altona).

Link to our [BSC-ETH2 Validator](https://altona.beaconcha.in/validator/a2b60b956869fd5dfe9874546b3cc4bc2ca42bcc3b9c48c8473b7881c4e94b4a57917b07bf0b22117c90daf2f59c2dde#overview)

## Hardware
- Raspberry pi 4 (4GB) (In hour case running [Ubuntu Server 20.04 for Raspberry Pi](https://ubuntu.com/download/raspberry-pi/thank-you?version=20.04&architecture=arm64+raspi))
- MicroSD card (32GB)
- Ethernet connection
- Standard peripherals 
- (Working on) 1TB HDD external drive as storage for the beacon blockchain

## Followed Guide
As it is shown on the [Lighthouse website](https://lighthouse-book.sigmaprime.io/become-a-validator.html) there are two ways of running a lighthouse validator:
- [Dockers](https://lighthouse-book.sigmaprime.io/become-a-validator-docker.html)
- [Buildig from source](https://lighthouse-book.sigmaprime.io/become-a-validator-source.html)

In our case, we decided to run the validator from source. We installed and configured the client in the Raspberry pi following [this guide](https://www.coincashew.com/coins/overview-eth/guide-how-to-stake-on-eth-2.0-altona-testnet-with-lighthouse-on-ubuntu).

For the step 12th "Send the validator deposit" you will need to have at least 32ETH from the Goerli testnet (non real money. Please be sure you DON'T USE real ETH) on your Goerli Metamask wallet. In case you don't have the 32ETH you can easily get them from the community asking for them on the [Lighthouse Discord](https://discord.com/invite/cyAszAh) or on the [Goerli Testnet Gitter](https://gitter.im/goerli/testnet). For that you will need to give them your wallet address. 

## Additional Information

#### Monitoring
Monitoring the status of your validator will be essential to check if all the processes were properly done, as the proper operation of the block Attestation and Proposition processes. Once the validator is working, you can easily find it on the [beaconcha.in](https://altona.beaconcha.in/).

#### Problems or doubts
If you experience problems while setting up or while running the Beacon-Node or the Validator you can openly expose your concerns in the [Lighthouse Discord](https://discord.com/invite/cyAszAh), [Goerli Testnet Gitter](https://gitter.im/goerli/testnet) or [Eth R&D Discord Server](https://discord.com/invite/VmG7Uxc).

We are facing some unexpected desconnection of the beacon node every 1-2 days. The post will be updated as soon as we find out the causes and the solutions. 

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
As next steps on the BSC-ETH2 project, we are considering on moving the Lighthouse client into a Docker based implementation, as well as including on the same raspberry pi more validators based on other available clients as:
- Nimbus
- Prysm
- Teku

## Related Information
- [Small Ethereum 2.0 overview](https://ethos.dev/beacon-chain/).
- Lighthouse [RESTful JSON HTTP API](https://lighthouse-book.sigmaprime.io/http.html).
- [Metamask Website](https://metamask.io/) for the ETH wallet.

