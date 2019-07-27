#include <iostream>

class RawBitMap
{
public:
    RawBitMap() : _data(NULL), _width(0), _height(0){};

    bool Initialise()
    {
        // Set a basic 2 by 2 bitmap for testing.
        //
        if (_data != NULL)
            delete[] _data;

        _width = 2;
        _height = 2;
        _data = new unsigned char[GetByteCount()];

        //
        _data[0] = 0;   // Pixels(0,0) red value
        _data[1] = 1;   // Pixels(0,0) green value
        _data[2] = 2;   // Pixels(0,0) blue value
        _data[3] = 253; // Pixels(1,0)
        _data[4] = 254;
        _data[5] = 255;
        _data[6] = 253; // Pixels(0,1)
        _data[7] = 254;
        _data[8] = 255;
        _data[9] = 0; // Pixels(1,1)
        _data[10] = 1;
        _data[11] = 2;

        return true;
    }

    // Perform a basic 'pixel' enlarging resample.
    bool Resample(int newWidth, int newHeight)
    {
        if (_data == NULL)
            return false;
        //
        // Get a new buuffer to interpolate into
        unsigned char *newData = new unsigned char[newWidth * newHeight * 3];

        double scaleWidth = (double)newWidth / (double)_width;
        double scaleHeight = (double)newHeight / (double)_height;

        for (int cy = 0; cy < newHeight; cy++)
        {
            for (int cx = 0; cx < newWidth; cx++)
            {
                int pixel = (cy * (newWidth * 3)) + (cx * 3);
                int nearestMatch = (((int)(cy / scaleHeight) * (_width * 3)) + ((int)(cx / scaleWidth) * 3));

                newData[pixel] = _data[nearestMatch];
                newData[pixel + 1] = _data[nearestMatch + 1];
                newData[pixel + 2] = _data[nearestMatch + 2];
            }
        }

        //
        delete[] _data;
        _data = newData;
        _width = newWidth;
        _height = newHeight;

        return true;
    }

    // Show the values of the Bitmap for demo.
    void ShowData()
    {
        std::cout << "Bitmap data:" << std::endl;
        std::cout << "============" << std::endl;
        std::cout << "Width:  " << _width << std::endl;
        std::cout << "Height: " << _height << std::endl;
        std::cout << "Data:" << std::endl;

        for (int cy = 0; cy < _height; cy++)
        {
            for (int cx = 0; cx < _width; cx++)
            {
                int pixel = (cy * (_width * 3)) + (cx * 3);
                std::cout << "rgb(" << (int)_data[pixel] << "," << (int)_data[pixel + 1] << "," << (int)_data[pixel + 2] << ") ";
            }
            std::cout << std::endl;
        }
        std::cout << "_________________________________________________________" << std::endl;
    }

    // Return the total number of bytes in the Bitmap.
    inline int GetByteCount()
    {
        return (_width * _height * 3);
    }

private:
    int _width;
    int _height;
    unsigned char *_data;
};

int main(int argc, char *argv[])
{
    RawBitMap bitMap;

    bitMap.Initialise();
    bitMap.ShowData();

    if (!bitMap.Resample(4, 4))
        std::cout << "Failed to resample bitMap:" << std::endl;
    bitMap.ShowData();

    bitMap.Initialise();
    if (!bitMap.Resample(3, 3))
        std::cout << "Failed to resample bitMap:" << std::endl;
    bitMap.ShowData();

    return 0;
}