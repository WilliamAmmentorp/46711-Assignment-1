# -*- coding: utf-8 -*-

from pathlib import Path

import numpy as np
import scipy.io as sio


"""Load system data."""
data_file = Path(__file__).resolve().parents[1] / "Assignment_data" / "system_q2.mat"
sys_data = sio.loadmat(data_file, squeeze_me=True)
A = sys_data["A"]
B = sys_data["B"]
C = sys_data["C"]
D = sys_data["D"]
strsps = sys_data["strsps"]
statename = np.asarray(sys_data["StateName"], dtype=str)
state_labels = np.asarray(sys_data.get("names_q2a", statename), dtype=str)


"""Determine eigenvalues, eigenvectors, and the participation matrix."""
eigenvalues, right_eigenvectors = np.linalg.eig(A)
left_eigenvectors = np.linalg.inv(right_eigenvectors)

# P_ik = v_ik * w_ki, where v is a right eigenvector and w is a left
# eigenvector. Scale each mode by its largest participation factor.
participation_matrix = right_eigenvectors * left_eigenvectors.T
participation_magnitude = np.abs(participation_matrix)
maximum_participation = np.max(participation_magnitude, axis=0)
normalized_participation = np.divide(
    participation_magnitude,
    maximum_participation,
    out=np.zeros_like(participation_magnitude),
    where=maximum_participation != 0,
)


"""Find the relevant input and output indices in the original system."""
def matlab_indices(field_name):
    """Return zero-based indices stored in a MATLAB `strsps` field."""
    indices = np.asarray(strsps[field_name].item(), dtype=int).ravel()
    return indices[indices > 0] - 1


speed_indices = matlab_indices("speed")
vref_indices = matlab_indices("vref")
if speed_indices.size == 0 or vref_indices.size == 0:
    raise ValueError("The system data must contain speed outputs and vref inputs.")


"""Reduce the analysis to electromechanical modes."""
electromechanical_state_mask = np.isin(statename, ["angle", "speed"])
electromechanical_participation = np.max(
    normalized_participation[electromechanical_state_mask, :],
    axis=0,
)
frequencies_hz = np.abs(np.imag(eigenvalues)) / (2 * np.pi)

# Keep both members of each complex-conjugate pair. The frequency range
# excludes zero-frequency and non-electromechanical control modes.
electromechanical_mode_mask = (
    (frequencies_hz >= 0.1)
    & (frequencies_hz <= 2.0)
    & (electromechanical_participation >= 0.1)
)
electromechanical_mode_indices = np.flatnonzero(electromechanical_mode_mask)
reduced_participation = normalized_participation[
    :, electromechanical_mode_indices
]


"""Calculate transfer-function residues."""
# For mode k, the residue from input j to output i is
# (C_i v_k) (w_k B_j), where w_k is row k of the inverse eigenvector matrix.
# The result is indexed as [output, input, mode].
output_modal_vectors = C @ right_eigenvectors
input_modal_vectors = left_eigenvectors @ B
residues = (
    output_modal_vectors[:, np.newaxis, :]
    * input_modal_vectors.T[np.newaxis, :, :]
)
speed_vref_residues = residues[
    np.ix_(speed_indices, vref_indices, electromechanical_mode_indices)
]
residue_magnitude = np.abs(speed_vref_residues)
residue_scale = np.max(residue_magnitude, axis=(0, 1))
normalized_speed_vref_residues = np.divide(
    residue_magnitude,
    residue_scale,
    out=np.zeros_like(residue_magnitude),
    where=residue_scale != 0,
)


def print_mode_summary():
    """Print modes and generator locations useful for PSS placement."""
    print("Electromechanical modes:")
    for mode_index in electromechanical_mode_indices:
        damping = -np.real(eigenvalues[mode_index]) / abs(eigenvalues[mode_index])
        dominant_indices = np.flatnonzero(
            normalized_participation[:, mode_index] >= 0.3
        )
        dominant_states = ", ".join(state_labels[dominant_indices])
        print(
            f"  mode {mode_index + 1:2d}: "
            f"lambda={eigenvalues[mode_index]: .5f}, "
            f"f={frequencies_hz[mode_index]:.3f} Hz, "
            f"zeta={damping:.3f}; "
            f"states: {dominant_states or 'none'}"
        )

    print("\nNormalized speed-to-vref residue magnitudes:")
    for reduced_mode, mode_index in enumerate(electromechanical_mode_indices):
        print(f"  mode {mode_index + 1}:")
        ranking = np.argsort(
            normalized_speed_vref_residues[:, :, reduced_mode].ravel()
        )[::-1]
        for flat_index in ranking[:3]:
            speed_position, vref_position = np.unravel_index(
                flat_index,
                normalized_speed_vref_residues[:, :, reduced_mode].shape,
            )
            print(
                f"    speed G{speed_position + 1} / vref G{vref_position + 1}: "
                f"{normalized_speed_vref_residues[speed_position, vref_position, reduced_mode]:.3f}"
            )


print_mode_summary()
