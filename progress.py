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
from qiskit.circuit.library import QFT, arithmetic
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit_algorithms.amplitude_amplifiers.grover import GroverResult

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

def point_addition(x1, y1, x2, y2, p):
  if x1 == x2 and y1 == y2:
    return point_doubling(x1, y1, p)
  lam = ((y2 - y1) * mod_inverse(x2 - x1, p)) % p
  x3 = (lam * lam - x1 - x2) % p
  y3 = (lam * (x1 - x3) - y1) % p
  return x3, y3

def point_doubling(x1, y1, p):
  lam = ((3 * x1 * x1) * mod_inverse(2 * y1, p)) % p
  x3 = (lam * lam - 2 * x1) % p
  y3 = (lam * (x1 - x3) - y1) % p
  return x3, y3

def scalar_multiplication(k, x, y, p):
  x_res, y_res = x, y
  k_bin = bin(k)[2:]
  for bit in k_bin[1:]:
    x_res, y_res = point_doubling(x_res, y_res, p)
    if bit == '1':
      x_res, y_res = point_addition(x_res, y_res, x, y, p)
  return x_res, y_res

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

def retrieve_job_result(job_id, target_address, quantum_registers):
    """Retrieve job results and check for valid private keys."""
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

def quantum_brute_force(public_key_x, g_x, g_y, p, min_range, max_range):
  quantum_registers = int(np.ceil(np.log2(max_range)))
  keyspace_size = max_range - min_range + 1
  print(f"Taille de l'espace de clés calculée : {keyspace_size}")
  print(f"Number of Qubits : {quantum_registers}")
  iterations = int(np.sqrt(float(max_range - min_range)))
  print(f"Calculated iterations: {iterations}")
  service = QiskitRuntimeService()
  
  circuit = QuantumCircuit(quantum_registers, quantum_registers)
  circuit.h(range(quantum_registers))
  circuit.append(QFT(quantum_registers).inverse(), range(quantum_registers))

  print("Quantum Circuit Details:")
  print(circuit)
  print(f"Circuit Depth: {circuit.depth()}, Circuit Size: {circuit.size()}")

  # Transpile and assemble the circuit
  print("Transpiling the quantum circuit...")
  transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
  print(f"Transpiled circuit depth: {transpiled_circuit.depth()}")

  print("Assembling the circuit into a Qobj...")
  qobj = assemble(transpiled_circuit)
  print("Qobj assembled successfully.")

  available_backends = service.backends()
  backend = service.backend('ibm_sherbrooke')
  print(f"Selected backend: {backend.name}")

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

  progress_step = len(counts) // 100
  progress = 0

  for i, private_key_bin in enumerate(counts):
    if i % progress_step == 0:
      print(f"Progress: {progress}%")
      progress += 1

    private_key = int(private_key_bin, 2)
    if private_key < min_range or private_key > max_range:
      continue

    computed_x, _ = scalar_multiplication(private_key, g_x, g_y, p)
    if computed_x == public_key_x:
      return private_key
  return None

if __name__ == "__main__":
  public_key_x_hex = "0x6ef0691fa9edd5a21e6be331d5c4aa21c18a520d"
  public_key_x = int(public_key_x_hex, 16)
  min_range = 0x10000
  max_range = 0x1FFFF
  p = int("0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
  g_x = int("0x3f688bae8321b8e02b7e6c0a55c2515fb25ab97d85fda842449f7bfa04e128c3", 16)
  g_y = int("0x393e3b1c529624e56840acbb10243ec9e0cfe99c3cffe1c87537b735bbba2d2f", 16)

  private_key = quantum_brute_force(public_key_x, g_x, g_y, p, min_range, max_range)
  if private_key:
    print(f"Private key found: {hex(private_key)}")
  else:
    print("Private key not found in the given range.")
