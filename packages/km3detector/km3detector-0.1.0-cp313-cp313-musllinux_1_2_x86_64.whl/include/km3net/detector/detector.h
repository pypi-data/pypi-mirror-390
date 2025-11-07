#ifndef KM3NET_DETECTOR_H
#define KM3NET_DETECTOR_H

#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <vector>
#include "km3net/detector/version.h"
#include "km3net/detector/module.h"

namespace km3net::detector {

  /**
   * The validity of the detector description
   *
   * (e.g. the validity time span of the alignment) in
   * Unix time UTC in seconds (0.1 s precision)
   */
  struct UTCTimeRange
  {
    /// UTC time, start of the validity of the detector file; e.g 0.0
    double valid_from{};
    /// UTC time, end of the validity of the detector file; e.g. 999999999999.9
    double valid_up_to{};
  };

  /**
   * UTM reference ellipsoid and UTM zone
   */
  struct UTMGrid
  {
    std::string key;   ///< UTM
    std::string wgs;   ///< WGS84
    std::string zone;  ///< 33N for ARCA, 32N for ORCA
  };

  /**
   * UTM position (in meters)
   */
  struct UTMPosition
  {
    double east{};   ///< easting of the UTM reference point of detector site
    double north{};  ///< northing of the UTM reference point of detector site
    double z{};      ///< depth below sea surface of the UTM reference point of detector site

    auto operator<=>(const UTMPosition &) const = default;
  };

  /**
   * Description of the detector geometry.
   *
   * It includes all necessary information about the detector position
   * (including all individual PMTs) and timing calibration.
   */
  class Detector
  {
  public:

    Detector(uint32_t                        id,
             Version                         version,
             const UTCTimeRange             &utc_time_range = {},
             const UTMGrid                  &utm_grid       = {},
             const UTMPosition              &utm_position   = {},
             const std::vector<std::string> &comments       = {});

    void append(const Module &module);

    [[nodiscard]] uint32_t id() const { return id_; }
    [[nodiscard]] Version  version() const { return version_; }

    [[nodiscard]] std::vector<Module> modules() const { return modules_; }

    [[nodiscard]] std::optional<Module> module(uint32_t module_id) const;
    [[nodiscard]] std::optional<Module> module(Location location) const;
    [[nodiscard]] std::optional<PMT>    pmt(uint32_t pmt_id) const;

    [[nodiscard]] std::vector<uint32_t>    duIDs() const { return du_ids_; }
    [[nodiscard]] std::vector<std::string> comments() const { return comments_; }

    void stripComments();

    [[nodiscard]] UTCTimeRange utc_time_range() const { return utc_time_range_; }
    [[nodiscard]] UTMGrid      utm_grid() const { return utm_grid_; }
    [[nodiscard]] UTMPosition  utm_position() const { return utm_position_; }

  private:

    /**
     * Textual comments.
     * e.g. how the detector file was created
     * and/or manipulated since its original creation.
     * Possibly empty.
     */
    std::vector<std::string> comments_;
    /// Detector Identifier
    uint32_t id_{};
    /// Version number
    Version version_;
    /// Validity time range
    UTCTimeRange utc_time_range_{};
    /// UTM Grid
    UTMGrid utm_grid_{};
    /// UTM Position
    UTMPosition utm_position_{};
    /// List of Modules (either base or optical modules)
    std::vector<Module> modules_;

    /// Update the internal maps
    void update();

    /// Internal list of DU numbers
    std::vector<uint32_t> du_ids_;
    /// Internal map to go from module ID (unique) to index in the modules vector
    std::map<uint32_t, uint32_t> module_to_index_;
    /// Internal map to go from Location to index in the modules vector
    std::map<Location, uint32_t> location_to_index_;
    /// Internal map to go from a PMT ID (unique) to a module ID (unique)
    std::map<uint32_t, uint32_t> pmt_id_to_module_id_;
  };


}  // namespace km3net::detector

#endif
