# *BSC Approach to rumor*

This repository compiles the work that the BSC-ETH2 team does while using rumor, along with a small starting guide that aims to get the basics for the incoming rumor based projects.

## *Introduction to rumor*

This section contains a small introduction summary to [rumor](https://github.com/protolambda/rumor). The documentation, information and tips written on this document will be based on the official documentation offered by [protolambda](https://notes.ethereum.org/@protolambda/rumor-tutorial#How-to-use-it) and our own experience obtained while learning about it. 

### *Definition of Rumor*

Rumor is an interactive shell that lets you generate custom p2p hosts in an Eth2 client environment. The  main purpose of rumor is to offer a detailed debugging into Logs/Jsons of any process that the host/client handles (peers, RCP connections, gossipsub protocol, etc...). Making it the perfect tool for debugging a Eth2 client or even the perfect way to explore the limits of the client itself and the network. 

### *Getting started with rumor*

#### Installing rumor 

To install rumor:
´~$ git clone git@github.com:protolambda/rumor.git´
´~$ cd rumor´
´$ go get ./...´
´$ go build -o rumor´

#### Run rumor
 
Rumor offers several options to run it:
´ attach      Attach to a running rumor server
  bare        Rumor as a bare JSON-formatted input/output process
  file        Run from a file
  help        Help about any command
  serve       Rumor as a server to attach to (IPC/TCP/WS socket)
  shell       Rumor as a human-readable shell´

The most important ones, from our point of view, are `file`, `shell` and `serve`. 

Taking into account that the beginning to rumors can be a bit tricky, we would suggest you to start by using the `$rumor shell` (NOTE: if your terminal session doesn’t recognize the command `rumor` , check if the folder `~/rumor` is included to the `$PATH` ). Once you get used to the tool you will be able to automate a few steps/processes by generating `.rumor` files that can be executed on a rumor shell by typing on the shell `include <file.rumor>`. 

The files `.rumor` are files that contain lists of shell commands. This means that any set of commands that you can type on the shell, you could gather them on a  `.rumor` file and just execute them with a single command `>include file.rumor`. Let’s  demonstrate it with an example:
This will include commands that are explained on the [documentation](https://notes.ethereum.org/@protolambda/rumor-tutorial#How-to-use-it) and that we will explain later in more detail.

In this first example we are going to see the implementation of the “shell + files” by starting a p2p host in different ways.

Generating a host just with the shell (run `$rumor shell` on a terminal)

`$ rumor shell`

`>> host start`

`>> host notify all`

`>> host listen`

Generating a file.rumor that starts the host

Create a `host-start.rumor` file with your favourite code editor and paste the following commands on it:

`host start`

`host notify all`

`host listen`


Save the file and open a new `$rumor shell` on a new terminal.

`$ rumor shell`

`>> include host-start.rumor`

You should see that both outputs are the same on both terminals. This feature is very useful to save us time typing the same commands every time.

Note: We recommend you to organize all your rumor scripts in folders, and remember to parse the path to the script from the working directory from where you are launching the rumor shell.  
e.g. 

`>> include rumor-test/host-start.rumor`


#### Actors

So far, we just started a single host on a rumor shell but rumor offers the figures of actors so you can generate many host on the same session while you are able to configure then on the go.

Let's make a single example to understand this in a better way.

On a `$ rumor shell` :

`$ rumor shell`

`>> alice: host start`

`>> alice: host notify all`

`>> alice: host listen`

Adding a “string + :” before a command, executes the command after the “ : ” on the actor environment, or generates a new actor with that name if it doesn't exist already.

Rumor offers another alternative to the use of actors, that serves the same purpose as `su` command on the terminal. By typing `<actor name>: me` all the following commands will refer to the specified actor.

On a new `$ rumor shell` :

`$ rumor shell`

`>> alice: me`

`>> host start`

`>> host notify all`

`>> host listen`

Check that the output logs have the same format as the previous test. On the logs, the actor name is specified between “[ ]”.

Rumor also allows to run a script on a specified actor.

`$ rumor shell`

`>> alice: include host-start.rumor`

`$ rumor shell`

`>> bob: me`

`>> include host-start.rumor`

#### Interaction with the rumor shell

Rumor is an interactive shell that has some *Bash* features. Meaning that we can use the basic shell script statements to generate our rumor scripts (statements, loops, variables, ect...) plus other functionalities that rumor adds (check [How to use it / Commons](https://notes.ethereum.org/@protolambda/rumor-tutorial#Commons) chapter on the official guide).

#### Rumor functionalities

Since rumor aims to debug Eth2 clients, it offers a huge variety of commands that let you build your custom p2p host and Eth2 client and manage the interaction between them. 

The list of commands and parameters that can be set is large and it goes increasing with the time, so might happen that parameters, commands or scripts get updated or included with the time.

For a big overview of the functionality that rumor offers check the [functionality section](https://notes.ethereum.org/@protolambda/rumor-tutorial#Functionality). 

Note: If you have any doubt about a specific command or flags that have to be parsed to commands, you can simply type `<comand> --help` on a rumor shell to get a description of the usage and the flags that can be parsed.

e.g. 

`$ rumor shell`

`>> host start --help`

Note: To get a deeper knowledge of the parameters or even the functionalities, you can visit the [Eth2 hacker start guide](https://notes.ethereum.org/@protolambda/eth2_start) were all the needed documentation is linked or provided. 


#### Incoming work

We are currently working on a detailed explanation of the rumor basic functionalities, along with examples that will help to understand their purpose.

We are actively working on a rumor based attack test on the medalla testnet, aiming to check the robustness of the network and explore possible vulnerabilities on the Libp2p GossipSub protocol.