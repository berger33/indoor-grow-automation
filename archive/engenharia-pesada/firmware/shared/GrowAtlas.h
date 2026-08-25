#pragma once

#ifdef ARDUINO
#include <Arduino.h>
#include <Wire.h>

namespace grow {

struct AtlasResult {
  float value;
  bool valid;
  uint8_t status;
};

class AtlasEzoI2C {
 public:
  explicit AtlasEzoI2C(uint8_t address) : address_(address) {}

  bool startRead(uint32_t now_ms) {
    if (pending_) return false;
    Wire.beginTransmission(address_);
    Wire.write('R');
    if (Wire.endTransmission() != 0) return false;
    pending_ = true;
    ready_at_ms_ = now_ms + 900;
    return true;
  }

  AtlasResult finishRead(uint32_t now_ms) {
    if (!pending_ || static_cast<int32_t>(now_ms - ready_at_ms_) < 0) {
      return {0.0F, false, 254};
    }
    pending_ = false;
    const uint8_t count = Wire.requestFrom(address_, static_cast<uint8_t>(20));
    if (count < 2) return {0.0F, false, 255};
    const uint8_t status = Wire.read();
    char buffer[19]{};
    std::size_t index = 0;
    while (Wire.available() && index < sizeof(buffer) - 1) {
      const char value = static_cast<char>(Wire.read());
      if (value == 0) break;
      buffer[index++] = value;
    }
    if (status != 1 || index == 0) return {0.0F, false, status};
    char* end = nullptr;
    const float value = strtof(buffer, &end);
    return {value, end != buffer && isfinite(value), status};
  }

  bool setTemperature(float celsius) {
    if (!isfinite(celsius) || celsius < 0.0F || celsius > 50.0F || pending_) return false;
    char command[16]{};
    snprintf(command, sizeof(command), "T,%.2f", static_cast<double>(celsius));
    Wire.beginTransmission(address_);
    Wire.write(reinterpret_cast<const uint8_t*>(command), strlen(command));
    return Wire.endTransmission() == 0;
  }

 private:
  uint8_t address_;
  uint32_t ready_at_ms_{0};
  bool pending_{false};
};

}  // namespace grow
#endif
