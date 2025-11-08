# sia/vqram.py: Virtual Quantum Random Access Memory Module
# Built on top of qbt.py - Simple, intuitive API for quantum state persistence

import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union

# Import the core quantum simulator
from .qbt import qbt, partial_trace

class QuantumNoiseFilter:
    """Advanced noise filtering for quantum state stabilization"""
    
    @staticmethod
    def spectral_cutoff(rho, threshold=1e-8):
        """Remove small eigenvalues causing numerical instability"""
        eigvals, eigvecs = np.linalg.eigh(rho)
        # Preserve trace while removing noise
        eigvals[eigvals < threshold] = 0
        if np.sum(eigvals) > 0:
            eigvals /= np.sum(eigvals)  # Renormalize
        rho_filtered = eigvecs @ np.diag(eigvals) @ eigvecs.conj().T
        return rho_filtered
    
    @staticmethod
    def tikhonov_regularization(rho, alpha=1e-6):
        """Stabilize ill-conditioned density matrices"""
        n = rho.shape[0]
        return (1 - alpha) * rho + alpha * np.eye(n) / n
    
    @staticmethod
    def entropy_constrained_filter(rho, max_entropy=2.0):
        """Limit quantum entropy to control noise amplification"""
        from scipy.linalg import eigvalsh
        
        eigvals = eigvalsh(rho)
        positive_eigs = eigvals[eigvals > 1e-12]
        if positive_eigs.size == 0:
            return rho
            
        current_entropy = -np.sum(positive_eigs * np.log2(positive_eigs))
        
        if current_entropy > max_entropy:
            return QuantumNoiseFilter.spectral_cutoff(rho)
        return rho
    
    @staticmethod
    def auto_filter(rho):
        """Automatic noise filtering with sensible defaults"""
        # Apply multiple filtering strategies
        rho_temp = QuantumNoiseFilter.tikhonov_regularization(rho)
        rho_temp = QuantumNoiseFilter.spectral_cutoff(rho_temp)
        rho_temp = QuantumNoiseFilter.entropy_constrained_filter(rho_temp)
        
        # Ensure valid quantum state
        trace = np.trace(rho_temp)
        if abs(trace - 1.0) > 1e-10 and trace != 0:
            rho_temp /= trace
            
        return rho_temp

class QuantumStateMetadata:
    """Metadata container for quantum states"""
    
    def __init__(self, state_id: str, num_qubits: int, source: str = "unknown"):
        self.state_id = state_id
        self.num_qubits = num_qubits
        self.source = source
        self.timestamp = datetime.now().isoformat()
        self.purity = 0.0
        self.entropy = 0.0
        self.fidelity = 1.0
        self.tags = []
        self.description = ""
        
    def calculate_metrics(self, rho):
        """Calculate quantum metrics for the state"""
        self.purity = float(np.trace(rho @ rho).real)
        
        eigvals = np.linalg.eigvalsh(rho)
        positive_eigs = eigvals[eigvals > 1e-12]
        if positive_eigs.size > 0:
            self.entropy = float(-np.sum(positive_eigs * np.log2(positive_eigs)))
        else:
            self.entropy = 0.0
            
    def to_dict(self):
        """Convert metadata to dictionary"""
        return {
            'state_id': self.state_id,
            'num_qubits': self.num_qubits,
            'source': self.source,
            'timestamp': self.timestamp,
            'purity': self.purity,
            'entropy': self.entropy,
            'fidelity': self.fidelity,
            'tags': self.tags,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create metadata from dictionary"""
        metadata = cls(data['state_id'], data['num_qubits'], data['source'])
        metadata.timestamp = data['timestamp']
        metadata.purity = data['purity']
        metadata.entropy = data['entropy']
        metadata.fidelity = data['fidelity']
        metadata.tags = data['tags']
        metadata.description = data['description']
        return metadata

class VirtualQRAM:
    """
    Virtual Quantum Random Access Memory
    Provides persistent, noise-filtered storage for quantum states
    """
    
    def __init__(self, storage_path: str = "./vqram_storage", auto_filter: bool = True):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.auto_filter = auto_filter
        self.filter = QuantumNoiseFilter()
        self.metadata_store = {}
        
        # Load existing metadata
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata from storage"""
        metadata_file = self.storage_path / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    for state_id, meta_dict in data.items():
                        self.metadata_store[state_id] = QuantumStateMetadata.from_dict(meta_dict)
            except:
                # Start fresh if metadata is corrupted
                self.metadata_store = {}
    
    def _save_metadata(self):
        """Save metadata to storage"""
        metadata_file = self.storage_path / "metadata.json"
        metadata_dict = {state_id: meta.to_dict() for state_id, meta in self.metadata_store.items()}
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
    
    def store_state(self, state_id: str, quantum_data: Union[np.ndarray, qbt], 
                   description: str = "", tags: List[str] = None) -> str:
        """
        Store a quantum state with noise filtering and persistence
        
        Args:
            state_id: Unique identifier for the state
            quantum_data: Density matrix or qbt object
            description: Human-readable description
            tags: List of tags for categorization
            
        Returns:
            State ID of the stored state
        """
        # Convert qbt to density matrix if needed
        if isinstance(quantum_data, qbt):
            rho = quantum_data.rho
            num_qubits = quantum_data.num_qubits
            source = f"qbt_circuit"
        else:
            rho = quantum_data
            num_qubits = int(np.log2(rho.shape[0]))
            source = "density_matrix"
        
        # Apply noise filtering if enabled
        if self.auto_filter:
            rho = self.filter.auto_filter(rho)
        
        # Ensure the state is valid
        trace = np.trace(rho)
        if abs(trace - 1.0) > 1e-10 and trace != 0:
            rho /= trace
        
        # Create and populate metadata
        metadata = QuantumStateMetadata(state_id, num_qubits, source)
        metadata.calculate_metrics(rho)
        metadata.description = description
        metadata.tags = tags or []
        
        # Save state and metadata
        state_file = self.storage_path / f"{state_id}.npy"
        np.save(state_file, rho)
        
        self.metadata_store[state_id] = metadata
        self._save_metadata()
        
        return state_id
    
    def load_state(self, state_id: str) -> Optional[np.ndarray]:
        """
        Load a quantum state from storage
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            Density matrix or None if not found
        """
        state_file = self.storage_path / f"{state_id}.npy"
        if not state_file.exists():
            return None
        
        try:
            rho = np.load(state_file)
            return rho
        except:
            return None
    
    def load_state_into_qbt(self, state_id: str, num_qubits: int = None) -> Optional[qbt]:
        """
        Load a stored state into a new qbt instance
        
        Args:
            state_id: Unique identifier for the state
            num_qubits: Number of qubits (inferred from state if None)
            
        Returns:
            qbt instance with the loaded state or None if error
        """
        rho = self.load_state(state_id)
        if rho is None:
            return None
        
        if num_qubits is None:
            num_qubits = int(np.log2(rho.shape[0]))
        
        # Create qbt instance and manually set the state
        qbt_instance = qbt(num_qubits)
        qbt_instance.rho = rho
        qbt_instance.statevector = None  # Mixed state, no statevector
        
        return qbt_instance
    
    def get_metadata(self, state_id: str) -> Optional[QuantumStateMetadata]:
        """Get metadata for a stored state"""
        return self.metadata_store.get(state_id)
    
    def list_states(self, tag: str = None) -> List[str]:
        """List all stored states, optionally filtered by tag"""
        if tag:
            return [state_id for state_id, meta in self.metadata_store.items() 
                   if tag in meta.tags]
        return list(self.metadata_store.keys())
    
    def delete_state(self, state_id: str) -> bool:
        """Delete a stored state and its metadata"""
        state_file = self.storage_path / f"{state_id}.npy"
        
        if state_file.exists():
            state_file.unlink()
        
        if state_id in self.metadata_store:
            del self.metadata_store[state_id]
            self._save_metadata()
            return True
        
        return False
    
    def state_info(self, state_id: str) -> Dict:
        """Get comprehensive information about a stored state"""
        metadata = self.get_metadata(state_id)
        if not metadata:
            return {}
        
        info = metadata.to_dict()
        rho = self.load_state(state_id)
        if rho is not None:
            info['shape'] = rho.shape
            info['data_type'] = str(rho.dtype)
        
        return info
    
    def calculate_fidelity(self, state_id1: str, state_id2: str) -> float:
        """
        Calculate fidelity between two stored states
        
        Args:
            state_id1: First state ID
            state_id2: Second state ID
            
        Returns:
            Fidelity value between 0 and 1
        """
        rho1 = self.load_state(state_id1)
        rho2 = self.load_state(state_id2)
        
        if rho1 is None or rho2 is None:
            return 0.0
        
        if rho1.shape != rho2.shape:
            return 0.0
        
        # For simplicity, use overlap for mixed states
        try:
            fidelity = np.trace(rho1 @ rho2).real
            return float(np.clip(fidelity, 0.0, 1.0))
        except:
            return 0.0
    
    def search_states(self, **filters) -> List[str]:
        """
        Search for states based on metadata filters
        
        Args:
            **filters: Key-value pairs to filter by (e.g., min_purity=0.8, max_entropy=1.0)
            
        Returns:
            List of matching state IDs
        """
        matching_states = []
        
        for state_id, metadata in self.metadata_store.items():
            match = True
            
            for key, value in filters.items():
                if key.startswith('min_'):
                    attr = key[4:]
                    if hasattr(metadata, attr):
                        if getattr(metadata, attr) < value:
                            match = False
                            break
                elif key.startswith('max_'):
                    attr = key[4:]
                    if hasattr(metadata, attr):
                        if getattr(metadata, attr) > value:
                            match = False
                            break
                else:
                    if hasattr(metadata, key):
                        if getattr(metadata, key) != value:
                            match = False
                            break
            
            if match:
                matching_states.append(state_id)
        
        return matching_states

# === SIMPLE API FUNCTIONS ===

# Global vQRAM instance for easy access
_global_vqram = None

def get_vqram(storage_path: str = "./vqram_storage") -> VirtualQRAM:
    """Get or create global vQRAM instance"""
    global _global_vqram
    if _global_vqram is None:
        _global_vqram = VirtualQRAM(storage_path)
    return _global_vqram

def save_state(state_id: str, quantum_data, description: str = "", tags: List[str] = None) -> str:
    """Simple function to save a quantum state"""
    vqram = get_vqram()
    return vqram.store_state(state_id, quantum_data, description, tags)

def load_state(state_id: str) -> np.ndarray:
    """Simple function to load a quantum state"""
    vqram = get_vqram()
    return vqram.load_state(state_id)

def load_qbt(state_id: str, num_qubits: int = None) -> qbt:
    """Simple function to load a state into a qbt instance"""
    vqram = get_vqram()
    return vqram.load_state_into_qbt(state_id, num_qubits)

def load_circuit(state_id: str, num_qubits: int = None) -> qbt:
    """Simple function to load a state into a qbt instance (alias for load_qbt)"""
    vqram = get_vqram()
    return vqram.load_state_into_qbt(state_id, num_qubits)

def list_saved_states(tag: str = None) -> List[str]:
    """List all saved quantum states"""
    vqram = get_vqram()
    return vqram.list_states(tag)

def get_state_info(state_id: str) -> Dict:
    """Get information about a saved state"""
    vqram = get_vqram()
    return vqram.state_info(state_id)

# === INTEGRATION WITH QBT CLASS ===

def _qbt_save_state(self, state_id: str, description: str = "", tags: List[str] = None) -> str:
    """Add save_state method to qbt class"""
    return save_state(state_id, self, description, tags)

# Monkey patch the qbt class to add vQRAM functionality
qbt.save_state = _qbt_save_state

# === DEMO AND USAGE EXAMPLES ===

def demo_vqram():
    """Demonstrate vQRAM functionality"""
    print("=== vQRAM Demonstration ===")
    
    # Create a quantum circuit using qbt
    qbt_instance = qbt(2)
    qbt_instance.h(0).cnot(0, 1)
    print("Created Bell state circuit")
    
    # Run the circuit
    qbt_instance.run()
    print("Circuit executed")
    
    # Save the state using the instance method
    state_id = qbt_instance.save_state("bell_state", "Bell state example", ["entangled", "demo"])
    print(f"State saved with ID: {state_id}")
    
    # Load the state back
    loaded_rho = load_state("bell_state")
    print(f"State loaded, shape: {loaded_rho.shape}")
    
    # Load into new qbt instance
    new_qbt = load_qbt("bell_state")
    print(f"New qbt instance created with {new_qbt.num_qubits} qubits")
    
    # Get state information
    info = get_state_info("bell_state")
    print(f"State purity: {info['purity']:.4f}")
    print(f"State entropy: {info['entropy']:.4f}")
    
    # List all saved states
    states = list_saved_states()
    print(f"Saved states: {states}")

if __name__ == "__main__":
    demo_vqram()