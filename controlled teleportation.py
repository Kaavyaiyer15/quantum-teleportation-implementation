# ---------------------------------------------------------------
# Qiskit implementation of the standard quantum teleportation
# protocol (Bennett et al., 1993)
# ---------------------------------------------------------------

# Import core Qiskit classes for constructing quantum circuits
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# Aer simulator backend (used if the circuit is executed)
from qiskit_aer import AerSimulator

# Tools for quantum state analysis
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace

# Numerical library for defining rotation angles
import numpy as np

# Matplotlib for optional circuit visualization
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# Parameters defining the arbitrary qubit state |ψ⟩ to teleport
# |ψ⟩ = Rz(φ) Ry(θ) |0⟩
# ---------------------------------------------------------------

theta = np.pi / 4   # rotation about Y-axis
phi   = np.pi / 3   # rotation about Z-axis


# ---------------------------------------------------------------
# Create quantum and classical registers
# q[0] : input qubit (unknown state)
# q[1] : Alice's half of Bell pair
# q[2] : Bob's half of Bell pair
# ---------------------------------------------------------------

q = QuantumRegister(3, 'q')
c = ClassicalRegister(2, 'c')   # stores Alice's measurement results

qc = QuantumCircuit(q, c)


# ---------------------------------------------------------------
# STEP 1 — Prepare the unknown state |ψ⟩ on qubit q[0]
# ---------------------------------------------------------------

qc.ry(theta, q[0])   # rotate around Y-axis
qc.rz(phi, q[0])     # rotate around Z-axis

qc.barrier(label="Input state")  # visual separation in circuit


# ---------------------------------------------------------------
# Save the input statevector for later verification
# ---------------------------------------------------------------

qc_input = QuantumCircuit(1)
qc_input.ry(theta, 0)
qc_input.rz(phi, 0)

# Convert preparation circuit into a statevector
sv_input = Statevector.from_instruction(qc_input)


# ---------------------------------------------------------------
# STEP 2 — Create Bell pair shared between Alice and Bob
# |β00⟩ = (|00⟩ + |11⟩)/√2
# ---------------------------------------------------------------

qc.h(q[1])           # create superposition
qc.cx(q[1], q[2])    # entangle Alice and Bob qubits

qc.barrier(label="Bell pair")


# ---------------------------------------------------------------
# Verify the no-signalling property before Alice measures
# Bob's reduced state should be maximally mixed (I/2)
# ---------------------------------------------------------------

qc_pre = QuantumCircuit(3)

# recreate circuit up to Bell pair stage
qc_pre.ry(theta, 0)
qc_pre.rz(phi, 0)
qc_pre.h(1)
qc_pre.cx(1, 2)

# obtain full three-qubit statevector
sv_pre = Statevector.from_instruction(qc_pre)

# trace out Alice's qubits (0 and 1)
rho_bob = partial_trace(sv_pre, [0,1])

print("\nBob's reduced density matrix before Alice measures:")
print(np.round(rho_bob.data,4))


# ---------------------------------------------------------------
# STEP 3 — Alice performs Bell-state measurement
# ---------------------------------------------------------------

qc.cx(q[0], q[1])    # entangle input with Alice's Bell qubit
qc.h(q[0])           # convert to Bell measurement basis

qc.barrier(label="Bell measurement")

# measure Alice's qubits and store results
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])

qc.barrier(label="Classical communication")


# ---------------------------------------------------------------
# STEP 4 — Bob applies conditional correction operations
# depending on Alice's measurement outcomes
# ---------------------------------------------------------------

# apply Pauli-X if second classical bit = 1
with qc.if_test((c[1], 1)):
    qc.x(q[2])

# apply Pauli-Z if first classical bit = 1
with qc.if_test((c[0], 1)):
    qc.z(q[2])

qc.barrier(label="Bob correction")


# ---------------------------------------------------------------
# Optional: draw the teleportation circuit
# ---------------------------------------------------------------

"""
fig = qc.draw('mpl')
plt.show()
"""