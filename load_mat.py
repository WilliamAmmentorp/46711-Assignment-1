
# File for loading the system data from the .mat file
import scipy.io as sio
import numpy as np

path = r"C:\Users\willi\OneDrive\Dokumenter\.DTU\Stability\46711-Assignment-1\Assignment_data"

files = ["system_q1a.mat", "system_q1b.mat", "system_q1c.mat", "system_q2.mat"]

# Load the files and print
q1a_data = sio.loadmat(f"{path}/{files[0]}", squeeze_me=True)
print(q1a_data)


# Q1.1.1

A = q1a_data['A_q1a']
latex_names = q1a_data['latex_names_q1a']
names_q1a = q1a_data['names_q1a']
print("A matrix for q1a:")
print(A)

import numpy as np

def find_eigenvalues(A):
    # Calculate eigenvalues using numpy
    eigenvalues, right_eigenvectors = np.linalg.eig(A)
    return eigenvalues, right_eigenvectors

lambda_A, _ = find_eigenvalues(A)

# Two complex lambdas are given: lambda[2] and lambda[4] with complex conjugate pairs.
# Find the frequency and damping ratio

def find_frequency_and_damping(lambda_value):
    frequency = np.imag(lambda_value) / (2 * np.pi)
    damping_ratio = -np.real(lambda_value) / np.sqrt(np.real(lambda_value)**2 + np.imag(lambda_value)**2)
    return frequency, damping_ratio

f_A2, omega_A2 = find_frequency_and_damping(lambda_A[2])
f_A4, omega_A4 = find_frequency_and_damping(lambda_A[4])



# Q1.2.1
# Load the files and print
q1b_data = sio.loadmat(f"{path}/{files[1]}", squeeze_me=True)
print(q1b_data)

A1b = q1b_data['A_q1b']
lambda_A1b, Phi_A1b = find_eigenvalues(A1b)
f_A1b2, omega_A1b2 = find_frequency_and_damping(lambda_A1b[2])
f_A1b6, omega_A1b6 = find_frequency_and_damping(lambda_A1b[6])

Psi_A1b = np.linalg.inv(Phi_A1b)

Participation_A1b = np.multiply(Phi_A1b, Psi_A1b.T)
state_labels_A1b = q1b_data['latex_names_q1b']
from Assignment_helpfunctions_part_I.P_matrix_write import latex_P_matrix

matrix = latex_P_matrix(Participation_A1b, state_labels_A1b, False, "latex_P_matrix_q1b.tex", 4, 0.1)

# Q1.3.1
q1c_data = sio.loadmat(f"{path}/{files[2]}", squeeze_me=True)
print(q1c_data)
A1c = q1c_data['A_q1c']
lambda_A1c, Phi_A1c = find_eigenvalues(A1c)

f_A1c4, omega_A1c4 = find_frequency_and_damping(lambda_A1c[4])
f_A1c7, omega_A1c7 = find_frequency_and_damping(lambda_A1c[7])

# Q1.3.2

def plot_time_response(matrix, initial_angle, time_interval, title):
    from scipy.integrate import solve_ivp
    import matplotlib.pyplot as plt

    initial_condition = np.zeros(matrix.shape[0])
    initial_condition[0] = initial_angle

    def system_dynamics(t, y):
        return matrix @ y

    t_span = (time_interval[0], time_interval[1])
    t_eval = np.linspace(time_interval[0], time_interval[1], 1000)

    solution = solve_ivp(system_dynamics, t_span, initial_condition, t_eval=t_eval)

    plt.figure(figsize=(10, 6))
    plt.plot(solution.t, solution.y[0], label='Δδ (Rotor Angle)')
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Δδ (rad)')
    plt.grid()
    plt.legend()
    plt.show()

t0 = 0
delta0 = 5 * np.pi / 180  # Convert degrees to radians
deltat = 5  # seconds
for matrix, label in zip([A, A1b, A1c], ["System A", "System B", "System C"]):
    plot_time_response(matrix, delta0, (t0, deltat), f"Time Response for {label}")