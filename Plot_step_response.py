# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 10:35:21 2026

@author: Jespe
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def plot_step_response(A_manual, A_avr, A_avr_pss, total_time):

    # Time vector
    t = np.arange(0, total_time, 0.001)

    # Initial condition: Δδ(0) = 5° = 0.087266 rad
    delta_index = 0   # Δδ is the first state in all three cases

    x0_manual = np.zeros(6)
    x0_manual[delta_index] = 0.087266

    x0_avr = np.zeros(9)
    x0_avr[delta_index] = 0.087266

    x0_avr_pss = np.zeros(13)
    x0_avr_pss[delta_index] = 0.087266

    plt.figure()

    for case_name, A, x0 in [
        ("Manual Excitation", A_manual, x0_manual),
        ("AVR Only", A_avr, x0_avr),
        ("AVR + PSS", A_avr_pss, x0_avr_pss)
    ]:
        lamb, Phi = np.linalg.eig(A)   # eigenvalues, right eigenvectors
        Psi = np.linalg.inv(Phi)       # left eigenvector matrix

        xt = np.zeros((len(x0), len(t)), dtype=complex)
        for k in range(len(t)):
            xt[:, k] = Phi.dot(np.exp(lamb*t[k]) * Psi.dot(x0))

        # Plot Δδ (real part — xt is complex)
        plt.plot(t, xt[delta_index, :].real, label=case_name)

    plt.title("Time Response of Δδ for All Three Cases")
    plt.xlabel("Time [s]")
    plt.ylabel("Δδ [rad]")
    plt.legend()
    plt.grid()
    plt.show()

    return
