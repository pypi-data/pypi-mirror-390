import sys
from .qbt import QuantumCircuit, MATPLOTLIB_AVAILABLE
import numpy as np 

def run_interactive_cli():
    """Starts the interactive command-line interface."""
    print("\n--- ⚛️ Sia Quantum Simulator CLI (sia-qsim) ---")
    print("Commands: demo <name>, set <N>, run <log>, fidelity <target_index>, analyze <plot>, bloch <qbits>, exit")
    
    # Initialize with default settings
    qc = QuantumCircuit(1, explain_steps=True)
    
    while True:
        try:
            command = input(f"sia_qbt ({qc.num_qubits}q)> ").strip()
            if not command: continue
            
            parts = command.lower().split()
            op = parts[0]
            
            if op in ['exit', 'quit']: break
            
            elif op == 'help':
                print("Commands: demo <name>, set <N>, run <log>, fidelity <target_state_index>, analyze <plot>, bloch <qbits>, explain, exit")
            
            elif op == 'set':
                if len(parts) < 2: 
                    print("Usage: set <Number of Qubits>")
                    continue
                n = int(parts[1])
                qc = QuantumCircuit(n, explain_steps=qc.explain_steps)
                print(f"Set number of qubits to {n}. Circuit cleared.")
            
            elif op == 'demo':
                if len(parts) < 2: 
                    print("Usage: demo <bell|grover|teleportation>")
                    continue
                qc.demo(parts[1])
            
            elif op == 'run':
                log = 'log' in parts
                print("\n--- Executing Circuit ---")
                qc.run(log_state_changes=log)
            
            elif op == 'analyze':
                plot = 'plot' in parts and MATPLOTLIB_AVAILABLE
                qc.analyze(plot=plot)
                
            elif op == 'bloch':
                if not MATPLOTLIB_AVAILABLE:
                    print("Error: Matplotlib is required for Bloch sphere plotting.")
                    continue
                # Parse specific qubits or plot all
                if len(parts) > 1 and parts[1].lower() != 'plot':
                    try:
                        # Expecting qubit indices separated by spaces/commas (e.g., bloch 0 1)
                        target_qubits = [int(q.strip(',')) for q in parts[1:]]
                        qc.plot_bloch(target_qubits=target_qubits)
                    except ValueError:
                        print("Usage: bloch <qbit_index 1> <qbit_index 2>...")
                else:
                    qc.plot_bloch() # Plot all qubits by default

            elif op == 'fidelity':
                if len(parts) < 2: 
                    print("Usage: fidelity <target_state_index> (e.g., '0' for |00..0> or '1' for |00..1>)")
                    continue
                
                target_index = int(parts[1])
                if target_index < 0 or target_index >= qc.max_dim:
                    print(f"Error: Target index {target_index} out of bounds for {qc.num_qubits} qubits (max index {qc.max_dim - 1}).")
                    continue
                    
                target_vec = np.zeros(qc.max_dim, dtype=complex)
                target_vec[target_index] = 1.0
                
                F = qc.fidelity_with_state(target_vec)
                basis_state_str = bin(target_index)[2:].zfill(qc.num_qubits)
                
                print(f"✅ Fidelity with state |{basis_state_str}⟩ ({target_index}): {F:.4f}")
            
            elif op == 'explain':
                qc.explain_steps = not qc.explain_steps
                print(f"Step-by-step explanation is now {'ON' if qc.explain_steps else 'OFF'}.")

            else:
                print(f"Unknown command: {command}. Type 'help'.")
                
        except IndexError:
            print("Error: Command missing arguments.")
        except (ValueError, TypeError) as e:
            print(f"Error: Invalid argument or state mismatch. {e}")
        except Exception as e:
            print(f"Runtime Error: {e}")

if __name__ == '__main__':
    run_interactive_cli()