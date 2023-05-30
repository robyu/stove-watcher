#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>

std::vector<int> readJPG(const std::string& filename, int& width, int& height) {
    cv::Mat image = cv::imread(filename, cv::IMREAD_COLOR);

    if (image.empty()) {
        throw std::runtime_error("Failed to read image: " + filename);
    }

    width = image.cols;
    height = image.rows;

    std::vector<int> pixelValues;
    pixelValues.reserve(width * height);

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            cv::Vec3b pixel = image.at<cv::Vec3b>(y, x);
            int red = pixel[2];
            int green = pixel[1];
            int blue = pixel[0];

            int rgbValue = (red << 16) | (green << 8) | blue;
            pixelValues.push_back(rgbValue);
        }
    }

    return pixelValues;
}

// Function to convert RGB values to hex format
std::vector<std::string> convertToHex(const std::vector<int>& rgb, int width, int height) {
    std::vector<std::string> hexValues(width * height);

    for (int i = 0; i < width * height; ++i) {
        int r = (rgb[i] >> 16) & 0xFF;
        int g = (rgb[i] >> 8) & 0xFF;
        int b = rgb[i] & 0xFF;

        // Convert RGB values to hex format: 0xRRGGBB
        std::string hexValue = "0x";
        hexValue += ((r < 16) ? "0" : "") + std::to_string(r);
        hexValue += ((g < 16) ? "0" : "") + std::to_string(g);
        hexValue += ((b < 16) ? "0" : "") + std::to_string(b);

        hexValues[i] = hexValue;
    }

    return hexValues;
}

// Test case for readJPG and convertToHex functions
void testReadJPG() {
    std::string filename = "example.jpg";
    int width, height;
    std::vector<int> pixels = readJPG(filename, width, height);

    std::vector<std::string> hexValues = convertToHex(pixels, width, height);

    // Print the hex values for verification
    for (const auto& hexValue : hexValues) {
        std::cout << hexValue << std::endl;
    }
}

// Entry point of the program
int main() {
    // Run the test case
    testReadJPG();

    return 0;
}
