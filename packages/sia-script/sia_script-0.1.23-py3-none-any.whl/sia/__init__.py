# sia/__init__.py
from .ntt import ntt
from .qbt import qbt as qbt_class
from .chi import chi as ChiClass
from .vqram import VirtualQRAM, get_vqram, save_state, load_state, load_circuit, list_states


chi = ChiClass(verbose=False)

qbt = qbt_class

_vqram_instance = None

def get_vqram_instance():
    """Get the global vQRAM instance"""
    global _vqram_instance
    if _vqram_instance is None:
        _vqram_instance = VirtualQRAM()
    return _vqram_instance

vqram = get_vqram_instance()

__all__ = [
    'ntt',
    'qbt', 
    'chi',
    'VirtualQRAM',
    'vqram',
    'get_vqram',
    'save_state',
    'load_state',
    'load_circuit',
    'list_states',
]