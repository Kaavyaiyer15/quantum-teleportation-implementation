from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Define parameters that determine the arbitrary state |ψ⟩
# that Alice wants to teleport
# ------------------------------------------------------------

theta = np.pi / 4     # rotation angle about Y-axis
phi   = np.pi / 3     # rotation angle about Z-axis

# ── Registers ─────────────────────────────────────────────
# Create 3 qubits:
# q[0] = input qubit containing the unknown state |ψ>
# q[1] = Alice's qubit from the entangled Bell pair
# q[2] = Bob's qubit from the entangled Bell pair
q = QuantumRegister(3, 'q')

# Create 2 classical bits to store Alice's measurement results
c = ClassicalRegister(2, 'c')

# Create the quantum circuit using the above registers
qc = QuantumCircuit(q, c)

# ── Step 1: Prepare input state |ψ> ───────────────────────
# Apply rotation around the Y-axis to q[0]
qc.ry(theta, q[0])

# Apply rotation around the Z-axis to q[0]
# Together Rz and Ry generate a general single-qubit state
qc.rz(phi, q[0])

qc.barrier(label="Input state")

# Save input state for fidelity verification
# Create a separate circuit representing the same state preparation
qc_input = QuantumCircuit(1)

# Apply the same rotations to reproduce the input state
qc_input.ry(theta, 0)
qc_input.rz(phi, 0)

# Convert this circuit into a statevector representation
# This allows us to compare the original and teleported states later
sv_input = Statevector.from_instruction(qc_input)
)

# ── Step 2: Create Bell pair between Alice and Bob ───────
# Apply Hadamard gate to Alice's Bell qubit
# This creates a superposition state
qc.h(q[1])

# Apply CNOT gate to entangle Alice's qubit (q1) with Bob's qubit (q2)
# Resulting state is the Bell state (|00⟩ + |11⟩)/√2
qc.cx(q[1], q[2])

# Barrier for visual separation
qc.barrier(label="Bell pair")

# ── Verify Bob's state before measurement (should be I/2) ─
# Build a temporary circuit that reproduces the system up to this stage
qc_pre = QuantumCircuit(3)

# Prepare the same input state
qc_pre.ry(theta, 0)
qc_pre.rz(phi, 0)

# Create the same Bell pair
qc_pre.h(1)
qc_pre.cx(1, 2)

# Convert the full 3-qubit circuit into a statevector
sv_pre = Statevector.from_instruction(qc_pre)

# Compute Bob's reduced density matrix by tracing out Alice's qubits
# (qubits 0 and 1)
rho_bob = partial_trace(sv_pre, [0,1])

# Print Bob's density matrix
# It should be maximally mixed (I/2), meaning Bob has no information
# about the teleported state before classical communication
print("\nBob's reduced density matrix before Alice measures:")
print(np.round(rho_bob.data,4))

# ── Step 3: Alice Bell measurement ───────────────────────
# Apply CNOT between input qubit and Alice's Bell qubit
# This entangles the unknown state with the Bell pair
qc.cx(q[0], q[1])

# Apply Hadamard to complete the Bell basis transformation
qc.h(q[0])

# Barrier marking Bell measurement stage
qc.barrier(label="Bell measurement")

# Measure Alice's qubits and store results in classical bits
qc.measure(q[0], c[0])   # first measurement bit
qc.measure(q[1], c[1])   # second measurement bit

# Barrier representing classical communication from Alice to Bob
qc.barrier(label="Classical communication")

# ── Step 4: Bob corrections ──────────────────────────────
# If the second classical bit is 1, apply a Pauli-X correction
with qc.if_test((c[1], 1)):
    qc.x(q[2])

# If the first classical bit is 1, apply a Pauli-Z correction
with qc.if_test((c[0], 1)):
    qc.z(q[2])

# Final barrier marking Bob's correction stage
qc.barrier(label="Bob correction")

""" ── Draw circuit ───────────────────────────────────────
fig = qc.draw('mpl')
plt.show() """
