// OpenQASM 2.0
include "qelib1.inc";

// Define the quantum circuit
qreg q[256]; // Quantum register with 256 qubits
creg c[256]; // Classical register with 256 bits

// Apply Hadamard gate to each qubit to put them in superposition
for (int i = 0; i < 256; i++) {
    h q[i];
}

// Measure the qubits
measure q -> c;
