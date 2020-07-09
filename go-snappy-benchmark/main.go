package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/golang/snappy"
)

func main() {
	var dataPath = flag.String("path", "/data", "Path of the data for the snappy compression test")
	var suffix = flag.String("suffix", ".json", "Path of the data for the snappy compression test")
	flag.Parse()

	var files []string

	// Get current working directory
	wd, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
	}
	// Add to working directory the path of the folder where all the test are
	wd = wd + *dataPath

	// Get all the names of the json files on the data folder
	err = filepath.Walk(wd, func(path string, info os.FileInfo, err error) error {
		files = append(files, path)
		return nil
	})
	if err != nil {
		panic(err)
	}

	// Iterate through the json files to make the compression test
	for _, file := range files {

		var avgCompresRatio []float64
		var avgCompresSpeed []float64
		var avgEncodeSpeed []float64
		var avgDecodeSpeed []float64

		// get the .json name
		p := strings.Replace(file, wd+"/", "", -1)

		// filter the files that finishes in .json
		if strings.HasSuffix(file, *suffix) {

			// Run the compression test 10 times for each block
			for i := 0; i < 10; i++ {

				// Open our jsonFile
				jsonFile, err := os.Open(file)
				// if we os.Open returns an error then handle it
				if err != nil {
					fmt.Println(err)
				} else {

					// defer the closing of our jsonFile so that we can parse it later on
					// Read the opened jsonFile as a byte array
					byteValue, _ := ioutil.ReadAll(jsonFile)

					// --- Compression Starts ---
					// Start the timer
					start1 := time.Now()
					// Compress the message with the snappy compressor
					compressmsg := snappy.Encode(nil, byteValue)
					// Stop the timer
					codetime := time.Since(start1)
					if err != nil {
						fmt.Println("Encode Failed")
					}

					// --- Descompression Starts ---
					// Run the timer
					start2 := time.Now()
					// Decode the message
					_, err = snappy.Decode(nil, compressmsg)
					decodetime := time.Since(start2)

					if err != nil {
						fmt.Println("Decode Failed")
					}

					// get the data to show it properly
					ctime := float64(codetime) / float64(time.Microsecond)
					dctime := float64(decodetime) / float64(time.Microsecond)

					compressRatio := (float64(len(byteValue)) / float64(len(compressmsg)))
					compressSpeed := (float64(len(byteValue)) / ctime)

					if i == 0 {
						fmt.Printf("%s - Block size(Bytes) %d - Compressed Block size (bytes) %d\n", p, len(byteValue), len(compressmsg))
						fmt.Printf("Encoding time (µs); Decoding time (µs); Compression ratio ; Compression Speed (MB/s)\n")
					}

					fmt.Printf("%.3f;%.3f;%.3f;%.3f\n", ctime, dctime, compressRatio, compressSpeed)

					avgEncodeSpeed = append(avgEncodeSpeed, ctime)
					avgDecodeSpeed = append(avgDecodeSpeed, dctime)
					avgCompresRatio = append(avgCompresRatio, compressRatio)
					avgCompresSpeed = append(avgCompresSpeed, compressSpeed)

					defer jsonFile.Close()
				}
			}
			var avgRatio float64 = 0
			var avgSpeed float64 = 0
			var avgEncode float64 = 0
			var avgDecode float64 = 0

			// Run stadistics of the taken averages
			for i := 0; i < len(avgCompresRatio); i++ {
				avgRatio = avgRatio + avgCompresRatio[i]
				avgSpeed = avgSpeed + avgCompresSpeed[i]
				avgEncode = avgEncode + avgEncodeSpeed[i]
				avgDecode = avgDecode + avgDecodeSpeed[i]
			}
			ratioMin, ratioMax := findMinAndMax(avgCompresRatio)
			speedMin, speedMax := findMinAndMax(avgCompresSpeed)
			EncodeMin, EncodeMax := findMinAndMax(avgEncodeSpeed)
			DecodeMin, DecodeMax := findMinAndMax(avgDecodeSpeed)

			fmt.Printf("%.3f;%.3f;%.3f;%.3f:MINIMUM\n", EncodeMin, DecodeMin, ratioMin, speedMin)
			fmt.Printf("%.3f;%.3f;%.3f;%.3f:AVERAGE\n", avgEncode/float64(len(avgEncodeSpeed)), avgDecode/float64(len(avgDecodeSpeed)), avgRatio/float64(len(avgCompresRatio)), avgSpeed/float64(len(avgCompresSpeed)))
			fmt.Printf("%.3f;%.3f;%.3f;%.3f:MAXIMUM\n", EncodeMax, DecodeMax, ratioMax, speedMax)

			fmt.Printf("\n")

		}
	}
}

func findMinAndMax(a []float64) (min float64, max float64) {
	min = a[0]
	max = a[0]
	for _, value := range a {
		if value < min {
			min = value
		}
		if value > max {
			max = value
		}
	}
	return min, max
}
