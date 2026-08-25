#include <Arduino.h>
#include <DallasTemperature.h>
#include <GrowAtlas.h>
#include <GrowBoard.h>
#include <GrowCore.h>
#include <HX711.h>
#include <OneWire.h>
#include <Preferences.h>
#include <Wire.h>

namespace pins {
constexpr uint8_t kShiftData = 23;
constexpr uint8_t kShiftClock = 18;
constexpr uint8_t kShiftLatch = 5;
constexpr uint8_t kShiftOutputEnable = 19;
constexpr uint8_t kLeak = 34;
constexpr uint8_t kEmergencyStop = 35;
constexpr uint8_t kOneWire = 4;
constexpr uint8_t kWaterScaleData = 32;
constexpr uint8_t kMixScaleData = 33;
constexpr uint8_t kScaleClock = 25;
}  // namespace pins

grow::SafeController<16> controller(5000);
grow::ShiftRegisterOutputs outputs(
    pins::kShiftData, pins::kShiftClock, pins::kShiftLatch, pins::kShiftOutputEnable);
OneWire one_wire(pins::kOneWire);
DallasTemperature water_temperature(&one_wire);
HX711 water_scale;
HX711 mix_scale;
Preferences preferences;
grow::AtlasEzoI2C ph_probe(99);
grow::AtlasEzoI2C ec_probe(100);
uint32_t last_cycle_ms = 0;
bool probes_pending = false;
float last_water_temperature = NAN;

static bool inputsSafe() {
  return digitalRead(pins::kLeak) == LOW && digitalRead(pins::kEmergencyStop) == HIGH;
}

void setup() {
  outputs.beginSafe();
  pinMode(pins::kLeak, INPUT_PULLDOWN);
  pinMode(pins::kEmergencyStop, INPUT_PULLUP);
  controller.boot(millis());
  Serial.begin(115200);
  Wire.begin();
  water_temperature.begin();
  water_temperature.setWaitForConversion(false);
  water_scale.begin(pins::kWaterScaleData, pins::kScaleClock);
  mix_scale.begin(pins::kMixScaleData, pins::kScaleClock);
  preferences.begin("grow-cal", true);
  const bool calibrated = preferences.isKey("water_scale") && preferences.isKey("mix_scale");
  if (calibrated && inputsSafe() && controller.completeBoot(true)) outputs.enable();
  water_temperature.requestTemperatures();
}

void loop() {
  const uint32_t now = millis();
  const bool leak_wet = digitalRead(pins::kLeak) == HIGH;
  const bool emergency_stop = digitalRead(pins::kEmergencyStop) == LOW;
  controller.feedWatchdog(now);
  controller.tick(now, leak_wet, true, emergency_stop);

  if (now - last_cycle_ms >= 1000) {
    last_cycle_ms = now;
    last_water_temperature = water_temperature.getTempCByIndex(0);
    water_temperature.requestTemperatures();
    const bool temperature_valid =
        grow::ReadingGuard::valid({last_water_temperature, true, true}, -20.0F, 60.0F);
    const bool scales_ready = water_scale.is_ready() && mix_scale.is_ready();
    if (temperature_valid && scales_ready && !probes_pending) {
      ph_probe.setTemperature(last_water_temperature);
      ec_probe.setTemperature(last_water_temperature);
      probes_pending = ph_probe.startRead(now) && ec_probe.startRead(now);
    }
    Serial.printf("heartbeat=fertigation state=%u temp_valid=%u scales=%u\n",
                  static_cast<unsigned>(controller.state()), temperature_valid, scales_ready);
  }

  if (probes_pending) {
    const grow::AtlasResult ph = ph_probe.finishRead(now);
    const grow::AtlasResult ec = ec_probe.finishRead(now);
    if (ph.status != 254 && ec.status != 254) {
      probes_pending = false;
      Serial.printf("ph_valid=%u ec_valid=%u\n", ph.valid, ec.valid);
    }
  }

  outputs.apply(controller);
  if (controller.state() == grow::NodeState::Alarm) outputs.disable();
  delay(10);
}
