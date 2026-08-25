#pragma once

#include <algorithm>
#include <cstdint>

constexpr uint8_t LOW = 0;
constexpr uint8_t HIGH = 1;
constexpr uint8_t INPUT = 0;
constexpr uint8_t OUTPUT = 1;
constexpr uint8_t INPUT_PULLUP = 2;
constexpr uint8_t ADC_11db = 3;

inline void digitalWrite(uint8_t, uint8_t) {}
inline void pinMode(uint8_t, uint8_t) {}
inline int digitalRead(uint8_t) { return LOW; }
inline void analogSetPinAttenuation(uint8_t, uint8_t) {}
inline uint32_t analogReadMilliVolts(uint8_t) { return 1500; }
inline uint32_t millis() { return 1; }
inline void delay(uint32_t) {}

template <typename T>
constexpr T min(T left, T right) {
  return std::min(left, right);
}

class SerialStub {
 public:
  void begin(uint32_t) {}

  template <typename... Args>
  int printf(const char*, Args...) {
    return 0;
  }
};

inline SerialStub Serial;
