# self_healing.py
import time
from shared_memory import SharedMemoryBus

class SelfHealingSystem:
    """Monitors and repairs system issues autonomously."""
    def __init__(self, bus):
        self.bus = bus

    def monitor(self):
        """Continuously monitor system health."""
        while True:
            sensor_data = self.bus.read_sensor_data()
            motor_command = self.bus.read_motor_command()

            # Detect potential issues (e.g., stuck motors or bad sensor readings)
            if motor_command == 1 and sensor_data[0] < 0.2:
                print("⚠️ Issue detected: Motor moving but no progress.")
                self.bus.write_motor_command(0)  # Stop the motor as a safeguard

            time.sleep(2)  # Monitor at regular intervals

if __name__ == "__main__":
    bus = SharedMemoryBus()
    healing_system = SelfHealingSystem(bus)
    healing_system.monitor()
