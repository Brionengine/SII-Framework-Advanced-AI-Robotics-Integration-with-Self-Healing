# secure_communication_protocol.py
"""
Secure Communication Protocol - Enforces remote-only control with AI blocking
Implements encrypted communication channels that explicitly prevent AI code transfer
"""

import socket
import ssl
import json
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import struct

class MessageType(Enum):
    """Secure message types"""
    COMMAND = "command"
    STATUS = "status" 
    HEARTBEAT = "heartbeat"
    EMERGENCY_STOP = "emergency_stop"
    AUTH_CHALLENGE = "auth_challenge"
    AUTH_RESPONSE = "auth_response"

class SecurityLevel(Enum):
    """Communication security levels"""
    MAXIMUM = "maximum"  # Full encryption + AI blocking
    HIGH = "high"       # Encryption + basic AI filtering  
    STANDARD = "standard"  # Basic encryption only

@dataclass
class SecureMessage:
    """Secure message structure"""
    msg_type: MessageType
    payload: Dict[str, Any]
    timestamp: float
    sender_id: str
    sequence_num: int
    checksum: str

class AIContentFilter:
    """Filters AI-related content from communications"""
    
    def __init__(self):
        # Prohibited AI-related keywords and patterns
        self.ai_keywords = {
            'neural_network', 'machine_learning', 'tensorflow', 'pytorch',
            'keras', 'sklearn', 'ai_model', 'deep_learning', 'consciousness',
            'quantum_ai', 'self_learning', 'autonomous_ai', 'ai_brain',
            'neural_net', 'backprop', 'gradient_descent', 'model_training',
            'inference_engine', 'knowledge_base', 'expert_system'
        }
        
        # Prohibited code patterns
        self.code_patterns = [
            'import tensorflow',
            'import torch', 
            'import keras',
            'from sklearn',
            'import qiskit',
            'class.*AI.*:',
            'def.*learn.*(',
            'def.*train.*(',
            'neural.*network',
            'consciousness.*core'
        ]
    
    def scan_content(self, content: str) -> Tuple[bool, List[str]]:
        """Scan content for AI-related material"""
        
        violations = []
        content_lower = content.lower()
        
        # Check for AI keywords
        for keyword in self.ai_keywords:
            if keyword in content_lower:
                violations.append(f"AI keyword detected: {keyword}")
        
        # Check for code patterns (simplified regex-like matching)
        for pattern in self.code_patterns:
            if pattern.lower() in content_lower:
                violations.append(f"AI code pattern detected: {pattern}")
        
        has_ai_content = len(violations) > 0
        return has_ai_content, violations
    
    def sanitize_message(self, message: str) -> str:
        """Remove or replace AI-related content"""
        
        sanitized = message
        
        # Replace AI keywords with safe alternatives
        for keyword in self.ai_keywords:
            if keyword in sanitized.lower():
                sanitized = sanitized.replace(keyword, "[BLOCKED_AI_CONTENT]")
        
        return sanitized

class SecureProtocolHandler:
    """Handles secure protocol communications with AI blocking"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MAXIMUM):
        self.security_level = security_level
        self.content_filter = AIContentFilter()
        
        # Security configuration
        self.shared_secret = b"secure_robot_control_key_2024"
        self.sequence_counter = 0
        self.message_log = []
        
        # Connection tracking
        self.authorized_clients = {}
        self.blocked_ips = set()
        
    def create_secure_message(self, msg_type: MessageType, payload: Dict, sender_id: str) -> SecureMessage:
        """Create a secure message with integrity checking"""
        
        # Filter AI content from payload
        if self.security_level == SecurityLevel.MAXIMUM:
            filtered_payload = self._filter_ai_content(payload)
        else:
            filtered_payload = payload
        
        # Create message
        timestamp = time.time()
        self.sequence_counter += 1
        
        # Generate checksum
        message_data = f"{msg_type.value}:{json.dumps(filtered_payload)}:{timestamp}:{sender_id}:{self.sequence_counter}"
        checksum = hmac.new(
            self.shared_secret,
            message_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        message = SecureMessage(
            msg_type=msg_type,
            payload=filtered_payload,
            timestamp=timestamp,
            sender_id=sender_id,
            sequence_num=self.sequence_counter,
            checksum=checksum
        )
        
        # Log message
        self.message_log.append({
            'timestamp': timestamp,
            'type': msg_type.value,
            'sender': sender_id,
            'sequence': self.sequence_counter
        })
        
        return message
    
    def _filter_ai_content(self, payload: Dict) -> Dict:
        """Filter AI content from message payload"""
        
        filtered_payload = {}
        
        for key, value in payload.items():
            if isinstance(value, str):
                # Scan string content
                has_ai, violations = self.content_filter.scan_content(value)
                if has_ai:
                    # Block or sanitize based on security level
                    if self.security_level == SecurityLevel.MAXIMUM:
                        filtered_payload[key] = "[BLOCKED: AI CONTENT DETECTED]"
                    else:
                        filtered_payload[key] = self.content_filter.sanitize_message(value)
                else:
                    filtered_payload[key] = value
            elif isinstance(value, dict):
                # Recursively filter nested dictionaries
                filtered_payload[key] = self._filter_ai_content(value)
            else:
                # Pass through non-string values
                filtered_payload[key] = value
        
        return filtered_payload
    
    def validate_message(self, message: SecureMessage) -> Tuple[bool, str]:
        """Validate incoming secure message"""
        
        # Check timestamp (prevent replay attacks)
        current_time = time.time()
        if abs(current_time - message.timestamp) > 300:  # 5 minute window
            return False, "Message timestamp outside acceptable window"
        
        # Verify checksum
        message_data = f"{message.msg_type.value}:{json.dumps(message.payload)}:{message.timestamp}:{message.sender_id}:{message.sequence_num}"
        expected_checksum = hmac.new(
            self.shared_secret,
            message_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if message.checksum != expected_checksum:
            return False, "Invalid message checksum"
        
        # Check for AI content (additional validation)
        if self.security_level == SecurityLevel.MAXIMUM:
            payload_str = json.dumps(message.payload)
            has_ai, violations = self.content_filter.scan_content(payload_str)
            if has_ai:
                return False, f"AI content detected: {violations}"
        
        return True, "Message validated"
    
    def serialize_message(self, message: SecureMessage) -> bytes:
        """Serialize message for transmission"""
        
        message_dict = {
            'type': message.msg_type.value,
            'payload': message.payload,
            'timestamp': message.timestamp,
            'sender_id': message.sender_id,
            'sequence_num': message.sequence_num,
            'checksum': message.checksum
        }
        
        # Convert to JSON and encode
        json_data = json.dumps(message_dict).encode('utf-8')
        
        # Add length prefix
        length = len(json_data)
        return struct.pack('!I', length) + json_data
    
    def deserialize_message(self, data: bytes) -> Optional[SecureMessage]:
        """Deserialize message from received data"""
        
        try:
            # Extract length
            if len(data) < 4:
                return None
            
            length = struct.unpack('!I', data[:4])[0]
            
            # Extract JSON data
            if len(data) < 4 + length:
                return None
            
            json_data = data[4:4+length].decode('utf-8')
            message_dict = json.loads(json_data)
            
            # Create SecureMessage object
            message = SecureMessage(
                msg_type=MessageType(message_dict['type']),
                payload=message_dict['payload'],
                timestamp=message_dict['timestamp'],
                sender_id=message_dict['sender_id'],
                sequence_num=message_dict['sequence_num'],
                checksum=message_dict['checksum']
            )
            
            return message
            
        except Exception as e:
            print(f"Message deserialization error: {e}")
            return None

class SecureRobotServer:
    """Secure server for robot control with AI blocking"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8443, 
                 security_level: SecurityLevel = SecurityLevel.MAXIMUM):
        self.host = host
        self.port = port
        self.protocol_handler = SecureProtocolHandler(security_level)
        self.running = False
        self.client_connections = {}
        
        # SSL context for encrypted communications
        self.ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for secure communications"""
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # In production, use proper certificates
        # For demo, create self-signed or use TLS settings
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # In production, use CERT_REQUIRED
        
        return context
    
    def start_server(self):
        """Start the secure robot control server"""
        
        self.running = True
        
        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            # Bind and listen
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Secure robot server listening on {self.host}:{self.port}")
            
            while self.running:
                # Accept client connection
                client_socket, client_address = server_socket.accept()
                
                # Check if client is blocked
                if client_address[0] in self.protocol_handler.blocked_ips:
                    print(f"Blocked connection from {client_address}")
                    client_socket.close()
                    continue
                
                print(f"Secure connection from {client_address}")
                
                # Handle client in separate thread (simplified for demo)
                self._handle_client(client_socket, client_address)
        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server_socket.close()
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """Handle secure client connection"""
        
        try:
            # Wrap socket with SSL
            ssl_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
            
            while self.running:
                # Receive data
                data = self._receive_full_message(ssl_socket)
                if not data:
                    break
                
                # Deserialize message
                message = self.protocol_handler.deserialize_message(data)
                if not message:
                    continue
                
                # Validate message
                is_valid, reason = self.protocol_handler.validate_message(message)
                if not is_valid:
                    print(f"Invalid message from {client_address}: {reason}")
                    
                    # Block client if too many invalid messages
                    self.protocol_handler.blocked_ips.add(client_address[0])
                    break
                
                # Process message
                response = self._process_secure_message(message, client_address)
                
                # Send response
                if response:
                    response_data = self.protocol_handler.serialize_message(response)
                    ssl_socket.send(response_data)
        
        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            client_socket.close()
    
    def _receive_full_message(self, ssl_socket) -> Optional[bytes]:
        """Receive complete message from SSL socket"""
        
        try:
            # Receive length header
            length_data = ssl_socket.recv(4)
            if len(length_data) != 4:
                return None
            
            length = struct.unpack('!I', length_data)[0]
            
            # Receive message data
            message_data = b''
            while len(message_data) < length:
                chunk = ssl_socket.recv(length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return length_data + message_data
            
        except Exception:
            return None
    
    def _process_secure_message(self, message: SecureMessage, client_address: Tuple[str, int]) -> Optional[SecureMessage]:
        """Process validated secure message"""
        
        if message.msg_type == MessageType.COMMAND:
            # Process robot command (AI-filtered)
            command = message.payload.get('command', '')
            
            # Additional AI content check
            has_ai, violations = self.protocol_handler.content_filter.scan_content(command)
            if has_ai:
                response_payload = {
                    'status': 'BLOCKED',
                    'reason': 'AI_CONTENT_DETECTED',
                    'violations': violations
                }
            else:
                # Execute safe command
                response_payload = {
                    'status': 'EXECUTED',
                    'result': f'Safe execution: {command}',
                    'timestamp': time.time()
                }
            
            # Create response message
            return self.protocol_handler.create_secure_message(
                MessageType.STATUS,
                response_payload,
                "ROBOT_CONTROLLER"
            )
        
        elif message.msg_type == MessageType.HEARTBEAT:
            # Respond to heartbeat
            return self.protocol_handler.create_secure_message(
                MessageType.HEARTBEAT,
                {'status': 'ALIVE', 'ai_blocked': True},
                "ROBOT_CONTROLLER"
            )
        
        return None
    
    def stop_server(self):
        """Stop the secure server"""
        self.running = False

# Example usage and testing
if __name__ == "__main__":
    
    # Create secure protocol handler
    protocol = SecureProtocolHandler(SecurityLevel.MAXIMUM)
    
    # Test AI content filtering
    test_payload = {
        'command': 'move_forward 10',
        'safe_param': 'value',
        'dangerous_ai': 'import tensorflow as tf; neural_network.train()'
    }
    
    # Create and validate message
    message = protocol.create_secure_message(
        MessageType.COMMAND,
        test_payload,
        "REMOTE_CONTROL_1"
    )
    
    print("Original payload:", test_payload)
    print("Filtered payload:", message.payload)
    
    # Validate message
    is_valid, reason = protocol.validate_message(message)
    print(f"Message validation: {is_valid}, {reason}")
    
    # Test serialization
    serialized = protocol.serialize_message(message)
    deserialized = protocol.deserialize_message(serialized)
    
    print("Serialization test passed:", deserialized.payload == message.payload)