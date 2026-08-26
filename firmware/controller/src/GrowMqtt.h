#pragma once

#include <cstdint>

#ifdef ARDUINO_ARCH_ESP32

#include <Arduino.h>
#include <GrowConnectivity.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

namespace grow::mqtt {

constexpr char kClientId[] = "grow-01-controller";
constexpr char kAvailabilityTopic[] =
    "grow/v1/grow-01/controller/state/availability";
constexpr char kHeartbeatTopic[] = "grow/v1/grow-01/controller/state/heartbeat";

class Connection {
 public:
  Connection()
      : mqtt_(tls_), wifi_retry_(10000), mqtt_retry_(5000),
        heartbeat_(15000) {}

  void begin() {
    if (!configured()) {
      Serial.println("mqtt=config_incomplete state=safe_offline");
      return;
    }
    tls_.setCACert(GROW_MQTT_CA);
    tls_.setCertificate(GROW_MQTT_CLIENT_CERT);
    tls_.setPrivateKey(GROW_MQTT_CLIENT_KEY);
    mqtt_.setServer(GROW_MQTT_HOST, GROW_MQTT_PORT);
    mqtt_.setKeepAlive(30);
    mqtt_.setSocketTimeout(5);
    mqtt_.setBufferSize(384);
    WiFi.mode(WIFI_STA);
    connectWifi();
  }

  void loop(uint32_t now_ms) {
    if (!configured()) return;

    if (WiFi.status() != WL_CONNECTED) {
      if (wifi_retry_.due(now_ms)) connectWifi();
      return;
    }

    if (!clock_started_) {
      configTime(0, 0, "pool.ntp.org", "time.nist.gov");
      clock_started_ = true;
      Serial.println("mqtt=waiting_for_clock");
    }
    if (!clockValid()) return;

    if (!mqtt_.connected()) {
      if (mqtt_retry_.due(now_ms)) connectMqtt();
      return;
    }

    mqtt_.loop();
    if (heartbeat_.due(now_ms, mqtt_.connected())) publishHeartbeat(now_ms);
  }

  bool connected() { return mqtt_.connected(); }

 private:
  static bool present(const char* value) {
    return value != nullptr && value[0] != '\0';
  }

  static bool configured() {
    return present(GROW_WIFI_SSID) && present(GROW_WIFI_PASSWORD) &&
           present(GROW_MQTT_HOST) && GROW_MQTT_PORT == 8883 &&
           present(GROW_MQTT_CA) && present(GROW_MQTT_CLIENT_CERT) &&
           present(GROW_MQTT_CLIENT_KEY);
  }

  static bool clockValid() {
    constexpr time_t kMinimumTrustedEpoch = 1700000000;
    return time(nullptr) >= kMinimumTrustedEpoch;
  }

  void connectWifi() {
    Serial.println("wifi=connecting");
    WiFi.begin(GROW_WIFI_SSID, GROW_WIFI_PASSWORD);
  }

  void connectMqtt() {
    const bool accepted = mqtt_.connect(
        kClientId, nullptr, nullptr, kAvailabilityTopic, 1, true, "offline",
        true);
    if (!accepted) {
      Serial.printf("mqtt=connect_failed code=%d\n", mqtt_.state());
      return;
    }
    mqtt_retry_.reset();
    mqtt_.publish(kAvailabilityTopic, "online", true);
    Serial.println("mqtt=connected tls=verified identity=grow-01-controller");
  }

  void publishHeartbeat(uint32_t now_ms) {
    char payload[112];
    const int written = snprintf(
        payload, sizeof(payload),
        "{\"schema_version\":1,\"sequence\":%lu,\"uptime_ms\":%lu}",
        static_cast<unsigned long>(heartbeat_.sequence()),
        static_cast<unsigned long>(now_ms));
    if (written > 0 && static_cast<size_t>(written) < sizeof(payload)) {
      mqtt_.publish(kHeartbeatTopic, payload, false);
    }
  }

  WiFiClientSecure tls_;
  PubSubClient mqtt_;
  grow::RetryThrottle wifi_retry_;
  grow::RetryThrottle mqtt_retry_;
  grow::HeartbeatSchedule heartbeat_;
  bool clock_started_{false};
};

}  // namespace grow::mqtt

#else

namespace grow::mqtt {

class Connection {
 public:
  void begin() {}
  void loop(uint32_t) {}
  bool connected() const { return false; }
};

}  // namespace grow::mqtt

#endif
