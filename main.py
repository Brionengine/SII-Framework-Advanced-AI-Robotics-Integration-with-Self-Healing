# main.py
from multiprocessing import Process
from ai_brain import AIBrain
from motor_control import MotorControl
from self_healing import SelfHealingSystem
from shared_memory import SharedMemoryBus

def main():
    bus = SharedMemoryBus()

    # Initialize subsystems
    ai_brain = AIBrain(bus)
    motor_control = MotorControl(bus)
    healing_system = SelfHealingSystem(bus)

    # Run subsystems in parallel
    ai_process = Process(target=ai_brain.run)
    motor_process = Process(target=motor_control.run)
    healing_process = Process(target=healing_system.monitor)

    ai_process.start()
    motor_process.start()
    healing_process.start()

    ai_process.join()
    motor_process.join()
    healing_process.join()

if __name__ == "__main__":
    main()
