// Windows camera enumeration using DirectShow APIs
// https://docs.microsoft.com/en-us/windows/win32/directshow/selecting-a-capture-device

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <windows.h>
#include <dshow.h>
#include <comutil.h>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>

#pragma comment(lib, "strmiids")
#pragma comment(lib, "comsuppwd.lib")

namespace py = pybind11;

// Define missing media type GUIDs only if not available in Windows SDK
// Most MEDIASUBTYPE GUIDs are now defined in uuids.h (Windows SDK)
namespace {
    // Helper to create GUID from components
    constexpr GUID MakeGUID(unsigned long data1, unsigned short data2, unsigned short data3,
                           unsigned char d4_0, unsigned char d4_1, unsigned char d4_2, unsigned char d4_3,
                           unsigned char d4_4, unsigned char d4_5, unsigned char d4_6, unsigned char d4_7) {
        return {data1, data2, data3, {d4_0, d4_1, d4_2, d4_3, d4_4, d4_5, d4_6, d4_7}};
    }

    // I420 is the only format that might not be in older SDKs (same as IYUV)
    #ifndef MEDIASUBTYPE_I420
    static const GUID MEDIASUBTYPE_I420 = MakeGUID(0x30323449, 0x0000, 0x0010, 0x80, 0x00, 0x00, 0xaa, 0x00, 0x38, 0x9b, 0x71);
    #endif
}

// Helper: Free media type resources
void FreeMediaType(AM_MEDIA_TYPE& mt)
{
    if (mt.cbFormat != 0)
    {
        CoTaskMemFree((PVOID)mt.pbFormat);
        mt.cbFormat = 0;
        mt.pbFormat = NULL;
    }
    if (mt.pUnk != NULL)
    {
        mt.pUnk->Release();
        mt.pUnk = NULL;
    }
}

void DeleteMediaType(AM_MEDIA_TYPE *pmt)
{
    if (pmt != NULL)
    {
        FreeMediaType(*pmt);
        CoTaskMemFree(pmt);
    }
}

// Helper: Enumerate DirectShow devices by category
HRESULT EnumerateDevices(REFGUID category, IEnumMoniker **ppEnum)
{
    ICreateDevEnum *pDevEnum;
    HRESULT hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL,
        CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pDevEnum));

    if (SUCCEEDED(hr))
    {
        hr = pDevEnum->CreateClassEnumerator(category, ppEnum, 0);
        if (hr == S_FALSE)
        {
            hr = VFW_E_NOT_FOUND;  // The category is empty
        }
        pDevEnum->Release();
    }
    return hr;
}

// Helper: Convert DirectShow pixel format GUID to string
std::string GetPixelFormatName(const GUID& subtype)
{
    // Common video formats
    if (subtype == MEDIASUBTYPE_RGB24) return "RGB24";
    if (subtype == MEDIASUBTYPE_RGB32) return "RGB32";
    if (subtype == MEDIASUBTYPE_RGB555) return "RGB555";
    if (subtype == MEDIASUBTYPE_RGB565) return "RGB565";
    if (subtype == MEDIASUBTYPE_ARGB32) return "ARGB32";

    // YUV formats
    if (subtype == MEDIASUBTYPE_YUY2) return "YUY2";
    if (subtype == MEDIASUBTYPE_UYVY) return "UYVY";
    if (subtype == MEDIASUBTYPE_I420) return "I420";
    if (subtype == MEDIASUBTYPE_IYUV) return "IYUV";
    if (subtype == MEDIASUBTYPE_YV12) return "YV12";
    if (subtype == MEDIASUBTYPE_NV12) return "NV12";

    // Compressed formats
    if (subtype == MEDIASUBTYPE_MJPG) return "MJPEG";
    if (subtype == MEDIASUBTYPE_dvsd) return "DV";
    if (subtype == MEDIASUBTYPE_H264) return "H264";

    // Unknown format - return FOURCC if available
    char fourcc[5] = {0};
    memcpy(fourcc, &subtype.Data1, 4);
    return std::string(fourcc);
}

// Helper: Query camera control capabilities
std::map<std::string, py::dict> QueryCameraControls(IBaseFilter* pFilter)
{
    std::map<std::string, py::dict> controls;

    // Query IAMCameraControl interface
    IAMCameraControl* pCameraControl = NULL;
    HRESULT hr = pFilter->QueryInterface(IID_IAMCameraControl, (void**)&pCameraControl);

    if (SUCCEEDED(hr))
    {
        // Define camera controls to query
        struct ControlInfo {
            long property;
            const char* name;
        };

        ControlInfo cameraControls[] = {
            {CameraControl_Pan, "pan"},
            {CameraControl_Tilt, "tilt"},
            {CameraControl_Roll, "roll"},
            {CameraControl_Zoom, "zoom"},
            {CameraControl_Exposure, "exposure"},
            {CameraControl_Iris, "iris"},
            {CameraControl_Focus, "focus"}
        };

        for (const auto& ctrl : cameraControls)
        {
            long minVal, maxVal, stepSize, defaultVal, flags;
            hr = pCameraControl->GetRange(ctrl.property, &minVal, &maxVal, &stepSize, &defaultVal, &flags);

            if (SUCCEEDED(hr))
            {
                py::dict ctrlDict;
                ctrlDict["min"] = minVal;
                ctrlDict["max"] = maxVal;
                ctrlDict["step"] = stepSize;
                ctrlDict["default"] = defaultVal;
                ctrlDict["auto"] = (flags & CameraControl_Flags_Auto) != 0;
                controls[ctrl.name] = ctrlDict;
            }
        }

        pCameraControl->Release();
    }

    // Query IAMVideoProcAmp interface
    IAMVideoProcAmp* pVideoProcAmp = NULL;
    hr = pFilter->QueryInterface(IID_IAMVideoProcAmp, (void**)&pVideoProcAmp);

    if (SUCCEEDED(hr))
    {
        struct ProcAmpInfo {
            long property;
            const char* name;
        };

        ProcAmpInfo procAmpControls[] = {
            {VideoProcAmp_Brightness, "brightness"},
            {VideoProcAmp_Contrast, "contrast"},
            {VideoProcAmp_Hue, "hue"},
            {VideoProcAmp_Saturation, "saturation"},
            {VideoProcAmp_Sharpness, "sharpness"},
            {VideoProcAmp_Gamma, "gamma"},
            {VideoProcAmp_WhiteBalance, "white_balance"},
            {VideoProcAmp_BacklightCompensation, "backlight_compensation"},
            {VideoProcAmp_Gain, "gain"}
        };

        for (const auto& ctrl : procAmpControls)
        {
            long minVal, maxVal, stepSize, defaultVal, flags;
            hr = pVideoProcAmp->GetRange(ctrl.property, &minVal, &maxVal, &stepSize, &defaultVal, &flags);

            if (SUCCEEDED(hr))
            {
                py::dict ctrlDict;
                ctrlDict["min"] = minVal;
                ctrlDict["max"] = maxVal;
                ctrlDict["step"] = stepSize;
                ctrlDict["default"] = defaultVal;
                ctrlDict["auto"] = (flags & VideoProcAmp_Flags_Auto) != 0;
                controls[ctrl.name] = ctrlDict;
            }
        }

        pVideoProcAmp->Release();
    }

    return controls;
}

// Main camera enumeration function
std::vector<py::dict> list_cameras()
{
    std::vector<py::dict> cameraList;

    // Initialize COM
    HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
    if (FAILED(hr))
    {
        throw std::runtime_error(
            "COM initialization failed with HRESULT 0x" +
            std::to_string((unsigned int)hr) +
            ". DirectShow may not be available on this system.");
    }

    IEnumMoniker *pEnum = NULL;
    hr = EnumerateDevices(CLSID_VideoInputDeviceCategory, &pEnum);

    if (FAILED(hr))
    {
        CoUninitialize();

        if (hr == VFW_E_NOT_FOUND)
        {
            // No cameras found - return empty list (not an error)
            return cameraList;
        }
        else
        {
            throw std::runtime_error(
                "Failed to enumerate video devices with HRESULT 0x" +
                std::to_string((unsigned int)hr) +
                ". Check camera drivers and permissions.");
        }
    }

    IMoniker *pMoniker = NULL;
    int deviceIndex = 0;

    while (pEnum->Next(1, &pMoniker, NULL) == S_OK)
    {
        py::dict cameraInfo;
        cameraInfo["index"] = deviceIndex++;

        IPropertyBag *pPropBag;
        hr = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
        if (FAILED(hr))
        {
            pMoniker->Release();
            continue;
        }

        // Get camera name
        VARIANT var;
        VariantInit(&var);

        hr = pPropBag->Read(L"Description", &var, 0);
        if (FAILED(hr))
        {
            hr = pPropBag->Read(L"FriendlyName", &var, 0);
        }

        if (SUCCEEDED(hr))
        {
            char *pValue = _com_util::ConvertBSTRToString(var.bstrVal);
            cameraInfo["name"] = std::string(pValue);
            delete[] pValue;
            VariantClear(&var);
        }

        // Get device path
        hr = pPropBag->Read(L"DevicePath", &var, 0);
        if (SUCCEEDED(hr))
        {
            char *pValue = _com_util::ConvertBSTRToString(var.bstrVal);
            cameraInfo["path"] = std::string(pValue);
            delete[] pValue;
            VariantClear(&var);
        }

        // Get supported resolutions, frame rates, and formats
        IBaseFilter *pFilter = NULL;
        hr = pMoniker->BindToObject(0, 0, IID_IBaseFilter, (void**)&pFilter);

        if (SUCCEEDED(hr))
        {
            // Query camera controls
            cameraInfo["controls"] = QueryCameraControls(pFilter);

            // Enumerate pins to get resolutions
            IEnumPins *pEnumPins = NULL;
            hr = pFilter->EnumPins(&pEnumPins);

            if (SUCCEEDED(hr))
            {
                std::vector<py::dict> resolutions;
                IPin *pPin = NULL;

                while (pEnumPins->Next(1, &pPin, NULL) == S_OK)
                {
                    IEnumMediaTypes *pEnumMediaTypes = NULL;
                    hr = pPin->EnumMediaTypes(&pEnumMediaTypes);

                    if (SUCCEEDED(hr))
                    {
                        AM_MEDIA_TYPE *mediaType = NULL;

                        // Track unique resolution combinations
                        std::map<std::string, py::dict> resolutionMap;

                        while (pEnumMediaTypes->Next(1, &mediaType, NULL) == S_OK)
                        {
                            if ((mediaType->formattype == FORMAT_VideoInfo) &&
                                (mediaType->cbFormat >= sizeof(VIDEOINFOHEADER)) &&
                                (mediaType->pbFormat != NULL))
                            {
                                VIDEOINFOHEADER* videoInfo = (VIDEOINFOHEADER*)mediaType->pbFormat;

                                int width = videoInfo->bmiHeader.biWidth;
                                int height = videoInfo->bmiHeader.biHeight;

                                // Calculate frame rate from AvgTimePerFrame
                                double fps = 0.0;
                                if (videoInfo->AvgTimePerFrame > 0)
                                {
                                    fps = 10000000.0 / videoInfo->AvgTimePerFrame;
                                }

                                // Get pixel format
                                std::string format = GetPixelFormatName(mediaType->subtype);

                                // Create unique key for resolution
                                std::string key = std::to_string(width) + "x" + std::to_string(height);

                                // Add or update resolution entry
                                if (resolutionMap.find(key) == resolutionMap.end())
                                {
                                    py::dict resDict;
                                    resDict["width"] = width;
                                    resDict["height"] = height;
                                    resDict["frame_rates"] = py::list();
                                    resDict["formats"] = py::list();
                                    resolutionMap[key] = resDict;
                                }

                                // Add frame rate if not already present
                                py::list frameRates = resolutionMap[key]["frame_rates"];
                                if (fps > 0)
                                {
                                    bool found = false;
                                    for (auto item : frameRates)
                                    {
                                        if (item.cast<double>() == fps)
                                        {
                                            found = true;
                                            break;
                                        }
                                    }
                                    if (!found)
                                    {
                                        frameRates.append(fps);
                                    }
                                }

                                // Add format if not already present
                                py::list formats = resolutionMap[key]["formats"];
                                bool formatFound = false;
                                for (auto item : formats)
                                {
                                    if (item.cast<std::string>() == format)
                                    {
                                        formatFound = true;
                                        break;
                                    }
                                }
                                if (!formatFound)
                                {
                                    formats.append(format);
                                }
                            }

                            DeleteMediaType(mediaType);
                        }

                        // Convert map to vector
                        for (const auto& pair : resolutionMap)
                        {
                            resolutions.push_back(pair.second);
                        }

                        pEnumMediaTypes->Release();
                    }

                    pPin->Release();
                }

                cameraInfo["resolutions"] = resolutions;
                pEnumPins->Release();
            }

            pFilter->Release();
        }

        cameraList.push_back(cameraInfo);

        pPropBag->Release();
        pMoniker->Release();
    }

    pEnum->Release();
    CoUninitialize();

    return cameraList;
}

// pybind11 module definition
PYBIND11_MODULE(camera_enum, m) {
    m.doc() = "Windows camera device enumeration using DirectShow APIs";

    m.def("list_cameras", &list_cameras,
          "Enumerate all video capture devices with detailed information\n\n"
          "Returns:\n"
          "    List[Dict]: List of camera information dictionaries, each containing:\n"
          "        - index (int): Camera index\n"
          "        - name (str): Camera friendly name\n"
          "        - path (str): Device path\n"
          "        - resolutions (List[Dict]): Supported resolutions with:\n"
          "            - width (int): Resolution width in pixels\n"
          "            - height (int): Resolution height in pixels\n"
          "            - frame_rates (List[float]): Supported frame rates in FPS\n"
          "            - formats (List[str]): Supported pixel formats (e.g., 'MJPEG', 'YUY2')\n"
          "        - controls (Dict): Available camera controls with min/max/default values\n\n"
          "Raises:\n"
          "    RuntimeError: If COM initialization fails or device enumeration fails");
}
