# cli_entry.py
import sys
import numpy as np
from .qbt import qbt, MATPLOTLIB_AVAILABLE

class SiaCLI:
    def __init__(self):
        self.qbt = qbt(2, explain_steps=True)  # Changed qc to qbt
        self.commands = {
            'help': self.show_help,
            'set': self.set_qubits,
            'demo': self.run_demo,
            'run': self.run_circuit,
            'analyze': self.analyze,
            'bloch': self.plot_bloch,
            'fidelity': self.calculate_fidelity,
            'explain': self.toggle_explain,
            'exit': self.exit_cli,
            'quit': self.exit_cli
        }
    
    def show_help(self, args):
        print("Available Commands:")
        print("  set <N>           - Set number of qubits")
        print("  demo <name>       - Load preset (bell/grover/teleportation)")
        print("  run [log]         - Execute circuit (add 'log' for details)")
        print("  analyze [plot]    - Show results (add 'plot' for histogram)")
        print("  bloch [qubits...] - Plot Bloch spheres")
        print("  fidelity <index>  - Calculate fidelity with basis state")
        print("  explain           - Toggle step explanations")
        print("  help              - Show this help")
        print("  exit/quit         - Exit CLI")
    
    def set_qubits(self, args):
        if len(args) < 1:
            print("Usage: set <number_of_qubits>")
            return
        try:
            n = int(args[0])
            self.qbt = qbt(n, explain_steps=self.qbt.explain_steps)  # Changed qc to qbt
            print(f"✓ Set to {n} qubits. Circuit cleared.")
        except ValueError:
            print("Error: Please enter a valid number")
    
    def run_demo(self, args):
        if len(args) < 1:
            print("Usage: demo <bell|grover|teleportation>")
            return
        self.qbt.demo(args[0])  # Changed qc to qbt
    
    def run_circuit(self, args):
        log = 'log' in args
        print("\n--- Executing Circuit ---")
        self.qbt.run(log_state_changes=log)  # Changed qc to qbt
    
    def analyze(self, args):
        plot = 'plot' in args and MATPLOTLIB_AVAILABLE
        self.qbt.analyze(plot=plot)  # Changed qc to qbt
    
    def plot_bloch(self, args):
        if not MATPLOTLIB_AVAILABLE:
            print("Error: Matplotlib not available")
            return
        try:
            target_qubits = [int(q) for q in args] if args else None
            self.qbt.plot_bloch(target_qubits=target_qubits)  # Changed qc to qbt
        except ValueError:
            print("Usage: bloch [qubit1 qubit2 ...]")
    
    def calculate_fidelity(self, args):
        if len(args) < 1:
            print("Usage: fidelity <state_index>")
            return
        try:
            target_index = int(args[0])
            target_vec = np.zeros(self.qbt.max_dim, dtype=complex)  # Changed qc to qbt
            target_vec[target_index] = 1.0
            F = self.qbt.fidelity_with_state(target_vec)  # Changed qc to qbt
            basis_state = bin(target_index)[2:].zfill(self.qbt.num_qubits)  # Changed qc to qbt
            print(f"✓ Fidelity with |{basis_state}⟩: {F:.4f}")
        except (ValueError, IndexError):
            print("Error: Invalid state index")
    
    def toggle_explain(self, args):
        self.qbt.explain_steps = not self.qbt.explain_steps  # Changed qc to qbt
        status = "ON" if self.qbt.explain_steps else "OFF"  # Changed qc to qbt
        print(f"✓ Step explanations: {status}")
    
    def exit_cli(self, args):
        print("Goodbye!")
        sys.exit(0)
    
    def run(self):
        print("\n--- ⚛️ Sia Quantum Simulator CLI ---")
        print("Type 'help' for commands, 'exit' to quit")
        
        while True:
            try:
                user_input = input(f"sia_qbt ({self.qbt.num_qubits}q)> ").strip()  # Changed qc to qbt
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"Unknown command: {command}. Type 'help'.")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")

def run_interactive_cli():
    cli = SiaCLI()
    cli.run()

if __name__ == '__main__':
    run_interactive_cli()