# ai_brain.py
import time
import random
from shared_memory import SharedMemoryBus

class AIBrain:
    """AI decision-making module."""
    def __init__(self, bus):
        self.bus = bus

    def run(self):
        """Continuously make decisions based on sensor data."""
        while True:
            sensor_data = self.bus.read_sensor_data()
            print(f"AI Brain: Sensor data: {sensor_data}")

            # Simple decision logic (can be replaced with advanced AI models)
            if sensor_data[0] > 0.5:
                self.bus.write_motor_command(1)  # Move forward
            elif sensor_data[1] > 0.5:
                self.bus.write_motor_command(2)  # Reverse
            else:
                self.bus.write_motor_command(0)  # Stop

            time.sleep(1)  # Simulate decision-making interval

if __name__ == "__main__":
    bus = SharedMemoryBus()
    ai_brain = AIBrain(bus)
    ai_brain.run()
