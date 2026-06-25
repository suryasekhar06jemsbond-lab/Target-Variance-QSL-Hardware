# Target-Variance Quantum Speed Limits from Projective Fidelity Reduction: Hardware Validation

This repository provides the official open-source Qiskit implementation and experimental hardware validation data for the target-variance quantum speed limit (QSL) framework. 

The core theoretical architecture was peer-reviewed and accepted for publication in the **International Journal of Modern Physics B** (Submission No.: JPB20080030R3). This project demonstrates the practical, hardware-capable deployment of the target-variance bound on utility-scale quantum processors.

## Key Milestone：Commuting-Sector Invariance
Traditional quantum speed limits—such as the Mandelstam-Tamm ($T_{MT}$) and Margolus-Levitin ($T_{ML}$) bounds—rely on tracking the global, evolving-state energy variance $\Delta H_{\rho(t)}$. In highly interacting many-body systems or large quantum processors, extensive background entanglement and coupling layers artificially inflate this global variance. This causes classical bounds to collapse ($T_{MT} \to 0$), yielding a trivial, uninformative zero-time speed limit that falsely implies the system can evolve instantly.

This research resolves this bottleneck by deriving a detector-conditioned QSL specialized for single-outcome projective measurement channels ($\pi_{\omega}$):

$$T \ge \frac{|\Theta(0) - \Theta_{*}|}{\Delta H_{\omega}}$$

Where $\Theta = \arccos\sqrt{F}$ is the Bures angle, and $\Delta H_{\omega}$ is the energy standard deviation evaluated strictly on the **fixed target state** $|\omega\rangle$. 

By proving **Theorem 4.6 (Commuting-Sector Invariance)**, this framework demonstrates that Hamiltonian components that commute with the target projector are completely filtered out of the speed limit. The bound is time-independent, requiring **zero state monitoring or exponential state tomography overhead**, making it uniquely optimized for modern, resource-constrained quantum hardware.

---

## Experimental Setup: 1D Transverse-Field Ising Model (TFIM)

We physically simulate the 1D Transverse-Field Ising Model on a 4-qubit register to observe the **Asymptotic Separation** between the target-variance bound and the classical Mandelstam-Tamm bound under strong coupling.

* **Hamiltonian:** $H = -J\sum_{i=1}^{N-1}\sigma_z^{(i)}\sigma_z^{(i+1)} - h\sum_{i=1}^{N}\sigma_x^{(i)}$ (with fixed $h = 1.0$, varying $J/h \in [0, 5]$)
* **Initial State ($|\psi(0)\rangle$):** Uniform X-basis product state $|++++\rangle$
* **Target State Projector ($|\omega\rangle$):** All-ones Z-basis ferromagnetic state $|1111\rangle$
* **Readout Discrimination Threshold:** $F_* = 0.15$
* **Target Hardware:** **ibm_fez** (156-qubit premium IBM Quantum Heron processor)
* **Shots:** 2,500 per time-slice circuit (Total batch workload: 20,000+ physical shots)

---

## Hardware-Ready Implementation Features

The production script `tfim_qsl_simulation.py` includes advanced compilation and mitigation layers designed for utility-scale deployment:

1. **Topological Layout Constraint:** Maps the 4-qubit register directly onto a physically verified, linearly connected qubit chain (`initial_layout=[1, 2, 3, 4]`) on the Heron coupling map. This completely eliminates the injection of noisy SWAP gates, minimizing two-qubit gate decoherence.
2. **Matrix-Free Measurement Mitigation (M3):** Integrates the `mthree` package to calibrate assignment error matrices on the active hardware register, resolving readout bit-flip noise before evaluating the projective fidelity.
3. **High-Efficiency Batching:** Pre-compiles all 2,100 parameterized Trotter circuits and submits them to the IBM Quantum Platform cloud scheduler inside a single, unified execution payload to circumvent multi-job queue latencies.

---

## Results & Visual Proof

The hardware data confirms the major analytical milestones of the manuscript:

* **The MT Collapse:** At strong coupling ($J/h = 5.0$), the traditional blue Mandelstam-Tamm curve decays near zero ($0.0142\text{ s}$), losing all predictive value.
* **The Stability of $T_\omega$:** The target-variance bound remains flawlessly flat as a constant horizontal constraint ($0.0725\text{ s}$), ignoring the background interaction inflation.
* **Quantum Nutation Capture:** Real hardware data points ($T_{actual}$) confirm that the system remains intrinsically slow. The strong coupling dynamically confines the state through fast, small-amplitude quantum nutations, pushing the hitting time upward ($0.40\text{ s}$) while remaining perfectly lower-bounded by the target-variance limit.

*Note: The hardware results cleanly capture the frequency of the manuscript's predicted trajectories, with readout amplitudes robustly corrected using M3 mitigation against native hardware dephasing channels.*

---

## How to Run on Real Hardware

* **Install dependencies:

Bash
pip install qiskit qiskit-ibm-runtime mthree matplotlib numpy
Configure your IBM Quantum credentials:

Python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_IBM_API_TOKEN")
Execute the validation pipeline:

Bash
python3 tfim_qsl_simulation.py

---

Citation
If you use this framework or hardware-benchmarking layout in your research, please cite our peer-reviewed paper:


@article{roy2026target,
  title={Target-Variance Quantum Speed Limits from Projective Fidelity Reduction},
  author={Roy, Surya Sekhar},
  journal={International Journal of Modern Physics B},
  volume={Accepted Manuscript},
  number={JPB20080030R3},
  year={2026},
  publisher={World Scientific Publishing Company}
}

---

Acknowledgments
We express our gratitude to the IBM Quantum community for providing access to utility-scale Heron computing architectures (ibm_fez) that made this experimental validation possible.

---

## Results & Validation

Below is the macro-level data extracted from the 156-qubit **ibm_fez** processor, confirming the asymptotic separation predicted by Theorem 5.2 as the many-body coupling strength scales extensively:

![Quantum Speed Limit Validation Benchmark](qsl_validation_plot_3.png)

## Hardware Compilation Profile

The transpiled circuit diagram below illustrates the native pulse-level gate routing on the IBM Quantum Heron architecture. By optimizing the physical register map, the compiler enforces a clean nearest-neighbor coupling loop with zero SWAP gate overhead:

![Heron Chip Circuit Native Compilation](circuit-d8uhclsbp3hs73861d7g_3.png)

## Raw Measurement Diagnostics

To evaluate the projective fidelity reduction threshold ($F_* = 0.15$), raw binary distributions are unpacked and corrected using Matrix-Free Measurement Mitigation (M3). Below is a representative diagnostic histogram of single-outcome state frequencies sampled from the hardware backend:

![Error Mitigated Hardware Measurement Histogram](job_d8uhc4ctqbtc73d1qdmg_results_c_3.png)

---
