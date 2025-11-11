#!/usr/bin/env python3
import numpy as np
import yaml
import h5py
import os
import warnings

warnings.simplefilter("always", DeprecationWarning)
warnings.formatwarning = lambda msg, *args, **kwargs: f"{msg}\n"

PARSER_VERSION = "0.2.1"

#----------------------------------------------------------
def _ensure_version(metadata):
    """Ensure the metadata contains the current parser version."""
    metadata["version"] = PARSER_VERSION
    return metadata


#----------------------------------------------------------
def write_hdf5(data, filepath):
    """
    Write a Bogoliubov state and associated fields to an HDF5 file.

    Arrays are written in Fortran (column-major) order for consistency
    with the Fortran-based binary format.
    """
    metadata = data['metadata'].copy()
    metadata = _ensure_version(metadata)

    prefix = metadata.pop('prefix', None)
    if prefix is None:
        raise ValueError("Missing 'prefix' in metadata; cannot determine HDF5 filename.")

    odir = os.path.dirname(filepath) or '.'
    os.makedirs(odir, exist_ok=True)

    fields = metadata.pop('field', None)

    with h5py.File(filepath, 'w') as h5f:
        # Save global metadata
        h5f.attrs['metadata_yaml'] = yaml.dump(metadata)

        # Save field data
        if fields is not None:
            fld_group = h5f.create_group('field')
            for fld in fields:
                key = fld['name']
                if key not in data:
                    continue
                arr = np.asfortranarray(data[key])
                dset = fld_group.create_dataset(key, data=arr, compression='gzip')

                # Copy field-specific metadata
                for k, v in fld.items():
                    if k not in ('name', 'suffix'):
                        dset.attrs[k] = v

        # Save wavefunctions
        if 'wavefunction' in metadata:
            wf_group = h5f.create_group('wavefunction')

            # --- Neutron block ---
            neu_group = wf_group.create_group('neutron')
            if 'statesn' in data:
                neu_group.create_dataset('states', data=np.asfortranarray(data['statesn']), compression='gzip')
            if 'un' in data:
                neu_group.create_dataset('u', data=np.asfortranarray(data['un']), compression='gzip')
            if 'vn' in data:
                neu_group.create_dataset('v', data=np.asfortranarray(data['vn']), compression='gzip')

            # --- Proton block ---
            pro_group = wf_group.create_group('proton')
            if 'statesp' in data:
                pro_group.create_dataset('states', data=np.asfortranarray(data['statesp']), compression='gzip')
            if 'up' in data:
                pro_group.create_dataset('u', data=np.asfortranarray(data['up']), compression='gzip')
            if 'vp' in data:
                pro_group.create_dataset('v', data=np.asfortranarray(data['vp']), compression='gzip')


#----------------------------------------------------------
def read_hdf5(filepath):
    """
    Read a Bogoliubov state and fields from an HDF5 file.
    Restores a metadata dictionary compatible with the binary/YAML format.
    """
    data = {}
    with h5py.File(filepath, 'r') as h5f:
        metadata_yaml = h5f.attrs['metadata_yaml']
        metadata = yaml.safe_load(metadata_yaml)

        prefix = os.path.splitext(os.path.basename(filepath))[0]
        metadata['prefix'] = prefix
        metadata = _ensure_version(metadata)
        data['metadata'] = metadata

        # Field data
        fld_group = None
        if 'field' in h5f:
            fld_group = h5f['field']
        elif 'variables' in h5f:
            fld_group = h5f['variables']
            warnings.warn("HDF5 group 'variables' is deprecated; use 'field' instead.", DeprecationWarning)

        if fld_group is not None:
            fields = []
            for key, dset in fld_group.items():
                data[key] = np.array(dset, order='F')
                fld_meta = {}
                for k, v in dset.attrs.items():
                    if isinstance(v, np.generic):
                        v = v.item()
                    fld_meta[k] = v
                fld_meta['name'] = key
                fld_meta['suffix'] = f"_{key}.bin"
                fields.append(fld_meta)
            metadata['field'] = fields

        # Wavefunctions
        if 'wavefunction' in h5f:
            wf_group = h5f['wavefunction']

            if 'neutron' in wf_group:
                neu_group = wf_group['neutron']
                if 'states' in neu_group:
                    data['statesn'] = np.array(neu_group['states'], order='F')
                if 'u' in neu_group:
                    data['un'] = np.array(neu_group['u'], order='F')
                if 'v' in neu_group:
                    data['vn'] = np.array(neu_group['v'], order='F')

            if 'proton' in wf_group:
                pro_group = wf_group['proton']
                if 'states' in pro_group:
                    data['statesp'] = np.array(pro_group['states'], order='F')
                if 'u' in pro_group:
                    data['up'] = np.array(pro_group['u'], order='F')
                if 'v' in pro_group:
                    data['vp'] = np.array(pro_group['v'], order='F')

    return data


#----------------------------------------------------------
def write_yaml(data, filepath):
    """
    Write Bogoliubov state and fields to YAML + binary format.
    Ensures binary arrays are written in strict Fortran (column-major) order.
    """
    metadata = _ensure_version(data['metadata'])
    prefix = metadata['prefix']
    odir = os.path.dirname(filepath) or '.'
    os.makedirs(odir, exist_ok=True)

    # Write YAML metadata
    with open(filepath, 'w') as file:
        yaml.dump(metadata, file)

    # Write fields
    if 'field' in metadata:
        fields = metadata['field']
        for fld in fields:
            key = fld['name']
            array = data[key]
            f_name = os.path.join(odir, prefix + fld['suffix'])
            with open(f_name, 'wb') as f:
                f.write(np.asfortranarray(array).tobytes(order='F'))

    # Write wavefunction block
    if 'wavefunction' in metadata:
        wf_meta = metadata['wavefunction']
        f_name = os.path.join(odir, prefix + wf_meta['suffix'])
        with open(f_name, 'wb') as file:
            buffer = (
                data['statesn'].tobytes(order='F') +
                data['statesp'].tobytes(order='F') +
                data['un'].tobytes() +
                data['vn'].tobytes() +
                data['up'].tobytes() +
                data['vp'].tobytes()
            )
            file.write(buffer)


#----------------------------------------------------------
def read_yaml(odir, header):
    """
    Read a Bogoliubov state and fields (potentials, densities)
    from YAML + binary format.
    """
    data = {}
    with open(header, 'r') as file:
        metadata = yaml.safe_load(file)
        metadata = _ensure_version(metadata)
        data['metadata'] = metadata

    if 'variables' in metadata:
        warnings.warn("YAML key 'variables' is deprecated; using 'field' instead.", DeprecationWarning)
        metadata['field'] = metadata.pop('variables')

    prefix = metadata['prefix']
    nx, ny, nz = metadata['nx'], metadata['ny'], metadata['nz']
    symmetry = metadata.get('symmetry', '')
    if symmetry == 'ev8':
        nx, ny, nz = nx // 2, ny // 2, nz // 2

    n_frames = metadata.get('frame', 1)
    if 'field' in metadata:
        fields = metadata['field']
        valid_fields = []
        for fld in fields:
            key = fld['name']
            f_name = os.path.join(odir, prefix + fld['suffix'])
            nc = fld['n_components']
            try:
                with open(f_name, 'rb'):
                    pass
            except FileNotFoundError:
                print(f"Warning: missing field file '{f_name}', skipping.")
                continue

            if n_frames == 1:
                shape = (nx, ny, nz, nc)
                if nc == 1:
                    shape = (nx, ny, nz)
            else:
                shape = (nx, ny, nz, nc, n_frames)
                if nc == 1:
                    shape = (nx, ny, nz, n_frames)

            data[key] = np.reshape(np.fromfile(f_name, dtype=np.float64), shape, order='F')
            valid_fields.append(fld)

        metadata['field'] = valid_fields

    if 'wavefunction' in metadata:
        wf_meta = metadata['wavefunction']
        f_name = os.path.join(odir, prefix + wf_meta['suffix'])
        nw_n = wf_meta['n_neutron_states']
        nw_p = wf_meta['n_proton_states']

        with open(f_name, 'rb') as file:
            statesn_bsize = nw_n * nx * ny * nz * 2 * np.complex128(0).nbytes
            buffer = file.read(statesn_bsize)
            data['statesn'] = np.reshape(np.frombuffer(buffer, dtype=np.complex128),
                                         (nx, ny, nz, 2, nw_n), order='F')

            statesp_bsize = nw_p * nx * ny * nz * 2 * np.complex128(0).nbytes
            buffer = file.read(statesp_bsize)
            data['statesp'] = np.reshape(np.frombuffer(buffer, dtype=np.complex128),
                                         (nx, ny, nz, 2, nw_p), order='F')

            un_bsize = nw_n * np.complex128(0).nbytes
            data['un'] = np.frombuffer(file.read(un_bsize), dtype=np.complex128)
            data['vn'] = np.frombuffer(file.read(un_bsize), dtype=np.complex128)

            up_bsize = nw_p * np.complex128(0).nbytes
            data['up'] = np.frombuffer(file.read(up_bsize), dtype=np.complex128)
            data['vp'] = np.frombuffer(file.read(up_bsize), dtype=np.complex128)

    return data


#----------------------------------------------------------
# Unified interface
def read(filepath):
    """
    Auto-detect file type and read accordingly.
      - .yaml/.yml → YAML format
      - .h5/.hdf5  → HDF5 format
    """
    if filepath.endswith(('.yaml', '.yml')):
        odir = os.path.dirname(filepath) or '.'
        return read_yaml(odir, filepath)
    elif filepath.endswith(('.h5', '.hdf5')):
        return read_hdf5(filepath)
    else:
        raise ValueError(f"Unrecognized file extension for '{filepath}'.")


def write(data, filepath):
    """
    Unified writer. File format is determined by the extension of `filepath`.
    """
    ext = os.path.splitext(filepath)[1].lower()
    data['metadata'] = _ensure_version(data['metadata'])
    if ext in ('.yaml', '.yml'):
        write_yaml(data, filepath)
    elif ext in ('.h5', '.hdf5'):
        write_hdf5(data, filepath)
    else:
        raise ValueError(f"Unknown file extension for output: '{filepath}'. Expected .yaml/.yml or .h5/.hdf5.")
