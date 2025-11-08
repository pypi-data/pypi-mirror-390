# sia/qbt.py: The Core Quantum Simulator Library Module (Import-Safe)

import numpy as np
from scipy.linalg import expm
from math import pi as PI
from functools import reduce
import sys

# Attempt to import Matplotlib (Optional Dependency)
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    
# --- I. CORE CONSTANTS AND MATRICES ---
I = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
T = np.array([[1, 0], [0, np.exp(1j * PI / 4)]], dtype=complex)
T_DAG = T.conj().T
GATE_MAP = {'I': I, 'X': X, 'Y': Y, 'Z': Z, 'H': H, 'S': S, 'T': T, 'TDAG': T_DAG}

# --- II. CORE MATH & UTILITIES ---

def kron_n(ops):
    """Kronecker product of a list of 2x2 (or NxN) operators."""
    return reduce(lambda a, b: np.kron(a, b), ops)

def _renormalize_rho(rho):
    """Ensures Tr(rho) = 1 for numerical stability."""
    tr = np.trace(rho)
    if abs(tr - 1.0) > 1e-10 and tr != 0: return rho / tr
    return rho

def partial_trace(rho, keep, num_qubits):
    """Computes the reduced density matrix by tracing out specified qubits."""
    if not keep: return np.array([[1.0]], dtype=complex)
    
    qubit_dims = [2] * num_qubits
    tensor_shape = tuple(qubit_dims + qubit_dims)
    reduced_rho = rho.reshape(tensor_shape) # Reshape 2^N x 2^N to 2x2x...x2 (2N dimensions)
    
    trace_indices = [i for i in range(num_qubits) if i not in keep]
    
    # Create pairs of axes to trace out: (bra_idx, ket_idx)
    trace_axes = [(i, i + num_qubits) for i in trace_indices]
    
    # Sort by the *ket* (highest) index in descending order. 
    # This minimizes the re-indexing complexity when tracing iteratively.
    trace_pairs = sorted(trace_axes, key=lambda p: p[1], reverse=True)
    
    removed_axes = set() # Set to track which original axis indices have been traced

    # Iteratively apply np.trace, adjusting the axis indices dynamically
    for ax_bra_orig, ax_ket_orig in trace_pairs:
        
        # 1. Calculate the current index for the 'bra' axis
        # (Original index - number of axes removed before it)
        removed_before_bra = len([ax for ax in removed_axes if ax < ax_bra_orig])
        current_ax_bra = ax_bra_orig - removed_before_bra

        # 2. Calculate the current index for the 'ket' axis
        removed_before_ket = len([ax for ax in removed_axes if ax < ax_ket_orig])
        current_ax_ket = ax_ket_orig - removed_before_ket
        
        # Apply the trace operation using the current indices
        reduced_rho = np.trace(reduced_rho, axis1=current_ax_bra, axis2=current_ax_ket)
        
        # Mark the original axes as removed for the next iteration's calculation
        removed_axes.add(ax_bra_orig)
        removed_axes.add(ax_ket_orig)

    final_dim = 2**len(keep)
    return reduced_rho.reshape((final_dim, final_dim))

# --- III. GATE & CHANNEL APPLICATION ---

def apply_single_qubit_gate(rho, U, target, num_qubits):
    ops = [U if q == target else I for q in range(num_qubits)]
    U_full = kron_n(ops)
    rho_new = U_full @ rho @ U_full.conj().T
    return _renormalize_rho(rho_new), U_full

def apply_controlled_gate(rho, U_target, control, target, num_qubits):
    P0 = np.array([[1, 0], [0, 0]], dtype=complex)
    P1 = np.array([[0, 0], [0, 1]], dtype=complex)
    ops0 = []; ops1 = []
    for q in range(num_qubits):
        if q == control: ops0.append(P0); ops1.append(P1)
        elif q == target: ops0.append(I); ops1.append(U_target)
        else: ops0.append(I); ops1.append(I)
    CU_full = kron_n(ops0) + kron_n(ops1)
    rho_new = CU_full @ rho @ CU_full.conj().T
    return _renormalize_rho(rho_new), CU_full

def _apply_kraus_channel(rho, channel_qubit, kraus_ops, num_qubits):
    """Generic Kraus operator application function."""
    rho_new = np.zeros_like(rho)
    for K_q in kraus_ops:
        ops_K = [K_q if idx == channel_qubit else I for idx in range(num_qubits)]
        K_full = kron_n(ops_K)
        rho_new += (K_full @ rho @ K_full.conj().T)
    return _renormalize_rho(rho_new)

# Noise Channels
def apply_bit_flip_channel(rho, q, p, num_qubits):
    K0 = np.sqrt(1 - p) * I; K1 = np.sqrt(p) * X
    return _apply_kraus_channel(rho, q, [K0, K1], num_qubits)
def apply_phase_flip_channel(rho, q, p, num_qubits):
    K0 = np.sqrt(1 - p) * I; K1 = np.sqrt(p) * Z
    return _apply_kraus_channel(rho, q, [K0, K1], num_qubits)
def apply_depolarizing_channel(rho, q, p, num_qubits):
    K0 = np.sqrt(1 - 3 * p / 4) * I; K1 = np.sqrt(p / 4) * X
    K2 = np.sqrt(p / 4) * Y; K3 = np.sqrt(p / 4) * Z
    return _apply_kraus_channel(rho, q, [K0, K1, K2, K3], num_qubits)

def apply_amplitude_damping_channel(rho, q, p, num_qubits):
    """Models energy decay (T1). Decays towards the ground state |0>."""
    K0 = np.array([[1, 0], [0, np.sqrt(1 - p)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(p)], [0, 0]], dtype=complex)
    return _apply_kraus_channel(rho, q, [K0, K1], num_qubits)

def apply_phase_damping_channel(rho, q, p, num_qubits):
    """Models decoherence (T2) without energy decay."""
    K0 = np.array([[1, 0], [0, np.sqrt(1 - p)]], dtype=complex)
    K1 = np.array([[0, 0], [0, np.sqrt(p)]], dtype=complex)
    return _apply_kraus_channel(rho, q, [K0, K1], num_qubits)

# --- IV. QUANTUM CIRCUIT CLASS ---

class qbt:
    """
    A Dual-State Quantum Simulator for educational purposes.
    Supports Statevector (pure) and Density Matrix (mixed/noisy) evolution.
    """
    def __init__(self, num_qubits, explain_steps=False):
        if num_qubits < 1 or num_qubits > 9:
            raise ValueError("Number of qubits must be between 1 and 9 for this minimalist simulator.")

        self.num_qubits = num_qubits
        self.max_dim = 2 ** num_qubits
        self.circuit_tokens = []
        self.explain_steps = explain_steps
        self.step_counter = 1
        self.statevector = np.zeros(self.max_dim, dtype=complex); self.statevector[0] = 1.0
        self.rho = np.outer(self.statevector, self.statevector.conj())
        
        self.ROT_MAP = {
            'RX': lambda theta: expm(-1j * theta / 2 * X),
            'RY': lambda theta: expm(-1j * theta / 2 * Y),
            'RZ': lambda theta: expm(-1j * theta / 2 * Z)
        }

    # --- Builder Methods ---
    def _add(self, op, *args):
        self.circuit_tokens.extend([op] + [str(arg) for arg in args])
        return self
    
    def _log_step(self, message):
        if self.explain_steps: print(f"[{self.step_counter:02d}] {message}")
        self.step_counter += 1

    def h(self, q): self._log_step(f"Hadamard (H) on Qubit {q}."); return self._add("H", q)
    def x(self, q): self._log_step(f"Pauli-X (X) on Qubit {q}."); return self._add("X", q)
    def cnot(self, c, t): self._log_step(f"CNOT: C{c} -> T{t}."); return self._add("CX", c, t)
    def cz(self, c, t): self._log_step(f"CZ: C{c} -> T{t} phase flip."); return self._add("CZ", c, t)
    def rx(self, q, theta): self._log_step(f"RX rotation of {theta:.3f} on Qubit {q}."); return self._add("RX", q, theta)
    def crx(self, c, t, theta): self._log_step(f"CRX: C{c} -> T{t} rotation."); return self._add("CRX", c, t, theta)
    def t(self, q): self._log_step(f"T gate (Pi/4 phase shift) on Qubit {q}."); return self._add("T", q)
    def tdag(self, q): self._log_step(f"T-dagger gate (-Pi/4 phase shift) on Qubit {q}."); return self._add("TDAG", q)
    
    def bf(self, q, p): self._log_step(f"Bit-Flip (BF) noise on Qubit {q} p={p:.3f}."); return self._add("BF", q, p)
    def pf(self, q, p): self._log_step(f"Phase-Flip (PF) noise on Qubit {q} p={p:.3f}."); return self._add("PF", q, p)
    def dp(self, q, p): self._log_step(f"Depolarizing (DP) noise on Qubit {q} p={p:.3f}."); return self._add("DP", q, p)
    def ad(self, q, p): self._log_step(f"Amplitude Damping (AD) on Qubit {q} p={p:.3f}. Simulating T1 decay."); return self._add("AD", q, p)
    def pd(self, q, p): self._log_step(f"Phase Damping (PD) on Qubit {q} p={p:.3f}. Simulating T2 decoherence."); return self._add("PD", q, p)
    def measure(self): self._log_step("Final Measurement Marker."); return self._add("M")

    # --- Preset Circuits Method ---
    def demo(self, name):
        """Loads and builds a famous preset quantum circuit."""
        name = name.lower()
        self.circuit_tokens = []; self.step_counter = 1
        
        if name == 'bell':
            self.num_qubits = 2; print(f"\n--- Building Bell State ($\Phi^+$) ---")
            self.h(0).cnot(0, 1).measure()
        elif name == 'grover':
            self.num_qubits = 3; print(f"\n--- Building 3-Qubit Grover Search ---")
            self.h(0).h(1).h(2); self._log_step("Applying Oracle..."); self.x(1).cz(0, 1).cz(1, 2).x(1) 
            self._log_step("Applying Diffusion Operator..."); self.h(0).h(1).h(2).x(0).x(1).x(2)
            self.cz(0, 1).cz(1, 2); self.x(0).x(1).x(2).h(0).h(1).h(2).measure()
        elif name == 'teleportation':
            self.num_qubits = 3; print(f"\n--- Building Quantum Teleportation Protocol ---")
            self.h(0); self.h(1).cnot(1, 2); self.cnot(0, 1).h(0).measure()
        else: print(f"Error: Demo '{name}' not found.")
        return self
    
    # --- Analysis Helpers ---
    def get_reduced_density_matrix(self, keep_qubits):
        return partial_trace(self.rho, keep_qubits, self.num_qubits)
    
    def bloch_vector(self, q):
        if q < 0 or q >= self.num_qubits: raise ValueError("Qubit index out of range.")
        rho_q = self.get_reduced_density_matrix([q])
        exp_x = np.trace(rho_q @ X).real
        exp_y = np.trace(rho_q @ Y).real
        exp_z = np.trace(rho_q @ Z).real
        return (float(np.round(exp_x, 6)), float(np.round(exp_y, 6)), float(np.round(exp_z, 6)))

    def fidelity_with_state(self, target_state):
        """Calculates the Fidelity F between the final density matrix and an ideal target state vector."""
        if isinstance(target_state, np.ndarray) and target_state.ndim == 1:
            if target_state.size != self.max_dim:
                 raise ValueError("Target state dimension mismatch.")
            overlap = target_state.conj().T @ self.rho @ target_state
            return np.sqrt(np.clip(np.real(overlap), 0, 1))
        else:
            raise TypeError("Target must be a NumPy statevector (1D array).")

    def probability_of_state(self, basis_state_string):
        """Returns the probability of measuring a specific basis state (e.g., '101')."""
        if len(basis_state_string) != self.num_qubits:
            raise ValueError(f"State string must have {self.num_qubits} qubits.")
        try:
            index = int(basis_state_string, 2)
        except ValueError:
            raise ValueError("Basis state string must contain only '0's and '1's.")
            
        diag_rho = np.real(np.diag(self.rho))
        return np.clip(diag_rho[index], 0.0, 1.0)

    # --- Execution ---
    def run(self, log_state_changes=False):
        """Executes the stored quantum circuit and returns the analysis summary."""
        self.statevector = np.zeros(self.max_dim, dtype=complex); self.statevector[0] = 1.0
        self.rho = np.outer(self.statevector, self.statevector.conj())
        tokens = self.circuit_tokens[:]; i = 0
        
        if log_state_changes: print(f"\n--- 🔄 State Evolution Log (Dim: {self.max_dim}x{self.max_dim}) ---")

        while i < len(tokens):
            op = tokens[i].upper(); is_unitary = False; U_full = None
            
            # Unitary Gates (I, X, Y, Z, H, S, T, TDAG)
            if op in GATE_MAP:
                q = int(tokens[i + 1]); U = GATE_MAP[op]; 
                self.rho, U_full = apply_single_qubit_gate(self.rho, U, q, self.num_qubits); is_unitary = True; i += 2
            
            # Rotation Gates (RX, RY, RZ)
            elif op in self.ROT_MAP:
                q = int(tokens[i + 1]); theta = float(tokens[i + 2]); U = self.ROT_MAP[op](theta)
                self.rho, U_full = apply_single_qubit_gate(self.rho, U, q, self.num_qubits); is_unitary = True; i += 3
            
            # Controlled Gates (CX, CZ, CRX)
            elif op in ['CX', 'CZ', 'CRX']:
                c = int(tokens[i + 1]); t = int(tokens[i + 2])
                if op == 'CX': U_target = X; adv = 3
                elif op == 'CZ': U_target = Z; adv = 3
                else: theta = float(tokens[i + 3]); U_target = self.ROT_MAP['RX'](theta); adv = 4
                self.rho, U_full = apply_controlled_gate(self.rho, U_target, c, t, self.num_qubits); is_unitary = True; i += adv

            # Noise Channels (BF, PF, DP, AD, PD)
            elif op in ['BF', 'PF', 'DP', 'AD', 'PD']:
                q = int(tokens[i + 1]); p = float(tokens[i + 2]); is_unitary = False; i += 3
                if op == 'BF': self.rho = apply_bit_flip_channel(self.rho, q, p, self.num_qubits)
                elif op == 'PF': self.rho = apply_phase_flip_channel(self.rho, q, p, self.num_qubits)
                elif op == 'DP': self.rho = apply_depolarizing_channel(self.rho, q, p, self.num_qubits)
                elif op == 'AD': self.rho = apply_amplitude_damping_channel(self.rho, q, p, self.num_qubits)
                elif op == 'PD': self.rho = apply_phase_damping_channel(self.rho, q, p, self.num_qubits)
            
            # Measurement Marker
            elif op == 'M': is_unitary = False; i += 1
            else: raise ValueError(f"Unknown operation: {op}")

            # Statevector Synchronization
            if is_unitary and self.statevector is not None: self.statevector = U_full @ self.statevector
            if not is_unitary: self.statevector = None 
            if log_state_changes: print(f"[{i}] {op} -> Rho[real]:\n{np.real(self.rho)}")

        return self.analyze()
        
    # --- Analysis & Plotting Methods ---
    def plot_bloch(self, target_qubits=None):
        """Plots the final state of the target qubits on the Bloch sphere."""
        if not MATPLOTLIB_AVAILABLE:
            print("Error: Matplotlib is required for plotting. Please install it.")
            return

        qubits_to_plot = target_qubits if target_qubits is not None else range(self.num_qubits)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title(f'Bloch Sphere Visualization (Qubits: {", ".join(map(str, qubits_to_plot))})')

        # Draw the sphere axes and surface
        u = np.linspace(0, 2 * np.pi, 50); v = np.linspace(0, np.pi, 50)
        x_sphere = np.outer(np.cos(u), np.sin(v)); y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x_sphere, y_sphere, z_sphere, color='b', alpha=0.05, linewidth=0)

        # Labels
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        ax.text(1.1, 0, 0, '|+⟩'); ax.text(-1.1, 0, 0, '|-⟩')
        ax.text(0, 0, 1.1, '|0⟩'); ax.text(0, 0, -1.1, '|1⟩')
        
        # Plot the final Bloch vectors
        for q in qubits_to_plot:
            if 0 <= q < self.num_qubits:
                x, y, z = self.bloch_vector(q)
                ax.quiver(0, 0, 0, x, y, z, color='r', linewidth=2, arrow_length_ratio=0.15)
                ax.scatter([x], [y], [z], color='k', s=50) 
                
        ax.set_xlim([-1, 1]); ax.set_ylim([-1, 1]); ax.set_zlim([-1, 1])
        ax.set_box_aspect([1, 1, 1]); plt.show()


    def analyze(self, plot=False):
        """Prints diagnostics and optionally plots the probability histogram."""
        
        diag_rho = np.real(np.diag(self.rho)); diag_rho = np.clip(diag_rho, 0.0, 1.0)
        rho_probs = diag_rho / diag_rho.sum() if diag_rho.sum() > 0 else diag_rho
        purity = np.trace(self.rho @ self.rho).real
        eigs = np.linalg.eigvals(self.rho); positive_eigs = eigs[eigs > 1e-12].real
        entropy = -np.sum(positive_eigs * np.log2(positive_eigs)) if positive_eigs.size > 0 else 0.0
        
        print("\n--- 🔬 Final State Analysis ---")
        print(f"**Global Purity (Tr(rho^2)): {purity:.4f}** (1.0 = Pure State)")
        print(f"**Entropy (S(rho)):    {entropy:.4f}** (0.0 = Pure State)")
        
        if self.statevector is None:
             print("⚠️ Statevector Invalidation: State is MIXED (Non-unitary operation detected).")
        
        print("\n--- Local Qubit Purity & Bloch Vector ---")
        for q in range(self.num_qubits):
            rho_q = self.get_reduced_density_matrix([q])
            local_purity = np.trace(rho_q @ rho_q).real
            bx, by, bz = self.bloch_vector(q)
            print(f"Qubit {q}: Purity={local_purity:.4f}, Bloch Vector=({bx}, {by}, {bz})")
        
        # Histogram Plotting Logic
        if plot and MATPLOTLIB_AVAILABLE:
            states = [bin(i)[2:].zfill(self.num_qubits) for i in range(self.max_dim)]
            plt.figure(figsize=(10, 6)); bar_width = 0.35; index = np.arange(self.max_dim)
            plt.bar(index, rho_probs, bar_width, label='Noisy Rho (Final)', color='red', alpha=0.6)
            
            if self.statevector is not None:
                sv_probs = np.real(self.statevector.conj() * self.statevector)
                plt.bar(index + bar_width, sv_probs, bar_width, label='Ideal SV (if Pure)', color='blue', alpha=0.6)
                plt.xticks(index + bar_width/2, states, rotation=45, ha='right')
            else:
                 plt.xticks(index, states, rotation=45, ha='right')

            plt.ylabel('Probability'); plt.xlabel('Computational Basis State $|q_{N-1}...q_0\\rangle$')
            plt.title('Final Probability Distribution'); plt.ylim(0, 1)
            plt.legend(); plt.tight_layout(); plt.show()

        return {'purity': purity, 'entropy': entropy}

# --- MAIN EXECUTION ENTRY POINT ---
if __name__ == "__main__":
    # This block is for internal testing/self-check only.
    print("sia.qbt: Running minimal self-test upon direct execution.")
    try:
        qbt_test = qbt(2, explain_steps=False)
        qbt_test.h(0).cnot(0, 1).ad(0, 0.1) # Bell state with amplitude damping
        qbt_test.run()
    except Exception as e:
        print(f"Self-test failed: {e}")
    if not MATPLOTLIB_AVAILABLE:
        print("Note: Matplotlib not available, skipping plot test.")