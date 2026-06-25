import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import mthree
import warnings

warnings.filterwarnings('ignore')

def get_tfim_circuit(N, J, h, t, dt):
    """Generates a 1D Transverse-Field Ising Model Trotter circuit."""
    steps = int(round(t / dt))
    qc = QuantumCircuit(N, N)
    qc.h(range(N))
    for _ in range(steps):
        for i in range(N - 1):
            qc.rzz(2 * J * dt, i, i + 1)
        for i in range(N):
            qc.rx(2 * h * dt, i)
    qc.measure(range(N), range(N))
    return qc

# 1. Secure Authentication with IBM Quantum
try:
    # Safely instantiates service assuming account has been saved locally via:
    # QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_TOKEN")
    service = QiskitRuntimeService()
    print("Successfully authenticated using saved environment credentials.")
except Exception:
    raise RuntimeError(
        "Authentication credentials not found on local disk. "
        "Please run QiskitRuntimeService.save_account() securely in your local environment "
        "before deploying this execution script to public repositories."
    )

# 2. Select a utility-scale backend (min 127 qubits)
backend = service.least_busy(operational=True, simulator=False, min_num_qubits=127)
print(f"Selected IBM Quantum backend: {backend.name}")

N = 4
h = 1.0
J_vals = np.linspace(0.0, 5.0, 11)
t_max = 5.0
dt = 0.1
times = np.arange(0, t_max + dt, dt)
shots = 4000

# 3. Calibrate M3 using the target hardware's topology map
print("Calibrating M3 Readout Mitigation on real hardware register...")
# Adjust physical_qubits list to follow a strictly connected linear line on your target hardware
physical_qubits = [1, 2, 3, 4] 
mit = mthree.M3Mitigation(backend)
mit.cals_from_system(physical_qubits)

threshold = 0.15
theta_star = np.arccos(np.sqrt(threshold))
f0 = 1.0 / (2**N)
theta_0 = np.arccos(np.sqrt(f0))

T_actual = []
T_omega_vals = []
T_MT_vals = []

print("Compiling all parameter circuits for parallel batch submission...")
all_compiled_circuits = []
# Pre-compile all circuits to submit them inside a single batch payload
for J in J_vals:
    for t in times:
        if t != 0:
            qc = get_tfim_circuit(N, J, h, t, dt)
            compiled_qc = transpile(qc, backend, initial_layout=physical_qubits, optimization_level=3)
            all_compiled_circuits.append(compiled_qc)

print(f"Submitting batch of {len(all_compiled_circuits)} circuits via Sampler V2 to avoid queue latency...")
sampler = Sampler(mode=backend)
sampler.options.default_shots = shots
job = sampler.run(all_compiled_circuits)
print(f"Batch Job submitted successfully! ID: {job.job_id()}")
print("Awaiting hardware response from cloud scheduler...")
result = job.result()

print("Processing mitigated hardware results...")
result_idx = 0
target_str = '1' * N

for J in J_vals:
    # Compute theoretical QSL bounds matching manuscript derivations
    T_omega = abs(theta_0 - theta_star) / (h * np.sqrt(N))
    T_MT = abs(theta_0 - theta_star) / (2 * np.sqrt(J**2 + h**2))
    T_omega_vals.append(T_omega)
    T_MT_vals.append(T_MT)
    
    actual_t = np.nan
    for t in times:
        if t == 0:
            f_t = f0
        else:
            # Unpack PubResults cleanly from SamplerV2 primitive layout
            pub_result = result[result_idx]
            counts = list(pub_result.data.values())[0].get_counts()
            
            # Apply M3 Readout Error Correction
            quasis = mit.apply_correction(counts, physical_qubits)
            f_t = quasis.get(target_str, 0)
            result_idx += 1
            
        # Extract the exact hitting time step where fidelity crosses the detection limit
        if f_t >= threshold and np.isnan(actual_t):
            actual_t = t
            
    print(f"J/h: {J:.2f}, T_actual: {actual_t}, T_omega: {T_omega:.4f}, T_MT: {T_MT:.4f}")
    T_actual.append(actual_t)

# 4. Generate and write the final validation plot
plt.figure(figsize=(10, 6))
plt.plot(J_vals, T_omega_vals, 'k--', linewidth=2, label=r'Target-Variance Bound ($T_\omega$)')
plt.plot(J_vals, T_MT_vals, 'b-', linewidth=2, label=r'Mandelstam-Tamm Bound ($T_{MT}$)')
plt.plot(J_vals, T_actual, 'ro', markersize=8, label=r'Actual Time ($T_{actual}$)')
plt.xlabel(r'Interaction Strength Ratio $J/h$', fontsize=14)
plt.ylabel(r'Evolution Time $T$', fontsize=14)
plt.title(r'Hardware QSL Bounds vs Actual Time ($N=4$, threshold $F=0.15$)', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, linestyle=':', alpha=0.7)
plt.tight_layout()
plt.savefig('hardware_qsl_validation_plot.png', dpi=300)
print("Validation plot safely saved to hardware_qsl_validation_plot.png")
