from qiskit import QuantumCircuit, Aer, execute
import numpy as np

class QBERC:
    def __init__(self):
        self.backend = Aer.get_backend('aer_simulator')
        self.emotion_labels = ["calm", "curious", "alert", "joy", "fear", "trust"]
        self.entangled_emotions = self._generate_emotion_qc()

    def _generate_emotion_qc(self):
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure([0,1,2], [0,1,2])
        return qc

    def sense_and_resonate(self, proximity, touch, sound_level):
        input_sum = proximity + touch + sound_level
        job = execute(self.entangled_emotions, self.backend, shots=1)
        result = job.result().get_counts()
        binary = list(result.keys())[0]
        index = int(binary, 2) % len(self.emotion_labels)
        return self.emotion_labels[index]

    def get_micro_gesture(self, emotion_state):
        gesture_map = {
            "calm": {"eye": "soft", "posture": "relaxed"},
            "curious": {"eye": "tilt", "posture": "lean_forward"},
            "alert": {"eye": "wide", "posture": "upright"},
            "joy": {"eye": "sparkle", "posture": "bounce"},
            "fear": {"eye": "darting", "posture": "retract"},
            "trust": {"eye": "still", "posture": "open_arms"},
        }
        return gesture_map.get(emotion_state, {})

class EmotionReflexLayer:
    def __init__(self):
        self.state = "neutral"
        self.qberc = QBERC()
        self.emotion_history = []
        self.quantum_weight = 0.4  # Weight for quantum emotional influence

    def update_emotion(self, sensory_input):
        # Classical emotion processing
        classical_state = self._classical_emotion_update(sensory_input)
        
        # Quantum emotion processing
        proximity = sensory_input.get("proximity", 1.0)
        touch = sensory_input.get("touch", 0)
        sound_level = sensory_input.get("sound_level", 0.5)
        quantum_state = self.qberc.sense_and_resonate(proximity, touch, sound_level)
        
        # Combine classical and quantum emotional states
        self.state = self._blend_emotions(classical_state, quantum_state)
        self.emotion_history.append(self.state)
        
        # Keep emotion history manageable
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)

    def _classical_emotion_update(self, sensory_input):
        if sensory_input.get("proximity", 1.0) < 0.2:
            return "surprised"
        elif sensory_input.get("touch", 0) > 0.8:
            return "comforted"
        else:
            return "neutral"

    def _blend_emotions(self, classical_state, quantum_state):
        # Map classical states to quantum emotion space
        classical_to_quantum = {
            "neutral": "calm",
            "surprised": "alert",
            "comforted": "trust"
        }
        
        # Get quantum equivalent of classical state
        classical_quantum = classical_to_quantum.get(classical_state, "calm")
        
        # Blend emotions based on history and current states
        if len(self.emotion_history) > 0:
            # Consider emotional continuity
            if self.emotion_history[-1] == classical_quantum:
                return classical_quantum
            elif self.emotion_history[-1] == quantum_state:
                return quantum_state
        
        # Weighted random choice between classical and quantum
        return np.random.choice(
            [classical_quantum, quantum_state],
            p=[1 - self.quantum_weight, self.quantum_weight]
        )

    def get_micro_gesture(self):
        # Get quantum-enhanced gestures
        quantum_gesture = self.qberc.get_micro_gesture(self.state)
        
        # Fallback to classical gestures if quantum returns empty
        if not quantum_gesture:
            gestures = {
                "neutral": {"eye": "normal", "mouth": "relaxed"},
                "surprised": {"eye": "wide", "mouth": "open"},
                "comforted": {"eye": "soft", "mouth": "smile"},
            }
            return gestures.get(self.state, gestures["neutral"])
        
        return quantum_gesture

    def demonstrate_qber(self, proximity=0.3, touch=0.8, sound_level=0.2):
        """
        Demonstrate the Quantum Bear Emotion Resonance system with specific sensory inputs.
        
        Args:
            proximity (float): Proximity sensor value (0-1)
            touch (float): Touch sensor value (0-1)
            sound_level (float): Sound level value (0-1)
            
        Returns:
            dict: Dictionary containing emotion and gesture information
        """
        # Create sensory input dictionary
        sensory_input = {
            "proximity": proximity,
            "touch": touch,
            "sound_level": sound_level
        }
        
        # Update emotion state
        self.update_emotion(sensory_input)
        
        # Get quantum emotion directly
        quantum_emotion = self.qberc.sense_and_resonate(proximity, touch, sound_level)
        quantum_gesture = self.qberc.get_micro_gesture(quantum_emotion)
        
        # Get hybrid emotion and gesture
        hybrid_gesture = self.get_micro_gesture()
        
        # Return comprehensive emotional state
        return {
            "quantum_emotion": quantum_emotion,
            "quantum_gesture": quantum_gesture,
            "hybrid_emotion": self.state,
            "hybrid_gesture": hybrid_gesture,
            "emotion_history": self.emotion_history[-3:] if self.emotion_history else []
        }

# Example usage:
if __name__ == "__main__":
    # Create emotion reflex layer
    emotion_layer = EmotionReflexLayer()
    
    # Demonstrate QBER with specific sensory inputs
    result = emotion_layer.demonstrate_qber(proximity=0.3, touch=0.8, sound_level=0.2)
    
    # Print results
    print("\nQuantum Bear Emotion Resonance Demo:")
    print(f"Quantum Emotion: {result['quantum_emotion']}")
    print(f"Quantum Gesture: {result['quantum_gesture']}")
    print(f"Hybrid Emotion: {result['hybrid_emotion']}")
    print(f"Hybrid Gesture: {result['hybrid_gesture']}")
    print(f"Recent Emotion History: {result['emotion_history']}")
