#pragma once

#include <cstdint>

namespace grow {

class RetryThrottle {
 public:
  explicit RetryThrottle(uint32_t interval_ms) : interval_ms_(interval_ms) {}

  bool due(uint32_t now_ms) {
    if (!armed_ || reached(now_ms, next_ms_)) {
      next_ms_ = now_ms + interval_ms_;
      armed_ = true;
      return true;
    }
    return false;
  }

  void reset() { armed_ = false; }

 private:
  static bool reached(uint32_t now_ms, uint32_t deadline_ms) {
    return static_cast<int32_t>(now_ms - deadline_ms) >= 0;
  }

  uint32_t interval_ms_;
  uint32_t next_ms_{0};
  bool armed_{false};
};

class HeartbeatSchedule {
 public:
  explicit HeartbeatSchedule(uint32_t interval_ms) : interval_ms_(interval_ms) {}

  bool due(uint32_t now_ms, bool connected) {
    if (!connected) {
      armed_ = false;
      return false;
    }
    if (!armed_ || reached(now_ms, next_ms_)) {
      next_ms_ = now_ms + interval_ms_;
      armed_ = true;
      ++sequence_;
      return true;
    }
    return false;
  }

  uint32_t sequence() const { return sequence_; }

 private:
  static bool reached(uint32_t now_ms, uint32_t deadline_ms) {
    return static_cast<int32_t>(now_ms - deadline_ms) >= 0;
  }

  uint32_t interval_ms_;
  uint32_t next_ms_{0};
  uint32_t sequence_{0};
  bool armed_{false};
};

}  // namespace grow
