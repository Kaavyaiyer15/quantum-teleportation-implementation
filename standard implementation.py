from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
import numpy as np
import matplotlib.pyplot as plt

theta = np.pi / 4
phi   = np.pi / 3

# ── Registers ─────────────────────────────────────────────
q = QuantumRegister(3, 'q')   # q0=input, q1=Alice, q2=Bob
c = ClassicalRegister(2, 'c')

qc = QuantumCircuit(q, c)

# ── Step 1: Prepare input state |ψ> ───────────────────────
qc.ry(theta, q[0])
qc.rz(phi, q[0])
qc.barrier(label="Input state")

# Save input state for fidelity verification
qc_input = QuantumCircuit(1)
qc_input.ry(theta, 0)
qc_input.rz(phi, 0)
sv_input = Statevector.from_instruction(qc_input)

# ── Step 2: Create Bell pair between Alice and Bob ───────
qc.h(q[1])
qc.cx(q[1], q[2])
qc.barrier(label="Bell pair")

# ── Verify Bob's state before measurement (should be I/2) ─
qc_pre = QuantumCircuit(3)
qc_pre.ry(theta, 0)
qc_pre.rz(phi, 0)
qc_pre.h(1)
qc_pre.cx(1, 2)

sv_pre = Statevector.from_instruction(qc_pre)

rho_bob = partial_trace(sv_pre, [0,1])

print("\nBob's reduced density matrix before Alice measures:")
print(np.round(rho_bob.data,4))

# ── Step 3: Alice Bell measurement ───────────────────────
qc.cx(q[0], q[1])
qc.h(q[0])

qc.barrier(label="Bell measurement")

qc.measure(q[0], c[0])
qc.measure(q[1], c[1])

qc.barrier(label="Classical communication")

# ── Step 4: Bob corrections ──────────────────────────────
with qc.if_test((c[1], 1)):
    qc.x(q[2])

with qc.if_test((c[0], 1)):
    qc.z(q[2])
qc.barrier(label="Bob correction")

""" ── Draw circuit ───────────────────────────────────────
fig = qc.draw('mpl')
plt.show() """