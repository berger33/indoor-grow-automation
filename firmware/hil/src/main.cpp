#include <GrowCore.h>
#include <GrowProcess.h>

#include <cstdlib>
#include <iostream>

using grow::NodeState;
using grow::ReadingGuard;
using grow::SafeController;
using grow::SensorSample;
using grow::TripReason;

static void require(bool condition, const char* message) {
  if (!condition) {
    std::cerr << "HIL failure: " << message << '\n';
    std::exit(1);
  }
}

int main() {
  SafeController<4> node(5000);
  node.boot(0);
  require(node.state() == NodeState::Boot, "reinício deve voltar para BOOT");
  require(!node.output(0), "saída deve iniciar desligada");
  require(node.completeBoot(true), "boot seguro deve completar");

  require(node.command(0, true, 100, 1000), "comando seguro deve iniciar");
  node.feedWatchdog(900);
  node.tick(1100, false, true, false);
  require(node.state() == NodeState::Alarm, "timeout deve reter alarme");
  require(node.reason() == TripReason::ActuatorTimeout, "motivo do timeout deve persistir");
  require(!node.output(0), "timeout deve cortar saída");
  require(node.resetAlarm(true, true, true), "rearme físico seguro deve voltar ao BOOT");
  require(!node.command(0, true, 1200, 1000), "BOOT nunca deve energizar saída");

  require(node.completeBoot(true), "segundo boot deve completar");
  node.feedWatchdog(1200);
  require(node.command(1, true, 1200, 1000), "bomba deve iniciar");
  node.tick(1300, true, true, false);
  require(node.reason() == TripReason::Leak, "vazamento deve prevalecer");
  require(!node.resetAlarm(false, true, true), "sensor molhado deve bloquear rearme");

  SafeController<4> restarted;
  restarted.boot(0);
  require(restarted.state() == NodeState::Boot && !restarted.output(1),
          "reinício não deve restaurar último comando");
  require(restarted.completeBoot(true), "boot após reinício deve ser explícito");
  restarted.feedWatchdog(1);
  require(restarted.command(2, true, 1, 1000), "atuador deve iniciar");
  restarted.tick(2, false, false, false);
  require(restarted.reason() == TripReason::HubLost, "perda de rede ativa deve cortar saída");

  const SensorSample failed_sensor{25.0F, false, true};
  require(!ReadingGuard::valid(failed_sensor, 0.0F, 50.0F), "falha de transporte deve invalidar leitura");
  SafeController<1> guarded;
  guarded.boot(0);
  require(guarded.completeBoot(true), "guarded boot");
  require(!guarded.command(0, true, 1, 1000, false), "sensor crítico inválido deve inibir comando");
  require(guarded.reason() == TripReason::SensorInvalid, "falha de sensor deve ficar retida");

  SafeController<12> diy;
  diy.boot(0);
  require(diy.completeBoot(true), "controlador DIY deve completar boot seguro");
  require(diy.commandOneOf(0, 0, 6, true, 1, 1000),
          "primeira dosadora deve iniciar");
  require(!diy.commandOneOf(1, 0, 6, true, 2, 1000),
          "segunda dosadora deve ser bloqueada enquanto outra estiver ativa");
  require(!diy.commandExclusive(5, 0, true, 2, 1000),
          "pH+ deve ser bloqueado enquanto pH- estiver ativo");
  require(diy.command(0, false, 3, 1000), "pH- deve desligar");
  require(diy.commandExclusive(5, 0, true, 4, 1000),
          "pH+ deve iniciar depois que pH- desligar");
  diy.tick(5, true, true, false);
  require(diy.reason() == TripReason::Leak && !diy.output(5),
          "vazamento deve cortar a dosadora no controlador DIY");

  const grow::PumpCalibration fill_cal{100.0F, 0.0F, true};
  const grow::PumpCalibration dose_cal{1.0F, 0.0F, true};
  const std::array<grow::PumpCalibration, 6> dose_calibrations{
      dose_cal, dose_cal, dose_cal, dose_cal, dose_cal, dose_cal};
  grow::BatchController batch;
  require(batch.start(0, 10.0F, {1, 1, 1, 1, 1, 1}, fill_cal,
                      dose_calibrations, dose_cal, dose_cal),
          "batelada calibrada deve iniciar");
  grow::BatchInputs process{0.0F, 6.0F, 1.8F, true, true, true, false, false};
  require(batch.tick(1, process) == grow::FillWater, "batelada deve encher primeiro");
  process.mix_liters = 10.0F;
  require(batch.tick(100, process) == grow::Mixer, "massa alvo deve iniciar dosagem");
  require(batch.tick(101, process) == grow::Nutrient0, "primeiro nutriente deve seguir a ordem");
  process.leak_detected = true;
  require(batch.tick(102, process) == 0 && batch.stage() == grow::BatchStage::Alarm,
          "vazamento deve abortar batelada e zerar saídas");

  std::cout << "HIL virtual: 7 cenários fail-safe aprovados\n";
  return 0;
}
