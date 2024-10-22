# shared_memory.py
import multiprocessing

class SharedMemoryBus:
    """Shared memory communication layer for AI and subsystems."""
    def __init__(self):
        self.motor_command = multiprocessing.Value('i', 0)  # 0 = stop, 1 = forward, 2 = reverse
        self.sensor_data = multiprocessing.Array('d', [0.0] * 3)  # Placeholder for 3 sensor values

    def read_motor_command(self):
        """Read the current motor command."""
        return self.motor_command.value

    def write_motor_command(self, command):
        """Write a new motor command."""
        self.motor_command.value = command

    def update_sensor_data(self, data):
        """Update sensor data."""
        for i in range(len(data)):
            self.sensor_data[i] = data[i]

    def read_sensor_data(self):
        """Read the current sensor data."""
        return list(self.sensor_data)
