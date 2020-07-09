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
    
## Results

We ran the Go version of snappy (github.com/golang/snappy) v0.0.1 on a Intel(R) Core(TM) i5-6600K CPU @ 3.50GHz with Go version 1.14 and tested it on 15 blocks downloaded from the ethereum blockchain. We ran the test 10 times for each block and we always obtained the exact same compressed result for each block, but the compression time changes, so we take the average of the 10 runs. We got an average compression ratio of 1.850, the minimum compression ratio observed was 1.507 and the maximum 2.416. The average compression speed was 508.922 MB/s, and we observed some variation on these numbers, going from 380.042 MB/s for the lowest to 785.055 MB/s for the fastest. We also noticed that in general decoding is almost twice faster than encoding, with the compression taking about 282µs for a ~100KB block, but only 149µs for decoding.

All the results can be found in the following spreadsheet:
https://docs.google.com/spreadsheets/d/1SoXvmPfm1BRVcdDm7CuwaWDjxp5a3NzGMBLViQjBNqA/edit?usp=sharing
