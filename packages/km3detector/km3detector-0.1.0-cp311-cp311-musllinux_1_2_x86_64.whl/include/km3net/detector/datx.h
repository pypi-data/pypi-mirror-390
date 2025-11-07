#ifndef KM3NET_DETECTORDatxH
#define KM3NET_DETECTORDatxH

#include "km3net/detector/detector.h"
#include <iostream>

namespace km3net::detector {

  Detector readDatx(std::istream &in);
  void     writeDatx(const Detector &detector, std::ostream &out);

  // convenience functions
  Detector readDatxFile(const std::string &filename);
  void     writeDatxFile(const Detector &detector, const std::string &filename);

}  // namespace km3net::detector

#endif
