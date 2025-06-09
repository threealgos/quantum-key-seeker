from qiskit.visualization import plot_histogram, plot_distribution
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.circuit.library import QFT
from qiskit.circuit import QuantumRegister, ClassicalRegister
from fractions import Fraction
from math import gcd
import logging
from Crypto.Hash import RIPEMD160, SHA256
from ecdsa import SigningKey, SECP256k1
from qiskit.quantum_info import PauliList, SparsePauliOp, Statevector, Operator
from qiskit.circuit.library import RYGate
from Crypto.PublicKey import ECC
from bitarray import bitarray
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator, Aer
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import base58

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load IBM Quantum account (replace with your token)
QiskitRuntimeService.save_account(
    channel='ibm_quantum',
    token='cda3d163aada7d1c4b7a6d721f2adf7843ca9b8a67a58fb6c41264254afd7e6565e6c405812baf261455fcb70f6b3d1e6371031a9196418269e1a9e901ad5b2d',  # Replace with your IBM Quantum token
    instance='ibm-q/open/main',
    overwrite=True,
    set_as_default=True
)

# Load the service
service = QiskitRuntimeService()
backend = service.backend("ibm_brisbane")

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

def public_key_to_btc_address(x, y, compressed=True):
    """Generates a Bitcoin address from the public key."""
    if compressed:
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        public_key = prefix + x.to_bytes(32, 'big')
    else:
        public_key = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    sha256 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    return ripemd160

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
        # Access the measurement results (which are binary strings like '010101')
        counts = job_result[0].data.c.get_counts()
        print("Counts retrieved from job:", counts)

        # Check each binary result for a valid private key
        for bin_key, count in counts.items():
            # Convert binary string to hex
            private_key_hex = binary_to_hex(bin_key)

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

def quantum_brute_force(public_key_x, g_x, g_y, p, min_range, max_range):
    target_address = "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm"
    quantum_registers = int(np.ceil(np.log2(max_range)))
    num_qubits = int(np.ceil(np.log2(max_range)))
    num_shots = 8192

    circuit = QuantumCircuit(num_qubits, num_qubits)
    circuit.h(range(num_qubits))
    circuit.append(QFT(num_qubits).inverse(), range(num_qubits))
    circuit.measure(range(num_qubits), range(num_qubits))

    print("Quantum Circuit:")
    print(circuit)
    print(f"Depth: {circuit.depth()}, Size: {circuit.size()}")

    service = QiskitRuntimeService()
    backend = service.backend("ibm_brisbane")

    print("Transpiling...")
    transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
    print(f"Transpiled depth: {transpiled_circuit.depth()}")

    print("Submitting job...")
    sampler = Sampler(backend)
    job = sampler.run([transpiled_circuit], shots=num_shots)
    job_id = job.job_id()
    print(f"Job submitted. ID: {job_id}")

    result = job.result()
    counts = result[0].data.c.get_counts() if hasattr(result[0].data, 'c') else result.get_counts(circuit)

    if not counts:
        print("No results received.")
        return None

    print("Measurement Results:")
    print(counts)

    found_key, compressed_address = retrieve_job_result(job_id, target_address, quantum_registers)

    if found_key:
        print("\nSUCCESS! Private key:")
        print(f"Found matching private key: {found_key}")
        print(f"HEX: {hex(found_key)}")
        print(f"DEC: {found_key}")
        with open("boom.txt", "w") as file:
            file.write("Measurement Results:\n")
            for bitstring, count in counts.items():
                file.write(f"{bitstring}: {count}\n")
        print("Results saved to boom.txt")
    else:
        print("No valid key found.")

    # Get most frequent result
    most_common = max(counts, key=counts.get)
    private_key = int(most_common, 2)
    print(f"Most frequent result: {most_common} (int: {private_key})")

    # Check key range
    if not (min_range <= private_key <= max_range):
        print("Most common key is out of the valid range.")
    else:
        # Verify by scalar multiplication
        computed_x, _ = scalar_multiplication(private_key, g_x, g_y, p)
        if computed_x == public_key_x:
            print("✅ Private Key Verified Successfully!")
            with open("boom.txt", "w") as f:
                f.write(f"Private Key: {private_key}\n")
                f.write(f"HEX: {hex(private_key)}\n")
                f.write(f"DEC: {private_key}\n")
            print("Saved to boom.txt")
            return private_key
        else:
            print("❌ Verification failed for most common key.")

    print("Trying other likely candidates...")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for key_bin, _ in sorted_counts:
        candidate_key = int(key_bin, 2)
        if not (min_range <= candidate_key <= max_range):
            continue

        computed_x, _ = scalar_multiplication(candidate_key, g_x, g_y, p)
        if computed_x == public_key_x:
            print("✅ Found valid private key during fallback!")
            with open("boom.txt", "w") as f:
                f.write(f"Private Key: {candidate_key}\n")
                f.write(f"HEX: {hex(candidate_key)}\n")
                f.write(f"DEC: {candidate_key}\n")
            print("Saved to boom.txt")
            return candidate_key

    print("❌ No valid key found in fallback check.")

    # Visualization
    print("Plotting histogram...")
    plot_histogram(counts)
    plt.show()

    return None


if __name__ == "__main__":
    public_key_x_hex = "0x6EF0691Fa9edd5a21e6BE331D5C4aA21c18A520d"
    public_key_x = int(public_key_x_hex, 16)
    min_range = 0x10000
    max_range = 0x1FFFF
    p = int("0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
    g_x = int("0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
    g_y = int("0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)
    
    key = quantum_brute_force(public_key_x, g_x, g_y, p, min_range, max_range)
    if key:
        print(f"✅ Final Private Key: {hex(key)}")
    else:
        print("❌ Could not determine the private key.")
