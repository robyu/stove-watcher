#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <iomanip>
#include <opencv2/opencv.hpp>

std::vector<std::uint32_t> readJPG(const std::string& filename, int& width, int& height) {
    cv::Mat image = cv::imread(filename, cv::IMREAD_COLOR);

    if (image.empty()) {
        throw std::runtime_error("Failed to read image: " + filename);
    }

    width = image.cols;
    height = image.rows;

    std::vector<std::uint32_t> rgbValues;
    rgbValues.reserve(width * height);

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            cv::Vec3b pixel = image.at<cv::Vec3b>(y, x);
            int red = pixel[2];
            int green = pixel[1];
            int blue = pixel[0];

            std::uint32_t rgbValue = (red << 16) | (green << 8) | blue;
            rgbValues.push_back(rgbValue);
        }
    }

    return rgbValues;
}

void prettyPrintHex(const std::vector<std::uint32_t>& values,
                    int numValuesToPrint,
                    int numValuesPerLine) {

    for (int i = 0; i < std::min(numValuesToPrint, static_cast<int>(values.size())); ++i) {
        std::cout << "0x" << std::setfill('0') << std::setw(6) << std::hex << values[i] << " ";
        if ((i + 1) % numValuesPerLine == 0) {
            std::cout << std::endl;
        }
    }				
}

// Entry point of the program
#if 0
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file>" << std::endl;
        return 1;
    }

    std::string inputFilename = argv[1];

    // Call the readJPG function with the input filename
    int width;
    int height;
    std::vector<std::uint32_t> rgbValues = readJPG(inputFilename, width, height);

    std::cout << "Read file " << inputFilename << " ("<< width << ", " << height << ")" << std::endl;
    
    
    prettyPrintHex(rgbValues, 10, 5);


    return 0;
}
#endif
