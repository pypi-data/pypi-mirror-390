#!/usr/bin/env python3
import sys, os, glob
import numpy as np
from saclay_parser import read, write
import math

def Complete_3D(nx,ny,nz,  F, symx = 1 , symy = 1, symz = 1):
  '''

    Obtain values for the function f in a complete box, starting from
    EV8-like values passed in.
    Input:
    -------
    nx,ny,nz    : mesh parameters
    F           : function values at said mesh coordinates
    symx        : sign obtained under x-reversal
    symy        : sign obtained under y-reversal
    symz        : sign obtained under z-reversal
    Output:
    -------
    complete    : array with all coordinates and function
                  values in the entire box.
  '''

  if(abs(symx) == 1):
      newx = 2*nx
  elif(abs(symx) == 0):
    newx =   nx
  else:
    raise ValueError

  if(abs(symy) == 1):
    newy = 2*ny
  elif(abs(symy) == 0):
    newy =   ny
  else:
    raise ValueError

  if(abs(symz) == 1):
    newz   = 2*nz
    offz   =   nz
  elif(abs(symz) == 0):
    newz =   nz
    offz =    0
  else:
    raise ValueError

  complete = np.zeros((newx, newy, newz))
  # Ordinary quadrant
  complete[nx:,ny:,offz:] = F

  # (x,y,z) => (-x,y,z)
  complete[  :nx,ny:,offz:] =  np.flip(F, axis=0) * symx
  # (x,y,z) => (x,-y,z)
  complete[nx:  ,  :ny,offz:] =  np.flip(F, axis=1) * symy
  # (x,y,z) => (x,y,-z)
  if(symz != 0):
    complete[nx:  ,ny:  ,  :nz] =  np.flip(F, axis=2)  * symz
  # (x,y,z) => (-x,-y,z)
  complete[  :nx,  :ny,offz:] =  np.flip(F, axis=(0,1)) * symx * symy
  if(symz != 0):
    # (x,y,z) => (-x, y,-z)
    complete[  :nx,ny:  ,:nz] =  np.flip(F, axis=(0,2)) * symx * symz
    # (x,y,z) => (x,-y,-z)
    complete[nx:,  :ny,:nz] =  np.flip(F, axis=(1,2))* symy * symz
    # (x,y,z) => (-x,-y,-z)
    complete[  :nx,  :ny,:nz] =  np.flip(F, axis=(0,1,2)) * symx * symy * symz

  return complete

def get_EV8_symmetries_spwfs():
    '''
        Obtain the symmetry properties of the spwfs as coded in MOCCa.

        Input:
            None
        Output:
            sx, sy, sz : (4,4) arrays with the symmetry properties of the 4
                        components of the spwfs in the 4 blocks. 
    '''

    sx = np.zeros((4,4))
    sy = np.zeros((4,4))
    sz = np.zeros((4,4))

    # BLOCK = 1
    sx[0,0] =  1 ; sy[0,0] = +1 ; sz[0,0] = +1
    sx[1,0] = -1 ; sy[1,0] = -1 ; sz[1,0] = +1
    sx[2,0] = -1 ; sy[2,0] = +1 ; sz[2,0] = -1
    sx[3,0] =  1 ; sy[3,0] = -1 ; sz[3,0] = -1

    # BLOCK 3
    sx[0,2] =  1 ; sy[0,2] = +1 ; sz[0,2] = -1
    sx[1,2] = -1 ; sy[1,2] = -1 ; sz[1,2] = -1
    sx[2,2] = -1 ; sy[2,2] = +1 ; sz[2,2] = +1
    sx[3,2] =  1 ; sy[3,2] = -1 ; sz[3,2] = +1

    return sx, sy, sz

def complex_to_real_spwfs(array):
  '''
      Convert complex spwfs to real representation.
      Input:
          array : (nx,ny,nz,2,n_states) complex array
      Output:
          r_array : (nx,ny,nz,4,n_states) real array
  '''

  r_array = np.zeros((array.shape[0], array.shape[1], array.shape[2], 4, array.shape[4]), dtype=np.float64)
  r_array[:,:,:,0,:] = np.real(array[:,:,:,0,:])
  r_array[:,:,:,1,:] = np.imag(array[:,:,:,0,:])
  r_array[:,:,:,2,:] = np.real(array[:,:,:,1,:])
  r_array[:,:,:,3,:] = np.imag(array[:,:,:,1,:])

  return r_array

def real_to_complex_spwfs(array):
  ''' 
      Convert real spwfs to complex representation. 
      Input:
          array : (nx,ny,nz,4,n_states) real array
      Output:
          c_array : (nx,ny,nz,2,n_states) complex array
  '''
  c_array = np.zeros((array.shape[0], array.shape[1], array.shape[2], 2, array.shape[4]), dtype=np.complex128)
  c_array[:,:,:,0,:] = array[:,:,:,0,:] + 1j*array[:,:,:,1,:]
  c_array[:,:,:,1,:] = array[:,:,:,2,:] + 1j*array[:,:,:,3,:]
  return c_array


def convert_array_EV8_EV1(array, nx,ny,nz, symx, symy, symz, nc=1):
    '''
        Convert an array from EV8 symmetry to EV1 symmetries.
        Input:
            array    : (nx,ny,nz) or (nx,ny,nz,nc) array
            nx,ny,nz : mesh parameters, half the values of the full simulation volume
            symx, symy, symz : arrays of length nc with the symmetry properties
                               of each component of the array.
            nc : number of components of the array (default 1)
        Output:
            array : (2*nx,2*ny,2*nz) or (2*nx,2*ny,2*nz,nc) array with 
                    the values of the function in the full simulation volume.
    '''

    # Break the symmetries of the EV8-like mesh to get a full box
    if(nc != 1):
      full_array = np.zeros((2*nx, 2*ny, 2*nz, nc), dtype=array.dtype)
    else:
      full_array = np.zeros((2*nx, 2*ny, 2*nz), dtype=array.dtype)

    if(nc != 1):
      for idx in range(nc):
        full_array[...,idx] = Complete_3D(nx,ny,nz,array[...,idx],symx[idx],sy[idx],sz[idx])
    else:
        full_array = Complete_3D(nx,ny,nz,array,sx[0],sy[0],sz[0])
    array = full_array

    return array

def break_syms_spwfs(states, symblocks, nx,ny,nz):
    '''
    Break the symmetries of the spwfs from EV8 to EV1.
    Input:
        states    : (2,nz,ny,nx,n_states) complex array with the spwfs in the EV8 simulation volume
        symblocks : list of length 4 with the number of states in each MOCCa symmetry block
        nx,ny,nz  : mesh parameters, half the values of the full simulation volume
    Output:
        c_states  : (n_states,2,2*nz,2*ny,2*nx) complex array with the spwfs in the full simulation volume
    '''


    # transform from complex to real representation
    states = complex_to_real_spwfs(states)
    # Get symmetry properties
    sx, sy, sz = get_EV8_symmetries_spwfs()

    c_states = np.zeros((2*nx,2*ny,2*nz,4,states.shape[-1]))

    si = 0
    for B in range(0,4):
      N = symblocks[B]
      for i in range(N):
        for k in range(4):
          c_states[:,:,:,k,si+i] = Complete_3D(nx,ny,nz,states[:,:,:,k,si+i], symx=sx[k,B], symy=sy[k,B], symz=sz[k,B])
          #print (i, np.sum(np.abs(c_states[:,:,:,:,si+i])**2)*data_all['metadata']['dx']**3)
      si = si + N
    # Transfer back to real numbers
    c_states = real_to_complex_spwfs(c_states)

    return c_states



#----------------------------------------------------------
#----------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import os
    import sys
    import numpy as np

    description = "Translate EV8 dataset into EV1 (no spatial symmetry)"
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

    # --- Read data ---
    data_all = read(input_path)

    sym = data_all["metadata"].get("symmetry", "").lower()
    if sym != "ev8":
        print(f"Symmetry is '{sym}', not 'ev8'. Aborting.")
        sys.exit(1)

    print("\n--- Input (EV8) ---")
    wf_meta = data_all["metadata"]["wavefunction"]
    print(f"Prefix: {data_all['metadata'].get('prefix')}")
    print(f"Neutron states: {wf_meta['n_neutron_states']}")
    print(f"Proton states: {wf_meta['n_proton_states']}")

    # --- Copy and modify metadata ---
    ev1_data = data_all.copy()
    ev1_data['metadata']['symmetry'] = 'ev1'

    nx = data_all['metadata']['nx'] // 2
    ny = data_all['metadata']['ny'] // 2
    nz = data_all['metadata']['nz'] // 2

    # --- Fields ---
    if 'variables' in data_all["metadata"]:
        variables = data_all['metadata']['variables']
        for field in variables:
            key = field['name']
            nc = field['n_components']

            sx = np.asarray(field['sx'])
            sy = np.asarray(field['sy'])
            sz = np.asarray(field['sz'])

            ev1_data[key] = convert_array_EV8_EV1(
                data_all[key], nx, ny, nz, symx=sx, symy=sy, symz=sz, nc=nc
            )

    # --- Wavefunctions ---
    wf_metadata = data_all['metadata']['wavefunction']
    nwn = wf_metadata['n_neutron_states']
    nwp = wf_metadata['n_proton_states']
    states_n = data_all["statesn"]
    states_p = data_all["statesp"]
    symblocks_n = wf_metadata['symblocks_n']
    symblocks_p = wf_metadata['symblocks_p']

    ev1_data["statesn"] = break_syms_spwfs(states_n, symblocks_n, nx, ny, nz)
    ev1_data["statesp"] = break_syms_spwfs(states_p, symblocks_p, nx, ny, nz)

    # --- Update prefix to match output ---
    output_dir = os.path.dirname(output_path) or "."
    output_base = os.path.basename(output_path)
    new_prefix = os.path.splitext(output_base)[0]
    ev1_data['metadata']['prefix'] = new_prefix

    # --- Ensure file extension matches chosen format ---
    out_ext = os.path.splitext(output_path)[1].lower()
    if not out_ext:
        if output_format in ("yaml", "yml"):
            output_path += ".yaml"
        elif output_format in ("hdf5", "h5"):
            output_path += ".h5"

    print("\n--- Output (EV1) ---")
    wf_meta = ev1_data["metadata"]["wavefunction"]
    print(f"Prefix: {ev1_data['metadata'].get('prefix')}")
    print(f"Neutron states: {wf_meta['n_neutron_states']}")
    print(f"Proton states: {wf_meta['n_proton_states']}")

    # --- Write result ---
    print(f"\nWriting to '{output_path}' ({output_format} format)")
    write(ev1_data, output_path)
