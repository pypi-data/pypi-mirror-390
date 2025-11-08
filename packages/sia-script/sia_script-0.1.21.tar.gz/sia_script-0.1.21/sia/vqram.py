# sia/vqram.py: Virtual Quantum Random Access Memory Module
# Built on top of qbt.py - Simple, intuitive API for quantum state persistence

import numpy as np
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Callable
import hashlib

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
        self.parent_states = []  # For tracking state evolution
        self.quantum_volume = 0.0  # Measure of quantum complexity
        
    def calculate_metrics(self, rho):
        """Calculate quantum metrics for the state"""
        self.purity = float(np.trace(rho @ rho).real)
        
        eigvals = np.linalg.eigvalsh(rho)
        positive_eigs = eigvals[eigvals > 1e-12]
        if positive_eigs.size > 0:
            self.entropy = float(-np.sum(positive_eigs * np.log2(positive_eigs)))
        else:
            self.entropy = 0.0
            
        # Calculate quantum volume approximation
        self.quantum_volume = float(np.sqrt(self.purity * (1 - self.entropy/max(1, self.num_qubits))))
            
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
            'quantum_volume': self.quantum_volume,
            'tags': self.tags,
            'description': self.description,
            'parent_states': self.parent_states
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create metadata from dictionary"""
        metadata = cls(data['state_id'], data['num_qubits'], data['source'])
        metadata.timestamp = data['timestamp']
        metadata.purity = data['purity']
        metadata.entropy = data['entropy']
        metadata.fidelity = data.get('fidelity', 1.0)
        metadata.quantum_volume = data.get('quantum_volume', 0.0)
        metadata.tags = data['tags']
        metadata.description = data['description']
        metadata.parent_states = data.get('parent_states', [])
        return metadata

class QMLTrainingHistory:
    """Track quantum machine learning training progress"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.loss_history = []
        self.parameter_history = []
        self.fidelity_history = []
        self.timestamps = []
        self.best_weights = None
        self.best_loss = float('inf')
        
    def add_epoch(self, loss, parameters, fidelity=1.0, timestamp=None):
        """Add training epoch data"""
        self.loss_history.append(float(loss))
        self.parameter_history.append([float(p) for p in parameters])
        self.fidelity_history.append(float(fidelity))
        self.timestamps.append(timestamp or datetime.now().isoformat())
        
        # Track best performance
        if loss < self.best_loss:
            self.best_loss = loss
            self.best_weights = parameters.copy()
    
    def to_dict(self):
        """Convert history to dictionary"""
        return {
            'model_id': self.model_id,
            'loss_history': self.loss_history,
            'parameter_history': self.parameter_history,
            'fidelity_history': self.fidelity_history,
            'timestamps': self.timestamps,
            'best_loss': self.best_loss,
            'best_weights': self.best_weights
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create history from dictionary"""
        history = cls(data['model_id'])
        history.loss_history = data['loss_history']
        history.parameter_history = data['parameter_history']
        history.fidelity_history = data.get('fidelity_history', [])
        history.timestamps = data['timestamps']
        history.best_loss = data.get('best_loss', float('inf'))
        history.best_weights = data.get('best_weights')
        return history

class QuantumModelSerializer:
    """Serialize and deserialize quantum ML models"""
    
    @staticmethod
    def generate_model_id(model_config: Dict) -> str:
        """Generate unique model ID from configuration"""
        config_str = json.dumps(model_config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:16]
    
    @staticmethod
    def serialize_quantum_model(model, model_config: Dict) -> Dict:
        """Serialize quantum ML model to dictionary"""
        model_data = {
            'type': 'quantum_ml_model',
            'model_config': model_config,
            'timestamp': datetime.now().isoformat(),
            'framework_version': '1.0'
        }
        
        # Extract model-specific data
        if hasattr(model, 'weights'):
            model_data['weights'] = model.weights.tolist() if isinstance(model.weights, np.ndarray) else model.weights
        if hasattr(model, 'num_qubits'):
            model_data['num_qubits'] = model.num_qubits
        if hasattr(model, 'circuit_tokens'):
            model_data['circuit_tokens'] = model.circuit_tokens
        if hasattr(model, 'trained'):
            model_data['trained'] = model.trained
            
        return model_data
    
    @staticmethod
    def deserialize_quantum_model(model_data: Dict, model_class=None):
        """Deserialize quantum ML model from dictionary"""
        if model_data.get('type') != 'quantum_ml_model':
            raise ValueError("Invalid quantum model data")
        
        if model_class:
            # Reconstruct model instance
            model = model_class(**model_data['model_config'])
            
            # Restore model state
            if 'weights' in model_data and hasattr(model, 'weights'):
                model.weights = np.array(model_data['weights'])
            if 'circuit_tokens' in model_data and hasattr(model, 'circuit_tokens'):
                model.circuit_tokens = model_data['circuit_tokens']
            if 'trained' in model_data and hasattr(model, 'trained'):
                model.trained = model_data['trained']
                
            return model
        else:
            return model_data

class QuantumStateRegistry:
    """Manage relationships between quantum states"""
    
    def __init__(self):
        self.state_graph = {}  # state_id -> [child_state_ids]
        self.state_lineage = {}  # state_id -> parent_state_id
        
    def add_relationship(self, parent_id: str, child_id: str):
        """Add parent-child relationship between states"""
        if parent_id not in self.state_graph:
            self.state_graph[parent_id] = []
        self.state_graph[parent_id].append(child_id)
        self.state_lineage[child_id] = parent_id
    
    def get_lineage(self, state_id: str) -> List[str]:
        """Get full lineage of a state"""
        lineage = []
        current_id = state_id
        
        while current_id in self.state_lineage:
            parent_id = self.state_lineage[current_id]
            lineage.append(parent_id)
            current_id = parent_id
            
        return lineage[::-1]  # Return from oldest to newest
    
    def get_children(self, state_id: str) -> List[str]:
        """Get all children of a state"""
        return self.state_graph.get(state_id, [])
    
    def is_ancestor(self, state_id: str, potential_ancestor: str) -> bool:
        """Check if one state is ancestor of another"""
        return potential_ancestor in self.get_lineage(state_id)

class VirtualQRAM:
    """
    Virtual Quantum Random Access Memory
    Provides persistent, noise-filtered storage for quantum states with QML enhancements
    """
    
    def __init__(self, storage_path: str = "./vqram_storage", auto_filter: bool = True):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.auto_filter = auto_filter
        self.filter = QuantumNoiseFilter()
        self.metadata_store = {}
        self.model_store = {}
        self.training_histories = {}
        self.state_registry = QuantumStateRegistry()
        self.serializer = QuantumModelSerializer()
        
        # Create subdirectories for organization
        (self.storage_path / "models").mkdir(exist_ok=True)
        (self.storage_path / "histories").mkdir(exist_ok=True)
        (self.storage_path / "states").mkdir(exist_ok=True)
        
        # Load existing data
        self._load_metadata()
        self._load_models()
        self._load_training_histories()
    
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
    
    def _load_models(self):
        """Load quantum models from storage"""
        models_dir = self.storage_path / "models"
        for model_file in models_dir.glob("*.json"):
            try:
                with open(model_file, 'r') as f:
                    model_data = json.load(f)
                model_id = model_file.stem
                self.model_store[model_id] = model_data
            except:
                continue
    
    def _load_training_histories(self):
        """Load training histories from storage"""
        histories_dir = self.storage_path / "histories"
        for history_file in histories_dir.glob("*.json"):
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                history_id = history_file.stem
                self.training_histories[history_id] = QMLTrainingHistory.from_dict(history_data)
            except:
                continue
    
    def store_state(self, state_id: str, quantum_data: Union[np.ndarray, qbt], 
                   description: str = "", tags: List[str] = None, 
                   parent_state: str = None) -> str:
        """
        Store a quantum state with noise filtering and persistence
        
        Args:
            state_id: Unique identifier for the state
            quantum_data: Density matrix or qbt object
            description: Human-readable description
            tags: List of tags for categorization
            parent_state: Parent state ID for lineage tracking
            
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
        
        # Track parent relationship
        if parent_state:
            metadata.parent_states = [parent_state]
            self.state_registry.add_relationship(parent_state, state_id)
        
        # Save state and metadata
        state_file = self.storage_path / "states" / f"{state_id}.npy"
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
        state_file = self.storage_path / "states" / f"{state_id}.npy"
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
    
    # === QUANTUM MACHINE LEARNING EXTENSIONS ===
    
    def store_quantum_model(self, model, model_config: Dict, description: str = "") -> str:
        """
        Store complete QML model (weights + architecture)
        
        Args:
            model: Quantum ML model instance
            model_config: Model configuration dictionary
            description: Human-readable description
            
        Returns:
            Model ID of the stored model
        """
        model_id = self.serializer.generate_model_id(model_config)
        
        # Serialize model data
        model_data = self.serializer.serialize_quantum_model(model, model_config)
        model_data['description'] = description
        
        # Save model
        model_file = self.storage_path / "models" / f"{model_id}.json"
        with open(model_file, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        self.model_store[model_id] = model_data
        return model_id
    
    def load_quantum_model(self, model_id: str, model_class=None):
        """
        Load trained QML model
        
        Args:
            model_id: Model identifier
            model_class: Class to instantiate (optional)
            
        Returns:
            Reconstructed model instance or model data
        """
        if model_id not in self.model_store:
            return None
        
        model_data = self.model_store[model_id]
        return self.serializer.deserialize_quantum_model(model_data, model_class)
    
    def store_training_history(self, history: QMLTrainingHistory):
        """
        Store QML training progress
        
        Args:
            history: QMLTrainingHistory instance
        """
        history_id = f"{history.model_id}_history"
        
        # Save history
        history_file = self.storage_path / "histories" / f"{history_id}.json"
        with open(history_file, 'w') as f:
            json.dump(history.to_dict(), f, indent=2)
        
        self.training_histories[history_id] = history
        return history_id
    
    def load_training_history(self, model_id: str) -> Optional[QMLTrainingHistory]:
        """
        Load training history for a model
        
        Args:
            model_id: Model identifier
            
        Returns:
            QMLTrainingHistory instance or None
        """
        history_id = f"{model_id}_history"
        return self.training_histories.get(history_id)
    
    def create_training_checkpoint(self, model, model_config: Dict, history: QMLTrainingHistory, 
                                 checkpoint_name: str = None) -> str:
        """
        Create comprehensive training checkpoint
        
        Args:
            model: Current model instance
            model_config: Model configuration
            history: Training history
            checkpoint_name: Optional checkpoint name
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = checkpoint_name or f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store model
        model_id = self.store_quantum_model(model, model_config, f"Checkpoint: {checkpoint_id}")
        
        # Store history
        self.store_training_history(history)
        
        # Create checkpoint metadata
        checkpoint_data = {
            'checkpoint_id': checkpoint_id,
            'model_id': model_id,
            'timestamp': datetime.now().isoformat(),
            'current_epoch': len(history.loss_history),
            'best_loss': history.best_loss
        }
        
        checkpoint_file = self.storage_path / "histories" / f"{checkpoint_id}_checkpoint.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        return checkpoint_id
    
    # === ADVANCED QUANTUM STATE OPERATIONS ===
    
    def evolve_state(self, initial_state_id: str, evolution_circuit: Callable, 
                    new_state_id: str, description: str = "") -> str:
        """
        Evolve a quantum state through a circuit and store result
        
        Args:
            initial_state_id: Starting state ID
            evolution_circuit: Function that takes qbt and applies gates
            new_state_id: ID for the evolved state
            description: Description of the evolution
            
        Returns:
            New state ID
        """
        # Load initial state
        initial_qbt = self.load_state_into_qbt(initial_state_id)
        if initial_qbt is None:
            raise ValueError(f"Initial state {initial_state_id} not found")
        
        # Apply evolution
        evolution_circuit(initial_qbt)
        initial_qbt.run()
        
        # Store evolved state
        return self.store_state(new_state_id, initial_qbt, description, 
                              parent_state=initial_state_id)
    
    def compute_state_similarity(self, state_id1: str, state_id2: str) -> Dict[str, float]:
        """
        Compute multiple similarity metrics between two states
        
        Args:
            state_id1: First state ID
            state_id2: Second state ID
            
        Returns:
            Dictionary of similarity metrics
        """
        rho1 = self.load_state(state_id1)
        rho2 = self.load_state(state_id2)
        
        if rho1 is None or rho2 is None:
            return {}
        
        if rho1.shape != rho2.shape:
            return {}
        
        metrics = {}
        
        # Fidelity
        try:
            fidelity = np.trace(rho1 @ rho2).real
            metrics['fidelity'] = float(np.clip(fidelity, 0.0, 1.0))
        except:
            metrics['fidelity'] = 0.0
        
        # Trace distance
        try:
            trace_dist = 0.5 * np.trace(np.abs(rho1 - rho2)).real
            metrics['trace_distance'] = float(trace_dist)
        except:
            metrics['trace_distance'] = 1.0
        
        # Hilbert-Schmidt distance
        try:
            hs_dist = np.trace((rho1 - rho2) @ (rho1 - rho2).conj().T).real
            metrics['hilbert_schmidt_distance'] = float(hs_dist)
        except:
            metrics['hilbert_schmidt_distance'] = 1.0
        
        return metrics
    
    def batch_operations(self, operations: List[Callable]) -> List[str]:
        """
        Execute multiple quantum operations in batch
        
        Args:
            operations: List of functions that return state IDs
            
        Returns:
            List of resulting state IDs
        """
        results = []
        for op in operations:
            try:
                result = op()
                if isinstance(result, str):
                    results.append(result)
            except Exception as e:
                print(f"Batch operation failed: {e}")
                results.append(None)
        
        return results
    
    # === EXISTING METHODS (Maintained for backward compatibility) ===
    
    def get_metadata(self, state_id: str) -> Optional[QuantumStateMetadata]:
        """Get metadata for a stored state"""
        return self.metadata_store.get(state_id)
    
    def list_states(self, tag: str = None) -> List[str]:
        """List all stored states, optionally filtered by tag"""
        if tag:
            return [state_id for state_id, meta in self.metadata_store.items() 
                   if tag in meta.tags]
        return list(self.metadata_store.keys())
    
    def list_models(self) -> List[str]:
        """List all stored quantum models"""
        return list(self.model_store.keys())
    
    def list_training_histories(self) -> List[str]:
        """List all stored training histories"""
        return list(self.training_histories.keys())
    
    def delete_state(self, state_id: str) -> bool:
        """Delete a stored state and its metadata"""
        state_file = self.storage_path / "states" / f"{state_id}.npy"
        
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
        
        # Add lineage information
        info['lineage'] = self.state_registry.get_lineage(state_id)
        info['children'] = self.state_registry.get_children(state_id)
        
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
        similarities = self.compute_state_similarity(state_id1, state_id2)
        return similarities.get('fidelity', 0.0)
    
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

# === NEW QML-ENHANCED API FUNCTIONS ===

def save_quantum_model(model, model_config: Dict, description: str = "") -> str:
    """Save a quantum machine learning model"""
    vqram = get_vqram()
    return vqram.store_quantum_model(model, model_config, description)

def load_quantum_model(model_id: str, model_class=None):
    """Load a quantum machine learning model"""
    vqram = get_vqram()
    return vqram.load_quantum_model(model_id, model_class)

def save_training_history(history: QMLTrainingHistory) -> str:
    """Save QML training history"""
    vqram = get_vqram()
    return vqram.store_training_history(history)

def load_training_history(model_id: str) -> Optional[QMLTrainingHistory]:
    """Load training history for a model"""
    vqram = get_vqram()
    return vqram.load_training_history(model_id)

def create_training_checkpoint(model, model_config: Dict, history: QMLTrainingHistory, 
                             checkpoint_name: str = None) -> str:
    """Create comprehensive training checkpoint"""
    vqram = get_vqram()
    return vqram.create_training_checkpoint(model, model_config, history, checkpoint_name)

def evolve_quantum_state(initial_state_id: str, evolution_circuit: Callable, 
                        new_state_id: str, description: str = "") -> str:
    """Evolve a quantum state through a circuit"""
    vqram = get_vqram()
    return vqram.evolve_state(initial_state_id, evolution_circuit, new_state_id, description)

def compute_quantum_similarity(state_id1: str, state_id2: str) -> Dict[str, float]:
    """Compute similarity metrics between two quantum states"""
    vqram = get_vqram()
    return vqram.compute_state_similarity(state_id1, state_id2)

# === INTEGRATION WITH QBT CLASS ===

def _qbt_save_state(self, state_id: str, description: str = "", tags: List[str] = None) -> str:
    """Add save_state method to qbt class"""
    return save_state(state_id, self, description, tags)

# Monkey patch the qbt class to add vQRAM functionality
qbt.save_state = _qbt_save_state

# === DEMO AND USAGE EXAMPLES ===

def demo_enhanced_vqram():
    """Demonstrate enhanced vQRAM functionality with QML features"""
    print("=== ENHANCED vQRAM DEMONSTRATION ===")
    
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
    
    # Demonstrate state evolution
    def add_rotation(circuit):
        circuit.ry(0, 0.5).rz(1, 0.3)
    
    evolved_id = evolve_quantum_state("bell_state", add_rotation, "evolved_bell", "Evolved Bell state")
    print(f"Evolved state saved with ID: {evolved_id}")
    
    # Demonstrate QML model storage
    class SimpleQMLModel:
        def __init__(self, num_qubits=3):
            self.num_qubits = num_qubits
            self.weights = np.random.randn(5)
            self.trained = True
            self.circuit_tokens = ["H", "0", "RX", "0", "0.5"]
    
    qml_model = SimpleQMLModel()
    model_config = {"num_qubits": 3, "type": "quantum_linear_regression"}
    model_id = save_quantum_model(qml_model, model_config, "Simple QML Model")
    print(f"QML model saved with ID: {model_id}")
    
    # Demonstrate training history
    training_history = QMLTrainingHistory(model_id)
    for epoch in range(3):
        training_history.add_epoch(
            loss=0.1 * (epoch + 1),
            parameters=np.random.randn(5).tolist(),
            fidelity=0.9 - 0.1 * epoch
        )
    
    history_id = save_training_history(training_history)
    print(f"Training history saved with ID: {history_id}")
    
    # Load and verify everything works
    loaded_model = load_quantum_model(model_id)
    loaded_history = load_training_history(model_id)
    
    print(f"Model loaded successfully: {loaded_model is not None}")
    print(f"History loaded successfully: {loaded_history is not None}")
    print(f"Best loss in history: {loaded_history.best_loss:.4f}")
    
    # Demonstrate state similarity
    similarity = compute_quantum_similarity("bell_state", "evolved_bell")
    print(f"State similarity - Fidelity: {similarity.get('fidelity', 0):.4f}")
    
    # List all content
    states = list_saved_states()
    print(f"All saved states: {states}")
    
    # Get detailed state info
    info = get_state_info("bell_state")
    print(f"Bell state purity: {info.get('purity', 0):.4f}")
    print(f"Bell state lineage: {info.get('lineage', [])}")

if __name__ == "__main__":
    demo_enhanced_vqram()