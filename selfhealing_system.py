import time
import random

class SelfHealingSystem:
    """Monitors and fixes system issues autonomously."""
    
    def __init__(self):
        self.health_status = "Healthy"
        self.performance_metrics = {"CPU": 30, "Memory": 40}

    def monitor_system(self):
        """Monitor for issues in real time."""
        while True:
            if random.random() > 0.85:  # Simulate random errors
                self.health_status = "Fault Detected"
                print("⚠️ Fault detected! Initiating debugging.")
                self.debug_and_fix()

            self.optimize_performance()
            time.sleep(2)

    def debug_and_fix(self):
        """Fix issues autonomously."""
        print("🔧 Running diagnostics...")
        time.sleep(1)
        # Simulate debugging process
        self.health_status = "Healthy"
        print("✅ Issue resolved.")

    def optimize_performance(self):
        """Optimize performance in real time."""
        print("🚀 Optimizing performance metrics...")
        # Simulate optimization process
        self.performance_metrics["CPU"] = max(10, self.performance_metrics["CPU"] - 5)
        print(f"Current CPU usage: {self.performance_metrics['CPU']}%")

if __name__ == "__main__":
    healing_system = SelfHealingSystem()
    healing_system.monitor_system()
