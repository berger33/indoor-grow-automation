#include <Adafruit_BME280.h>
#include <Adafruit_MLX90614.h>
#include <Arduino.h>
#include <GrowBoard.h>
#include <GrowCore.h>
#include <Wire.h>

#include <array>

namespace pins {
constexpr uint8_t kExhaust = 25;
constexpr uint8_t kHumidifier = 26;
constexpr uint8_t kHumidifierLevel = 34;
constexpr uint8_t kLeak = 35;
constexpr uint8_t kEmergencyStop = 27;
constexpr uint8_t kCo2Analog = 33;
}  // namespace pins

grow::SafeController<2> controller(5000);
grow::DirectOutputBank<2> outputs(std::array<uint8_t, 2>{pins::kExhaust, pins::kHumidifier});
Adafruit_BME280 bme;
Adafruit_MLX90614 mlx;
uint32_t last_sample_ms = 0;

void setup() {
  outputs.beginSafe();
  pinMode(pins::kHumidifierLevel, INPUT_PULLDOWN);
  pinMode(pins::kLeak, INPUT_PULLDOWN);
  pinMode(pins::kEmergencyStop, INPUT_PULLUP);
  controller.boot(millis());
  Serial.begin(115200);
  Wire.begin();
  const bool sensors_ok = bme.begin(0x76) && mlx.begin();
  const bool physical_safe = digitalRead(pins::kLeak) == LOW &&
                             digitalRead(pins::kEmergencyStop) == HIGH;
  controller.completeBoot(sensors_ok && physical_safe);
}

void loop() {
  const uint32_t now = millis();
  const bool leak_wet = digitalRead(pins::kLeak) == HIGH;
  const bool emergency_stop = digitalRead(pins::kEmergencyStop) == LOW;
  controller.feedWatchdog(now);
  controller.tick(now, leak_wet, true, emergency_stop);

  if (now - last_sample_ms >= 2000 && controller.state() != grow::NodeState::Boot) {
    last_sample_ms = now;
    const float temperature = bme.readTemperature();
    const float humidity = bme.readHumidity();
    const float leaf = mlx.readObjectTempC();
    const bool climate_valid =
        grow::ReadingGuard::valid({temperature, true, true}, -20.0F, 60.0F) &&
        grow::ReadingGuard::valid({humidity, true, true}, 0.0F, 100.0F) &&
        grow::ReadingGuard::valid({leaf, true, true}, -40.0F, 85.0F);
    const bool level_ok = digitalRead(pins::kHumidifierLevel) == HIGH;
    const bool exhaust_on = !climate_valid || temperature >= 28.0F || humidity >= 85.0F;
    const bool humidifier_on = climate_valid && level_ok && !exhaust_on && humidity <= 55.0F;
    controller.command(0, exhaust_on, now, 15UL * 60UL * 1000UL);
    controller.command(1, humidifier_on, now, 15UL * 60UL * 1000UL, level_ok);
    const uint16_t co2_raw = analogRead(pins::kCo2Analog);
    Serial.printf(
        "heartbeat=climate temp=%.2f ur=%.2f leaf=%.2f co2_raw=%u co2_control=disabled\n",
        temperature, humidity, leaf, co2_raw);
  }

  outputs.apply(controller);
  delay(10);
}
