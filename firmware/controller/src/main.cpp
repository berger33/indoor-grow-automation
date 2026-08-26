#include <Arduino.h>
#include <DHT.h>
#include <GrowBoard.h>
#include <GrowCore.h>
#include <Preferences.h>

#include "GrowMqtt.h"

#include <array>
#include <cmath>

namespace pins {
constexpr std::array<uint8_t, 6> kDosing{21, 22, 23, 25, 26, 27};
constexpr std::array<uint8_t, 6> kRelays{13, 14, 16, 17, 18, 19};
constexpr uint8_t kDht22 = 4;
constexpr uint8_t kMinimumLevel = 32;
constexpr uint8_t kMaximumLevel = 33;
constexpr uint8_t kPhAnalog = 34;
constexpr uint8_t kEcAnalog = 35;
constexpr uint8_t kLeak = 36;
constexpr uint8_t kLocalStop = 39;
}  // namespace pins

enum Output : std::size_t {
  PhDown = 0,
  Nutrient1 = 1,
  Nutrient2 = 2,
  Nutrient3 = 3,
  Nutrient4 = 4,
  PhUp = 5,
  Mixing = 6,
  Irrigation = 7,
  Drain = 8,
  Exhaust = 9,
  Humidifier = 10,
  Auxiliary = 11,
  Count = 12,
};

struct LinearCalibration {
  float slope{NAN};
  float intercept{NAN};

  bool valid() const {
    return std::isfinite(slope) && std::isfinite(intercept) && slope != 0.0F;
  }

  float convert(float volts) const {
    return valid() && std::isfinite(volts) ? slope * volts + intercept : NAN;
  }
};

grow::SafeController<Output::Count> controller(5000);
grow::DirectOutputBank<6> dosing_outputs(pins::kDosing);
grow::ActiveLowRelayBank<6> relay_outputs(pins::kRelays);
DHT climate_sensor(pins::kDht22, DHT22);
Preferences preferences;
grow::mqtt::Connection hub_connection;
LinearCalibration ph_calibration;
LinearCalibration ec_calibration;
uint8_t wet_confirmations = 0;
uint32_t last_sample_ms = 0;
bool exhaust_demand = false;
bool humidifier_demand = false;

static bool physicalInputsSafe() {
  return digitalRead(pins::kLeak) == LOW &&
         digitalRead(pins::kLocalStop) == HIGH;
}

static bool commandDosing(Output output, bool energize, uint32_t now_ms,
                          uint32_t timeout_ms, bool chemistry_valid) {
  if (output > PhUp) return false;
  if ((output == PhDown && controller.output(PhUp)) ||
      (output == PhUp && controller.output(PhDown))) {
    return false;
  }
  return controller.commandOneOf(output, PhDown, Mixing, energize, now_ms,
                                 timeout_ms, chemistry_valid);
}

static bool commandWater(Output output, bool energize, uint32_t now_ms,
                         uint32_t timeout_ms, bool level_valid) {
  if (output == Irrigation) {
    return controller.commandExclusive(Irrigation, Drain, energize, now_ms,
                                       timeout_ms, level_valid);
  }
  if (output == Drain) {
    return controller.commandExclusive(Drain, Irrigation, energize, now_ms,
                                       timeout_ms, level_valid);
  }
  return false;
}

static void loadCalibration() {
  preferences.begin("grow-diy", true);
  if (preferences.isKey("ph_slope") && preferences.isKey("ph_offset")) {
    ph_calibration.slope = preferences.getFloat("ph_slope");
    ph_calibration.intercept = preferences.getFloat("ph_offset");
  }
  if (preferences.isKey("ec_slope") && preferences.isKey("ec_offset")) {
    ec_calibration.slope = preferences.getFloat("ec_slope");
    ec_calibration.intercept = preferences.getFloat("ec_offset");
  }
  preferences.end();
}

void setup() {
  dosing_outputs.beginSafe();
  relay_outputs.beginSafe();
  pinMode(pins::kMinimumLevel, INPUT_PULLUP);
  pinMode(pins::kMaximumLevel, INPUT_PULLUP);
  // GPIO36/GPIO39 não têm pull interno: o io-map exige resistores externos.
  pinMode(pins::kLeak, INPUT);
  pinMode(pins::kLocalStop, INPUT);
  analogSetPinAttenuation(pins::kPhAnalog, ADC_11db);
  analogSetPinAttenuation(pins::kEcAnalog, ADC_11db);
  climate_sensor.begin();
  Serial.begin(115200);
  loadCalibration();
  hub_connection.begin();
  controller.boot(millis());
  controller.completeBoot(physicalInputsSafe());
  // Referencia a função para que warnings tratem o roteador como parte do build.
  (void)commandDosing;
  (void)commandWater;
}

void loop() {
  const uint32_t now = millis();
  hub_connection.loop(now);
  const bool wet_sample = digitalRead(pins::kLeak) == HIGH;
  wet_confirmations = wet_sample
                          ? static_cast<uint8_t>(min(3, wet_confirmations + 1))
                          : 0;
  const bool leak_confirmed = wet_confirmations >= 3;
  const bool local_stop = digitalRead(pins::kLocalStop) == LOW;
  controller.feedWatchdog(now);
  controller.tick(now, leak_confirmed, hub_connection.connected(), local_stop);

  if (now - last_sample_ms >= 2000 &&
      controller.state() != grow::NodeState::Boot &&
      controller.state() != grow::NodeState::Alarm) {
    last_sample_ms = now;
    const float temperature = climate_sensor.readTemperature();
    const float humidity = climate_sensor.readHumidity();
    const bool climate_valid =
        grow::ReadingGuard::valid({temperature, true, true}, -10.0F, 60.0F) &&
        grow::ReadingGuard::valid({humidity, true, true}, 0.0F, 100.0F);

    if (!climate_valid || temperature >= 28.0F || humidity >= 85.0F) {
      exhaust_demand = true;
    } else if (temperature <= 26.0F && humidity <= 78.0F) {
      exhaust_demand = false;
    }
    if (!climate_valid || exhaust_demand || humidity >= 65.0F) {
      humidifier_demand = false;
    } else if (humidity <= 55.0F) {
      humidifier_demand = true;
    }

    controller.command(Exhaust, exhaust_demand, now, 6UL * 60UL * 60UL * 1000UL);
    controller.command(Humidifier, humidifier_demand, now,
                       30UL * 60UL * 1000UL, climate_valid && !leak_confirmed);

    const float ph_volts = analogReadMilliVolts(pins::kPhAnalog) / 1000.0F;
    const float ec_volts = analogReadMilliVolts(pins::kEcAnalog) / 1000.0F;
    const float ph = ph_calibration.convert(ph_volts);
    const float ec = ec_calibration.convert(ec_volts);
    const bool level_minimum = digitalRead(pins::kMinimumLevel) == LOW;
    const bool level_maximum = digitalRead(pins::kMaximumLevel) == LOW;
    Serial.printf(
        "heartbeat=controller state=%u temp=%.2f ur=%.2f ph_v=%.3f ph=%.3f "
        "ec_v=%.3f ec=%.3f level_min=%u level_max=%u calibrated=%u\n",
        static_cast<unsigned>(controller.state()), temperature, humidity,
        ph_volts, ph, ec_volts, ec, level_minimum, level_maximum,
        ph_calibration.valid() && ec_calibration.valid());
  }

  dosing_outputs.apply(controller, PhDown);
  relay_outputs.apply(controller, Mixing);
  delay(10);
}

#ifndef ARDUINO_ARCH_ESP32
int main() {
  setup();
  loop();
  return 0;
}
#endif
