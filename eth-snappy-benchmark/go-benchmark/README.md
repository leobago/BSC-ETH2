# eth-snappy-test

Benchmark code to meassure the compression ratio and speed of the snappy compressor(golang version).

The code reads all the json files of the given folder and start making the compression and decompression giving the average of the compress ratio and speed.

## Usage

1. git clone the repository
2. Build the go code
    ´go build -o snappy´
3. Run the code (by default reads the .json files in the /data folder)
    ´./snappy´

Note: the code will print the compression results on the stdout by default, ´./snappy > <filename.txt>´ if you want to save the results in a file
    
## Experimental Setup

We ran the Go version of snappy (github.com/golang/snappy) v0.0.1 on a Intel(R) Core(TM) i5-6600K CPU @ 3.50GHz with Go version 1.14. 

## Results

Here we provide a summary of wath we found, but all the results can be found in the following spreadsheet:
https://docs.google.com/spreadsheets/d/1SoXvmPfm1BRVcdDm7CuwaWDjxp5a3NzGMBLViQjBNqA/edit?usp=sharing

### Standard Snappy Benchmarks

To get an idea of what to expect, and make sure our numbers were comparable to standard snappy compression numbers, we ran the integrated benchmarks that come with the snappy compressor, in the same experimental setup that we run the ethereum block compression experiments. We got an average compression speed of 789 MB/s.

### Eth1

We tested snappy on 15 blocks downloaded from the Ethereum main chain. We ran the test 10 times for each block and we always obtained the exact same compressed result for each block, but the compression time changes, so we take the average of the 10 runs. We got an average **compression ratio of 1.850**, the minimum compression ratio observed was 1.507 and the maximum 2.416. The average **compression speed was 508 MB/s**, and we observed some variation on these numbers, going from 380 MB/s for the lowest to 785 MB/s for the fastest. We also noticed that in general decoding is almost twice faster than encoding, with the compression taking about 282µs for a ~100KB block, but only 149µs for decoding.

### ETH2

We tested snappy on 19 blocks downloaded from the ethereum2.0 Altona blockchain. We ran the test 10 times for each block and we always obtained the exact same compressed result for each block, but the compression time changes, so we take the average of the 10 runs. We got an average **compression ratio of 1.635**, the minimum compression ratio observed was 1.283 and the maximum 2.049. The average **compression speed was 911 MB/s**, and we observed some variation on these numbers, going from 476 MB/s for the lowest to 1235 MB/s for the fastest. We also noticed that in general decoding is over twice faster than encoding, with the compression taking about 7.5µs for a ~6KB block, but only 3.2µs for decoding.

Note: the missing blocks on the eth2-data were blocks that were missed (not proposed).
