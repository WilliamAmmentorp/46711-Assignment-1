# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 10:35:21 2026

@author: Jespe
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def plot_step_response(A_manual, A_avr, A_avr_pss, total_time):
    
    # Time vector: 0 to 5 seconds
    t = np.linspace(0, total_time, 1000)
    
    # Define initial conditions and delta_index for each case
    # Assume Δδ is the first state in all cases
    delta_index_manual = 0
    delta_index_avr = 0
    delta_index_avr_pss = 0
    
    # Initial condition: Δδ(0) = 5° = 0.087266 rad
    x0_manual = np.zeros(6)
    x0_manual[delta_index_manual] = 0.087266
    
    x0_avr = np.zeros(9)
    x0_avr[delta_index_avr] = 0.087266
    
    x0_avr_pss = np.zeros(13)
    x0_avr_pss[delta_index_avr_pss] = 0.087266
    
    # Simulate and plot Δδ for all three cases
    plt.figure()

    for case_name, A, x0, delta_index in [
        ("Manual Excitation", A_manual, x0_manual, delta_index_manual),
        ("AVR Only", A_avr, x0_avr, delta_index_avr),
        ("AVR + PSS", A_avr_pss, x0_avr_pss, delta_index_avr_pss)
    ]:

        # State-space equation: dx/dt = A*x
        def state_derivative(time, x):
            return A @ x

        # Numerically solve the state equations
        sol = solve_ivp(
            state_derivative,
            [t[0], t[-1]],
            x0,
            t_eval=t
        )

        # Extract Δδ
        delta_response = sol.y[delta_index, :]

        # Plot Δδ
        plt.plot(t, delta_response, label=case_name)
    
    plt.title("Time Response of Δδ for All Three Cases")
    plt.xlabel("Time [s]")
    plt.ylabel("Δδ [rad]")
    plt.legend()
    plt.grid()
    plt.show()

    return