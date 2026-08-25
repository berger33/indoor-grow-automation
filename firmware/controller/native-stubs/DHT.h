#pragma once

#include <cstdint>

constexpr uint8_t DHT22 = 22;

class DHT {
 public:
  DHT(uint8_t, uint8_t) {}
  void begin() {}
  float readTemperature() { return 25.0F; }
  float readHumidity() { return 60.0F; }
};
