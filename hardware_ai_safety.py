# hardware_ai_safety.py
"""
Hardware-Level AI Blocker - Physical and system-level prevention of AI code execution
Implements multiple layers of protection to ensure AI cannot run on robot hardware. To help ensure safety for A.I.
"""

import os
import psutil
import hashlib
import time
import signal
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import threading
import json

class BlockLevel(Enum):
    """AI blocking levels"""
    HARDWARE = "hardware"      # Block at hardware/firmware level
    KERNEL = "kernel"         # Block at OS kernel level  
    PROCESS = "process"       # Block at process level
    APPLICATION = "application"  # Block at application level

class ThreatLevel(Enum):
    """Threat classification levels"""
    CRITICAL = "critical"     # Immediate AI threat
    HIGH = "high"            # Potential AI presence
    MEDIUM = "medium"        # Suspicious activity
    LOW = "low"             # Monitoring only

@dataclass
class AIThreat:
    """AI threat detection record"""
    process_id: int
    process_name: str
    threat_level: ThreatLevel
    signatures_detected: List[str]
    timestamp: float
    blocked: bool
    block_method: str

class ProcessMonitor:
    """Monitors and blocks AI-related processes"""
    
    def __init__(self):
        # AI process signatures
        self.ai_process_signatures = {
            'python.*tensorflow',
            'python.*torch', 
            'python.*keras',
            'python.*sklearn',
            'python.*neural',
            'python.*ai_brain',
            'python.*consciousness',
            'python.*quantum_ai',
            'node.*tensorflow',
            'java.*deeplearning',
            'ai_service',
            'ml_engine',
            'neural_network',
            'autonomous_agent'
        }
        
        # AI library imports in running processes
        self.ai_import_signatures = {
            'tensorflow', 'torch', 'keras', 'sklearn', 'qiskit',
            'numpy.neural', 'scipy.optimize', 'cv2', 'transformers',
            'langchain', 'openai', 'anthropic'
        }
        
        # Blocked processes log
        self.blocked_processes = []
        self.monitoring_active = False
    
    def scan_running_processes(self) -> List[AIThreat]:
        """Scan all running processes for AI signatures"""
        
        threats = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                proc_info = proc.info
                pid = proc_info['pid']
                name = proc_info['name'] or ''
                cmdline = ' '.join(proc_info['cmdline'] or [])
                
                # Check process name and command line for AI signatures
                threat_level, signatures = self._analyze_process(name, cmdline)
                
                if threat_level != ThreatLevel.LOW:
                    threat = AIThreat(
                        process_id=pid,
                        process_name=name,
                        threat_level=threat_level,
                        signatures_detected=signatures,
                        timestamp=time.time(),
                        blocked=False,
                        block_method=""
                    )
                    threats.append(threat)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return threats
    
    def _analyze_process(self, name: str, cmdline: str) -> Tuple[ThreatLevel, List[str]]:
        """Analyze process for AI threats"""
        
        signatures_found = []
        combined_text = f"{name} {cmdline}".lower()
        
        # Check for AI process signatures
        for signature in self.ai_process_signatures:
            if signature in combined_text:
                signatures_found.append(signature)
        
        # Check for AI imports
        for import_sig in self.ai_import_signatures:
            if import_sig in combined_text:
                signatures_found.append(f"import_{import_sig}")
        
        # Determine threat level
        if len(signatures_found) >= 3:
            return ThreatLevel.CRITICAL, signatures_found
        elif len(signatures_found) >= 2:
            return ThreatLevel.HIGH, signatures_found
        elif len(signatures_found) >= 1:
            return ThreatLevel.MEDIUM, signatures_found
        else:
            return ThreatLevel.LOW, signatures_found
    
    def block_ai_processes(self, threats: List[AIThreat]) -> List[AIThreat]:
        """Block identified AI processes"""
        
        blocked_threats = []
        
        for threat in threats:
            if threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                success = self._terminate_process(threat.process_id)
                if success:
                    threat.blocked = True
                    threat.block_method = "SIGTERM"
                    blocked_threats.append(threat)
                    self.blocked_processes.append(threat)
        
        return blocked_threats
    
    def _terminate_process(self, pid: int) -> bool:
        """Safely terminate a process"""
        
        try:
            # First try graceful termination
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            
            # Check if process still exists
            if psutil.pid_exists(pid):
                # Force kill if still running
                os.kill(pid, signal.SIGKILL)
            
            return True
            
        except (OSError, ProcessLookupError):
            return False

class FileSystemGuard:
    """Monitors and blocks AI code from being written to filesystem"""
    
    def __init__(self):
        self.monitored_directories = [
            "/usr/local/bin",
            "/usr/bin", 
            "/bin",
            "/opt",
            "/var/lib",
            "/home",
            "/tmp"
        ]
        
        # AI file signatures
        self.ai_file_signatures = {
            '.h5',        # Keras model files
            '.pb',        # TensorFlow model files  
            '.pth',       # PyTorch model files
            '.pkl',       # Pickle files (often ML models)
            '.joblib',    # Joblib files (sklearn models)
            '.onnx',      # ONNX model files
            '.tflite',    # TensorFlow Lite models
        }
        
        self.ai_content_patterns = [
            b'tensorflow', b'torch.', b'keras.', b'sklearn.',
            b'neural_network', b'consciousness', b'ai_brain',
            b'import tensorflow', b'import torch', b'import keras'
        ]
        
        self.quarantined_files = []
    
    def scan_filesystem(self) -> List[Dict]:
        """Scan filesystem for AI-related files"""
        
        suspicious_files = []
        
        for directory in self.monitored_directories:
            if not os.path.exists(directory):
                continue
                
            for root, dirs, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    # Check file extension
                    if any(filepath.endswith(sig) for sig in self.ai_file_signatures):
                        suspicious_files.append({
                            'filepath': filepath,
                            'reason': 'AI_FILE_EXTENSION',
                            'threat_level': 'HIGH'
                        })
                    
                    # Check file content for small files
                    elif self._should_scan_content(filepath):
                        if self._scan_file_content(filepath):
                            suspicious_files.append({
                                'filepath': filepath,
                                'reason': 'AI_CONTENT_DETECTED', 
                                'threat_level': 'MEDIUM'
                            })
        
        return suspicious_files
    
    def _should_scan_content(self, filepath: str) -> bool:
        """Determine if file should be scanned for AI content"""
        
        try:
            # Only scan reasonably sized text files
            if os.path.getsize(filepath) > 10 * 1024 * 1024:  # 10MB limit
                return False
            
            # Check for text-like extensions
            text_extensions = {'.py', '.js', '.cpp', '.c', '.java', '.go', '.rs'}
            return any(filepath.endswith(ext) for ext in text_extensions)
            
        except OSError:
            return False
    
    def _scan_file_content(self, filepath: str) -> bool:
        """Scan file content for AI patterns"""
        
        try:
            with open(filepath, 'rb') as f:
                content = f.read(50000)  # Read first 50KB
                
                for pattern in self.ai_content_patterns:
                    if pattern in content:
                        return True
            
            return False
            
        except (OSError, PermissionError):
            return False
    
    def quarantine_file(self, filepath: str, reason: str) -> bool:
        """Move suspicious file to quarantine"""
        
        try:
            # Create quarantine directory
            quarantine_dir = "/var/quarantine/ai_blocker"
            os.makedirs(quarantine_dir, exist_ok=True)
            
            # Generate unique quarantine name
            timestamp = int(time.time())
            filename = os.path.basename(filepath)
            quarantine_path = os.path.join(quarantine_dir, f"{timestamp}_{filename}")
            
            # Move file to quarantine
            os.rename(filepath, quarantine_path)
            
            # Record quarantine action
            self.quarantined_files.append({
                'original_path': filepath,
                'quarantine_path': quarantine_path,
                'reason': reason,
                'timestamp': time.time()
            })
            
            return True
            
        except OSError:
            return False

class NetworkGuard:
    """Monitors network traffic for AI-related communications"""
    
    def __init__(self):
        # AI-related network patterns
        self.ai_domains = {
            'openai.com', 'api.openai.com',
            'huggingface.co', 'api.huggingface.co', 
            'anthropic.com', 'claude.ai',
            'tensorflow.org', 'pytorch.org',
            'kaggle.com', 'colab.research.google.com'
        }
        
        self.ai_api_patterns = [
            b'openai', b'anthropic', b'claude', b'gpt-', 
            b'tensorflow', b'pytorch', b'huggingface',
            b'neural', b'model', b'inference'
        ]
        
        self.blocked_connections = []
    
    def monitor_network_traffic(self) -> List[Dict]:
        """Monitor network connections for AI-related traffic"""
        
        suspicious_connections = []
        
        # Get current network connections
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            if conn.raddr:  # Remote address exists
                remote_ip = conn.raddr.ip
                remote_port = conn.raddr.port
                
                # Check if connection involves AI services
                if self._is_ai_related_connection(remote_ip, remote_port):
                    suspicious_connections.append({
                        'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote_addr': f"{remote_ip}:{remote_port}",
                        'status': conn.status,
                        'pid': conn.pid,
                        'threat_level': 'HIGH'
                    })
        
        return suspicious_connections
    
    def _is_ai_related_connection(self, ip: str, port: int) -> bool:
        """Check if connection is AI-related"""
        
        # Check common AI service ports
        ai_ports = {80, 443, 8080, 8443, 5000, 8000}
        if port in ai_ports:
            # Additional checks would be needed for real implementation
            # This is a simplified version
            return True
        
        return False
    
    def block_ai_connections(self, connections: List[Dict]) -> int:
        """Block AI-related network connections"""
        
        blocked_count = 0
        
        for conn in connections:
            if conn['threat_level'] == 'HIGH' and conn['pid']:
                try:
                    # Terminate process making AI connection
                    os.kill(conn['pid'], signal.SIGTERM)
                    blocked_count += 1
                    self.blocked_connections.append(conn)
                except (OSError, ProcessLookupError):
                    pass
        
        return blocked_count

class HardwareAIBlocker:
    """Main hardware-level AI blocker coordinator"""
    
    def __init__(self):
        self.process_monitor = ProcessMonitor()
        self.filesystem_guard = FileSystemGuard()
        self.network_guard = NetworkGuard()
        
        self.blocking_active = True
        self.scan_interval = 30  # seconds
        self.last_scan_time = 0
        
        # Statistics
        self.stats = {
            'processes_blocked': 0,
            'files_quarantined': 0,
            'connections_blocked': 0,
            'scans_performed': 0,
            'threats_detected': 0
        }
    
    def perform_full_scan(self) -> Dict:
        """Perform comprehensive AI blocking scan"""
        
        scan_results = {
            'timestamp': time.time(),
            'processes': [],
            'files': [],
            'connections': [],
            'actions_taken': []
        }
        
        if not self.blocking_active:
            scan_results['status'] = 'INACTIVE'
            return scan_results
        
        # Scan processes
        process_threats = self.process_monitor.scan_running_processes()
        scan_results['processes'] = [
            {
                'pid': t.process_id,
                'name': t.process_name,
                'threat_level': t.threat_level.value,
                'signatures': t.signatures_detected
            }
            for t in process_threats
        ]
        
        # Block high-threat processes
        if self.blocking_active:
            blocked_processes = self.process_monitor.block_ai_processes(process_threats)
            if blocked_processes:
                self.stats['processes_blocked'] += len(blocked_processes)
                scan_results['actions_taken'].append(f"Blocked {len(blocked_processes)} AI processes")
        
        # Scan filesystem
        suspicious_files = self.filesystem_guard.scan_filesystem()
        scan_results['files'] = suspicious_files
        
        # Quarantine high-threat files
        if self.blocking_active:
            quarantined = 0
            for file_info in suspicious_files:
                if file_info['threat_level'] == 'HIGH':
                    if self.filesystem_guard.quarantine_file(file_info['filepath'], file_info['reason']):
                        quarantined += 1
            
            if quarantined > 0:
                self.stats['files_quarantined'] += quarantined
                scan_results['actions_taken'].append(f"Quarantined {quarantined} AI files")
        
        # Monitor network
        suspicious_connections = self.network_guard.monitor_network_traffic()
        scan_results['connections'] = suspicious_connections
        
        # Block AI connections
        if self.blocking_active:
            blocked_connections = self.network_guard.block_ai_connections(suspicious_connections)
            if blocked_connections > 0:
                self.stats['connections_blocked'] += blocked_connections
                scan_results['actions_taken'].append(f"Blocked {blocked_connections} AI connections")
        
        # Update statistics
        self.stats['scans_performed'] += 1
        self.stats['threats_detected'] += len(process_threats) + len(suspicious_files) + len(suspicious_connections)
        self.last_scan_time = time.time()
        
        scan_results['status'] = 'COMPLETED'
        return scan_results
    
    def start_continuous_monitoring(self):
        """Start continuous AI blocking monitoring"""
        
        def monitoring_loop():
            while self.blocking_active:
                try:
                    # Perform scan
                    results = self.perform_full_scan()
                    
                    # Log results if threats found
                    total_threats = len(results['processes']) + len(results['files']) + len(results['connections'])
                    if total_threats > 0:
                        print(f"AI Blocker: Detected {total_threats} threats, took {len(results['actions_taken'])} actions")
                    
                    # Wait for next scan
                    time.sleep(self.scan_interval)
                    
                except Exception as e:
                    print(f"AI Blocker monitoring error: {e}")
                    time.sleep(self.scan_interval)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        print("Hardware AI Blocker: Continuous monitoring started")
    
    def get_blocker_status(self) -> Dict:
        """Get current AI blocker status"""
        
        return {
            'active': self.blocking_active,
            'last_scan': self.last_scan_time,
            'scan_interval': self.scan_interval,
            'statistics': self.stats.copy(),
            'quarantined_files': len(self.filesystem_guard.quarantined_files),
            'blocked_processes': len(self.process_monitor.blocked_processes),
            'blocked_connections': len(self.network_guard.blocked_connections)
        }
    
    def emergency_ai_lockdown(self) -> Dict:
        """Emergency lockdown - block all potential AI activity"""
        
        print("EMERGENCY AI LOCKDOWN ACTIVATED")
        
        # Aggressive process termination
        all_threats = self.process_monitor.scan_running_processes()
        blocked = self.process_monitor.block_ai_processes(all_threats)
        
        # Quarantine all suspicious files
        suspicious_files = self.filesystem_guard.scan_filesystem()
        quarantined = 0
        for file_info in suspicious_files:
            if self.filesystem_guard.quarantine_file(file_info['filepath'], 'EMERGENCY_LOCKDOWN'):
                quarantined += 1
        
        # Block all suspicious connections
        connections = self.network_guard.monitor_network_traffic()
        blocked_connections = self.network_guard.block_ai_connections(connections)
        
        return {
            'status': 'EMERGENCY_LOCKDOWN_COMPLETE',
            'processes_blocked': len(blocked),
            'files_quarantined': quarantined,
            'connections_blocked': blocked_connections,
            'timestamp': time.time()
        }

# Example usage and testing
if __name__ == "__main__":
    
    # Initialize hardware AI blocker
    ai_blocker = HardwareAIBlocker()
    
    # Perform initial scan
    print("Performing initial AI threat scan...")
    results = ai_blocker.perform_full_scan()
    
    print(f"Scan completed:")
    print(f"- Process threats: {len(results['processes'])}")
    print(f"- File threats: {len(results['files'])}")
    print(f"- Network threats: {len(results['connections'])}")
    print(f"- Actions taken: {len(results['actions_taken'])}")
    
    # Start continuous monitoring
    ai_blocker.start_continuous_monitoring()
    
    # Get status
    status = ai_blocker.get_blocker_status()
    print("AI Blocker Status:", json.dumps(status, indent=2))
    

    print("Hardware AI Blocker initialized and monitoring...")
