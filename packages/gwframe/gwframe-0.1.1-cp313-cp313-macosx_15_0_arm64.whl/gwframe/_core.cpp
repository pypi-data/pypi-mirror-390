// Copyright (c) 2025, California Institute of Technology and contributors
//
// You should have received a copy of the licensing terms for this
// software included in the file "LICENSE" located in the top-level
// directory of this package. If you did not, you can view a copy at
// https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

// Nanobind bindings for LDASTools frameCPP
//
// This provides simplified Python bindings for the frameCPP library
// for reading and writing gravitational wave frame files.

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/shared_ptr.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/vector.h>

#include <memory>
#include <sstream>

#include <boost/shared_ptr.hpp>

// Include frameCPP headers
#include <framecpp/Common/CheckSum.hh>
#include <framecpp/Common/MemoryBuffer.hh>
#include <framecpp/Common/Verify.hh>
#include <framecpp/Detectors.hh>
#include <framecpp/Dimension.hh>
#include <framecpp/FrAdcData.hh>
#include <framecpp/FrDetector.hh>
#include <framecpp/FrHistory.hh>
#include <framecpp/FrProcData.hh>
#include <framecpp/FrSimData.hh>
#include <framecpp/FrTOC.hh>
#include <framecpp/FrVect.hh>
#include <framecpp/FrameH.hh>
#include <framecpp/GPSTime.hh>
#include <framecpp/IFrameStream.hh>
#include <framecpp/OFrameStream.hh>

namespace nb = nanobind;
using namespace nb::literals;

// ============================================================================
// Helper functions
// ============================================================================

std::string get_version() {
    return "0.1.0";
}

// Empty deleter for shared_ptr (when Python owns the object)
// Using a static function instead of lambdas reduces overhead
template <typename T> void empty_deleter(T*) {}

// Helper template to create ndarray from typed data pointer
template <typename T>
inline nb::object create_ndarray_impl(void* data_ptr, size_t size,
                                      nb::handle owner = nb::handle()) {
    size_t shape[1] = {size};
    if (owner) {
        return nb::cast(nb::ndarray<nb::numpy, T>(static_cast<T*>(data_ptr), 1, shape, owner));
    } else {
        return nb::cast(nb::ndarray<nb::numpy, T>(static_cast<T*>(data_ptr), 1, shape));
    }
}

// Dispatch helper for all FrVect types - handles type-specific array creation
inline nb::object create_ndarray_for_type(int type, void* data_ptr, size_t size,
                                          nb::handle owner = nb::handle()) {
    switch (type) {
    case FrameCPP::FrVect::FR_VECT_8R:
        return create_ndarray_impl<double>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_4R:
        return create_ndarray_impl<float>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_8S:
        return create_ndarray_impl<int64_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_4S:
        return create_ndarray_impl<int32_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_2S:
        return create_ndarray_impl<int16_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_1U:
        return create_ndarray_impl<uint8_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_2U:
        return create_ndarray_impl<uint16_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_4U:
        return create_ndarray_impl<uint32_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_8U:
        return create_ndarray_impl<uint64_t>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_8C:
        return create_ndarray_impl<std::complex<float>>(data_ptr, size, owner);
    case FrameCPP::FrVect::FR_VECT_16C:
        return create_ndarray_impl<std::complex<double>>(data_ptr, size, owner);
    default:
        throw std::runtime_error("Unsupported FrVect data type");
    }
}

// Helper: Read channel from bytes using MemoryBuffer
// This encapsulates: create buffer → load bytes → create stream → read channel
// Takes nb::bytes from Python and converts to std::string for MemoryBuffer
// IMPORTANT: Keeps buffer alive by storing it as static to prevent premature destruction
FrameCPP::FrProcData* read_proc_from_bytes(nb::bytes data, unsigned int frame,
                                           const std::string& channel) {
    // Convert nb::bytes to std::string (binary data)
    std::string data_str(data.c_str(), data.size());

    // Allocate on heap to keep alive beyond function scope
    // Note: This leaks memory but ensures data validity
    // In production, would need proper lifetime management
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);

    auto* stream = new FrameCPP::IFrameStream(false, buffer);

    // Read channel data - this should copy the data
    auto ptr = stream->ReadFrProcData(frame, channel);

    // Force data decompression to materialize it before buffer might be deallocated
    if (ptr && ptr->RefData().size() > 0) {
        auto vect = ptr->RefData()[0];
        if (vect) {
            vect->GetDataUncompressed(); // Force decompression
        }
    }

    return ptr.get();
}

FrameCPP::FrAdcData* read_adc_from_bytes(nb::bytes data, unsigned int frame,
                                         const std::string& channel) {
    std::string data_str(data.c_str(), data.size());
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);
    auto* stream = new FrameCPP::IFrameStream(false, buffer);
    auto ptr = stream->ReadFrAdcData(frame, channel);

    if (ptr && ptr->RefData().size() > 0) {
        auto vect = ptr->RefData()[0];
        if (vect) {
            vect->GetDataUncompressed();
        }
    }

    return ptr.get();
}

FrameCPP::FrSimData* read_sim_from_bytes(nb::bytes data, unsigned int frame,
                                         const std::string& channel) {
    std::string data_str(data.c_str(), data.size());
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);
    auto* stream = new FrameCPP::IFrameStream(false, buffer);
    auto ptr = stream->ReadFrSimData(frame, channel);

    if (ptr && ptr->RefData().size() > 0) {
        auto vect = ptr->RefData()[0];
        if (vect) {
            vect->GetDataUncompressed();
        }
    }

    return ptr.get();
}

// Convert GPSTime to Python tuple (seconds, nanoseconds)
std::tuple<unsigned int, unsigned int> gpstime_to_tuple(const FrameCPP::GPSTime& gps) {
    return std::make_tuple(gps.getSec(), gps.getNSec());
}

// Convert Python float to GPSTime
FrameCPP::GPSTime float_to_gpstime(double gps_float) {
    unsigned int seconds = static_cast<unsigned int>(gps_float);
    unsigned int nanoseconds = static_cast<unsigned int>((gps_float - seconds) * 1e9);
    return FrameCPP::GPSTime(seconds, nanoseconds);
}

// Convert GPSTime to Python float
double gpstime_to_float(const FrameCPP::GPSTime& gps) {
    return static_cast<double>(gps.getSec()) + gps.getNSec() * 1e-9;
}

// Helper: Read frame header from bytes to get GPS time
std::tuple<unsigned int, unsigned int> read_frame_gps_time(nb::bytes data, unsigned int frame) {
    std::string data_str(data.c_str(), data.size());
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);
    auto* stream = new FrameCPP::IFrameStream(false, buffer);

    // Read frame header
    auto ptr = stream->ReadFrameN(frame);
    auto frame_ptr = boost::dynamic_pointer_cast<FrameCPP::FrameH>(ptr);
    if (!frame_ptr) {
        throw std::runtime_error("Unable to read frame header");
    }

    auto gtime = frame_ptr->GetGTime();
    auto result = std::make_tuple(gtime.getSec(), gtime.getNSec());

    // Clean up
    delete stream;
    delete buffer;

    return result;
}

// Helper: Validate frame file checksums from bytes
void validate_frame_checksums(nb::bytes data) {
    // Convert nb::bytes to std::string (binary data)
    std::string data_str(data.c_str(), data.size());

    // Create memory buffer and stream
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);
    auto* stream = new FrameCPP::IFrameStream(false, buffer);

    // Create and configure verifier for file-level checksum only
    FrameCPP::Common::Verify verifier;
    verifier.BufferSize(data.size());
    verifier.UseMemoryMappedIO(false);
    verifier.CheckDataValid(false);
    verifier.Expandability(false);
    verifier.MustHaveEOFChecksum(true);
    verifier.Strict(false);
    verifier.ValidateMetadata(false);
    verifier.CheckFileChecksumOnly(true);

    // Validate - will throw VerifyException on failure
    verifier(*stream);

    // Clean up
    delete stream;
    delete buffer;
}

// Helper: Get frame times from bytes
// Returns vector of (start_time, duration) tuples for all frames
std::vector<std::tuple<double, double>> get_frame_times_from_bytes(nb::bytes data) {
    std::string data_str(data.c_str(), data.size());
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);
    auto* stream = new FrameCPP::IFrameStream(false, buffer);

    std::vector<std::tuple<double, double>> frame_times;

    try {
        unsigned int n_frames = stream->GetNumberOfFrames();

        for (unsigned int i = 0; i < n_frames; ++i) {
            auto ptr = stream->ReadFrameN(i);
            auto frame_ptr = boost::dynamic_pointer_cast<FrameCPP::FrameH>(ptr);
            if (frame_ptr) {
                auto gtime = frame_ptr->GetGTime();
                double start_time = static_cast<double>(gtime.getSec()) + gtime.getNSec() * 1e-9;
                double duration = frame_ptr->GetDt();
                frame_times.push_back(std::make_tuple(start_time, duration));
            }
        }
    } catch (...) {
        // Clean up and rethrow
        delete stream;
        delete buffer;
        throw;
    }

    // Clean up
    delete stream;
    delete buffer;

    return frame_times;
}

// Helper: Enumerate all channel names from bytes
// Returns tuple of (proc_channels, adc_channels, sim_channels)
std::tuple<std::vector<std::string>, std::vector<std::string>, std::vector<std::string>>
enumerate_channels_from_bytes(nb::bytes data, unsigned int frame_index) {
    std::string data_str(data.c_str(), data.size());
    auto* buffer = new FrameCPP::Common::MemoryBuffer(std::ios::in, false);
    buffer->str(data_str);
    auto* stream = new FrameCPP::IFrameStream(false, buffer);

    // Read frame header
    auto ptr = stream->ReadFrameN(frame_index);
    auto frame_ptr = boost::dynamic_pointer_cast<FrameCPP::FrameH>(ptr);
    if (!frame_ptr) {
        throw std::runtime_error("Unable to read frame header");
    }

    std::vector<std::string> proc_channels;
    std::vector<std::string> adc_channels;
    std::vector<std::string> sim_channels;

    // Pre-allocate capacity to avoid reallocations during enumeration
    auto& proc_data = frame_ptr->RefProcData();
    proc_channels.reserve(proc_data.size());

    auto& adc_data = frame_ptr->RefAuxData();
    adc_channels.reserve(adc_data.size());

    auto& sim_data = frame_ptr->RefSimData();
    sim_channels.reserve(sim_data.size());

    // Enumerate proc channels
    for (auto it = proc_data.begin(); it != proc_data.end(); ++it) {
        if (*it) {
            proc_channels.push_back((*it)->GetName());
        }
    }

    // Enumerate ADC channels (stored in AuxData for ADC)
    for (auto it = adc_data.begin(); it != adc_data.end(); ++it) {
        if (*it) {
            // ADC data can be either FrAdcData or other aux types
            // Try to extract name if it's FrAdcData
            auto adc_ptr = boost::dynamic_pointer_cast<FrameCPP::FrAdcData>(*it);
            if (adc_ptr) {
                adc_channels.push_back(adc_ptr->GetName());
            }
        }
    }

    // Enumerate sim channels
    for (auto it = sim_data.begin(); it != sim_data.end(); ++it) {
        if (*it) {
            sim_channels.push_back((*it)->GetName());
        }
    }

    // Clean up
    delete stream;
    delete buffer;

    return std::make_tuple(proc_channels, adc_channels, sim_channels);
}

// ============================================================================
// Python Bindings
// ============================================================================

NB_MODULE(_core, m) {
    m.doc() = "Core C++ bindings for gwframe (LDASTools frameCPP wrapper)";

    // Export version
    m.def("__version__", &get_version, "Get the version of gwframe");

    // Memory-based reading helpers
    m.def("read_proc_from_bytes", &read_proc_from_bytes, "data"_a, "frame"_a, "channel"_a,
          nb::rv_policy::reference, "Read processed data channel from bytes");
    m.def("read_adc_from_bytes", &read_adc_from_bytes, "data"_a, "frame"_a, "channel"_a,
          nb::rv_policy::reference, "Read ADC data channel from bytes");
    m.def("read_sim_from_bytes", &read_sim_from_bytes, "data"_a, "frame"_a, "channel"_a,
          nb::rv_policy::reference, "Read simulated data channel from bytes");

    // Frame metadata helpers
    m.def("read_frame_gps_time", &read_frame_gps_time, "data"_a, "frame"_a,
          "Read GPS time from frame header in bytes (returns (sec, nsec) tuple)");

    // Frame validation helper
    m.def("validate_frame_checksums", &validate_frame_checksums, "data"_a,
          "Validate checksums in frame file bytes");

    // Frame times helper
    m.def("get_frame_times_from_bytes", &get_frame_times_from_bytes, "data"_a,
          "Get frame times from bytes (returns list of (start_time, duration) tuples for all "
          "frames)");

    // Channel enumeration helper
    m.def(
        "enumerate_channels_from_bytes", &enumerate_channels_from_bytes, "data"_a, "frame"_a,
        "Enumerate all channel names from bytes (returns tuple of (proc, adc, sim) channel lists)");

    // ------------------------------------------------------------------------
    // GPSTime - GPS time handling
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::GPSTime>(m, "GPSTime", "GPS time representation")
        .def(nb::init<>(), "Create GPSTime at epoch 0")
        .def(nb::init<unsigned int, unsigned int>(), "sec"_a, "nsec"_a = 0,
             "Create GPSTime from seconds and nanoseconds")
        .def_prop_ro("sec", &FrameCPP::GPSTime::getSec, "GPS seconds")
        .def_prop_ro("nsec", &FrameCPP::GPSTime::getNSec, "GPS nanoseconds")
        .def("get_leap_seconds", &FrameCPP::GPSTime::GetLeapSeconds,
             "Get leap seconds (TAI-UTC offset) for this GPS time")
        .def("to_float", &gpstime_to_float, "Convert to float seconds")
        .def("to_tuple", &gpstime_to_tuple, "Convert to (sec, nsec) tuple")
        .def("__repr__",
             [](const FrameCPP::GPSTime& self) {
                 std::ostringstream oss;
                 oss << "GPSTime(" << self.getSec() << ", " << self.getNSec() << ")";
                 return oss.str();
             })
        .def("__float__", &gpstime_to_float);

    // Helper function to create GPSTime from float
    m.def("gpstime_from_float", &float_to_gpstime, "gps"_a, "Create GPSTime from float seconds");

    // ------------------------------------------------------------------------
    // IFrameFStream - Input frame stream for reading
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::IFrameFStream>(m, "IFrameFStream", "Input stream for reading GWF files")
        .def(
            "__init__",
            [](FrameCPP::IFrameFStream* t, const std::string& filename) {
                new (t) FrameCPP::IFrameFStream(filename.c_str());
            },
            "filename"_a, "Open a GWF file for reading")
        .def("get_number_of_frames", &FrameCPP::IFrameFStream::GetNumberOfFrames,
             "Get the total number of frames in the file")
        .def(
            "read_frame_n",
            [](FrameCPP::IFrameFStream& self, unsigned int n) -> FrameCPP::FrameH* {
                auto ptr = self.ReadFrameN(n);
                return ptr.get(); // Return raw pointer, nanobind will manage lifetime
            },
            "n"_a, nb::rv_policy::reference, "Read frame number n")
        .def(
            "read_fr_proc_data",
            [](FrameCPP::IFrameFStream& self, unsigned int frame,
               const std::string& channel) -> FrameCPP::FrProcData* {
                auto ptr = self.ReadFrProcData(frame, channel);
                return ptr.get();
            },
            "frame"_a, "channel"_a, nb::rv_policy::reference, "Read processed data from frame")
        .def(
            "read_fr_adc_data",
            [](FrameCPP::IFrameFStream& self, unsigned int frame,
               const std::string& channel) -> FrameCPP::FrAdcData* {
                auto ptr = self.ReadFrAdcData(frame, channel);
                return ptr.get();
            },
            "frame"_a, "channel"_a, nb::rv_policy::reference, "Read ADC data from frame")
        .def(
            "read_fr_sim_data",
            [](FrameCPP::IFrameFStream& self, unsigned int frame,
               const std::string& channel) -> FrameCPP::FrSimData* {
                auto ptr = self.ReadFrSimData(frame, channel);
                return ptr.get();
            },
            "frame"_a, "channel"_a, nb::rv_policy::reference, "Read simulated data from frame")
        .def(
            "get_toc",
            [](FrameCPP::IFrameFStream& self) -> const FrameCPP::FrTOC* {
                auto ptr = self.GetTOC();
                return ptr.get();
            },
            nb::rv_policy::reference, "Get the table of contents")
        .def("__repr__", [](const FrameCPP::IFrameFStream&) { return "<IFrameFStream>"; });

    // ------------------------------------------------------------------------
    // MemoryBuffer - In-memory buffer for reading from bytes
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::Common::MemoryBuffer>(m, "MemoryBuffer",
                                               "In-memory buffer for reading GWF data from bytes")
        .def(
            "__init__",
            [](FrameCPP::Common::MemoryBuffer* t) {
                new (t) FrameCPP::Common::MemoryBuffer(std::ios::in, false);
            },
            "Create memory buffer for input")
        .def("str", nb::overload_cast<const std::string&>(&FrameCPP::Common::MemoryBuffer::str),
             "data"_a, "Load bytes into buffer");

    // ------------------------------------------------------------------------
    // IFrameMemStream - Memory-based frame stream (wraps IFrameStream)
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::IFrameStream>(m, "IFrameMemStream",
                                       "Input stream for reading GWF data from memory buffer")
        .def(
            "__init__",
            [](FrameCPP::IFrameStream* t, FrameCPP::Common::MemoryBuffer* buffer) {
                new (t) FrameCPP::IFrameStream(false, buffer);
            },
            "buffer"_a, "Create stream from memory buffer")
        .def("get_number_of_frames", &FrameCPP::IFrameStream::GetNumberOfFrames,
             "Get the total number of frames")
        .def(
            "read_frame_n",
            [](FrameCPP::IFrameStream& self, unsigned int n) -> FrameCPP::FrameH* {
                auto ptr = self.ReadFrameN(n);
                // Cast from Object to FrameH
                auto frame_ptr = boost::dynamic_pointer_cast<FrameCPP::FrameH>(ptr);
                if (!frame_ptr) {
                    throw std::runtime_error("Unable to read frame");
                }
                return frame_ptr.get();
            },
            "n"_a, nb::rv_policy::reference, "Read frame number n")
        .def("__repr__", [](const FrameCPP::IFrameStream&) { return "<IFrameMemStream>"; });

    // ------------------------------------------------------------------------
    // OFrameFStream - Output frame stream for writing
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::OFrameFStream>(m, "OFrameFStream", "Output stream for writing GWF files")
        .def(
            "__init__",
            [](FrameCPP::OFrameFStream* t, const std::string& filename) {
                new (t) FrameCPP::OFrameFStream(filename.c_str());
            },
            "filename"_a, "Open a GWF file for writing")
        // Get underlying stream pointer
        .def(
            "stream",
            [](FrameCPP::OFrameFStream& self) -> FrameCPP::OFrameFStream::stream_type* {
                return self.Stream();
            },
            nb::rv_policy::reference, "Get underlying stream pointer")
        // Write frame with compression
        .def(
            "write_frame",
            [](FrameCPP::OFrameFStream& self, FrameCPP::FrameH& frame, int compression,
               int compression_level) {
                // Get underlying stream pointer
                auto* s = self.Stream();
                if (s) {
                    // Create shared_ptr with empty deleter (frame is owned by Python)
                    auto frame_ptr = boost::shared_ptr<FrameCPP::FrameH>(
                        &frame, empty_deleter<FrameCPP::FrameH>);
                    // Use CRC checksum
                    s->WriteFrame(frame_ptr, compression, compression_level,
                                  FrameCPP::Common::CheckSum::CRC);
                }
            },
            "frame"_a, "compression"_a, "compression_level"_a,
            "Write frame with specified compression")
        .def("__repr__", [](const FrameCPP::OFrameFStream&) { return "<OFrameFStream>"; });

    // ------------------------------------------------------------------------
    // FrTOC - Table of Contents
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrTOC>(m, "FrTOC", "Frame table of contents")
        // Channel list methods - extract keys from maps returned by Get* methods
        // use const reference to avoid map copy, emplace_back for direct construction
        .def(
            "get_adc",
            [](const FrameCPP::FrTOC& self) -> std::vector<std::string> {
                const auto& map = self.GetADC();
                std::vector<std::string> keys;
                keys.reserve(map.size());
                for (const auto& pair : map) {
                    keys.emplace_back(pair.first);
                }
                return keys;
            },
            "Get list of ADC channel names")
        .def(
            "get_proc",
            [](const FrameCPP::FrTOC& self) -> std::vector<std::string> {
                const auto& map = self.GetProc();
                std::vector<std::string> keys;
                keys.reserve(map.size());
                for (const auto& pair : map) {
                    keys.emplace_back(pair.first);
                }
                return keys;
            },
            "Get list of Proc channel names")
        .def(
            "get_sim",
            [](const FrameCPP::FrTOC& self) -> std::vector<std::string> {
                const auto& map = self.GetSim();
                std::vector<std::string> keys;
                keys.reserve(map.size());
                for (const auto& pair : map) {
                    keys.emplace_back(pair.first);
                }
                return keys;
            },
            "Get list of Sim channel names")
        .def("get_time_s", &FrameCPP::FrTOC::GetGTimeS,
             "Get GPS start times (seconds) for each frame")
        .def("get_time_ns", &FrameCPP::FrTOC::GetGTimeN,
             "Get GPS start times (nanoseconds) for each frame")
        .def("get_dt", &FrameCPP::FrTOC::GetDt, "Get durations for each frame");

    // ------------------------------------------------------------------------
    // FrameH - Frame header
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrameH>(m, "FrameH", "Frame header")
        .def(nb::init<>(), "Create an empty frame")
        .def(nb::init<const std::string&, int, unsigned int, const FrameCPP::GPSTime&,
                      unsigned short, double>(),
             "name"_a, "run"_a, "frame"_a, "gps_time"_a, "leap_seconds"_a, "duration"_a,
             "Create frame with full parameters (name, run, frame_number, gps_time, leap_seconds, "
             "duration)")
        .def("set_name", &FrameCPP::FrameH::SetName, "name"_a, "Set the frame name")
        .def("get_name", &FrameCPP::FrameH::GetName, "Get the frame name")
        .def("set_run", &FrameCPP::FrameH::SetRun, "run"_a, "Set the run number")
        .def("get_run", &FrameCPP::FrameH::GetRun, "Get the run number")
        .def("get_frame", &FrameCPP::FrameH::GetFrame, "Get the frame number")
        .def("set_gps_time", &FrameCPP::FrameH::SetGTime, "gps"_a, "Set the GPS start time")
        // Overload for direct integer input (avoids GPSTime object creation)
        .def(
            "set_gps_time",
            [](FrameCPP::FrameH& self, unsigned int sec, unsigned int nsec) {
                self.SetGTime(FrameCPP::GPSTime(sec, nsec));
            },
            "sec"_a, "nsec"_a = 0, "Set GPS time from seconds and nanoseconds")
        .def("get_gps_time", &FrameCPP::FrameH::GetGTime, "Get the GPS start time")
        .def("set_dt", &FrameCPP::FrameH::SetDt, "dt"_a, "Set the frame duration")
        .def("get_dt", &FrameCPP::FrameH::GetDt, "Get the frame duration")
        // Append methods
        .def(
            "append_frhistory",
            [](FrameCPP::FrameH& self, const FrameCPP::FrHistory& hist) {
                self.RefHistory().append(hist);
            },
            "history"_a, "Append a history/metadata entry")
        .def(
            "append_fr_proc_data",
            [](FrameCPP::FrameH& self, FrameCPP::FrProcData& data) {
                self.RefProcData().append(data);
            },
            "data"_a, "Append FrProcData to frame")
        .def(
            "append_fr_sim_data",
            [](FrameCPP::FrameH& self, FrameCPP::FrSimData& data) {
                self.RefSimData().append(data);
            },
            "data"_a, "Append FrSimData to frame")
        // FIXME: ADC data support needs to be added
        // ADC channels require GetRawData()->SetRawData()/RefFirstAdc() which needs
        // proper initialization. See gstlal framecpp_channelmux.cc:368-371 for reference.
        .def(
            "append_fr_detector_proc",
            [](FrameCPP::FrameH& self, FrameCPP::FrDetector& detector) {
                self.RefDetectProc().append(detector);
            },
            "detector"_a, "Append FrDetector for processed data")
        .def(
            "append_fr_detector_sim",
            [](FrameCPP::FrameH& self, FrameCPP::FrDetector& detector) {
                self.RefDetectSim().append(detector);
            },
            "detector"_a, "Append FrDetector for simulated data")
        // Write method
        .def(
            "write",
            [](FrameCPP::FrameH& self, FrameCPP::OFrameFStream& stream, int compression,
               int compression_level) {
                // Get underlying stream pointer
                auto* s = stream.Stream();
                if (s) {
                    // Use shared_ptr with empty deleter (Python owns the frame)
                    // This avoids the expensive frame copy
                    auto frame_ptr =
                        boost::shared_ptr<FrameCPP::FrameH>(&self, empty_deleter<FrameCPP::FrameH>);
                    // Use CRC checksum
                    s->WriteFrame(frame_ptr, compression, compression_level,
                                  FrameCPP::Common::CheckSum::CRC);
                }
            },
            "stream"_a, "compression"_a = 6, "compression_level"_a = 6,
            "Write frame to output stream (default: ZERO_SUPPRESS_OTHERWISE_GZIP)")
        .def("__repr__", [](const FrameCPP::FrameH& self) {
            std::ostringstream oss;
            oss << "<FrameH name='" << self.GetName()
                << "' t0=" << gpstime_to_float(self.GetGTime()) << " dt=" << self.GetDt() << ">";
            return oss.str();
        });

    // ------------------------------------------------------------------------
    // FrHistory - Metadata/history entries
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrHistory>(m, "FrHistory", "Frame history/metadata")
        .def(nb::init<const std::string&, unsigned int, const std::string&>(), "name"_a, "time"_a,
             "comment"_a, "Create history entry with name, GPS time, and comment")
        .def("get_name", &FrameCPP::FrHistory::GetName, "Get history entry name")
        .def("get_comment", &FrameCPP::FrHistory::GetComment, "Get history comment");

    // ------------------------------------------------------------------------
    // FrDetector - Detector information
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrDetector>(m, "FrDetector", "Detector information")
        .def("get_name", &FrameCPP::FrDetector::GetName, "Get detector name")
        .def("get_prefix", &FrameCPP::FrDetector::GetPrefix, "Get detector prefix (e.g., 'H1')")
        .def("get_latitude", &FrameCPP::FrDetector::GetLatitude, "Get detector latitude in radians")
        .def("get_longitude", &FrameCPP::FrDetector::GetLongitude,
             "Get detector longitude in radians")
        .def("get_elevation", &FrameCPP::FrDetector::GetElevation,
             "Get detector elevation in meters")
        .def("get_arm_x_azimuth", &FrameCPP::FrDetector::GetArmXazimuth,
             "Get X arm azimuth in radians")
        .def("get_arm_y_azimuth", &FrameCPP::FrDetector::GetArmYazimuth,
             "Get Y arm azimuth in radians")
        .def("get_arm_x_altitude", &FrameCPP::FrDetector::GetArmXaltitude,
             "Get X arm altitude in radians")
        .def("get_arm_y_altitude", &FrameCPP::FrDetector::GetArmYaltitude,
             "Get Y arm altitude in radians")
        .def("get_arm_x_midpoint", &FrameCPP::FrDetector::GetArmXmidpoint,
             "Get X arm midpoint in meters")
        .def("get_arm_y_midpoint", &FrameCPP::FrDetector::GetArmYmidpoint,
             "Get Y arm midpoint in meters")
        .def("get_local_time", &FrameCPP::FrDetector::GetLocalTime,
             "Get local time offset in seconds");

    // Bind detector_location_type enum
    nb::enum_<FrameCPP::detector_location_type>(m, "DetectorLocationType", "Detector location type")
        .value("G1", FrameCPP::DETECTOR_LOCATION_G1, "GEO")
        .value("H1", FrameCPP::DETECTOR_LOCATION_H1, "Hanford 4k")
        .value("H2", FrameCPP::DETECTOR_LOCATION_H2, "Hanford 2k")
        .value("K1", FrameCPP::DETECTOR_LOCATION_K1, "KAGRA")
        .value("L1", FrameCPP::DETECTOR_LOCATION_L1, "Livingston")
        .value("T1", FrameCPP::DETECTOR_LOCATION_T1, "TAMA")
        .value("V1", FrameCPP::DETECTOR_LOCATION_V1, "Virgo");

    // Detector location constants for backwards compatibility
    m.attr("DETECTOR_LOCATION_G1") = static_cast<int>(FrameCPP::DETECTOR_LOCATION_G1); // 0 - GEO
    m.attr("DETECTOR_LOCATION_H1") =
        static_cast<int>(FrameCPP::DETECTOR_LOCATION_H1); // 1 - Hanford 4k
    m.attr("DETECTOR_LOCATION_H2") =
        static_cast<int>(FrameCPP::DETECTOR_LOCATION_H2); // 2 - Hanford 2k
    m.attr("DETECTOR_LOCATION_K1") = static_cast<int>(FrameCPP::DETECTOR_LOCATION_K1); // 3 - KAGRA
    m.attr("DETECTOR_LOCATION_L1") =
        static_cast<int>(FrameCPP::DETECTOR_LOCATION_L1); // 4 - Livingston
    m.attr("DETECTOR_LOCATION_T1") = static_cast<int>(FrameCPP::DETECTOR_LOCATION_T1); // 5 - TAMA
    m.attr("DETECTOR_LOCATION_V1") = static_cast<int>(FrameCPP::DETECTOR_LOCATION_V1); // 6 - Virgo

    // GetDetector function - retrieves detector information for location and GPS time
    m.def("get_detector", &FrameCPP::GetDetector, "location"_a, "gps_time"_a,
          nb::rv_policy::reference,
          "Get detector information for a specific location and GPS time");

    // ------------------------------------------------------------------------
    // VerifyException - Exception raised during frame file validation
    // ------------------------------------------------------------------------
    nb::exception<FrameCPP::Common::VerifyException>(m, "VerifyException");

    // ------------------------------------------------------------------------
    // Verify - Frame file validation/checksum verification
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::Common::Verify>(m, "Verify", "Frame file validator")
        .def(nb::init<>(), "Create a new Verify object")
        // Configuration methods
        .def("buffer_size", nb::overload_cast<>(&FrameCPP::Common::Verify::BufferSize, nb::const_),
             "Get I/O buffer size")
        .def(
            "set_buffer_size",
            [](FrameCPP::Common::Verify& self, size_t bytes) { self.BufferSize(bytes); }, "bytes"_a,
            "Set I/O buffer size in bytes")
        .def(
            "set_use_memory_mapped_io",
            [](FrameCPP::Common::Verify& self, bool use) { self.UseMemoryMappedIO(use); }, "use"_a,
            "Enable/disable memory-mapped I/O")
        .def(
            "set_check_data_valid",
            [](FrameCPP::Common::Verify& self, bool check) { self.CheckDataValid(check); },
            "check"_a, "Enable/disable data valid field checking")
        .def(
            "set_expandability",
            [](FrameCPP::Common::Verify& self, bool check) { self.Expandability(check); },
            "check"_a, "Enable/disable compressed data expandability checking")
        .def(
            "set_must_have_eof_checksum",
            [](FrameCPP::Common::Verify& self, bool must) { self.MustHaveEOFChecksum(must); },
            "must"_a, "Require EOF checksum structure")
        .def(
            "set_strict", [](FrameCPP::Common::Verify& self, bool strict) { self.Strict(strict); },
            "strict"_a, "Enable/disable strict frame spec conformance")
        .def(
            "set_validate_metadata",
            [](FrameCPP::Common::Verify& self, bool validate) { self.ValidateMetadata(validate); },
            "validate"_a, "Enable/disable metadata validation")
        .def(
            "set_check_file_checksum_only",
            [](FrameCPP::Common::Verify& self, bool check) { self.CheckFileChecksumOnly(check); },
            "check"_a, "Enable file-level checksum checking only")
        // Verification method - accepts IFrameStream from memory buffer
        .def(
            "__call__",
            [](FrameCPP::Common::Verify& self, FrameCPP::IFrameStream& stream) { self(stream); },
            "stream"_a, "Verify a frame stream");


    // ------------------------------------------------------------------------
    // Dimension - Array dimension metadata
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::Dimension>(m, "Dimension", "Array dimension")
        .def(nb::init<unsigned int, double, const std::string&, double>(), "nx"_a, "dx"_a, "unit"_a,
             "start_x"_a = 0.0, "Create a dimension descriptor")
        .def_prop_ro("nx", &FrameCPP::Dimension::GetNx, "Number of elements")
        .def_prop_ro("dx", &FrameCPP::Dimension::GetDx, "Spacing between elements")
        .def_prop_ro("start_x", &FrameCPP::Dimension::GetStartX, "Starting offset")
        .def("__repr__", [](const FrameCPP::Dimension& self) {
            std::ostringstream oss;
            oss << "<Dimension nx=" << self.GetNx() << " dx=" << self.GetDx() << ">";
            return oss.str();
        });

    // ------------------------------------------------------------------------
    // FrVect - Data vector & type constants
    // ------------------------------------------------------------------------
    // Bind FrVect class to expose type constants as static read-only properties
    // Using def_prop_ro_static() with lambdas for lazy evaluation (avoids mutex race at module
    // init) Cast to int for proper Python conversion
    nb::class_<FrameCPP::FrVect>(m, "FrVect", "Frame data vector")
        // Type constants as static read-only properties (evaluated lazily when accessed)
        .def_prop_ro_static(
            "FR_VECT_8R", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_8R); },
            "double type")
        .def_prop_ro_static(
            "FR_VECT_4R", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_4R); },
            "float type")
        .def_prop_ro_static(
            "FR_VECT_4S", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_4S); },
            "int32 type")
        .def_prop_ro_static(
            "FR_VECT_2S", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_2S); },
            "int16 type")
        .def_prop_ro_static(
            "FR_VECT_8S", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_8S); },
            "int64 type")
        .def_prop_ro_static(
            "FR_VECT_1U", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_1U); },
            "uint8 type")
        .def_prop_ro_static(
            "FR_VECT_2U", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_2U); },
            "uint16 type")
        .def_prop_ro_static(
            "FR_VECT_4U", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_4U); },
            "uint32 type")
        .def_prop_ro_static(
            "FR_VECT_8U", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_8U); },
            "uint64 type")
        .def_prop_ro_static(
            "FR_VECT_8C", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_8C); },
            "complex64 type")
        .def_prop_ro_static(
            "FR_VECT_16C",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::FR_VECT_16C); },
            "complex128 type")
        // Compression constants as static read-only properties
        .def_prop_ro_static(
            "RAW", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::RAW); },
            "No compression")
        .def_prop_ro_static(
            "GZIP", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::GZIP); },
            "GZIP compression")
        .def_prop_ro_static(
            "DIFF_GZIP", [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::DIFF_GZIP); },
            "Differentiate then GZIP")
        .def_prop_ro_static(
            "ZERO_SUPPRESS_WORD_2",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::ZERO_SUPPRESS_WORD_2); },
            "Zero suppress 2-byte words")
        .def_prop_ro_static(
            "ZERO_SUPPRESS_WORD_4",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::ZERO_SUPPRESS_WORD_4); },
            "Zero suppress 4-byte words")
        .def_prop_ro_static(
            "ZERO_SUPPRESS_WORD_8",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::ZERO_SUPPRESS_WORD_8); },
            "Zero suppress 8-byte words")
        .def_prop_ro_static(
            "ZERO_SUPPRESS_OTHERWISE_GZIP",
            [](nb::handle) {
                return static_cast<int>(FrameCPP::FrVect::ZERO_SUPPRESS_OTHERWISE_GZIP);
            },
            "Zero suppress integers, GZIP floats")
        .def_prop_ro_static(
            "BEST_COMPRESSION",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::BEST_COMPRESSION); },
            "Try all modes, use best compression")
        // Backward compatibility aliases
        .def_prop_ro_static(
            "ZERO_SUPPRESS_SHORT",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::ZERO_SUPPRESS_SHORT); },
            "Alias for ZERO_SUPPRESS_WORD_2")
        .def_prop_ro_static(
            "ZERO_SUPPRESS_INT_FLOAT",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrVect::ZERO_SUPPRESS_INT_FLOAT); },
            "Alias for ZERO_SUPPRESS_WORD_4")
        // Constructor for writing
        .def(
            "__init__",
            [](FrameCPP::FrVect* t, const std::string& name, int type, unsigned int ndim,
               const FrameCPP::Dimension& dim, const std::string& unit_y) {
                // Constructor expects pointer to Dimension, so pass address
                new (t) FrameCPP::FrVect(name, type, ndim, &dim, unit_y);
            },
            "name"_a, "type"_a, "ndim"_a, "dimension"_a, "unit_y"_a = "",
            "Create FrVect for writing data")
        // Data access methods
        .def("get_name", &FrameCPP::FrVect::GetName, "Get vector name")
        .def("get_type", &FrameCPP::FrVect::GetType, "Get data type")
        .def("get_n_data", &FrameCPP::FrVect::GetNData, "Get number of data elements")
        .def("get_n_dim", &FrameCPP::FrVect::GetNDim, "Get number of dimensions")
        .def(
            "get_dim",
            [](FrameCPP::FrVect& self, unsigned int dim) -> FrameCPP::Dimension& {
                return self.GetDim(dim);
            },
            "dim"_a, nb::rv_policy::reference_internal, "Get dimension at index")
        .def("get_unit_y", &FrameCPP::FrVect::GetUnitY, "Get Y-axis unit")
        .def("is_compressed", &FrameCPP::FrVect::Compression,
             "Check if this vector is compressed (returns 0 if uncompressed, non-zero if "
             "compressed)")
        .def(
            "get_compression_scheme",
            [](FrameCPP::FrVect& self) -> int {
                // GetCompress() returns the compression scheme
                // This is version-specific but should be available at runtime
                return self.GetCompress();
            },
            "Get compression scheme (e.g., 256=RAW, 257=GZIP, 259=DIFF_GZIP)")
        // get_data_array - Create a NumPy array view of the C++ data, not a copy
        .def(
            "get_data_array",
            [](FrameCPP::FrVect& self) -> nb::object {
                auto data_ptr = self.GetDataUncompressed();
                nb::handle owner_handle = nb::cast(&self, nb::rv_policy::reference);
                return create_ndarray_for_type(self.GetType(), data_ptr.get(), self.GetNData(),
                                               owner_handle);
            },
            nb::rv_policy::reference_internal, "Get data array (writable for setting data)")
        // set_data - Directly copy data from NumPy array
        .def(
            "set_data",
            [](FrameCPP::FrVect& self, nb::ndarray<nb::numpy> src) {
                auto dst_ptr = self.GetDataUncompressed();
                size_t n_samples = self.GetNData();

                // Validate array size matches
                if (src.shape(0) != n_samples) {
                    throw std::runtime_error("Array size mismatch");
                }

                // Get element size based on type
                size_t elem_size = 0;
                switch (self.GetType()) {
                case FrameCPP::FrVect::FR_VECT_8R:
                    elem_size = sizeof(double);
                    break;
                case FrameCPP::FrVect::FR_VECT_4R:
                    elem_size = sizeof(float);
                    break;
                case FrameCPP::FrVect::FR_VECT_8S:
                    elem_size = sizeof(int64_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_4S:
                    elem_size = sizeof(int32_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_2S:
                    elem_size = sizeof(int16_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_1U:
                    elem_size = sizeof(uint8_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_2U:
                    elem_size = sizeof(uint16_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_4U:
                    elem_size = sizeof(uint32_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_8U:
                    elem_size = sizeof(uint64_t);
                    break;
                case FrameCPP::FrVect::FR_VECT_8C:
                    elem_size = sizeof(std::complex<float>);
                    break;
                case FrameCPP::FrVect::FR_VECT_16C:
                    elem_size = sizeof(std::complex<double>);
                    break;
                default:
                    throw std::runtime_error("Unsupported FrVect data type");
                }

                // Direct memcpy for maximum speed
                std::memcpy(dst_ptr.get(), src.data(), n_samples * elem_size);
            },
            "src"_a, "Set data from NumPy array (optimized direct copy)")
        // GetDataUncompressed - Get uncompressed data as NumPy array
        .def(
            "get_data_uncompressed",
            [](FrameCPP::FrVect& self) -> nb::object {
                auto data_ptr = self.GetDataUncompressed();
                return create_ndarray_for_type(self.GetType(), data_ptr.get(), self.GetNData());
            },
            nb::rv_policy::reference_internal, "Get uncompressed data as NumPy array");

    // ------------------------------------------------------------------------
    // FrProcData - Processed data container
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrProcData>(m, "FrProcData", "Processed data container")
        // Type constants as static read-only properties
        .def_prop_ro_static(
            "UNKNOWN_TYPE",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::UNKNOWN_TYPE); },
            "Unknown type")
        .def_prop_ro_static(
            "TIME_SERIES",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::TIME_SERIES); },
            "Time series type")
        .def_prop_ro_static(
            "FREQUENCY_SERIES",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::FREQUENCY_SERIES); },
            "Frequency series type")
        .def_prop_ro_static(
            "OTHER_1D_SERIES_DATA",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::OTHER_1D_SERIES_DATA); },
            "Other 1D series type")
        .def_prop_ro_static(
            "TIME_FREQUENCY",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::TIME_FREQUENCY); },
            "Time-frequency type")
        .def_prop_ro_static(
            "WAVELETS", [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::WAVELETS); },
            "Wavelets type")
        .def_prop_ro_static(
            "MULTI_DIMENSIONAL",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::MULTI_DIMENSIONAL); },
            "Multi-dimensional type")
        // Subtype constants as static read-only properties
        .def_prop_ro_static(
            "UNKNOWN_SUB_TYPE",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::UNKNOWN_SUB_TYPE); },
            "Unknown subtype")
        .def_prop_ro_static(
            "DFT", [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::DFT); },
            "DFT subtype")
        .def_prop_ro_static(
            "AMPLITUDE_SPECTRAL_DENSITY",
            [](nb::handle) {
                return static_cast<int>(FrameCPP::FrProcData::AMPLITUDE_SPECTRAL_DENSITY);
            },
            "ASD subtype")
        .def_prop_ro_static(
            "POWER_SPECTRAL_DENSITY",
            [](nb::handle) {
                return static_cast<int>(FrameCPP::FrProcData::POWER_SPECTRAL_DENSITY);
            },
            "PSD subtype")
        .def_prop_ro_static(
            "CROSS_SPECTRAL_DENSITY",
            [](nb::handle) {
                return static_cast<int>(FrameCPP::FrProcData::CROSS_SPECTRAL_DENSITY);
            },
            "CSD subtype")
        .def_prop_ro_static(
            "COHERENCE",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::COHERENCE); },
            "Coherence subtype")
        .def_prop_ro_static(
            "TRANSFER_FUNCTION",
            [](nb::handle) { return static_cast<int>(FrameCPP::FrProcData::TRANSFER_FUNCTION); },
            "Transfer function subtype")
        // Constructor for writing
        .def(nb::init<const std::string&, const std::string&, unsigned short, unsigned short,
                      double, double, double, float, double, double>(),
             "name"_a, "comment"_a, "type"_a, "subtype"_a, "time_offset"_a, "trange"_a,
             "fshift"_a = 0.0, "phase"_a = 0.0f, "frange"_a = 0.0, "bandwidth"_a = 0.0,
             "Create FrProcData for writing")
        .def("get_name", &FrameCPP::FrProcData::GetName, "Get channel name")
        .def("get_comment", &FrameCPP::FrProcData::GetComment, "Get comment")
        .def("get_time_offset", &FrameCPP::FrProcData::GetTimeOffset, "Get time offset")
        .def("get_t_range", &FrameCPP::FrProcData::GetTRange, "Get time range")
        .def("get_f_range", &FrameCPP::FrProcData::GetFRange, "Get frequency range (Nyquist)")
        .def(
            "get_data_size",
            [](FrameCPP::FrProcData& self) -> size_t { return self.RefData().size(); },
            "Get number of data vectors")
        .def(
            "get_data_vector",
            [](FrameCPP::FrProcData& self, size_t index) -> FrameCPP::FrVect* {
                return self.RefData()[index].get();
            },
            "index"_a = 0, nb::rv_policy::reference, "Get data vector at index (default 0)")
        .def(
            "append_data",
            [](FrameCPP::FrProcData& self, FrameCPP::FrVect& vect) {
                self.RefData().append(
                    boost::shared_ptr<FrameCPP::FrVect>(&vect, empty_deleter<FrameCPP::FrVect>));
            },
            "vect"_a, "Append FrVect to this FrProcData");

    // ------------------------------------------------------------------------
    // FrAdcData - ADC data container
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrAdcData>(m, "FrAdcData", "ADC data container")
        // Constructor for writing
        .def(nb::init<const std::string&, unsigned short, unsigned short, unsigned short, double>(),
             "name"_a, "channelgroup"_a, "channelid"_a, "nbits"_a, "sample_rate"_a,
             "Create FrAdcData for writing")
        .def("get_name", &FrameCPP::FrAdcData::GetName, "Get channel name")
        .def("get_comment", &FrameCPP::FrAdcData::GetComment, "Get comment")
        .def("get_time_offset", &FrameCPP::FrAdcData::GetTimeOffset, "Get time offset")
        .def("set_time_offset", &FrameCPP::FrAdcData::SetTimeOffset, "offset"_a, "Set time offset")
        .def("get_sample_rate", &FrameCPP::FrAdcData::GetSampleRate, "Get sample rate")
        .def(
            "get_data_size",
            [](FrameCPP::FrAdcData& self) -> size_t { return self.RefData().size(); },
            "Get number of data vectors")
        .def(
            "get_data_vector",
            [](FrameCPP::FrAdcData& self, size_t index) -> FrameCPP::FrVect* {
                return self.RefData()[index].get();
            },
            "index"_a = 0, nb::rv_policy::reference, "Get data vector at index (default 0)")
        .def(
            "append_data",
            [](FrameCPP::FrAdcData& self, FrameCPP::FrVect& vect) {
                self.RefData().append(
                    boost::shared_ptr<FrameCPP::FrVect>(&vect, empty_deleter<FrameCPP::FrVect>));
            },
            "vect"_a, "Append FrVect to this FrAdcData");

    // ------------------------------------------------------------------------
    // FrSimData - Simulated data container
    // ------------------------------------------------------------------------
    nb::class_<FrameCPP::FrSimData>(m, "FrSimData", "Simulated data container")
        // Constructor for writing
        .def(nb::init<const std::string&, const std::string&, double, double, float, float>(),
             "name"_a, "comment"_a, "sample_rate"_a, "time_offset"_a, "fshift"_a = 0.0f,
             "phase"_a = 0.0f, "Create FrSimData for writing")
        .def("get_name", &FrameCPP::FrSimData::GetName, "Get channel name")
        .def("get_comment", &FrameCPP::FrSimData::GetComment, "Get comment")
        .def("get_time_offset", &FrameCPP::FrSimData::GetTimeOffset, "Get time offset")
        .def("get_sample_rate", &FrameCPP::FrSimData::GetSampleRate, "Get sample rate")
        .def(
            "get_data_size",
            [](FrameCPP::FrSimData& self) -> size_t { return self.RefData().size(); },
            "Get number of data vectors")
        .def(
            "get_data_vector",
            [](FrameCPP::FrSimData& self, size_t index) -> FrameCPP::FrVect* {
                return self.RefData()[index].get();
            },
            "index"_a = 0, nb::rv_policy::reference, "Get data vector at index (default 0)")
        .def(
            "append_data",
            [](FrameCPP::FrSimData& self, FrameCPP::FrVect& vect) {
                self.RefData().append(
                    boost::shared_ptr<FrameCPP::FrVect>(&vect, empty_deleter<FrameCPP::FrVect>));
            },
            "vect"_a, "Append FrVect to this FrSimData");
}
