#include <Arduino.h>
#include <GrowCore.h>

namespace pins {
constexpr uint8_t kLeakRack = 34;
constexpr uint8_t kLeakFloor = 35;
constexpr uint8_t kEmergencyStop = 32;
constexpr uint8_t kGlobalEnable = 25;
}  // namespace pins

grow::SafeController<1> controller(3000);
uint8_t wet_confirmations = 0;
uint32_t last_heartbeat_ms = 0;

void setup() {
  digitalWrite(pins::kGlobalEnable, LOW);
  pinMode(pins::kGlobalEnable, OUTPUT);
  pinMode(pins::kLeakRack, INPUT_PULLDOWN);
  pinMode(pins::kLeakFloor, INPUT_PULLDOWN);
  pinMode(pins::kEmergencyStop, INPUT_PULLUP);
  controller.boot(millis());
  Serial.begin(115200);
  const bool dry = digitalRead(pins::kLeakRack) == LOW && digitalRead(pins::kLeakFloor) == LOW;
  controller.completeBoot(dry && digitalRead(pins::kEmergencyStop) == HIGH);
}

void loop() {
  const uint32_t now = millis();
  const bool wet_sample =
      digitalRead(pins::kLeakRack) == HIGH || digitalRead(pins::kLeakFloor) == HIGH;
  wet_confirmations = wet_sample ? static_cast<uint8_t>(min(3, wet_confirmations + 1)) : 0;
  const bool leak_confirmed = wet_confirmations >= 3;
  const bool emergency_stop = digitalRead(pins::kEmergencyStop) == LOW;
  controller.feedWatchdog(now);
  controller.tick(now, leak_confirmed, true, emergency_stop);
  digitalWrite(pins::kGlobalEnable,
               controller.state() == grow::NodeState::Idle ? HIGH : LOW);
  if (now - last_heartbeat_ms >= 1000) {
    last_heartbeat_ms = now;
    Serial.printf("heartbeat=safety state=%u leak=%u estop=%u\n",
                  static_cast<unsigned>(controller.state()), leak_confirmed, emergency_stop);
  }
  delay(10);
}
