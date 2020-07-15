#include <fstream>
#include <chrono>
#include <ctime>
#include <iostream>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <jsoncpp/json/json.h>
#include <stdio.h>
#include "snappy/snappy.h"

using namespace std;

void findMinAndMax (vector<float> vec, float * min, float * max){
    int i;
    *min = vec[0];
	*max = vec[0];
	for ( i = 0 ; i < vec.size() ; i++) {
		if (vec[i] < *min) {
			*min = vec[i];
		}
		if (vec[i] > *max) {
			*max = vec[i];
		}
	}
}

int main(int argc, char* argv[]) {
    const char *folderName;
    
    DIR *dp;
    struct dirent *entry;

    int i;

    long sizeBlock = 0;
    long sizeBlockCompress = 0;

    if (argc < 2){
        folderName = "./eth2-data";
    }else{
        folderName = argv[1];
    }

    cout << "Folder name: "<< folderName << endl;

    // Iteration through the files of the data folder where the .json for the tests are located
    dp = opendir(folderName);
    if (dp != nullptr) {
        while ((entry = readdir(dp))){
            // Parse the files that are in the folder
            if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")){
                continue;
            }else{
                // Routine for reading the block.json and run the benchmark
                // Definition of the variables
                vector<float> avgCompressRatio = {};
                vector<float> avgCompressSpeed = {}; 
                vector<float> avgEncodeSpeed   = {};
                vector<float> avgDecodeSpeed   = {};

                sizeBlock = 0;
                sizeBlockCompress = 0;

                
                // Run the comrpession test 10 times for each block to get an average
                for (i = 0; i < 10; i++){
                    
                    // Set up the proper path to open the json file
                    string folder(folderName);
                    string path = folder + "/" + string(entry->d_name);

                    // Open .json file
                    std::ifstream jsonfile(path);

                    if (jsonfile.is_open()) { 
                        // Initialize the arrays
                        string output;
                        string output_uncom;

                        float compressRatio = 0;
                        float compressSpeed = 0;

                        // get length of file and set pointer of the file to the beginning:
                        jsonfile.seekg (0, jsonfile.end);
                        int length = jsonfile.tellg();
                        jsonfile.seekg (0, jsonfile.beg);
                        
                        // Define a file were the json will be loaded
                        char buffer[length];
                        
                        // read data as a block:
                        jsonfile.read (buffer,length);
                 
                        string block(buffer);

                        sizeBlock = block.size();
                        
                        // ---- Compression starts ----
                        // Run timer1
                        auto t1 = std::chrono::high_resolution_clock::now();
                        snappy::Compress(block.data(), block.size(), &output);

                        // Run timer2
                        auto t2 = std::chrono::high_resolution_clock::now();
                        
                        // Get the difference between both timers (nanoseconds)
                        float encodetime = std::chrono::duration_cast<std::chrono::nanoseconds>( t2 - t1 ).count();

                        sizeBlockCompress = output.size();

                        // ---- Decompression starts ----
                        // Run timer3
                        auto t3 = std::chrono::high_resolution_clock::now();
                        snappy::Uncompress(output.data(), output.size(), &output_uncom);

                        // Run timer4
                        auto t4 = std::chrono::high_resolution_clock::now();
                        
                        // Get the difference between both timers (nanoseconds)
                        float decodetime = std::chrono::duration_cast<std::chrono::nanoseconds>( t4 - t3 ).count();

                        if (i == 0){
                            cout << entry->d_name << " - Block size (bytes): "<< sizeBlock << " - Block size compressed (bytes): "<< sizeBlockCompress << endl;    
                            cout << "Encoding time (µs); Decoding time (µs); Compression ratio ; Compression Speed (MB/s)" << endl;               
                        }
/*
                        cout << "Encode Time: " << encodetime << endl;
                        cout << "Decode Time: " << decodetime << endl;
*/

                        // Pass the readed time to micoseconds
                        encodetime = encodetime/1000.0;
                        decodetime = decodetime/1000.0;

                        compressRatio = ((float)sizeBlock / (float)sizeBlockCompress);
                        compressSpeed = (sizeBlock /encodetime);

                        // Print the resultos on the stdout
                        cout << encodetime << ";" << decodetime << ";" << compressRatio << ";" << compressSpeed << endl;

                        // Insert new meassurements to the avg vectors
                        avgCompressRatio.insert(avgCompressRatio.end(),compressRatio);
                        avgCompressSpeed.insert(avgCompressSpeed.end(),compressSpeed);
                        avgEncodeSpeed.insert(avgEncodeSpeed.end(),encodetime);
                        avgDecodeSpeed.insert(avgDecodeSpeed.end(),decodetime);

                    }else{
                        cout << "Error trying to open: " << entry->d_name << endl;
                    }

                    jsonfile.close();
                }


                // Analyze the average of each block
                float avgRatio = 0;
                float avgSpeed = 0;
                float avgEncode = 0;
                float avgDecode = 0;
                float ratioMin = 0, ratioMax = 0;
                float speedMin = 0, speedMax = 0;
                float EncodeMin = 0, EncodeMax = 0;
                float DecodeMin = 0, DecodeMax = 0;


                int j; 
                // Run stadistics of the taken averages
                for (j = 0; j < avgCompressRatio.size(); j++) {
                    avgRatio = avgRatio + avgCompressRatio[j];
                    avgSpeed = avgSpeed + avgCompressSpeed[j];
                    avgEncode = avgEncode + avgEncodeSpeed[j];
                    avgDecode = avgDecode + avgDecodeSpeed[j];
                }
                avgRatio = avgRatio / avgCompressRatio.size();
                avgSpeed = avgSpeed / avgCompressRatio.size();
                avgEncode = avgEncode / avgCompressRatio.size();
                avgDecode = avgDecode / avgCompressRatio.size();

                findMinAndMax(avgCompressRatio, &ratioMin, &ratioMax);
                findMinAndMax(avgCompressSpeed, &speedMin, &speedMax);
                findMinAndMax(avgEncodeSpeed, &EncodeMin, &EncodeMax);
                findMinAndMax(avgDecodeSpeed, &DecodeMin, &DecodeMax);

                cout << EncodeMin << ";" << DecodeMin << ";" << ratioMin << ";" << speedMin << " MINIMUM"<< endl;
                cout << avgEncode << ";" << avgDecode << ";" << avgRatio << ";" << avgSpeed << " AVERAGE"<< endl;
                cout << EncodeMax << ";" << DecodeMax << ";" << ratioMax << ";" << speedMax << " MAXIMUM"<< endl;

                cout << "" << endl;

            }
        }
    }
    else{
        cout << "Folder name: " << folderName << " doesn't exist" << endl;
    }
    


    closedir(dp);
    cout << "" << endl;
    cout << "Test Finished" << endl;

}