import numpy as np
import keyboard
import time

from scipy.interpolate import interp1d
from scipy.optimize import least_squares

from abc import ABC
from MMLToolbox.coord import CoordSystem
from MMLToolbox.optic import OpticSystem
from MMLToolbox.senis import SenisSystem
from MMLToolbox.ni import NISystem
from MMLToolbox.localMag import StoreMagneticAligner

class MagneticAligner(ABC):
    def __init__(self,sma:StoreMagneticAligner,coord:CoordSystem,optic:OpticSystem,ni:NISystem,senis:SenisSystem):
        self.sma = sma
        self.optic = optic
        self.coord = coord
        self.ni = ni
        self.senis = senis

  ################## User Functions ################## 
    def optic_scan_conductor(self,optic_orientation:str) -> None:
        ret = {}
        Rc = 800
        startpos,xc,yc,zc = self._get_optic_values_from_h5(optic_orientation)
        R_mc = np.array([xc,yc,zc])
        indir = np.where(np.abs(yc) == 1)[0]
        ds = np.arange(-1200,1201,150)
        mes = self._scan_optic_1D(startpos,ds,yc)
        ind = ~np.isnan(mes[:,7])
        mes = mes[ind,:]
        ds = ds[ind]

        _, ds0is = self._filter_points(mes, ds)
        pmax = startpos.copy()
        pmax[indir] = startpos[indir] + ds0is * yc[indir]
        interp_func = interp1d(mes[:, indir[0]], mes[:, 7], kind='linear', fill_value="extrapolate")
        pmax[2] = interp_func(pmax[indir][0])

        t_mc = pmax - Rc * zc
        dxc = np.arange(-5000, 5001, 1000)
        dal = np.arange(-90, 91, 10)
        dyc = np.sin(np.radians(dal)) * Rc

        mespc1, mespc2 = np.meshgrid(dxc, dyc)
        mespc3 = np.sqrt(Rc**2 - mespc2**2)
        mespc = np.stack((mespc1, mespc2, mespc3), axis=-1)

        R_cm = np.linalg.inv(R_mc)
        t_cm = -np.dot(R_mc, t_mc)

        mes = self._scan_mes_points(mespc, R_cm, t_cm)
        mespointlist = mes[:, :, [3, 4, 7]].reshape(-1, 3)
        dc0 = xc
        R0 = Rc

        # First filter
        pc, dc, Rc, reserr1 = self._fit_conductor_geometry(mespointlist, dc0, R0)
        ind = np.where(np.abs(reserr1) < 30)[0]
        mespointlist_new = mespointlist[ind, :]

        # Second filter
        pc, dc, Rc, reserr2 = self._fit_conductor_geometry(mespointlist_new, dc0, R0)
        ind = np.where(np.abs(reserr2) < 15)[0]
        mespointlist_new = mespointlist_new[ind, :]

        # Third filter
        pc, dc, Rc, reserr3 = self._fit_conductor_geometry(mespointlist_new, dc0, R0)
        ind = np.where(np.abs(reserr3) < 8)[0]
        mespointlist_new = mespointlist_new[ind, :]

        # Check data reduction
        self._check_data_reduction(mespointlist,mespointlist_new)
        
        # Final fit
        pc, dc, Rc, reserr = self._fit_conductor_geometry(mespointlist_new, dc0, R0)

        # Check for outliers
        self._check_outliers(reserr)

        ret["Rc"] = Rc
        ret["reserr"] = reserr
        ret["mes"] = mes
        ret["mespointlist"] = mespointlist
        ret["mespointlist_new"] = mespointlist_new

        return pc, dc, ret
    
    def mag_scan_conductor(self,pc,dc,orientation,mscan):
        startpos,ds_ideal,_,_,_ = self._get_magnetic_values_from_h5(orientation,mscan)
        ds1 = self._get_ds(dc,ds_ideal)
        self._init_pos_coord(startpos,orientation)
        M1,new_stpm1,IO_mes1,mes1 = self._mag_scan_conductor(orientation,mscan,dc,ds1)

        return ds1,M1,new_stpm1,IO_mes1,mes1   

    def close(self):
        self.coord.close()
        self.senis.close()
        self.optic.close()
        self.ni.stop()
        
  ################## Private Functions ################## 
    def _mag_scan_conductor(self,orientation,mscan,dc,ds):
        startpos,ds_ideal,la,pszc_ideal,IO = self._get_magnetic_values_from_h5(orientation,mscan)
        lap = np.linspace(np.min(la),np.max(la),20)


        mes = self._scan_magnetic_1D_senis_dif(startpos,lap,ds,IO)
        M = mes[:,14:17]
        IO_mes = np.mean(mes[:,-1])
        mM = np.mean(np.abs(M),axis=0)
        im = np.argmin(mM)
        io = [i for i in range(3) if i != im]

        fit1 = self._fit_mag_scan(M[:,io[0]],lap,IO_mes,pszc_ideal)
        fit2 = self._fit_mag_scan(M[:,io[1]],lap,IO_mes,pszc_ideal)

        psyc = np.mean([fit1["psyc"], fit2["psyc"]])
        pszc = np.mean([fit1["pszc"], fit2["pszc"]])

        zc = np.cross(dc,ds)
        new_startpos = startpos-ds*psyc-zc*pszc+zc*pszc_ideal
        dsp = np.linalg.norm(new_startpos-startpos)
        print(f"\ndsp = {dsp}")
        if not self._continue_programm(): 
            ret = self._create_ret(startpos,pszc_ideal,mes,new_startpos,zc)
            return M,startpos,IO_mes,ret

        mes = self._scan_magnetic_1D_senis_dif(new_startpos,la,ds,IO)
        M = mes[:,14:17]
        ret = self._create_ret(startpos,pszc_ideal,mes,new_startpos,zc)

        return M,new_startpos,IO_mes,ret
    
    @staticmethod
    def _continue_programm():
        is_ok = None
        print("Press [Enter] to continue or [Esc] to stop...")

        while True:
            if keyboard.is_pressed("enter"):
                print("Continuing...\n")
                is_ok = True
                break
            elif keyboard.is_pressed("esc"):
                print("Execution stopped by user.")
                is_ok = False
                break
            time.sleep(0.01)
        return is_ok
    
    @staticmethod
    def _create_ret(startpos,pszc_ideal,mes,new_startpos,zc):
        ret = {}
        ret["startpos"] = startpos
        ret["pszc_ideal"] = pszc_ideal
        ret["mes"] = mes
        ret["new_startpos"] = new_startpos
        ret["zc"] = zc
        return ret

    def _scan_magnetic_1D_senis_dif(self,starptos,la,ds,IO):
        ls = len(la)
        mes = np.zeros((ls,18))
        self.coord.absolute_pos(x=[starptos[0],1000],y=[starptos[1],1000],z=[starptos[2],1000]) # check for initial position
        print("Is position ok?")
        if not self._continue_programm(): return mes

        for it in range(ls):
            mespos = starptos+ds*la[it]
            self.coord.absolute_pos(x=[mespos[0],500],y=[mespos[1],500],z=[mespos[2],500],precision_mode=True)
            value = self.coord.get_pos()
            self.ni.start(startup_duration=0.5,max_voltage=IO,target_voltage=IO,freq=5,waveform="ramp")
            Bx,By,Bz = self.senis.measure()
            U,I = self.ni.measure()
            self.ni.stop()
            mes[it,0:3] = mespos
            mes[it,3:6] = value
            mes[it,6],mes[it,7],mes[it,8] = Bx,By,Bz
            mes[it,9] = I

            self.ni.start(startup_duration=0.5,max_voltage=-IO,target_voltage=-IO,freq=5,waveform="ramp")
            Bx,By,Bz = self.senis.measure()
            U,I = self.ni.measure()
            self.ni.stop()
            mes[it,10],mes[it,11],mes[it,12] = Bx,By,Bz
            mes[it,13] = I

            mes[it,14:] = (mes[it,6:10]-mes[it,10:14])/2

        self.ni.stop() # Make sure, amplifier shut off
        return mes

    def _get_optic_values_from_h5(self,orientation:str):
        startpos = self.sma.read(f"def/{orientation}/oscan/startpos")
        xc = self.sma.read(f"def/{orientation}/oscan/xc")
        yc = self.sma.read(f"def/{orientation}/oscan/yc")
        zc = np.cross(xc,yc)
        return startpos,xc,yc,zc
    
    def _get_magnetic_values_from_h5(self,orientation:str,mscan:str):
        startpos = self.sma.read(f"def/{orientation}/{mscan}/startpos")
        ds_ideal = self.sma.read(f"def/{orientation}/{mscan}/ds_ideal")
        la = self.sma.read(f"def/{orientation}/{mscan}/la")
        pszc_ideal = self.sma.read(f"def/{orientation}/{mscan}/pszc_ideal")
        IO = self.sma.read(f"def/{orientation}/{mscan}/IO")
        return startpos,ds_ideal,la,pszc_ideal,IO
    
    @staticmethod
    def _get_ds(dc,ds_ideal):
        ds = ds_ideal - dc * np.dot(dc, ds_ideal)
        ds = ds / np.linalg.norm(ds)
        return ds
    
    def _init_pos_coord(self,startpos,orientation):
          if orientation=="or4":
            self.coord.absolute_pos(x=[startpos[0],5000])
            self.coord.absolute_pos(y=[startpos[1],5000])
            self.coord.absolute_pos(z=[startpos[2],5000])
          else:
            self.coord.absolute_pos(z=[startpos[2]+10000,5000]) # move to save position
            self.coord.absolute_pos(x=[startpos[0],5000],y=[startpos[1],5000])
            self.coord.absolute_pos(z=[startpos[2],1000])

    @staticmethod
    def _get_new_stpo(orientation,startpos,pc,dc):
        if orientation == "or1":
            new_stpo = (startpos[0]-pc[0])/dc[0]*dc+pc+np.array([0,0,880+800])
        elif orientation == "or2":
            new_stpo = (startpos[1]-pc[1])/dc[1]*dc+pc+np.array([0,0,880+800])
        elif orientation == "or3":
            n = np.array([1,0,0])
            new_stpo = -np.dot(n,(pc-startpos))/np.dot(n,dc)*dc+pc+[0,0,880*np.sqrt(2)+800]
        elif orientation == "or4":
            n = np.array([0,1,0])
            new_stpo = -np.dot(n,(pc-startpos))/np.dot(n,dc)*dc+pc+[0,0,880*np.sqrt(2)+800]

        return new_stpo

    
    def _scan_optic_1D(self, startpos, ds, dir):
        self.coord.absolute_pos(x=[startpos[0],5000],y=[startpos[1],5000],z=[startpos[2]+500,5000])
        mes = np.zeros((ds.shape[0],8))
        for it,d in enumerate(ds):
            mespos = startpos+dir*d
            mes[it,0:3]=mespos
            self.coord.absolute_pos(x=[mespos[0],500],y=[mespos[1],500],z=[mespos[2],500],precision_mode=True)
            mes[it,3:6]=self.coord.get_pos()
            value, std = self.optic.measure()
            mes[it,6] = value
            mes[it,7] = mes[it,2] - mes[it,6]
        return mes
    
    def _scan_mes_points(self,mespc,R_cm,t_cm):
        s = mespc.shape
        mes = np.zeros((s[0], s[1], 8))  # Initialize the result array

        for in2 in range(s[1]):
            for in1 in range(s[0]):
                mesp = R_cm @ (mespc[in1, in2, :3].reshape(3, 1) - t_cm.reshape(3, 1))
                mespos = mesp.flatten() + np.array([0, 0, 2000])
                mes[in1, in2, :3] = mespos
                self.coord.absolute_pos(x=[mespos[0],500],y=[mespos[1],500],z=[mespos[2],500],precision_mode=True)
                mes[in1, in2, 3:6] = self.coord.get_pos()
                value, std = self.optic.measure()
                mes[in1, in2, 6] = value
                mes[in1, in2, 7] = mes[in1, in2, 5] - mes[in1, in2, 6]

        endpos = mespos + np.array([0, 0, 10000])
        self.coord.absolute_pos(x=[endpos[0],500],y=[endpos[1],500],z=[endpos[2],5000])
        return mes
    
    @staticmethod
    def _filter_points(mes, ds):
        # Calculate the midpoints between adjacent ds values
        dsdif = (ds[:-1] + ds[1:]) / 2
        dmesdif = np.diff(mes[:, 7]) / np.diff(ds) 

        ds0 = []
        # Find zero crossings
        for in0 in range(len(dsdif) - 1):
            if dmesdif[in0] * dmesdif[in0 + 1] < 0:
                # Interpolate to find the zero crossing
                interp_func = interp1d(dmesdif[in0:in0+2], dsdif[in0:in0+2], kind='linear')
                zero_crossing = interp_func(0)
                ds0.append(zero_crossing)
                #plt.plot([zero_crossing, zero_crossing], [np.max(dmesdif), np.min(dmesdif)], '--k')

        # Find the zero crossing closest to zero
        ds0 = np.array(ds0)
        in0 = np.argmin(np.abs(ds0))
        ds0is = ds0[in0]

        # Filter the measurements based on proximity to the zero crossing
        in0 = np.where(np.abs(ds - ds0is) < 800)[0]
        fmes = mes[in0, :]
        return fmes, ds0is

    @staticmethod
    def _check_data_reduction(mes,mes_new):
        lmesp = len(mes)
        lmespnew = len(mes_new)
        if (lmespnew / lmesp) < 0.8:
            print(f"More than 80% of the measurement data are sorted out! ({lmespnew}/{lmesp})")
        print(f"{lmespnew}/{lmesp} are taken for the optical fitting!")

    @staticmethod
    def _check_outliers(reserr):
        dmaxal = 12
        dmax = np.max(np.abs(reserr))
        if dmax > dmaxal:
            print(f"Difference to ideal geometry is {dmax:.1f} µm, which is higher than the allowed value of {dmaxal:.1f} µm!")

    def _fit_conductor_geometry(self,mespointlist, dc0, Rc0):
        """
        Fits the conductor geometry.
        """
        # Filter NaN values
        ind = np.where(~np.isnan(mespointlist[:, 2]))[0]
        mpl = mespointlist[ind, :]

        # Find maximum absolute direction component
        inm = np.argmax(np.abs(dc0))
        ino = [i for i in range(3) if i != inm]

        # Calculate initial conductor center
        pc0 = np.mean(mpl, axis=0)
        pc = pc0 - dc0 * np.dot(dc0, pc0)

        # Convert to fitting parameters
        fpar = self.pc2fpar(pc, ino)
        x0 = [fpar[0], fpar[1], dc0[ino[0]], dc0[ino[1]], Rc0]

        # Optimization settings
        options = {'ftol': 1e-15, 'xtol': 1e-18, 'max_nfev': 50000, 'verbose': 2}

        # Perform non-linear least squares optimization
        result = least_squares(self.fitFunc, x0, args=(mpl, inm, ino, dc0), **options)

        # Retrieve fitted parameters
        x = result.x
        dc = self.fpar2dc([x[2], x[3]], inm, ino, dc0)
        pc = self.fpar2pc([x[0], x[1]], dc, inm, ino)
        Rc = x[4]

        # Residual errors
        reserr = self.fitFunc(x, mpl, inm, ino, dc0)

        return pc, dc, Rc, reserr

    def fitFunc(self,x, mpl, inm, ino, dc0):
        """
        Fit function for non-linear least squares.
        """
        dc = self.fpar2dc([x[2], x[3]], inm, ino, dc0)
        pc = self.fpar2pc([x[0], x[1]], dc, inm, ino)
        F = np.zeros(len(mpl))

        for inx in range(len(mpl)):
            F[inx] = x[4] - np.linalg.norm(np.cross(dc, mpl[inx, :3] - pc))

        return F

    @staticmethod
    def dc2fpar(dc, ino):
        """
        Convert direction vector to fitting parameters.
        """
        return [dc[ino[0]], dc[ino[1]]]

    @staticmethod
    def fpar2dc(fpar, inm, ino, dc0):
        """
        Convert fitting parameters to direction vector.
        """
        dc = np.zeros(3)
        dc[ino[0]] = fpar[0]
        dc[ino[1]] = fpar[1]
        dc[inm] = np.sqrt(1 - fpar[0]**2 - fpar[1]**2) * np.sign(dc0[inm])
        return dc

    @staticmethod
    def pc2fpar(pc, ino):
        """
        Convert center point to fitting parameters.
        """
        return [pc[ino[0]], pc[ino[1]]]

    @staticmethod
    def fpar2pc(fpar, dc, inm, ino):
        """
        Convert fitting parameters to center point.
        """
        pc = np.zeros(3)
        pc[ino[0]] = fpar[0]
        pc[ino[1]] = fpar[1]
        pc[inm] = -(dc[ino[0]] * fpar[0] + dc[ino[1]] * fpar[1]) / dc[inm]
        return pc

    @staticmethod
    def _get_mag_mes_val(x, la, K):
        return (x[3] * K * (np.sin(np.radians(x[2])) * x[1] + np.cos(np.radians(x[2])) * (la + x[0])) /
            ((la + x[0])**2 + x[1]**2))

    def _fitfun(self,x, K, Mg, lag):
        return self._get_mag_mes_val(x, lag, K) - Mg

    def _fit_mag_scan(self,M, la, I0, psz0):
        K = 2e-7 * I0 * 1e6 # [K] = T*m --> 1e6 --> [K] = mT*mm 
        lag = la * 1e-3  # [la] = µm --> 1e-3 --> [lag] = mm
        x0 = np.array([0, psz0[0] * 1e-3, 45, 1])
        
        options = {'ftol': 1e-15, 'xtol': 1e-15, 'verbose': 0}
        res = least_squares(self._fitfun, x0, args=(K, M, lag), **options)
        x = res.x
        
        Berrmax = 1e-3  # Filter border [mT] for outliers
        dB = (M - self._get_mag_mes_val(x, lag, K)) / I0  # in mT
        ind = np.abs(dB) < Berrmax
        
        Mg = M[ind]
        lag = lag[ind]
        
        res = least_squares(self._fitfun, x0, args=(K, Mg, lag), **options)
        x = res.x
        
        # if len(Mg) / len(M) < 0.7:
        #     print(f'Only {len(Mg)} of {len(M)} values are used for fitting!')
        #     input("Press Enter to continue...")
        
        # err = (Mg - self._get_mag_mes_val(x, lag, K)) / I0
        
        # if np.max(np.abs(err)) > Berrmax:
        #     print(f'There are still values that differ more than Berrmax (={Berrmax * 1e3} µT)')
        #     import matplotlib.pyplot as plt
        #     plt.plot(lag, err * 1e3, '.-')
        #     plt.grid(True)
        #     plt.xlabel('\u03BB [mm]')
        #     plt.title(f'st={np.std(err) * 1e3} µT')
        #     plt.ylabel('\u0394 Signal [µT] @ 1A')
        #     plt.show()
        #     input("Press Enter to continue...")
        
        fit = {
            'psyc': x[0] * 1e3,
            'pszc': x[1] * 1e3,
            'd1': x[2],
            'Se': x[3]
        }
        
        return fit
