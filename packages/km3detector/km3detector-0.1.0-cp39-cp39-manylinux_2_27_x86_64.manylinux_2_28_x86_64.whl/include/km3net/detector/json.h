#ifndef KM3NET_DETECTOR_JSON_H
#define KM3NET_DETECTOR_JSON_H

#include "km3net/detector/detector.h"
#include <ostream>

namespace km3net::detector {

  void writeJson(const Detector &detector, std::ostream &out);

  // convenience functions
  void writeJsonFile(const Detector &detector, const std::string &filename);
}  // namespace km3net::detector

#endif
