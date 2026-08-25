#pragma once

#ifdef ARDUINO
#include <Arduino.h>

#include <array>
#include <cstddef>

namespace grow {

template <std::size_t Count>
class DirectOutputBank {
 public:
  explicit DirectOutputBank(const std::array<uint8_t, Count>& pins) : pins_(pins) {}

  void beginSafe() {
    for (const uint8_t pin : pins_) {
      digitalWrite(pin, LOW);
      pinMode(pin, OUTPUT);
      digitalWrite(pin, LOW);
    }
  }

  template <typename Controller>
  void apply(const Controller& controller) {
    for (std::size_t index = 0; index < Count; ++index) {
      digitalWrite(pins_[index], controller.output(index) ? HIGH : LOW);
    }
  }

 private:
  std::array<uint8_t, Count> pins_;
};

class ShiftRegisterOutputs {
 public:
  ShiftRegisterOutputs(uint8_t data, uint8_t clock, uint8_t latch, uint8_t output_enable)
      : data_(data), clock_(clock), latch_(latch), output_enable_(output_enable) {}

  void beginSafe() {
    digitalWrite(output_enable_, HIGH);
    pinMode(output_enable_, OUTPUT);
    pinMode(data_, OUTPUT);
    pinMode(clock_, OUTPUT);
    pinMode(latch_, OUTPUT);
    write(0);
  }

  void enable() { digitalWrite(output_enable_, LOW); }
  void disable() {
    digitalWrite(output_enable_, HIGH);
    write(0);
  }

  template <typename Controller>
  void apply(const Controller& controller) {
    uint16_t word = 0;
    for (std::size_t index = 0; index < 16; ++index) {
      if (controller.output(index)) word |= static_cast<uint16_t>(1U << index);
    }
    write(word);
  }

 private:
  void write(uint16_t word) {
    digitalWrite(latch_, LOW);
    shiftOut(data_, clock_, MSBFIRST, static_cast<uint8_t>(word >> 8));
    shiftOut(data_, clock_, MSBFIRST, static_cast<uint8_t>(word & 0xFF));
    digitalWrite(latch_, HIGH);
  }

  uint8_t data_;
  uint8_t clock_;
  uint8_t latch_;
  uint8_t output_enable_;
};

}  // namespace grow
#endif
