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
  void apply(const Controller& controller, std::size_t offset = 0) {
    for (std::size_t index = 0; index < Count; ++index) {
      digitalWrite(pins_[index], controller.output(offset + index) ? HIGH : LOW);
    }
  }

 private:
  std::array<uint8_t, Count> pins_;
};

template <std::size_t Count>
class ActiveLowRelayBank {
 public:
  explicit ActiveLowRelayBank(const std::array<uint8_t, Count>& pins) : pins_(pins) {}

  void beginSafe() {
    for (const uint8_t pin : pins_) {
      // A escrita antes de OUTPUT reduz pulsos em módulos ativos em LOW.
      digitalWrite(pin, HIGH);
      pinMode(pin, OUTPUT);
      digitalWrite(pin, HIGH);
    }
  }

  template <typename Controller>
  void apply(const Controller& controller, std::size_t offset = 0) {
    for (std::size_t index = 0; index < Count; ++index) {
      digitalWrite(pins_[index], controller.output(offset + index) ? LOW : HIGH);
    }
  }

 private:
  std::array<uint8_t, Count> pins_;
};

}  // namespace grow
#endif
