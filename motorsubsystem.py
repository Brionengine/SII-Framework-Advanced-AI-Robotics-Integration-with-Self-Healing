# motor_control.py
import time
from shared_memory import SharedMemoryBus

class MotorControl:
    """Control motors based on commands from the shared memory bus."""
    def __init__(self, bus):
        self.bus = bus

    def run(self):
        """Continuously read motor commands and act."""
        while True:
            command = self.bus.read_motor_command()
            if command == 1:
                print("Motor: Moving Forward")
            elif command == 2:
                print("Motor: Reversing")
            else:
                print("Motor: Stopped")
            time.sleep(0.5)  # Simulate hardware loop delay

if __name__ == "__main__":
    bus = SharedMemoryBus()
    motor_control = MotorControl(bus)
    motor_control.run()
