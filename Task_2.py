
# File for loading the system data from the .mat file
from matplotlib import table

import scipy.io as sio
import numpy as np
from Assignment_helpfunctions_part_I.P_matrix_write import latex_P_matrix, excel_P_matrix


def find_eigenvalues(A):
    # Calculate eigenvalues using numpy
    eigenvalues, right_eigenvectors = np.linalg.eig(A)
    return eigenvalues, right_eigenvectors


def find_frequency_and_damping(lambda_value):
    frequency = np.imag(lambda_value) / (2 * np.pi)
    damping_ratio = -np.real(lambda_value) / np.sqrt(np.real(lambda_value)**2 + np.imag(lambda_value)**2)
    return frequency, damping_ratio

def find_participation_matrix(data):

    lambdas, Phi = find_eigenvalues(data)

    Psi = np.linalg.inv(Phi)
    Participation = np.multiply(Phi, Psi.T)
    return lambdas, Phi, Participation

def excel_P_matrix(P, state_labels, Matlab_array, filename, bold_limit, with_bold):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Border, Side

    limit = bold_limit
    bold_font = Font(bold=True)
    left_border = Border(left=Side(style='thin'))
    top_double_border = Border(top=Side(style='double'))

    wb = Workbook()
    ws = wb.active
    ws.title = 'Participation matrix'

    n1, n2 = P.shape

    # Standardize the participation matrix along the rows (states). Standardize by dividing each row by the maximum absolute value in that row.
    for i in range(n1):
        max_val = np.max(np.abs(P[i, :]))
        if max_val > 0:
            P[i, :] /= max_val

    for i in range(n1):
        for j in range(n2):
            if not with_bold:
                if np.abs(P[i, j]) > limit:
                    cell = ws.cell(row=i+1, column=j+1, value=round(float(np.abs(P[i, j])), 3))
                else:
                    cell = ws.cell(row=i+1, column=j+1, value=0.0)
            else:
                cell = ws.cell(row=i+1, column=j+1, value=round(float(np.abs(P[i, j])), 3))
                if np.abs(P[i, j]) > limit:
                    cell.font = bold_font


        label = state_labels[i, 0][0] if Matlab_array else state_labels[i]
        label_cell = ws.cell(row=i+1, column=n2+1, value=label)
        label_cell.border = left_border

    for j in range(n2):
        name = f"\N{GREEK SMALL LETTER LAMDA}_{j+1}"
        cell = ws.cell(row=n1+1, column=j+1, value=name)
        cell.border = top_double_border

    wb.save(filename)

path = r"C:\Users\willi\OneDrive\Dokumenter\.DTU\Stability\46711-Assignment-1\Assignment_data"

file = "system_q2.mat"

# Load the files and print
q2_data = sio.loadmat(f"{path}/{file}", squeeze_me=True)
A = q2_data["A"]
B = q2_data["B"]
C = q2_data["C"]
D = q2_data["D"]
DeviceName = q2_data["DeviceName"]
StateName = q2_data["StateName"]
latex_names_q2a = q2_data["latex_names_q2a"]
names_q2a = q2_data["names_q2a"]
strsps = q2_data["strsps"]

# Q2.1.1

# Construct the participation matrix P for the system. The table should be stored in appendix of
# your report.

lambdas, Phi, Participation = find_participation_matrix(A)

# Q2.1.2

# Construct a table that shows the eigenvalues of the system, the frequency and the damping of the
# oscillating modes and a description of the dominating states in the mode. The table should be
# similar to the one at page 815 in the textbook

f = []
omega = []
for l in lambdas:
    f.append(find_frequency_and_damping(l)[0])
    omega.append(find_frequency_and_damping(l)[1])

import pandas as pd
df = pd.DataFrame(columns=["Eigenvalue", "Real", "Imaginary", "Frequency (Hz)", "Damping Ratio", "Dominating States"])
df["Eigenvalue"] = ["λ" + str(i+1) for i in range(len(lambdas))]
df["Real"] = np.real(lambdas)
df["Imaginary"] = np.imag(lambdas)
df["Frequency (Hz)"] = f
df["Damping Ratio"] = omega


threshold = 0.3
excel_P_matrix(Participation, StateName, False, "latex_P_matrix_Q2.xlsx", threshold, True)

# Now we will create a table with one column of the eigenvalues name, one column with the eigenvalue, one column with the frequency, one with the damping ratio, and one with the dominating states.
# The dominating states are found by looking at the excel_P_matrix with the bold values

# Import excel file

excel_file = pd.read_excel("latex_P_matrix_Q2.xlsx", sheet_name="Participation matrix", header=None)

dominating = []
for i in range(len(lambdas)):
    states = [StateName[j] for j in range(len(StateName)) if excel_file.iloc[j, i] > threshold]
    dominating.append(", ".join(states))

df["Dominating States"] = dominating

df.to_excel("eigenvalue_table_Q2.xlsx", index=False)

# Q2.1.3

# Identify the modes of electromechanical oscillation and determine whether one of these modes
# has a critically low damping (ζ ≤ 0.1). Furthermore, identify the zero-modes and explain why
# they appear in your results

# lambda = sigma + j*omega

# Eigenvalue lambda17 - lambda24 is actual mechanical modes
# The dampening ratios are

print("Damping ratios for mechanical modes:")
for i in range(16, 23):
    print(f"Mode {i+1}: {omega[i]:.3f}")

# The zero modes are explained by the lack of any meaningful dynamics in the system.



# Q2.1.4

# Plot the shape of the oscillating electromechanical modes and describe the mode characteristics
# inter-area mode or local mode?). Explain how the plots should be interpreted. Hint: in order to
# plot the modes, the function plot_phasor() can be used. The function can be found in the
# file-sharing folder on Learn.)


from Assignment_helpfunctions_part_I.plot_phasor_diagram_sss import plot_phasors
import matplotlib.pyplot as plt

plot_phasors(Participation[:, 16:23], ['r', 'g', 'b', 'c', 'm', 'y', "k"], [f"Mode {i+1}" for i in range(16, 23)])



# Q2.1.5

# Plot the linearized time response of all four rotor angles when only the inter area mode is excited.
# How is the mode shape related to the time response?


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


rotor_idx = [0, 7, 14, 21]                   # rotor angle states of G1..G4
rotor_idx = [16, 17, 18, 19]
k = 20                                       # inter-area mode (use lambdas[20], conj is lambdas[21])
print(lambdas[k], lambdas[k].imag / (2*np.pi), "Hz")

# --- Scale the mode so the largest rotor angle starts at delta0
delta0 = 5 * np.pi / 180
v = Phi[:, k]
v = v / v[rotor_idx][np.argmax(np.abs(v[rotor_idx]))]   # normalise: largest angle component is real (phase 0)
v = v * delta0
x0 = v.real                                  # initial condition that excites ONLY this mode

# --- Simulate the linear system
t = np.linspace(0, 5, 1000)
sol = solve_ivp(lambda t, x: A @ x, (0, 5), x0, t_eval=t, rtol=1e-9, atol=1e-12)

# --- Plot the four rotor angles
names = ["G1", "G2", "G3", "G4"]
plt.figure(figsize=(10, 6))
for n, i in zip(names, rotor_idx):
    plt.plot(sol.t, np.degrees(sol.y[i]), label=n)

# Optional check: analytic modal response should lie on top of the simulation
x_modal = (v[:, None] * np.exp(lambdas[k] * t)[None, :]).real
for i in rotor_idx:
    plt.plot(t, np.degrees(x_modal[i]), 'k:', lw=1)

plt.title(f"Rotor angles, inter-area mode only (f = {lambdas[k].imag/(2*np.pi):.3f} Hz)")
plt.xlabel("Time (s)")
plt.ylabel("Δδ (deg)")
plt.grid()
plt.legend()
plt.show()

# --- Mode shape (rotor angle components)
ms = v[rotor_idx]
for n, c in zip(names, ms):
    print(f"{n}: |v| = {abs(c)/delta0:.3f}, phase = {np.degrees(np.angle(c)):.1f}°")





# In this part of the assignment, you are asked to design power system stabilizers to improve the small
# signal stability of the initial system. The aim is to achieve a minimum damping ratio of 10% for every
# electromechanical mode in the system.


# Q.2.2.1

# Use participation factors and residues to identify suitable locations for installing power system
# stabilizers. Keep in mind that there may be both local and interarea modes with insufficient
# damping. This needs to be considered when choosing appropriate locations. Identify three lo-
# cations that you will use further on. Hint: use Identify_PSS_locations_help code
# provided on Learn

# Using speed as the feedback variable connected to the voltage reference input
speed_indices = np.asarray(strsps["speed"].item(), dtype=int).ravel() - 1
vref_indices = np.asarray(strsps["vref"].item(), dtype=int).ravel() - 1
modes = range(16,19)

# make a matrix with 4 rows, and 4*3 columns
n_speed = len(speed_indices)
n_vref = len(vref_indices)
res_matrix = np.zeros((n_speed, n_vref * len(modes)))   # (4, 12)

Phi_inv = np.linalg.inv(Phi)   # compute once

for k, i in enumerate(modes):
    obs = C[speed_indices, :] @ Phi[:, i]          # (4,) observability of mode i at the speed outputs
    ctr = Phi_inv[i, :] @ B[:, vref_indices]       # (4,) controllability of mode i from the vref inputs

    res = np.outer(obs, ctr)                       # (4, 4) residue of mode i
    res_matrix[:, k*n_vref:(k+1)*n_vref] = np.abs(res)

res_matrix_sum = np.sum(res_matrix, axis=1)   # sum over all modes for each speed index 
# We want to investigate G1, G2 and G3, since they have the greatest residues for the inter-area mode



# Q.2.2.2

# Use the Python-control library to obtain the phase response of the system for the frequency
# range of the electromechanical modes. Hint: use the code PSS_design_help.py provided
# on Learn.
import control.statesp as stsp

generator = 4   # generator 2,3, or 4

# 2) Lookup tables -> input/output indices of this generator (0-based)
vref_idx = int(np.ravel(strsps["vref"].item()[generator-1])[0]) - 1
pe_idx   = int(np.ravel(strsps["pe"].item()[generator-1])[0]) - 1

# 3) Eliminate rotor angle and speed states
names = np.char.strip(np.asarray(StateName, dtype=str))
keep  = ~((names == "angle") | (names == "speed"))      # boolean mask, 20 states left

A_red   = A[np.ix_(keep, keep)]            # 20x20
B_siso  = B[keep, vref_idx].reshape(-1, 1) # 20x1
C_siso  = C[pe_idx, keep].reshape(1, -1)   # 1x20
D_siso  = D[pe_idx, vref_idx].reshape(1, 1)# 1x1

sys_red = stsp.StateSpace(A_red, B_siso, C_siso, D_siso)

# 4) Frequency response over the electromechanical range (~0.1 - 3000 Hz)
f = np.logspace(np.log10(0.1), np.log10(2), 300)
w = 2 * np.pi * f
mag, phase, omega = sys_red.frequency_response(w, squeeze=None)
phase_sys = np.degrees(np.unwrap(np.squeeze(phase)))

# 5) PSS transfer function (textbook start values)
Kstab, Tw, Tn1, Td1, Tn2, Td2 = 20.0, 10.0, 0.05, 0.02, 3.0, 5.4
s = 1j * w
H_pss = Kstab * (s*Tw/(1 + s*Tw)) * ((1 + s*Tn1)/(1 + s*Td1)) * ((1 + s*Tn2)/(1 + s*Td2))
phase_pss = np.degrees(np.unwrap(np.angle(H_pss)))

# 6) Plot: the PSS phase should roughly mirror the plant's phase lag
plt.figure(figsize=(9, 5))
plt.semilogx(f, phase_sys, label=f"Reduced system Vref→Pe (G{generator})")
plt.semilogx(f, -phase_sys, '--', label="–(system phase) = ideal PSS phase")
plt.semilogx(f, phase_pss, label="PSS (initial settings)")
plt.axhline(0, color='k', lw=0.5)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Phase (deg)")
plt.title(f"Phase response, generator {generator}")
plt.grid(True, which="both")
plt.legend()
plt.show()


# Q.2.2.3

# Identify suitable values for the phase compensation Tn1,Td1,Tn2,Td2 that maximize the effi-
# ciency of the PSS across the relevant frequency range. The gain of the stabilizer is fixed to
# Kstab = 20 and the time constant of the washout filter Tw should be in the range 10s ≤ Tw ≤
# 30s. As a starting point use the settings provided in the textbook:
# Kstab = 20.0, Tw = 10.0, Tn1 = 0.05, Td1 = 0.02, Tn2 = 3.0, Td2 = 5.4

Tw = 10.0
Tn1 = 0.10
Td1 = 0.01
Tn2 = 3.0
Td2 = 5.0
H_pss_new = Kstab * (s*Tw/(1 + s*Tw)) * ((1 + s*Tn1)/(1 + s*Td1)) * ((1 + s*Tn2)/(1 + s*Td2))
phase_pss_new = np.degrees(np.unwrap(np.angle(H_pss_new)))
plt.figure(figsize=(9, 5))
plt.semilogx(f, -phase_sys, '--', label="–(system phase) = ideal PSS phase")
plt.semilogx(f, phase_pss_new, label=f"PSS (value={Td1})")
plt.axhline(0, color='k', lw=0.5)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Phase (deg)")
plt.title(f"Phase response, generator {generator}")
plt.grid(True, which="both")
plt.legend()
plt.show()

# Q.2.2.4

# Test the performance of your solution by: (Use Add_PSS_help.py for this part)
# 1. Adding only a single stabilizer to the system. Repeat this process for each of your chosen
# locations and compare the system performance. Discuss the differences in performance in
# terms of which modes are affected and how their damping is affected depending on the
# location

""" Add a PSS to the system """
"""############################################################################

Form a PSS state space object "pss" based on the desired settings
Add the pss object to an existing state space system "sys"
The function "pss_sys=addPSS(sys,pss,strsps,gen)" in stsp_functions.py returns a new state space system "pss_sys" 
where the PSS is added to machine "gen".

If another PSS should be added the function can be called again using the system that already contains 
a pss as input. For example: "pss2_sys=addPSS(pss_sys,pss2,strsps,gen2)"

############################################################################"""

# Form a PSS state space object "pss" based on the desired settings


from Assignment_helpfunctions_part_II import stsp_functions as sf
PSS = sf.pss_stsp(Kstab, Tw, Tn1, Td1, Tn2, Td2)
sys = stsp.StateSpace(A, B, C, D)
generator = 4
pss_sys = sf.addPSS(sys, PSS, strsps, generator)

import control as ct

def siso_channel(sys_, g):
    """Vref -> Pe channel of generator g (same indices in base and PSS systems)."""
    vref_i = int(np.ravel(strsps["vref"].item()[g-1])[0]) - 1
    pe_i   = int(np.ravel(strsps["pe"].item()[g-1])[0]) - 1
    return sys_[pe_i, vref_i]

t = np.linspace(0, 15, 3000)
sys = stsp.StateSpace(A, B, C, D)
PSS = sf.pss_stsp(Kstab, Tw, Tn1, Td1, Td1 and Tn2, Td2) if False else sf.pss_stsp(Kstab, Tw, Tn1, Td1, Tn2, Td2)

gens = [2, 3, 4]   # your chosen generators

fig, axs = plt.subplots(len(gens), 1, figsize=(10, 3.2*len(gens)), sharex=True)
for ax, g in zip(np.atleast_1d(axs), gens):
    # Base system and system with PSS at generator g
    T, y_base = ct.step_response(siso_channel(sys, g), t)
    pss_sys   = sf.addPSS(sys, PSS, strsps, g)
    T, y_pss  = ct.step_response(siso_channel(pss_sys, g), t)

    ax.plot(T, y_base, label="No PSS")
    ax.plot(T, y_pss,  label=f"PSS at G{g}")
    ax.set_ylabel(f"ΔPe G{g} (p.u.)")
    ax.grid(True); ax.legend()
np.atleast_1d(axs)[-1].set_xlabel("Time (s)")
plt.suptitle("Step response Vref → Pe, base vs. PSS")
plt.tight_layout(); plt.show()

# 2. Adding two of your stabilizers to the system. Are these two stabilizers enough to damp all
# electromechanical system modes?

fig, axs = plt.subplots(len(gens), 1, figsize=(10, 3.2*len(gens)), sharex=True)
for ax, g in zip(np.atleast_1d(axs), gens):
    # Base system and system with PSS at generator g
    T, y_base = ct.step_response(siso_channel(sys, g), t)
    pss_sys   = sf.addPSS(sys, PSS, strsps, g)
    if g == 2:
        pss_sys2 = sf.addPSS(pss_sys, PSS, strsps, 3)
    if g == 3:
        pss_sys2 = sf.addPSS(pss_sys, PSS, strsps, 4)
    if g == 4:
        pss_sys2 = sf.addPSS(pss_sys, PSS, strsps, 2)
    T, y_pss  = ct.step_response(siso_channel(pss_sys2, g), t)

    ax.plot(T, y_base, label="No PSS")
    ax.plot(T, y_pss,  label=f"PSS at G{g}")
    ax.set_ylabel(f"ΔPe G{g} (p.u.)")
    ax.grid(True); ax.legend()
np.atleast_1d(axs)[-1].set_xlabel("Time (s)")
plt.suptitle("Step response Vref → Pe, base vs. PSS")
plt.tight_layout(); plt.show()
# 3. Comparing the small signal stability of the system using your stabilizers with the perfor-
# mance of stabilizers in the same locations using the initial values provided in Q.2.2.3.

Kstab, Tw, Tn1, Td1, Tn2, Td2 = 20.0, 10.0, 0.05, 0.02, 3.0, 5.4
# Kstab, Tw, Tn1, Td1, Tn2, Td2 = 20.0, 10.0, 0.10, 0.01, 3.0, 5.0
PSS = sf.pss_stsp(Kstab, Tw, Tn1, Td1, Td1 and Tn2, Td2) if False else sf.pss_stsp(Kstab, Tw, Tn1, Td1, Tn2, Td2)
fig, axs = plt.subplots(len(gens), 1, figsize=(10, 3.2*len(gens)), sharex=True)
for ax, g in zip(np.atleast_1d(axs), gens):
    # Base system and system with PSS at generator g
    T, y_base = ct.step_response(siso_channel(sys, g), t)
    pss_sys   = sf.addPSS(sys, PSS, strsps, g)
    if g == 2:
        pss_sys2 = sf.addPSS(pss_sys, PSS, strsps, 3)
    if g == 3:
        pss_sys2 = sf.addPSS(pss_sys, PSS, strsps, 4)
    if g == 4:
        pss_sys2 = sf.addPSS(pss_sys, PSS, strsps, 2)
    T, y_pss  = ct.step_response(siso_channel(pss_sys2, g), t)

    ax.plot(T, y_base, label="No PSS")
    ax.plot(T, y_pss,  label=f"PSS at G{g}")
    ax.set_ylabel(f"ΔPe G{g} (p.u.)")
    ax.grid(True); ax.legend()
np.atleast_1d(axs)[-1].set_xlabel("Time (s)")
plt.suptitle("Step response Vref → Pe, base vs. PSS")
plt.tight_layout(); plt.show()
# A function adding power system stabilizers to the A matrix will be provided as part of the help
# files.


# Q.2.2.5 

# Plot the time response of all four rotor angles for your final solution when only the inter area
# mode is excited. Discuss the effect of the power system stabilizer when comparing this plot to
# the one from Q.2.1.5

Kstab, Tw, Tn1, Td1, Tn2, Td2 = 20.0, 10.0, 0.10, 0.01, 3.0, 5.0
PSS_final = sf.pss_stsp(Kstab, Tw, Tn1, Td1, Tn2, Td2)

final_gens = [2, 3]

sys = stsp.StateSpace(A, B, C, D)
pss_final = sys
for g in final_gens:
    pss_final = sf.addPSS(pss_final, PSS_final, strsps, g)

A_pss = pss_final.A
n_pss = A_pss.shape[0] - A.shape[0]            # 3 states per PSS

# Same initial condition as Q2.1.5, PSS states start at zero
x0_pss = np.concatenate([x0, np.zeros(n_pss)])

time = 20
t = np.linspace(0, time, 1000)                    # same window as Q2.1.5
sol_pss = solve_ivp(lambda t, x: A_pss @ x, (0, time), x0_pss,
                    t_eval=t, rtol=1e-9, atol=1e-12)
sol = solve_ivp(lambda t, x: A @ x, (0, time), x0, t_eval=t, rtol=1e-9, atol=1e-12)


# --- Plot: rotor angles with PSS (solid) vs. without PSS (dashed)
colors = ['C0', 'C1', 'C2', 'C3']
plt.figure(figsize=(10, 6))
for n, i, c in zip(names, rotor_idx, colors):
    plt.plot(sol_pss.t, np.degrees(sol_pss.y[i]), color=c, label=f"{n} with PSS")
    plt.plot(sol.t,     np.degrees(sol.y[i]),     color=c, ls='--', lw=1, label=f"{n} no PSS")
plt.title(f"Rotor angles, inter-area mode excited, PSS at {', '.join('G'+str(g) for g in final_gens)}")
plt.xlabel("Time (s)"); plt.ylabel("Δδ (deg)")
plt.grid(); plt.legend(ncol=2); plt.show()