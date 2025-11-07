import numpy as np

from collections import namedtuple
from scipy.optimize import least_squares

from MMLToolbox.coord import CoordSystem
from MMLToolbox.optic import OpticSystem


MeasParams = namedtuple("MeasParams", ["phi_min","phi_max","phi_delta","theta_min", "theta_max","theta_delta"])
MEAS_PARAMS = {
    0: MeasParams(0,361,20,15,31,2.5),
    1: MeasParams(0,361,20,0,61,5)
}

class OpticAligner:
    """Aligns optical systems using coordinate measurements."""

    def __init__(self, coord: CoordSystem, optic: OpticSystem, r_ref=2500):
        """Initialize OpticAligner with coordinate and optic systems."""
        self.coord = coord
        self.optic = optic
        self.r_ref = r_ref

        self._sphere_meas_params = MEAS_PARAMS.get(optic.id_sens, MeasParams(None,None,None,None,None,None))


  ################## User Functions ################## 
    def get_sphere_center(self, start_pos=None, x=None, y=None):
        """Measure cartesian grid and fit to find sphere center."""
        if start_pos is None:
            start_pos = self.coord.get_pos()
        if x is None:
            x = np.arange(-1000, 1001, 250)
        if y is None:
            y = np.arange(-1000, 1001, 250)

        val = self._scan_optic_cart(start_pos, x, y)
        _, _, m, R, _, reserr = self._fit_spherical_tilt_least_square(val)
        #start_pos = self._init_start_position(m)
        return m, val, R,reserr
    
    def init_sphere_center(self,m):
        smp = self._sphere_meas_params
        x,y,z = self._sph2cart(smp.theta_min/180*np.pi,smp.phi_min/180*np.pi,self.r_ref)
        new_pos = m + np.array([x,y,z])
        self.coord.absolute_pos(x=[new_pos[0],500],y=[new_pos[1],500],z=[new_pos[2],500])

        for id,delta_z in enumerate(range(-450,451,100)):
          m_new = m[2]+z+delta_z
          self.coord.absolute_pos(z=[m_new,100])
          value, std = self.optic.measure()
          if value>0 and value<300 and std<10:
            break

        z_pos = self.coord.get_pos()[2]-value+20
        self.coord.absolute_pos(z=[z_pos,50],precision_mode=True)
        pos = self.coord.get_pos()
        startpos = np.array([m[0],m[1],pos[2]])
        value,std = self.optic.measure()
        print(f"Sphere position initialized:\nmean_optic={value:.2f}µm std_optic={std:.2f}µm")
        return startpos

    def calibrate_optic(self, start_pos, m, phi=None, theta=None):
        """Perform spherical scan and calculate adjustment advice."""
        smp = self._sphere_meas_params
        if phi is None:
            phi = np.arange(smp.phi_min,smp.phi_max,smp.phi_delta)/180*np.pi
        if theta is None:
            theta = np.arange(smp.theta_min,smp.theta_max,smp.theta_delta)/180*np.pi

        ret = {'dphi': phi, 'dtheta': theta}
        val = self._scan_optic_spherical(start_pos, dtheta=ret['dtheta'], dphi=ret['dphi'])
        ret['ax'], ret['ay'], ret['m'], ret['R'], ret['d'], ret['reserr'] = self._fit_spherical_tilt_least_square(val)

        uax = -0.180 * np.tan(np.deg2rad(ret['ax'])) / 0.5e-3
        uay = -0.155 * np.tan(np.deg2rad(ret['ay'])) / 0.5e-3

        print(
            f"Please adjust the screw\n-for alpha_x about {uax:.6f} turns"
            f"\n-for alpha_y about {uay:.6f} turns."
        )

        # spnew = m + np.array([0, 0, 2600])
        ret['val'] = val
        return ret, val


  ################## Private Functions ################## 
    def _scan_optic_cart(self, start_pos, dxs, dys):
        """Perform grid scan in x and y directions."""
        lx = len(dxs)
        ly = len(dys)
        mes = np.zeros((ly, lx, 6))

        for iy, dy in enumerate(dys):
            for ix, dx in enumerate(dxs):
                new_pos = start_pos + np.array([dx, dy, 0])
                self.coord.absolute_pos(
                    x=[new_pos[0], 500],
                    y=[new_pos[1], 500],
                    precision_mode=True)
                mes[iy, ix, :3] = self.coord.get_pos()
                mes[iy, ix, 3:5] = self.optic.measure()

        mes[:, :, 5] = mes[:, :, 2] - mes[:, :, 3]
        return mes

    def _scan_optic_spherical(self,start_pos,dtheta,dphi):
        """Perform spherical scan around start position."""
        R = self.r_ref
        ltheta = len(dtheta)
        lphi = len(dphi)

        mes = np.zeros((lphi, ltheta, 6))

        for iphi in range(lphi):
            for itheta in range(ltheta):
                dpos = np.array(self._sph2cart(theta=dtheta[itheta], phi=dphi[iphi], r=R))
                dpos[2] = 0
                pos = start_pos + dpos
                self.coord.absolute_pos(
                    x=[pos[0], 500],
                    y=[pos[1], 500],
                    precision_mode=True)
                mes[iphi, itheta, :3] = self.coord.get_pos()
                mes[iphi, itheta, 3:5] = self.optic.measure()

        mes[:, :, 5] = mes[:, :, 2] - mes[:, :, 3]
        return mes

    @staticmethod
    def _sph2cart(theta, phi, r):
        """Convert spherical to cartesian coordinates."""
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z

    def _fit_spherical_tilt(self, val):
        """Fit a spherical tilt to measurement data."""
        lval = val.reshape(-1, 6)
        x, y, z, o = lval[:, 0], lval[:, 1], lval[:, 2], lval[:, 3]
        ind = ~np.isnan(o)
        x, y, z, o = x[ind], y[ind], z[ind], o[ind]

        A = np.column_stack((np.ones(len(o)), o, x, y, o * x, o * y))
        b = o**2 + x**2 + y**2 + z**2
        w = np.linalg.pinv(A) @ b

        m = np.array([w[2] / 2, w[3] / 2, 0])
        d = np.array([-w[4] / 2, -w[5] / 2, 0])
        d[2] = -np.sqrt(1 - (d[0]**2) - (d[1]**2))
        m[2] = np.mean(z) + ((w[1] / 2) - d[0] * m[0] - d[1] * m[1]) / d[2]
        R = np.sqrt(w[0] + np.dot(m, m) - 2 * np.mean(z) * m[2])
        ax = np.degrees(np.arctan(d[1] / d[2]))
        ay = np.degrees(np.arctan(d[0] / d[2]))

        print(f'ax = {ax:.4f}°   ay = {ay:.4f}°  R = {R:.1f}µm')

        return ax, ay, m, R, d

    @staticmethod
    def _residuals(params, rad, o):
        """Calculate residuals for least squares fit."""
        R = params[0]
        m = params[1:4]
        d0 = params[4:7] / np.linalg.norm(params[4:7])

        diffs = (o[:, np.newaxis] * d0 + rad - m)
        return np.sum(diffs**2, axis=1) - R**2

    def _fit_spherical_tilt_least_square(self, val):
        """Perform full least squares spherical tilt fit."""
        lval = val.reshape(-1, 6)
        rad = np.array(lval[:, :3])
        o = lval[:, 3]

        ind = ~np.isnan(o)
        rad, o = rad[ind, :], o[ind]

        d0_init = np.array([0.0, 0.0, -1.0])
        d0_init /= np.linalg.norm(d0_init)

        surface_points = rad + o[:, None] * d0_init
        m0 = np.mean(surface_points, axis=0)
        R0 = self.r_ref
        p0 = np.concatenate([[R0], m0, d0_init])

        lower_bounds = [2400,-np.inf,-np.inf,-np.inf,-np.inf,-np.inf,-np.inf]
        upper_bounds = [2600,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf]

        options = {'ftol': 1e-15, 'xtol': 1e-15, 'verbose': 2}
        result = least_squares(self._residuals, p0,bounds=(lower_bounds,upper_bounds),args=(rad, o),**options)

        R_fit = result.x[0]
        m_fit = result.x[1:4]
        d0_fit = result.x[4:7] / np.linalg.norm(result.x[4:7])

        ax = np.degrees(np.arctan(d0_fit[1] / d0_fit[2]))
        ay = np.degrees(np.arctan(d0_fit[0] / d0_fit[2]))
        reserr = self._residuals(np.concatenate(([R_fit],m_fit,d0_fit)),rad,o)
        reserr_array = np.column_stack((rad[:,0],rad[:,1],reserr))

        print(f'ax = {ax:.4f}°   ay = {ay:.4f}°  R = {R_fit:.1f}µm')

        return ax,ay,m_fit,R_fit,d0_fit,reserr_array