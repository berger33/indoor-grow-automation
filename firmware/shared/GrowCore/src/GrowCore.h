#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <cmath>

namespace grow {

enum class NodeState : uint8_t { Boot, Idle, Active, Alarm };
enum class TripReason : uint8_t {
  None,
  Leak,
  ActuatorTimeout,
  HubLost,
  Watchdog,
  SensorInvalid,
  EmergencyStop,
};

struct SensorSample {
  float value;
  bool transport_ok;
  bool fresh;
};

class ReadingGuard {
 public:
  static bool valid(const SensorSample& sample, float minimum, float maximum) {
    return sample.transport_ok && sample.fresh && std::isfinite(sample.value) &&
           sample.value >= minimum && sample.value <= maximum;
  }
};

template <std::size_t OutputCount>
class SafeController {
 public:
  explicit SafeController(uint32_t watchdog_timeout_ms = 5000)
      : watchdog_timeout_ms_(watchdog_timeout_ms) {
    forceAllOff();
  }

  void boot(uint32_t now_ms) {
    forceAllOff();
    state_ = NodeState::Boot;
    reason_ = TripReason::None;
    boot_completed_ = false;
    last_watchdog_feed_ms_ = now_ms;
    watchdog_started_ = true;
  }

  bool completeBoot(bool physical_inputs_safe) {
    if (!physical_inputs_safe || state_ != NodeState::Boot) return false;
    state_ = NodeState::Idle;
    boot_completed_ = true;
    return true;
  }

  bool command(std::size_t output, bool energize, uint32_t now_ms,
               uint32_t absolute_timeout_ms, bool critical_sensor_valid = true) {
    if (!boot_completed_ || state_ == NodeState::Alarm || output >= OutputCount ||
        absolute_timeout_ms == 0 || !critical_sensor_valid) {
      if (!critical_sensor_valid) trip(TripReason::SensorInvalid);
      return false;
    }
    if (!energize) {
      outputs_[output] = false;
      deadlines_[output] = 0;
      state_ = anyOn() ? NodeState::Active : NodeState::Idle;
      return true;
    }
    if (outputs_[output]) return true;  // Repetição não renova o prazo absoluto.
    outputs_[output] = true;
    deadlines_[output] = now_ms + absolute_timeout_ms;
    state_ = NodeState::Active;
    return true;
  }

  void tick(uint32_t now_ms, bool leak_wet, bool hub_online, bool emergency_stop) {
    if (state_ == NodeState::Alarm) return;
    if (emergency_stop) return trip(TripReason::EmergencyStop);
    if (leak_wet) return trip(TripReason::Leak);
    if (!hub_online && state_ == NodeState::Active) return trip(TripReason::HubLost);
    if (watchdog_started_ && elapsed(now_ms, last_watchdog_feed_ms_) >= watchdog_timeout_ms_) {
      return trip(TripReason::Watchdog);
    }
    for (std::size_t i = 0; i < OutputCount; ++i) {
      if (outputs_[i] && deadlineReached(now_ms, deadlines_[i])) {
        return trip(TripReason::ActuatorTimeout);
      }
    }
  }

  void feedWatchdog(uint32_t now_ms) {
    if (state_ != NodeState::Alarm) {
      last_watchdog_feed_ms_ = now_ms;
      watchdog_started_ = true;
    }
  }

  bool resetAlarm(bool leak_dry, bool emergency_released, bool physical_ack) {
    if (state_ != NodeState::Alarm || !leak_dry || !emergency_released || !physical_ack) {
      return false;
    }
    forceAllOff();
    reason_ = TripReason::None;
    state_ = NodeState::Boot;
    boot_completed_ = false;
    return true;
  }

  bool output(std::size_t index) const {
    return index < OutputCount ? outputs_[index] : false;
  }
  NodeState state() const { return state_; }
  TripReason reason() const { return reason_; }

 private:
  static uint32_t elapsed(uint32_t now, uint32_t before) { return now - before; }
  static bool deadlineReached(uint32_t now, uint32_t deadline) {
    return static_cast<int32_t>(now - deadline) >= 0;
  }
  bool anyOn() const {
    for (const bool value : outputs_) if (value) return true;
    return false;
  }
  void forceAllOff() {
    outputs_.fill(false);
    deadlines_.fill(0);
  }
  void trip(TripReason reason) {
    forceAllOff();
    state_ = NodeState::Alarm;
    reason_ = reason;
  }

  std::array<bool, OutputCount> outputs_{};
  std::array<uint32_t, OutputCount> deadlines_{};
  NodeState state_{NodeState::Boot};
  TripReason reason_{TripReason::None};
  uint32_t watchdog_timeout_ms_;
  uint32_t last_watchdog_feed_ms_{0};
  bool watchdog_started_{false};
  bool boot_completed_{false};
};

}  // namespace grow
