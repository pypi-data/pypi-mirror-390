import unittest
import numpy as np
import os

import parser

#----------------------------------------------------------
#----------------------------------------------------------
class TestParser(unittest.TestCase):

    #----------------------------------------------------------
    def create_dummy_rho(self, shape, center=None, sigma=1.0):
        """
        Generate a 3D field of shape (nz,ny,nx).
        Numpy stores things in row order...
        """
        nx, ny, nz = shape
        if center is None:
            center = (nx // 2, ny // 2, nz // 2)
        if isinstance(sigma, (int, float)):
            sigma = (sigma, sigma, sigma)

        x = np.arange(0, nx)
        y = np.arange(0, ny)
        z = np.arange(0, nz)
        z, y, x = np.meshgrid(z, y, x, indexing='ij')

        cx, cy, cz = center
        sx, sy, sz = sigma

        field = x*y*z * np.exp(-(((x - cx) ** 2) / (2 * sx ** 2) +
                            ((y - cy) ** 2) / (2 * sy ** 2) +
                            ((z - cz) ** 2) / (2 * sz ** 2)))
        return field 

    #----------------------------------------------------------
    def create_dummy_data(self):
        '''
        Create a dummy dataset to test the parser
        '''
        data = {}

        # Create the metadata
        nx, ny, nz = 8, 10, 12 
        nw_proton  = 14
        nw_neutron = 16

        metadata = {}
        metadata['nx'] = nx
        metadata['ny'] = ny
        metadata['nz'] = nz
        metadata['dx'] = 0.9
        metadata['dy'] = 0.8
        metadata['dz'] = 0.7
        metadata['prefix'] = 'dummy'
        metadata['description'] = "This is some dummy data"
        metadata['Z'] = 10
        metadata['N'] = 12
        metadata['frames'] = 1
        metadata['t0'] = 0.
        metadata['dt'] = 0.
        data['metadata'] = metadata

        # Create fields data
        rho_n_metadata = {}
        rho_n_metadata['name'] = 'rho_n'
        rho_n_metadata['n_components'] = 1
        rho_n_metadata['type'] = "real"
        rho_n_metadata['unit'] = "fm^-3"
        rho_n_metadata['suffix'] = "_rho_n.wdat"
        data['rho_n'] = self.create_dummy_rho((nx,ny,nz))

        j_metadata = {}
        j_metadata['name'] = 'j'
        j_metadata['n_components'] = 3
        j_metadata['type'] = "real"
        j_metadata['unit'] = "xxx"
        j_metadata['suffix'] = "_j.wdat"
        data['j'] = np.random.rand(3, nz, ny, nx).astype(np.float64)

        metadata['variables'] = [rho_n_metadata, j_metadata]

        # Create wavefunction data
        wf_metadata = {}
        wf_metadata['representation']   = 'canonical'
        wf_metadata['n_proton_states']  = nw_proton 
        wf_metadata['n_neutron_states'] = nw_neutron
        wf_metadata['suffix'] = '_state'
        metadata['wavefunction'] = wf_metadata

        data['un']      = np.random.rand(nw_neutron).astype(np.complex128)
        data['vn']      = np.random.rand(nw_neutron).astype(np.complex128)
        data['statesn'] = np.random.rand(nw_neutron, 2, nz, ny, nx).astype(np.complex128)
        data['up']      = np.random.rand(nw_proton).astype(np.complex128)
        data['vp']      = np.random.rand(nw_proton).astype(np.complex128)
        data['statesp'] = np.random.rand(nw_proton, 2, nz, ny, nx).astype(np.complex128)

        return data

    #----------------------------------------------------------
    def remove_files(self, data):
        metadata = data['metadata']
        prefix = metadata['prefix']
        os.remove(prefix+'.yaml')
        os.remove(prefix+metadata['wavefunction']['suffix'])
        for s in [v['suffix'] for v in metadata['variables']]:
            os.remove(prefix+s)

    #----------------------------------------------------------
    def test_write_1d_field(self):
        data = self.create_dummy_data()
        parser.write(data, '.')

        f = data['rho_n']
        metadata = data['metadata']
        nx,ny,nz = metadata['nx'], metadata['ny'], metadata['nz']
        ix,iy,iz = 2,3,4
        fzyx_target = f[iz,iy,ix]

        read_data = np.fromfile('dummy_rho_n.wdat', dtype=np.float64)
        flat_index = ix + nx*iy + nx*ny*iz
        fzyx = read_data[flat_index]

        self.assertEqual(read_data.size, f.size)
        self.assertEqual(fzyx, fzyx_target)
        self.remove_files(data)

    #----------------------------------------------------------
    def test_write_neutron_states(self):
        data = self.create_dummy_data()
        parser.write(data, '.')

        metadata = data['metadata']
        nx,ny,nz = metadata['nx'], metadata['ny'], metadata['nz']
        nw_n     = metadata['wavefunction']['n_neutron_states']
        ix,iy,iz,ispin,iw = 5,6,7,0,8
        phi_target = data['statesn'][iw,ispin,iz,iy,ix]

        with open('dummy_state', 'rb') as file:
            whole_buffer = file.read()
        statesn_bsize = nw_n * nx*ny*nz*2 * np.complex128(0.).nbytes
        buffer = whole_buffer[0:statesn_bsize]
        read_data = np.frombuffer(buffer, dtype=np.complex128)
        flat_index = ix + nx*iy + nx*ny*iz + nx*ny*nz*ispin + nx*ny*nz*2*iw
        phi = read_data[flat_index]

        self.assertEqual(read_data.size, data['statesn'].size)
        self.assertEqual(phi, phi_target)
        self.remove_files(data)

    #----------------------------------------------------------
    def test_write_proton_states(self):
        data = self.create_dummy_data()
        parser.write(data, '.')

        metadata = data['metadata']
        nx,ny,nz = metadata['nx'], metadata['ny'], metadata['nz']
        nw_n       = metadata['wavefunction']['n_neutron_states']
        nw_p       = metadata['wavefunction']['n_proton_states']
        ix,iy,iz,ispin,iw = 5,6,7,1,9
        phi_target = data['statesp'][iw,ispin,iz,iy,ix]

        with open('dummy_state', 'rb') as file:
            whole_buffer = file.read()
        statesn_bsize = nw_n * nx*ny*nz*2 * np.complex128(0.).nbytes
        statesp_bsize = nw_p * nx*ny*nz*2 * np.complex128(0.).nbytes
        buffer = whole_buffer[statesn_bsize:statesn_bsize+statesp_bsize]
        read_data = np.frombuffer(buffer, dtype=np.complex128)
        flat_index = ix + nx*iy + nx*ny*iz + nx*ny*nz*ispin + nx*ny*nz*2*iw
        phi = read_data[flat_index]

        self.assertEqual(read_data.size, data['statesp'].size)
        self.assertEqual(phi, phi_target)
        self.remove_files(data)

    #----------------------------------------------------------
    def test_write_up(self):
        data = self.create_dummy_data()
        parser.write(data, '.')

        metadata = data['metadata']
        nx,ny,nz = metadata['nx'], metadata['ny'], metadata['nz']
        nw_n       = metadata['wavefunction']['n_neutron_states']
        nw_p       = metadata['wavefunction']['n_proton_states']
        iw         = 3
        up_target = data['up'][iw]

        with open('dummy_state', 'rb') as file:
            whole_buffer = file.read()
        statesn_bsize = nw_n * nx*ny*nz*2 * np.complex128(0.).nbytes
        statesp_bsize = nw_p * nx*ny*nz*2 * np.complex128(0.).nbytes
        un_bsize = nw_n * np.complex128(0.).nbytes
        up_bsize = nw_p * np.complex128(0.).nbytes
        start = statesn_bsize + statesp_bsize + 2*un_bsize
        stop  = start + up_bsize 
        buffer = whole_buffer[start:stop]
        read_data = np.frombuffer(buffer, dtype=np.complex128)
        flat_index = iw
        up = read_data[flat_index]

        self.assertEqual(read_data.size, data['up'].size)
        self.assertEqual(up, up_target)
        self.remove_files(data)

    #----------------------------------------------------------
    def test_write_read(self):
        data = self.create_dummy_data()
        parser.write(data, '.')

        read_data = parser.read('./', 'dummy.yaml')

        # metadata
        # self.assertEqual(data['metadata'], read_data['metadata'])

        # fields
        rho_diff = np.linalg.norm(data['rho_n'] - read_data['rho_n'])
        self.assertLess(rho_diff, 1e-15)

        # wavefunction
        wf_diff  = 0.
        wf_diff += np.linalg.norm(data['statesn'] - read_data['statesn'])
        wf_diff += np.linalg.norm(data['statesp'] - read_data['statesp'])
        wf_diff += np.linalg.norm(data['un'] - read_data['un'])
        wf_diff += np.linalg.norm(data['vn'] - read_data['vn'])
        wf_diff += np.linalg.norm(data['up'] - read_data['up'])
        wf_diff += np.linalg.norm(data['vp'] - read_data['vp'])
        self.assertLess(wf_diff, 1e-15)


#----------------------------------------------------------
#----------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
