#ifndef KM3NET_DETECTOR_DETX_H
#define KM3NET_DETECTOR_DETX_H

#include "km3net/detector/detector.h"
#include <iostream>

namespace km3net::detector {

  Detector readDetx(std::istream &in);
  void     writeDetx(const Detector &detector, std::ostream &out);

  // convenience functions
  Detector readDetxFile(const std::string &filename);
  void     writeDetxFile(const Detector &detector, const std::string &filename);

  // toString functions
  std::string toString(const Position3D &pos);
  std::string toString(const Quaternion3D &quaternion);
  std::string toString(const Direction3D &direction);
  std::string toString(const UTCTimeRange &utc_time_range);
  std::string toString(const UTMGrid &grid);
  std::string toString(const UTMPosition &utm);
  std::string toString(const PMT &pmt);
  std::string toString(const Location &location);
  std::string toString(const Module &m);
  std::string toString(const Detector &detector);

}  // namespace km3net::detector

#endif
