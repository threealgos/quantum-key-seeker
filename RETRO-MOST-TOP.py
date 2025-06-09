from qiskit.visualization import plot_histogram, plot_distribution
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Options
from qiskit.circuit.library import QFT
from qiskit.circuit import QuantumRegister, ClassicalRegister
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from fractions import Fraction
from math import gcd
import logging
from collections import Counter
from qiskit.circuit.controlflow.break_loop import BreakLoopPlaceholder
from qiskit.circuit.library import ZGate, MCXGate
from collections import Counter
from Crypto.Hash import RIPEMD160, SHA256  # Import from pycryptodome
from ecdsa import SigningKey, SECP256k1
from qiskit.quantum_info import PauliList, SparsePauliOp, Statevector, Operator
from qiskit.circuit import Parameter
from qiskit.circuit.library import RYGate
from Crypto.PublicKey import ECC
from bitarray import bitarray
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator, Aer
from qiskit_ibm_runtime import Estimator
from qiskit.circuit.library import RYGate, GroverOperator
import math
from math import ceil, log2
import matplotlib.pyplot as plt
from qiskit import QuantumRegister, ClassicalRegister, AncillaRegister
import numpy as np
import random
import time
import hashlib
import base58

# Load IBMQ account using QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel='ibm_quantum',
    token='cda3d163aada7d1c4b7a6d721f2adf7843ca9b8a67a58fb6c41264254afd7e6565e6c405812baf261455fcb70f6b3d1e6371031a9196418269e1a9e901ad5b2d',  # Replace with your actual token
    instance='ibm-q/open/main',
    overwrite=True,
    set_as_default=True
)

# Load the "open" credentials
service = QiskitRuntimeService()

# Secp256k1 curve parameters
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
G_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
G_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (G_X, G_Y)

def mod_inverse(a, p):
    """Compute the modular inverse of a modulo p."""
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        ratio = high // low
        nm, new_low = hm - lm * ratio, high - low * ratio
        lm, low, hm, high = nm, new_low, lm, low
    return lm % p

def point_doubling(x, y, p):
    """Elliptic curve point doubling formula."""
    s = (3 * x**2) * mod_inverse(2 * y, p) % p
    x_res = (s**2 - 2 * x) % p
    y_res = (s * (x - x_res) - y) % p
    return x_res, y_res

def point_addition(x1, y1, x2, y2, p):
    """Elliptic curve point addition formula."""
    if x1 == x2 and y1 == y2:
        return point_doubling(x1, y1, p)
    if x1 == x2:
        if y1 == -y2 % p:
            return None, None
        lam = (3 * x1**2 + 1) * mod_inverse(2 * y1, p) % p
    else:
        lam = (y2 - y1) * mod_inverse(x2 - x1, p) % p
    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3

def scalar_multiplication(k, x, y, p):
    """Perform scalar multiplication on an elliptic curve point."""
    if k == 0 or x is None or y is None:
        return None, None
    result_x, result_y = None, None
    addend_x, addend_y = x, y
    while k > 0:
        if k & 1:
            if result_x is None:
                result_x, result_y = addend_x, addend_y
            else:
                result_x, result_y = point_addition(result_x, result_y, addend_x, addend_y, p)
        addend_x, addend_y = point_addition(addend_x, addend_y, addend_x, addend_y, p)
        k >>= 1
    return result_x, result_y

def setup_elliptic_curve(public_key_hex):
    if public_key_hex.startswith('02') or public_key_hex.startswith('03'):
        x_hex = public_key_hex[2:]
        x = int(x_hex, 16)
        y_squared = (pow(x, 3, P) + A * x + B) % P
        y = pow(y_squared, (P + 1) // 4, P)
        if (public_key_hex.startswith('02') and y % 2 != 0) or (public_key_hex.startswith('03') and y % 2 == 0):
            y = P - y
    else:
        x_hex = public_key_hex[2:66]
        y_hex = public_key_hex[66:130]
        x = int(x_hex, 16)
        y = int(y_hex, 16)
    return (x, y), P, A, B

def create_superposition(circuit, qr):
    for qubit in qr:
        circuit.h(qubit)

def modular_exponentiation_operator(circuit, control, target, public_key_x, public_key_y, n_count, p):
    for i in range(n_count):
        power = 2**i
        point_x, point_y = scalar_multiplication(power, G_X, G_Y, p)
        for j in range(min(4, len(target))):
            circuit.cp(np.pi / (2**(j+1)), control[i], target[j])

def find_period_from_measurement(counts, num_qubits):
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    most_frequent = sorted_counts[0][0]
    measured_phase = int(most_frequent[:num_qubits], 2)
    phase = measured_phase / (2**num_qubits)
    frac = Fraction(phase).limit_denominator(SECP256K1_ORDER)
    period = frac.denominator
    if 1 <= period <= 2**num_qubits - 1:
        return period
    return None

def majority_vote(results, num_qubits):
    periods = [find_period_from_measurement(counts, num_qubits) for counts in results if counts]
    valid_periods = [p for p in periods if p is not None]
    if not valid_periods:
        return None
    return Counter(valid_periods).most_common(1)[0][0]

def verify_private_key(private_key, public_key_hex, G_X, G_Y, p):
    public_key_point, _, _, _ = setup_elliptic_curve(public_key_hex)
    point_x, point_y = scalar_multiplication(private_key, G_X, G_Y, p)
    if point_y is None:
        return False
    computed_public_key = "03" + format(point_x, '064x') if point_y % 2 else "02" + format(point_x, '064x')
    return computed_public_key == public_key_hex

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
    ripemd160 = RIPEMD160.new()
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

# Convert binary string to hexadecimal
def binary_to_hex(bin_str):
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(64)  # Pad hex string to ensure it's 64 characters long (32 bytes)

# Function to plot the result histogram of counts
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
    plt.title('Histogram of Measurement Counts')
    plt.tight_layout()
    plt.show()

# Function to get the top 10 most frequent counts
def get_top_10_frequent(counts):
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top_10_counts = sorted_counts[:10]
    print(f"Top 10 most frequent counts: {top_10_counts}")
    
    private_key_candidates = [int(bitstring, 2) for bitstring, _ in top_10_counts]
    return private_key_candidates

# Function to convert binary string to hexadecimal
def binary_to_hex(bin_str):
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(64)  # Pad hex string to ensure it's 64 characters long (32 bytes)

# Function to generate compressed Bitcoin address from private key
def private_key_to_compressed_address(private_key_hex):
    try:
        private_key = bytes.fromhex(private_key_hex)
    except ValueError as e:
        print(f"Invalid hexadecimal private key: {private_key_hex}. Error: {e}")
        return None  # Return None if invalid hex is encountered

    if len(private_key) != 32:  # Ensure correct length for private key
        print(f"Invalid private key length: {len(private_key)} bytes (expected 32).")
        return None

    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.verifying_key

    public_key = b'\x02' + vk.to_string()[:32] if vk.pubkey.point.y() % 2 == 0 else b'\x03' + vk.to_string()[:32]
    sha256_hash = hashlib.sha256(public_key).digest()

    # Use pycryptodome's RIPEMD160
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_hash)
    hash160 = ripemd160.digest()

    address = b'\x00' + hash160
    checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]
    return base58.b58encode(address + checksum).decode()

# Additional function to process the counts
def process_counts(counts):
    # Get the most common 5 counts
    most_common = counts.most_common(5)
    print("Top 5 most common measurement results:")
    for (bin_key, count) in most_common:
        hex_key = binary_to_hex(''.join(map(str, bin_key)))
        print(f"Binary: {''.join(map(str, bin_key))}, Hex: {hex_key}, Count: {count}")    

# Additional code to access job results directly
def retrieve_job_result(job_id, target_address, quantum_registers):
    print("🔧 Initializing Qiskit Runtime Service...")
    service = QiskitRuntimeService(
        channel='ibm_quantum',
        instance='ibm-q/open/main',
        token='cda3d163aada7d1c4b7a6d721f2adf7843ca9b8a67a58fb6c41264254afd7e6565e6c405812baf261455fcb70f6b3d1e6371031a9196418269e1a9e901ad5b2d'
    )

    print(f"📡 Retrieving job result for job ID: {job_id}...")
    try:
        job = service.job(job_id)
        job_result = job.result()
    except Exception as e:
        print(f"❌ Error retrieving job result: {e}")
        return None, None

    print("📦 Job result structure loaded.")
    try:
        pub_result = job_result['results'][0]
        samples = pub_result['data']['c']['samples']

        print(f"🧪 Samples retrieved: {len(samples)}")
        meas_list = [bin(int(sample, 16))[2:].zfill(quantum_registers) for sample in samples]
        print(f"🔢 Converted {len(meas_list)} samples to bitstrings.")

        counts = Counter(meas_list)
        print(f"🔍 Unique measurement patterns: {len(counts)}")

        for i, (bin_key, count) in enumerate(counts.items(), start=1):
            private_key_hex = binary_to_hex(bin_key)
            compressed_address = private_key_to_compressed_address(private_key_hex)

            print(f"🔁 [{i}/{len(counts)}] Checking key: {private_key_hex} -> {compressed_address}")

            if compressed_address == target_address:
                print(f"✅ MATCH FOUND! Private key: {private_key_hex}")

                # Save to boom.txt
                with open('boom.txt', 'a') as file:
                    file.write(f"Private Key: {private_key_hex}\n")
                    file.write(f"Compressed Address: {compressed_address}\n\n")

                return private_key_hex, compressed_address

        print("❌ No matching private key found.")
        return None, None

    except KeyError as e:
        print(f"❌ Key error accessing measurement data: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None

# Main execution section (example use)
def main():
    job_id = 'd133595mya70008egwrg'
    target_address = '19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR'
    quantum_registers = 70
    num_qubits = 70
    num_shots = 8192

    print(f"🚀 Checking job ID: {job_id} against target address: {target_address}")
    private_key_hex, compressed_address = retrieve_job_result(job_id, target_address, quantum_registers)
    

    if private_key_hex:
        print(f"\n✅ SUCCESS! Found matching private key:")
        print(f"HEX: {private_key_hex}")
        print(f"Address: {compressed_address}")
    else:
        print("❌ No valid key found.")

if __name__ == '__main__':
    main()
