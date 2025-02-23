#i realy hope you get me some Donation for the Quantum project_ 1NEJcwfcEm7Aax8oJNjRUnY3hEavCjNrai /////
from qiskit import QuantumCircuit, transpile, assemble
from qiskit.circuit.controlflow.break_loop import BreakLoopPlaceholder
from qiskit.circuit.library import ZGate, MCXGate
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit.primitives import SamplerResult
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from collections import Counter
from Crypto.Hash import RIPEMD160, SHA256  # Import from pycryptodome
from ecdsa import SigningKey, SECP256k1
from qiskit_ibm_runtime import Options
from qiskit.primitives import Sampler
from bitarray import bitarray
from qiskit_ibm_runtime import SamplerV2, EstimatorV2, Options, OptionsV2, Session
from qiskit.quantum_info import PauliList, SparsePauliOp, Statevector, Operator
from qiskit.circuit import Parameter
#from qiskit_aer.primitives import SamplerV2  # for simulator
#from qiskit_ibm_runtime import SamplerV2 as real_sampler  # for hardware
#from qiskit_algorithms.optimizers import AmplificationProblem, CustomCircuitOracle
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator, Aer
from qiskit_ibm_runtime import Estimator
from qiskit.circuit.library import RYGate, GroverOperator
import random
import time
import hashlib
import base58
import numpy as np
import math
from math import ceil, log2
#from qiskit.providers.ibmq import IBMQ
from qiskit.visualization import plot_histogram, plot_distribution
import matplotlib.pyplot as plt
from qiskit import QuantumRegister, ClassicalRegister, AncillaRegister
from qiskit.circuit.library import QFT, Arithmetic
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_algorithms.amplitude_amplifiers.grover import GroverResult
from qiskit.algorithms import Shor
from qiskit.utils import QuantumInstance

# Load IBMQ account using QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel='ibm_quantum',
    token='dde8ed432a4c90c9c6f294e1b8b37338aed79f7545c4870397c65afce7d38b8d0501de702d0799207710adb651b0816f08d221359c89ec62deb3c1d369f1efe7',  # Replace with your actual token
    instance='ibm-q/open/main',
    overwrite=True,
    set_as_default=True
)

# Load the service
service = QiskitRuntimeService()

# Elliptic Curve Parameters (Secp256k1)
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
g_x = 0x3f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3
g_y = 0x393e3b1c529624e56840acbb10243ec9e0cfe99c3cffe1c87537b735bbba2d2f
G = (0x3f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3,
     0x393e3b1c529624e56840acbb10243ec9e0cfe99c3cffe1c87537b735bbba2d2f)
Px = 0xb67cb6edeabc0c8b927c9ea327628e7aa63e2d52
Gx = 0x3f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3
Gy = 0x393e3b1c529624e56840acbb10243ec9e0cfe99c3cffe1c87537b735bbba2d2f

# Public Key
public_key_hex = "033f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3"
x_Q = int(public_key_hex[2:], 16)

# Modular Inverse Function
def mod_inverse(a, p):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        ratio = high // low
        nm, new_low = hm - lm * ratio, high - low * ratio
        lm, low, hm, high = nm, new_low, lm, low
    return lm % p

# Elliptic Curve Point Addition
def point_addition(x1, y1, x2, y2, p):
    if x1 == x2 and y1 == y2:
        return point_doubling(x1, y1, p)
    lam = ((y2 - y1) * mod_inverse(x2 - x1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3

# Elliptic Curve Point Doubling
def point_doubling(x1, y1, p):
    lam = ((3 * x1 * x1) * mod_inverse(2 * y1, p)) % p
    x3 = (lam * lam - 2 * x1) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3

# Scalar Multiplication
def scalar_multiplication(k, x, y, p):
    x_res, y_res = x, y
    k_bin = bin(k)[2:]
    for bit in k_bin[1:]:
        x_res, y_res = point_doubling(x_res, y_res, p)
        if bit == '1':
            x_res, y_res = point_addition(x_res, y_res, x, y, p)
    return x_res, y_res

# Quantum Circuit for ECDLP using QPE + QFT
def quantum_circuit(num_qubits, Gx, Gy, Px, p):
    # Quantum registers
    q_x = QuantumRegister(num_qubits, 'x')  # Register for the private key
    anc = QuantumRegister(1, 'ancilla')    # Ancilla qubit
    c = ClassicalRegister(num_qubits + 1, 'c')  # Classical register for measurement
    qc = QuantumCircuit(q_x, anc, c)

    # Initialize superposition
    qc.h(q_x)
    qc.h(anc)

    # Quantum Phase Estimation (QPE) for ECDLP
    for i in range(num_qubits):
        # Controlled point doubling: Q = [2^i]G
        Qx, Qy = scalar_multiplication(2**i, Gx, Gy, p)

        # Controlled point addition: Q = Q + [2^i]G if the i-th bit of k is 1
        qc.cswap(anc, q_x[i], q_x[i])  # Controlled swap for addition

        # Compare Qx to Px (the target public key)
        qc.cx(q_x[i], anc)  # Controlled NOT for equality check

    # Apply inverse QFT
    qc.append(QFT(num_qubits, do_swaps=True).inverse(), q_x)

    # Measurement
    qc.measure(q_x, c[:num_qubits])
    qc.measure(anc[0], c[num_qubits])

    return qc

def private_key_to_compressed_address(private_key_hex):
    """Convertit une clé privée en une adresse Bitcoin compressée."""
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.verifying_key
    public_key_bytes = vk.to_string()
    x_coord = public_key_bytes[:32]
    y_coord = public_key_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y_coord, 'big') % 2 == 0 else b'\x03'
    compressed_public_key = prefix + x_coord

    sha256_pk = hashlib.sha256(compressed_public_key).digest()
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_pk)
    hashed_public_key = ripemd160.digest()

    network_byte = b'\x00' + hashed_public_key
    sha256_first = hashlib.sha256(network_byte).digest()
    sha256_second = hashlib.sha256(sha256_first).digest()
    checksum = sha256_second[:4]
    binary_address = network_byte + checksum
    return base58.b58encode(binary_address).decode('utf-8')

# Fonction pour convertir une clé publique en hachage de clé publique (SHA256 -> RIPEMD160)
def public_key_to_public_key_hash(public_key_hex):    
    try:
        # Étape 1 : Effectuer SHA-256 sur la clé publique
        sha256_hash = SHA256.new(bytes.fromhex(public_key_hex)).digest()
        
        # Étape 2 : Effectuer RIPEMD-160 sur le résultat de SHA-256 en utilisant Cryptodome
        ripemd160 = RIPEMD160.new()  # Utilisation de RIPEMD160 de Cryptodome
        ripemd160.update(sha256_hash)
        ripemd160_hash = ripemd160.digest()
        
        # Retourner le hachage de la clé publique en format hexadécimal
        return ripemd160_hash.hex()
    
    except ValueError as e:
        raise ValueError(f"Entrée invalide pour la clé publique hex : {e}")

# Fonction pour convertir un binaire en hexadécimal
def binary_to_hex(bin_key):
    bin_key = bin_key.zfill(128)  # Assurer un remplissage de 128 bits
    return hex(int(bin_key, 2))[2:].zfill(64)

# Convertir une chaîne binaire en hexadécimal
def binary_to_hex(bin_str):
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(64)  #  # Ensure the hex string is 64 characters (32 bytes)

# Get the top 10 most frequent results
def get_top_10_frequent(counts):
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top_10_counts = sorted_counts[:10]
    print(f"Top 10 most frequent counts: {top_10_counts}")
    return [int(bitstring, 2) for bitstring, _ in top_10_counts]

# Retrieve job result and verify valid private keys
def retrieve_job_result(job_id, target_address, num_qubits):
    print(f"Retrieving job result for job ID: {job_id}...")
    service = QiskitRuntimeService()

    try:
        # Retrieve job result from the quantum device
        job = service.job(job_id)
        job_result = job.result()
        print(f"Job result retrieved for job ID {job_id}")
    except Exception as e:
        print(f"Error retrieving job result: {e}")
        return None, None

    try:
        # Access measurement results (binary strings like '010101')
        result = job.result()
        counts = result[0].data.c.get_counts()
        print("Counts retrieved from job:", counts)

        print("Retrieving the most frequent results...")
        private_key_candidates = get_top_10_frequent(counts)
        print("Top 10 most frequent counts from The Quantum Circuit:", private_key_candidates)

        # Verify each binary result for a valid private key
        for bin_key, count in counts.items():
            bin_key = bin_key.strip()

            # Ensure the key is exactly 18 bits
            if len(bin_key) < num_qubits:
                bin_key = bin_key.ljust(num_qubits, '0')
            elif len(bin_key) > num_qubits:
                bin_key = bin_key[:num_qubits]

            print(f"\nVerifying binary key (first 18 bits): {bin_key} with length {len(bin_key)}")
            print(f"Key count: {count}")

            # Convert binary string to hexadecimal
            private_key_hex = binary_to_hex(bin_key)
            if private_key_hex is None:
                continue  # Skip if conversion failed

            # Convert to compressed Bitcoin address
            compressed_address = private_key_to_compressed_address(private_key_hex)

            # Verify if the private key produces the target Bitcoin address
            if compressed_address == target_address:
                print(f"Valid private key found: {private_key_hex}")

                # Save the valid private key and address to boom.txt
                with open('boom.txt', 'a') as file:
                    file.write(f"Private Key: {private_key_hex}\n")
                    file.write(f"Compressed Address: {compressed_address}\n\n")

                return private_key_hex, compressed_address

        print("No matching private key found.")
        return None, None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

# Plot histogram of measurement results
def plot_result_histogram(counts):
    plot_histogram(counts)
    labels, values = zip(*counts.items())  # Unpack the counts dictionary
    if isinstance(labels[0], str) and all(set(label).issubset({'0', '1'}) for label in labels):
        hex_labels = [binary_to_hex(label) for label in labels]
    else:
        hex_labels = labels
    
    plt.bar(range(len(values)), values, tick_label=hex_labels)
    plt.xlabel('Private Keys (Hex)' if isinstance(hex_labels[0], str) else 'Private Key Candidates')
    plt.ylabel('Counts')
    plt.title('Measurement Counts Histogram')
    plt.tight_layout()
    plt.show()

def plot_results_histogram(counts):
    labels, values = zip(*counts.items())
    hex_labels = [binary_to_hex(label) for label in labels]
    plt.bar(range(len(values)), values, tick_label=hex_labels)
    plt.xlabel('Private Keys (Hex)')
    plt.ylabel('Counts')
    plt.title('Measurement Counts Histogram')
    plt.xticks(rotation=90)
    plt.show()

# Main Function
def main():
    min_range = 0x10000
    max_range = 0x1FFFF
    num_qubits = int(np.ceil(np.log2(max_range))) + 1  # +1 for ancilla qubit
    target_address = "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm"
    public_key_hex = "033f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3"
    x_Q = int(public_key_hex[2:], 16)
    keyspace_size = max_range - min_range + 1
    print(f"Taille de l'espace de clés calculée : {keyspace_size}")
    print(f"Number of Qubits : {num_qubits}")

    # Initialize Qiskit Runtime Service
    service = QiskitRuntimeService()
    available_backends = service.backends()
    backend = service.backend('ibm_sherbrooke')
    print(f"Selected backend: {backend.name}")

    while True:
        # Create and run the quantum circuit
        print(f"\nInitializing circuit with {num_qubits} qubits...")
        qc = quantum_circuit(num_qubits, G[0], G[1], x_Q, p)

        print("Quantum Circuit Details:")
        print(qc)
        print(f"Circuit Depth: {qc.depth()}, Circuit Size: {qc.size()}")

        # Transpile and assemble the circuit
        print("Transpiling the quantum circuit...")
        transpiled_circuit = transpile(qc, backend=backend, optimization_level=3)
        print(f"Transpiled circuit depth: {transpiled_circuit.depth()}")

        print("Assembling the circuit into a Qobj...")
        qobj = assemble(transpiled_circuit)
        print("Qobj assembled successfully.")

        # Submit the job to the backend
        print("Submitting the job to the backend...")
        sampler = SamplerV2(backend)
        job = sampler.run([transpiled_circuit], shots=8192)
        job_id = job.job_id()
        print(f"Job submitted. Job ID: {job_id}")

        # Wait for results
        print("Waiting for results...")
        result = job.result()
        counts = result[0].data.c.get_counts()
        print("Results received.")
        print("Measurement Results:")
        print(counts)

        # Plot the histogram of results
        print("Plotting result histogram...")
        plot_histogram(counts)
        plot_results_histogram(counts)
        plot_result_histogram(counts)    
        plot_histogram(counts, title="Measurement Results Distribution")
        plt.show()
  
        # plot_distribution(counts, legend=["Ibm Brisbane - Quantum ECDLP Solver"])
        print("Plotting result distributions...")
        plot_distribution(counts, legend=["Ibm Sherbrooke - Quantum ECDLP Solver"])

        # Post-process results to find the private key
        private_key_candidates = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)[:10]
        print("Top candidates:", private_key_candidates)

        found_key = None
        for candidate in private_key_candidates:
            try:
                key_bin = candidate[:-1]  # Exclude the ancilla qubit
                key_int = int(key_bin, 2)
                if key_int < min_range or key_int > max_range:
                    continue
                computed_x, _ = scalar_multiplication(key_int, G[0], G[1], p)
                if computed_x == x_Q:
                    found_key = key_int
                    print(f"\nVALID KEY FOUND: {hex(found_key)}")
                    with open("boom.txt", "a") as file:
                        file.write(f"\nPrivate Key: {found_key}\n")
                        file.write(f"HEX: {hex(found_key)}\n")
                        file.write(f"DEC: {found_key}\n")
                    print("Private key saved to boom.txt")
                    break
            except Exception as e:
                print(f"Error processing candidate {candidate}: {str(e)}")
        else:
            print("No valid key found in this batch. Resubmitting job...")
            continue  # Restart the loop if no key is found

        # Retrieve and verify job results
        found_key, compressed_address = retrieve_job_result(job_id, target_address, num_qubits)
        if found_key:
            print("\nSUCCESS! Private key:")
            print(f"Found matching private key: {found_key}")
            print(f"HEX: {hex(found_key)}")
            print(f"DEC: {found_key}")
        # Save the results to boom.txt
        with open("boom.txt", "w") as file:
            file.write("Measurement Results:\n")
            for bitstring, count in counts.items():
                file.write(f"{bitstring}: {count}\n")
        print("Results saved to boom.txt")
        break  # Exit the loop if a valid key is found
    else:
        print("\nFailed to find private key. Resubmitting job...")

if __name__ == "__main__":
    main()
