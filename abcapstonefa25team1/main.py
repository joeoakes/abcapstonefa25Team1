from qiskit import QuantumCircuit
from qiskit_aer import Aer

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure_all()

backend = Aer.get_backend("qasm_simulator")
result = backend.run(qc, shots=16, memory=True).result()

memory = result.get_memory(qc)
print(memory)
