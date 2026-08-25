#pragma once

class Preferences {
 public:
  bool begin(const char*, bool) { return true; }
  bool isKey(const char*) const { return true; }
  float getFloat(const char*) const { return 1.0F; }
  void end() {}
};
