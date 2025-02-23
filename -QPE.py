#i realy hope you get me some Donation for the Quantum project_ 1NEJcwfcEm7Aax8oJNjRUnY3hEavCjNrai /////
#Assembling the circuit into a Qobj.../content/01.py:393: DeprecationWarning: The function ``qiskit.compiler.assembler.assemble()`` is deprecated as of qiskit 1.2. It will be removed in the 2.0 release.
#The `Qobj` class and related functionality are part of the deprecated `BackendV1` workflow,  and no longer necessary for `BackendV2`. If a user workflow requires `Qobj` it likely relies on deprecated functionality and should be updated to use `BackendV2`. qobj = assemble(transpiled_circuit)Qobj assembled successfully.

from qiskit import QuantumCircuit, transpile, assemble
from qiskit.circuit.controlflow.break_loop import BreakLoopPlaceholder
from qiskit.circuit.library import ZGate, MCXGate
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit.primitives import SamplerResult
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from collections import Counter
from Crypto.Hash import RIPEMD160, SHA256  # Import from pycryptodome
from ecdsa import SigningKey, SECP256k1
from qiskit_ibm_runtime import SamplerV2, EstimatorV2, Options, OptionsV2, Session
from qiskit.quantum_info import PauliList, SparsePauliOp, Statevector, Operator
from qiskit.circuit import Parameter
#from qiskit_aer.primitives import SamplerV2  # for simulator
#from qiskit_ibm_runtime import SamplerV2 as real_sampler  # for hardware
from qiskit.circuit.library import RYGate
from qiskit.visualization import plot_histogram, plot_distribution
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_algorithms.amplitude_amplifiers.grover import GroverResult
#from qiskit.providers.ibmq.job import Job
from Crypto.PublicKey import ECC
from qiskit_ibm_runtime import Options
from qiskit.primitives import Sampler
from bitarray import bitarray
#from qiskit_aer.primitives import SamplerV2  # for simulator
#from qiskit_ibm_runtime import SamplerV2 as real_sampler  # for hardware
#from qiskit_algorithms.optimizers import AmplificationProblem, CustomCircuitOracle
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator, Aer
from qiskit_ibm_runtime import Estimator
from qiskit.circuit.library import RYGate, GroverOperator
from math import ceil, log2
#from qiskit.providers.ibmq import IBMQ
import matplotlib.pyplot as plt
from qiskit import QuantumRegister, ClassicalRegister, AncillaRegister
import numpy as np
import random
import time
import hashlib
import base58
import math

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
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x3f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3,
     0x393e3b1c529624e56840acbb10243ec9e0cfe99c3cffe1c87537b735bbba2d2f)

# Public Key
public_key_hex = "033f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3"
x_Q = int(public_key_hex[2:], 16)

def gcd(a, b):
    """Computes the greatest common divisor of a and b using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a

def mod_exp(base, exp, mod):
    """Performs modular exponentiation: (base^exp) % mod."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:  # If exp is odd
            result = (result * base) % mod
        exp = exp >> 1  # Divide exp by 2
        base = (base * base) % mod
    return result

def find_period(a, N):
    """Finds the period of a^x % N for a given base a."""
    x = a
    r = 1
    while x != 1:
        x = (x * a) % N
        r += 1
        if r > N:  # If no period found
            return None
    return r

def shor_algorithm(N):
    """Classical implementation of Shor's factoring algorithm."""
    if N % 2 == 0:
        return 2  # 2 is a factor of all even numbers
    
    # Try random values of a
    for _ in range(100):  # Try 100 different values for a
        a = random.randint(2, N-1)
        
        # Check if gcd(a, N) is non-trivial
        common_divisor = gcd(a, N)
        if common_divisor > 1:
            return common_divisor
        
        # Find the period of a^x % N
        r = find_period(a, N)
        if r and r % 2 == 0:
            # Find factors using the period
            factor1 = gcd(mod_exp(a, r//2, N) - 1, N)
            factor2 = gcd(mod_exp(a, r//2, N) + 1, N)
            if factor1 > 1 and factor1 < N:
                return factor1
            if factor2 > 1 and factor2 < N:
                return factor2
    
    return None  # If no factor is found after 100 attempts

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

def scalar_multiplication(k, x, y, p):
    x_res, y_res = x, y
    k_bin = bin(k)[2:]
    for bit in k_bin[1:]:
        x_res, y_res = point_doubling(x_res, y_res, p)
        if bit == '1':
            x_res, y_res = point_addition(x_res, y_res, x, y, p)
    return x_res, y_res

def point_doubling(x, y, p):
    # Elliptic curve point doubling formula
    s = (3 * x**2) * pow(2 * y, -1, p) % p
    x_res = (s**2 - 2 * x) % p
    y_res = (s * (x - x_res) - y) % p
    return x_res, y_res

def point_addition(x1, y1, x2, y2, p):
    # Elliptic curve point addition formula
    if x1 == x2 and y1 == y2:
        return point_doubling(x1, y1, p)
    s = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x_res = (s**2 - x1 - x2) % p
    y_res = (s * (x1 - x_res) - y1) % p
    return x_res, y_res

##private_key = solve_ecdlp(p, x_Q)
def solve_ecdlp(p, x_Q):
    """Solves ECDLP using Shor's algorithm."""
    # Step 1: Factor the modulus p using Shor's algorithm
    private_key = shor_algorithm(p)
    if private_key is None:
        print("Failed to factor modulus p.")
        return None
    return private_key

# Function to convert private key to compressed Bitcoin address
def private_key_to_compressed_address(private_key_hex):
    print(f"Converting private key {private_key_hex} to Bitcoin address...")
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.verifying_key
    public_key_bytes = vk.to_string()
    x_coord = public_key_bytes[:32]
    y_coord = public_key_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y_coord, 'big') % 2 == 0 else b'\x03'
    compressed_public_key = prefix + x_coord

    sha256_pk = hashlib.sha256(compressed_public_key).digest()
    ripemd160 = RIPEMD160.new()  # Using Cryptodome's RIPEMD160
    ripemd160.update(sha256_pk)
    hashed_public_key = ripemd160.digest()

    network_byte = b'\x00' + hashed_public_key
    sha256_first = hashlib.sha256(network_byte).digest()
    sha256_second = hashlib.sha256(sha256_first).digest()
    checksum = sha256_second[:4]

    binary_address = network_byte + checksum
    bitcoin_address = base58.b58encode(binary_address).decode('utf-8')
    print(f"Generated Bitcoin address: {bitcoin_address}")
    return bitcoin_address   

# Function to convert public key to Public-Key-Hash (SHA256 -> RIPEMD160)
def public_key_to_public_key_hash(public_key_hex):    
    try:
        # Step 1: Perform SHA-256 on the public key
        sha256_hash = SHA256.new(bytes.fromhex(public_key_hex)).digest()
        
        # Step 2: Perform RIPEMD-160 on the result of SHA-256 using Cryptodome
        ripemd160 = RIPEMD160.new()  # Using Cryptodome's RIPEMD160
        ripemd160.update(sha256_hash)
        ripemd160_hash = ripemd160.digest()
        
        # Return the Public-Key-Hash in hexadecimal format
        return ripemd160_hash.hex()
    
    except ValueError as e:
        raise ValueError(f"Invalid input for public key hex: {e}")

# Get the top 10 most frequent results
def get_top_10_frequent(counts):
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top_10_counts = sorted_counts[:10]
    print(f"Top 10 most frequent counts: {top_10_counts}")
    return [int(bitstring, 2) for bitstring, _ in top_10_counts]

# Function to convert binary to hex
def binary_to_hex(bin_key):
    bin_key = bin_key.zfill(128)  # Ensure 128-bit padding
    return hex(int(bin_key, 2))[2:].zfill(64)

# Convertir une chaîne binaire en hexadécimal
def binary_to_hex(bin_str):
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(64)  # Remplir la chaîne hex pour s'assurer qu'elle fait 64 caractères (32 octets)

def retrieve_job_result(job_id, target_address, quantum_registers):
    """Retrieve job results and check for valid private keys."""
    target_address = "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm"
    print(f"Retrieving job result for job ID: {job_id}...")
    service = QiskitRuntimeService()
    quantum_registers = 20  # Use 20 qubits for the search
    try:
        # Retrieve job result from the quantum device
        job = service.job(job_id)
        job_result = job.result()
        print(f"Job result retrieved for job ID {job_id}")
    except Exception as e:
        print(f"Error retrieving job result: {e}")
        return None, None

    try:
        # Access the measurement results (which are binary strings like '010101')
        counts = job_result[0].data.c.get_counts()
        print("Counts retrieved from job:", counts)

        # Post-process results to find the private key
        private_key_candidates = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)[:10]
        print("Top candidates:", private_key_candidates)

        # Check each binary result for a valid private key
        for bin_key, count in counts.items():
            bin_key = bin_key.strip()

            # Ensure the key is exactly 20 bits
            if len(bin_key) < quantum_registers:
                bin_key = bin_key.ljust(quantum_registers, '0')
            elif len(bin_key) > quantum_registers:
                bin_key = bin_key[:quantum_registers]

            print(f"\nChecking binary key (first 20 bits): {bin_key} with length {len(bin_key)}")
            print(f"Key count: {count} times generated")

            # Convert binary string to hex
            private_key_hex = binary_to_hex(bin_key)
            if private_key_hex is None:
                continue  # Skip if conversion failed

            # Convert to compressed Bitcoin address
            compressed_address = private_key_to_compressed_address(private_key_hex)

            # Check if the private key produces the target Bitcoin address
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

def shor_oracle(qc, a, N, qubits):
    """Adds Shor's algorithm as an oracle to the quantum circuit."""
    for i in range(len(qubits)):
        qc.cx(qubits[i], a)  # Controlled modular exponentiation

def quantum_circuit(num_qubits, Gx, Gy, Px, p):
    q_x = QuantumRegister(num_qubits, 'x')  # Register for the private key
    anc = QuantumRegister(1, 'ancilla')     # Ancilla qubit
    qc_aux = QuantumRegister(num_qubits, 'auxiliary')  # Auxiliary register for swaps
    c = ClassicalRegister(num_qubits + 1, 'c')  # Classical register for measurement
    qc = QuantumCircuit(q_x, anc, qc_aux, c)

    # Initialize superposition
    qc.h(q_x)
    qc.h(anc)

    # ECDLP Oracle: Find k such that [k]G = P
    for i in range(num_qubits):
        # Controlled point doubling: Q = [2^i]G
        Qx, Qy = scalar_multiplication(2**i, Gx, Gy, p)

        # Controlled point addition: Q = Q + [2^i]G if the i-th bit of k is 1
        qc.cswap(anc, q_x[i], qc_aux[i])  # Use auxiliary qubit for swap

        # Compare Qx to Px (the target public key)
        qc.cx(q_x[i], anc)  # Controlled NOT for equality check

    # Add Shor's oracle to factor the modulus p
    shor_oracle(qc, anc, p, q_x)

    # Apply inverse QFT
    qc.append(QFT(num_qubits, do_swaps=True).inverse(), q_x)

    # Measurement
    qc.measure(q_x, c[:num_qubits])
    qc.measure(anc[0], c[num_qubits])

    return qc

# Main Function
def main():
    min_range = 0x10000
    max_range = 0x1FFFF
    num_qubits = int(np.ceil(np.log2(max_range))) + 1  # +1 for ancilla qubit
    target_address = "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm"
    public_key_x_hex = "0x6ef0691fa9edd5a21e6be331d5c4aa21c18a520d"
    public_key_hash = "0xb67cb6edeabc0c8b927c9ea327628e7aa63e2d52"
    public_key_hex = "033f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3"
    keyspace_size = max_range - min_range + 1
    print(f"Calculated keyspace size: {keyspace_size}")
    print(f"Number of Qubits: {num_qubits}")
    iterations = int(np.sqrt(float(max_range - min_range)))
    print(f"Calculated iterations: {iterations}")
    quantum_registers = 20  # Use 20 qubits for the search

    # Convert public key (x-coordinate) and modulus (p) from hexadecimal to integers
    x_Q = int(public_key_x_hex, 16)
    p = int(public_key_hex, 16)  # The modulus of the elliptic curve (field modulus)

    # Create and run the quantum circuit
    print(f"\nInitializing circuit with {num_qubits} qubits...")
    qc = quantum_circuit(num_qubits, G[0], G[1], x_Q, p)

    print("Quantum Circuit Details:")
    print(qc)
    print(f"Circuit Depth: {qc.depth()}, Circuit Size: {qc.size()}")

    # Initialize Qiskit Runtime Service
    service = QiskitRuntimeService()
    available_backends = service.backends()
    backend = service.backend('ibm_sherbrooke')
    print(f"Selected backend: {backend}")
    
    print("Transpiling the quantum circuit...")
    transpiled_circuit = transpile(qc, backend=backend, optimization_level=3)
    print(f"Transpiled circuit depth: {transpiled_circuit.depth()}")
    
    print("Assembling the circuit into a Qobj...")
    qobj = assemble(transpiled_circuit)
    print("Qobj assembled successfully.")
    
    print("Submitting the job to the backend...")
    sampler = SamplerV2(backend)
    job = sampler.run([transpiled_circuit], shots=8192)
    job_id = job.job_id()
    print(f"Job submitted. Job ID: {job_id}")
    
    print("Waiting for results...")
    result = job.result()
    counts = result[0].data.c.get_counts()
    print("Results received.")
    print("Measurement Results:")
    print(counts)

    if not counts:
        print("No results returned from the quantum circuit!")
        return None

    # Plot the histogram of results
    # plot_distribution(counts, legend=["Ibm Brisbane - Shor"])
    print("Plotting result distributions...")
    plot_distribution(counts, legend=["Ibm Sherbrooke - Quantum ECDLP Solver"])
    print("Plotting result histogram...")
    plot_histogram(counts)
    plt.show()

          # Retrieve and verify job results
    found_key, compressed_address = retrieve_job_result(job_id, target_address, quantum_registers)

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
    else:
        print("No valid key found. Resubmitting job...")

    # Extract the private key from the measurement results
    private_key = int(max(counts, key=counts.get), 2)
    print(f"Private Key Found: {private_key}")
    
    # Verify the private key by performing scalar multiplication on the elliptic curve
    computed_x, _ = scalar_multiplication(private_key, G[0], G[1], p)
    if computed_x == x_Q:
        print("Private Key Verified Successfully!")
        
        with open("boom.txt", "w") as file:
            file.write(f"Private Key: {private_key}\n")
            file.write(f"HEX: {hex(private_key)}\n")
            file.write(f"DEC: {private_key}\n")
        print("Private key saved to boom.txt")
    else:
        print("Private Key Verification Failed.")

if __name__ == "__main__":
    main()