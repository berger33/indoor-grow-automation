#pragma once

#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace grow {

struct PumpCalibration {
  float milliliters_per_second;
  float intercept_milliliters;
  bool valid;

  uint32_t runtimeMs(float requested_ml, uint32_t maximum_ms) const {
    if (!valid || !std::isfinite(requested_ml) || requested_ml <= intercept_milliliters ||
        milliliters_per_second <= 0.0F) {
      return 0;
    }
    const float milliseconds =
        (requested_ml - intercept_milliliters) / milliliters_per_second * 1000.0F;
    if (!std::isfinite(milliseconds) || milliseconds <= 0.0F || milliseconds > maximum_ms) {
      return 0;
    }
    return static_cast<uint32_t>(milliseconds);
  }
};

enum class BatchStage : uint8_t {
  Idle,
  Fill,
  Dose,
  Homogenize,
  EcCorrection,
  PhCorrection,
  Ready,
  Alarm,
};

enum BatchOutput : uint16_t {
  FillWater = 1U << 0,
  Mixer = 1U << 1,
  Nutrient0 = 1U << 2,
  PhDown = 1U << 8,
  PhUp = 1U << 9,
};

struct BatchConfig {
  float target_ph{6.0F};
  float ph_deadband{0.1F};
  float target_ec{1.8F};
  float ec_deadband{0.1F};
  uint32_t between_nutrients_ms{60'000};
  uint32_t homogenize_ms{60'000};
  uint32_t ph_settle_ms{60'000};
  uint32_t ph_pulse_ms{1'000};
  uint32_t dilution_timeout_ms{480'000};
  uint32_t chemistry_timeout_ms{900'000};
};

struct BatchInputs {
  float mix_liters;
  float ph;
  float ec;
  bool critical_readings_valid;
  bool water_available;
  bool capacity_available;
  bool leak_detected;
  bool emergency_stop;
};

class BatchController {
 public:
  explicit BatchController(BatchConfig config = BatchConfig()) : config_(config) {}

  bool start(uint32_t now_ms, float target_liters,
             const std::array<float, 6>& recipe_ml,
             const PumpCalibration& fill_calibration,
             const std::array<PumpCalibration, 6>& nutrient_calibrations,
             const PumpCalibration& ph_down_calibration,
             const PumpCalibration& ph_up_calibration) {
    if (stage_ != BatchStage::Idle || !std::isfinite(target_liters) ||
        target_liters < 1.0F || target_liters > 50.0F || !fill_calibration.valid ||
        !ph_down_calibration.valid || !ph_up_calibration.valid) {
      return false;
    }
    for (std::size_t index = 0; index < recipe_ml.size(); ++index) {
      if (!std::isfinite(recipe_ml[index]) || recipe_ml[index] < 0.0F ||
          recipe_ml[index] > 500.0F || !nutrient_calibrations[index].valid) {
        return false;
      }
    }
    target_liters_ = target_liters;
    recipe_ml_ = recipe_ml;
    fill_calibration_ = fill_calibration;
    nutrient_calibrations_ = nutrient_calibrations;
    ph_down_calibration_ = ph_down_calibration;
    ph_up_calibration_ = ph_up_calibration;
    stage_ = BatchStage::Fill;
    stage_started_ms_ = now_ms;
    sequence_ = 0;
    output_word_ = 0;
    return true;
  }

  uint16_t tick(uint32_t now_ms, const BatchInputs& inputs) {
    if (stage_ == BatchStage::Idle || stage_ == BatchStage::Ready ||
        stage_ == BatchStage::Alarm) {
      return output_word_ = 0;
    }
    if (inputs.leak_detected || inputs.emergency_stop ||
        !inputs.critical_readings_valid) {
      trip();
      return output_word_;
    }
    switch (stage_) {
      case BatchStage::Fill:
        return fill(now_ms, inputs);
      case BatchStage::Dose:
        return dose(now_ms);
      case BatchStage::Homogenize:
        output_word_ = Mixer;
        if (elapsed(now_ms) >= config_.homogenize_ms) enter(BatchStage::EcCorrection, now_ms);
        return output_word_;
      case BatchStage::EcCorrection:
        return correctEc(now_ms, inputs);
      case BatchStage::PhCorrection:
        return correctPh(now_ms, inputs);
      default:
        return output_word_ = 0;
    }
  }

  BatchStage stage() const { return stage_; }
  std::size_t sequence() const { return sequence_; }
  uint16_t outputs() const { return output_word_; }

 private:
  uint16_t fill(uint32_t now_ms, const BatchInputs& inputs) {
    if (!inputs.water_available || !inputs.capacity_available) return trip();
    if (inputs.mix_liters >= target_liters_) {
      enter(BatchStage::Dose, now_ms);
      return output_word_ = Mixer;
    }
    if (elapsed(now_ms) >= fill_calibration_.runtimeMs(target_liters_ * 1000.0F, 480'000)) {
      return trip();
    }
    return output_word_ = FillWater;
  }

  uint16_t dose(uint32_t now_ms) {
    if (sequence_ >= recipe_ml_.size()) {
      enter(BatchStage::Homogenize, now_ms);
      return output_word_ = Mixer;
    }
    const uint32_t runtime = nutrient_calibrations_[sequence_].runtimeMs(
        recipe_ml_[sequence_], 30'000);
    if (recipe_ml_[sequence_] > 0.0F && runtime == 0) return trip();
    const uint32_t stage_elapsed = elapsed(now_ms);
    if (stage_elapsed < runtime) {
      return output_word_ = static_cast<uint16_t>(Nutrient0 << sequence_);
    }
    if (stage_elapsed < runtime + config_.between_nutrients_ms) {
      return output_word_ = Mixer;
    }
    ++sequence_;
    stage_started_ms_ = now_ms;
    return output_word_ = Mixer;
  }

  uint16_t correctEc(uint32_t now_ms, const BatchInputs& inputs) {
    if (inputs.ec < config_.target_ec - config_.ec_deadband) return trip();
    if (inputs.ec <= config_.target_ec + config_.ec_deadband) {
      enter(BatchStage::PhCorrection, now_ms);
      return output_word_ = Mixer;
    }
    if (!inputs.water_available || !inputs.capacity_available ||
        elapsed(now_ms) >= config_.dilution_timeout_ms) {
      return trip();
    }
    return output_word_ = static_cast<uint16_t>(FillWater | Mixer);
  }

  uint16_t correctPh(uint32_t now_ms, const BatchInputs& inputs) {
    if (elapsed(now_ms) >= config_.chemistry_timeout_ms) return trip();
    if (inputs.ph >= config_.target_ph - config_.ph_deadband &&
        inputs.ph <= config_.target_ph + config_.ph_deadband) {
      stage_ = BatchStage::Ready;
      return output_word_ = 0;
    }
    const uint32_t cycle = config_.ph_pulse_ms + config_.ph_settle_ms;
    const bool pulse = elapsed(now_ms) % cycle < config_.ph_pulse_ms;
    if (!pulse) return output_word_ = Mixer;
    if (inputs.ph > config_.target_ph) {
      if (ph_down_calibration_.runtimeMs(1.0F, config_.ph_pulse_ms) == 0) return trip();
      return output_word_ = PhDown;
    }
    if (ph_up_calibration_.runtimeMs(1.0F, config_.ph_pulse_ms) == 0) return trip();
    return output_word_ = PhUp;
  }

  uint16_t trip() {
    stage_ = BatchStage::Alarm;
    return output_word_ = 0;
  }
  uint32_t elapsed(uint32_t now_ms) const { return now_ms - stage_started_ms_; }
  void enter(BatchStage stage, uint32_t now_ms) {
    stage_ = stage;
    stage_started_ms_ = now_ms;
  }

  BatchConfig config_{};
  BatchStage stage_{BatchStage::Idle};
  float target_liters_{0.0F};
  std::array<float, 6> recipe_ml_{};
  PumpCalibration fill_calibration_{};
  std::array<PumpCalibration, 6> nutrient_calibrations_{};
  PumpCalibration ph_down_calibration_{};
  PumpCalibration ph_up_calibration_{};
  uint32_t stage_started_ms_{0};
  std::size_t sequence_{0};
  uint16_t output_word_{0};
};

}  // namespace grow
