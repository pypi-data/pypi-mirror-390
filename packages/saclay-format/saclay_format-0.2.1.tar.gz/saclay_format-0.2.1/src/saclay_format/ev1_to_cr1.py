#!/usr/bin/env python3
import sys, os
import numpy as np

from saclay_parser import read, write

def kramers_partner(states):
    """
    Construct Kramers partners for 2-spinor wavefunctions:
        psi_T = i sigma_y psi* -> ( psi_down*, -psi_up* )
    Input shape:  (nx, ny, nz, 2, nw)
    Output shape: (nx, ny, nz, 2, nw)
    """
    conj = np.conjugate(states)
    up   = conj[..., 0, :]
    dn   = conj[..., 1, :]
    partner = np.empty_like(states)
    partner[..., 0, :] = dn
    partner[..., 1, :] = -up
    return partner

def check_orthonormality(states, tol=1e-10):
    """
    Check orthonormality of a set of wavefunctions.
    states: shape (nx, ny, nz, 2, nw)
    """
    nx, ny, nz, _, nw = states.shape
    flat = states.reshape(-1, nw)  # (nx*ny*nz*2, nw)
    overlaps = flat.conj().T @ flat  # Gram matrix (nw, nw)
    # Normalize
    norms = np.sqrt(np.real(np.diag(overlaps)))
    overlaps = overlaps / (norms[:, None] * norms[None, :])
    deviation = np.max(np.abs(overlaps - np.eye(nw)))
    print("Max deviation from orthonormality: {:.2e}".format(deviation))
    if deviation > tol:
        print("Warning: orthonormality check FAILED")
    else:
        print("Orthonormality OK")

def interleave_with_partners(states, partners):
    """
    Interleave original states and their Kramers partners along the last axis:
    [1,2,...,N] + [1*,2*,...,N*] -> [1,1*,2,2*,...,N,N*]
    """
    shape = list(states.shape)
    shape[-1] *= 2  # double last axis
    interleaved = np.empty(shape, dtype=states.dtype)
    interleaved[..., ::2] = states
    interleaved[..., 1::2] = partners
    return interleaved


def interleave_amplitudes(arr):
    # arr: shape (N, ...)
    conj = np.conjugate(arr)
    shape = list(arr.shape)
    shape[0] *= 2
    interleaved = np.empty(shape, dtype=arr.dtype)
    interleaved[::2] = arr
    interleaved[1::2] = conj
    return interleaved

def ev1_to_cr1(data):
    """
    Translate EV1 dataset into CR1 by doubling wavefunctions.
    Only wavefunctions and metadata are modified.
    """
    md    = data["metadata"].copy()
    wf_md = md.get("wavefunction", {}).copy()

    nw_n = wf_md["n_neutron_states"]
    nw_p = wf_md["n_proton_states"]

    # Build Kramers partners
    statesn = data["statesn"]
    statesp = data["statesp"]
    pn = kramers_partner(statesn)
    pp = kramers_partner(statesp)

    statesn_cr1 = interleave_with_partners(statesn, pn)
    statesp_cr1 = interleave_with_partners(statesp, pp)

    # Bogoliubov amplitudes
    un = data["un"]; vn = data["vn"]
    up = data["up"]; vp = data["vp"]

    un_cr1 = interleave_amplitudes(un)
    vn_cr1 = interleave_amplitudes(vn)
    up_cr1 = interleave_amplitudes(up)
    vp_cr1 = interleave_amplitudes(vp)

    # Update metadata
    md["symmetry"] = "cr1"
    md["prefix"]   = md.get("prefix", "run") + "_cr1"
    wf_md["n_neutron_states"] = 2 * nw_n
    wf_md["n_proton_states"]  = 2 * nw_p
    md["wavefunction"] = wf_md

    cr1_data = data.copy()
    cr1_data['metadata'] = md
    cr1_data['statesn']  = statesn_cr1
    cr1_data['statesp']  = statesp_cr1
    cr1_data['un']       = un_cr1
    cr1_data['vn']       = vn_cr1
    cr1_data['up']       = up_cr1
    cr1_data['vp']       = vp_cr1

    return cr1_data

def sort_by_occupation(data):
    """
    Sort states and Bogoliubov amplitudes by descending occupation number.
    Occupation is |v|^2 summed over all spatial and spin coordinates.
    """
    vn = data["vn"]
    vp = data["vp"]

    occ_n = np.sum(np.abs(vn)**2, axis=tuple(range(1, vn.ndim)))  # shape (N_n,)
    occ_p = np.sum(np.abs(vp)**2, axis=tuple(range(1, vp.ndim)))  # shape (N_p,)

    idx_n = np.argsort(-occ_n)  # descending
    idx_p = np.argsort(-occ_p)

    # Sort all neutron-related arrays
    data["statesn"] = data["statesn"][..., idx_n]
    data["un"] = data["un"][idx_n]
    data["vn"] = data["vn"][idx_n]

    # Sort all proton-related arrays
    data["statesp"] = data["statesp"][..., idx_p]
    data["up"] = data["up"][idx_p]
    data["vp"] = data["vp"][idx_p]

    return data
    
    
#----------------------------------------------------------
#----------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import os
    import sys

    description = "Translate EV1 dataset into CR1 (no symmetry)"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "input",
        help="Input file (.yaml/.yml or .h5/.hdf5)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file name (.yaml/.yml or .h5/.hdf5). Default: overwrite input"
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["yaml", "yml", "hdf5", "h5"],
        help="Output format (default: same as input)"
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or input_path
    output_format = args.format

    if not os.path.exists(input_path):
        print(f"Input file '{input_path}' not found.")
        sys.exit(1)

    # --- Determine input format ---
    ext = os.path.splitext(input_path)[1].lower()
    if ext in (".yaml", ".yml"):
        input_format = "yaml"
    elif ext in (".h5", ".hdf5"):
        input_format = "hdf5"
    else:
        print(f"Unsupported input file extension '{ext}'.")
        sys.exit(1)

    # --- Default output format same as input ---
    if output_format is None:
        output_format = input_format

    # --- Prevent invalid conversion YAML -> HDF5 ---
    if input_format == "yaml" and output_format in ("hdf5", "h5"):
        print("ERROR: cannot convert YAML input directly to HDF5. Aborting.")
        sys.exit(1)

    # --- Read input ---
    data_all = read(input_path)

    sym = data_all["metadata"].get("symmetry", "").lower()
    if sym != "ev1":
        print(f"Symmetry is '{sym}', not 'ev1'. Aborting.")
        sys.exit(1)

    print("\n--- Input (EV1) ---")
    wf_meta = data_all["metadata"]["wavefunction"]
    print(f"Prefix: {data_all['metadata'].get('prefix')}")
    print(f"Neutron states: {wf_meta['n_neutron_states']}")
    print(f"Proton states: {wf_meta['n_proton_states']}")

    # --- Translation EV1 -> CR1 ---
    data_cr1 = ev1_to_cr1(data_all)
    # data_cr1 = sort_by_occupation(data_cr1)  # optional

    # --- Update prefix to match output ---
    output_dir = os.path.dirname(output_path) or "."
    output_base = os.path.basename(output_path)
    new_prefix = os.path.splitext(output_base)[0]
    data_cr1["metadata"]["prefix"] = new_prefix

    # --- Ensure file extension matches chosen format ---
    out_ext = os.path.splitext(output_path)[1].lower()
    if not out_ext:
        if output_format in ("yaml", "yml"):
            output_path += ".yaml"
        elif output_format in ("hdf5", "h5"):
            output_path += ".h5"

    # --- Write output ---
    print(f"\nWriting to '{output_path}' ({output_format} format)")
    write(data_cr1, output_path)

    print("\n--- Output (CR1) ---")
    wf_meta = data_cr1["metadata"]["wavefunction"]
    print(f"Prefix: {data_cr1['metadata'].get('prefix')}")
    print(f"Neutron states: {wf_meta['n_neutron_states']}")
    print(f"Proton states: {wf_meta['n_proton_states']}")

    # --- Check orthonormality ---
    print("\nChecking neutron states:")
    check_orthonormality(data_cr1["statesn"])
    print("Checking proton states:")
    check_orthonormality(data_cr1["statesp"])
