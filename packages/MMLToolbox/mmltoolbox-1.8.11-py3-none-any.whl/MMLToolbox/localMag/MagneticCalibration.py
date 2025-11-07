import numpy as np
from scipy.optimize import least_squares, minimize
from numpy.linalg import inv

from MMLToolbox.localMag import StoreMagneticAligner

#TODO: save

class MagneticCalibration:
    def __init__(self, store: StoreMagneticAligner):
        self.store = store

    def _get_mag_mes_val(self, x, la, K):
        psy, psz, d1, Se, M0 = x
        la_shifted = la + psy
        num = np.sin(np.radians(d1)) * psz + np.cos(np.radians(d1)) * la_shifted
        denom = la_shifted ** 2 + psz ** 2
        return Se * K * num / denom + M0

    def _fitfun(self, x, K, M, lag):
        #print(x)
        return self._get_mag_mes_val(x, lag, K) - M

    def _fit_mag_scan_off(self, M, la, I0, psz0):
        K = 2e-7 * I0 * 1e6
        la = la.flatten()
        lag = la * 1e-3
        x0 = np.array([0, psz0 * 1e-3, 45, 1, 0])
        Berrmax = 1e-3

        options = {'ftol': 1e-15, 'xtol': 1e-15, 'verbose': 2, 'method': "trf"}
        lower_bounds = [-np.inf, 0.0, -180, 0.0, -np.inf]
        upper_bounds = [ np.inf, np.inf, 180, np.inf, np.inf]

        result = least_squares(self._fitfun, x0, bounds=(lower_bounds,upper_bounds), args=(K, M, lag), **options)
        dB = (M - self._get_mag_mes_val(result.x, lag, K)) / I0
        ind = np.abs(dB) < Berrmax

        M_filtered = M[ind]
        lag_filtered = lag[ind]

        result = least_squares(self._fitfun,x0,bounds=(lower_bounds,upper_bounds), args=(K, M_filtered, lag_filtered), xtol=1e-15, ftol=1e-15)
        print(result.x)
        return {
            "psyc": result.x[0] * 1e3,
            "pszc": result.x[1] * 1e3,
            "d1": result.x[2],
            "Se": result.x[3],
            "M0": result.x[4]
        }

    def _rotation_and_translation(self, fit, orientation, mscan):
        oscan_group = f"cal/{orientation}/oscan"
        mscan_group = f"cal/{orientation}/{mscan}"

        fit["psad"] = self.store.read(f"{mscan_group}/startpos")
        fit["xc"] = self.store.read(f"{oscan_group}/dc")
        fit["yc"] = self.store.read(f"{mscan_group}/ds")
        fit["zc"] = np.cross(fit["xc"], fit["yc"])

        fit["Rmc"] = np.vstack([fit["xc"], fit["yc"], fit["zc"]])
        fit["tmc"] = self.store.read(f"{oscan_group}/pc")
        fit["Rcm"] = inv(fit["Rmc"])
        fit["tcm"] = -fit["Rmc"] @ fit["tmc"]

        return fit

    def _fit_line_intersect(self, pa: np.ndarray, da: np.ndarray):
        def residual(x):
            return np.concatenate([
                np.cross(da[i], x - pa[i]) for i in range(len(pa))
            ])
        
        x0 = np.mean(pa, axis=0)
        result = least_squares(residual, x0)
        x = result.x
        resdis = [np.linalg.norm(np.cross(da[i], x - pa[i])) for i in range(len(pa))]
        return x, resdis

    def _fit_normal_vec(self, nBequ: np.ndarray, direction: str):
        if direction == "x":
            nB_ideal = np.array([1, 0, 0])
        elif direction == "y":
            nB_ideal = np.array([0, 1, 0])
        else:
            nB_ideal = np.array([0, 0, 1])

        ind = np.argmax(np.abs(nB_ideal))
        io = [i for i in range(3) if i != ind]

        def objective(x):
            candidate = np.zeros(3)
            candidate[io[0]] = x[0]
            candidate[io[1]] = x[1]
            candidate[ind] = np.sqrt(1 - x[0]**2 - x[1]**2) * np.sign(nB_ideal[ind])
            projections = nBequ @ candidate
            return -np.sum(projections ** 2)

        res = minimize(objective, [nB_ideal[io[0]], nB_ideal[io[1]]], bounds=[(-1, 1), (-1, 1)])
        x = res.x
        nB = np.zeros(3)
        nB[io[0]] = x[0]
        nB[io[1]] = x[1]
        nB[ind] = np.sqrt(1 - x[0]**2 - x[1]**2) * np.sign(nB_ideal[ind])
        return nB / np.linalg.norm(nB)

    def process(self, scan_list: list[str], direction: str) -> dict:
        axis_col = {"x": 0, "y": 1, "z": 2}
        col = axis_col[direction]

        pb, dpB, nBequ = [], [], []

        for scan in scan_list:
            orientation, mscan = scan.split(".")

            M = self.store.read(f"cal/{orientation}/{mscan}/M")[:, col]
            la = self.store.read(f"def/{orientation}/{mscan}/la")
            I0 = self.store.read(f"cal/{orientation}/{mscan}/IO")[0]
            psz0 = self.store.read(f"def/{orientation}/{mscan}/pszc_ideal")[0]

            fit = self._fit_mag_scan_off(M, la, I0, psz0)
            fit = self._rotation_and_translation(fit, orientation, mscan)

            Rcm = fit["Rcm"]
            tmc = fit["tmc"]
            pszc = fit["pszc"]
            psyc = fit["psyc"]
            psad = fit["psad"]
            xc, yc, zc = fit["xc"], fit["yc"], fit["zc"]

            pb.append(Rcm[:, 1] * psyc + Rcm[:, 2] * pszc + tmc - psad)
            dpB.append(Rcm[:, 0])

            if direction == "x":
                nBequ.append(np.sin(np.radians(fit["d1"])) * zc + np.cos(np.radians(fit["d1"])) * yc)
            elif direction == "y":
                nBequ.append(np.sin(np.radians(fit["d1"])) * xc + np.cos(np.radians(fit["d1"])) * zc)
            else:
                nBequ.append(np.sin(np.radians(fit["d1"])) * yc + np.cos(np.radians(fit["d1"])) * xc)

        pb = np.array(pb)
        dpB = np.array(dpB)
        nBequ = np.array(nBequ)

        pB_fit, resdis = self._fit_line_intersect(pb, dpB)
        nB_fit = self._fit_normal_vec(nBequ, direction)

        return {
            "pb": pB_fit,
            "nB": nB_fit,
            "resdis": resdis,
            "pb_all": pb
        }

    @staticmethod
    def print_summary(results: dict):
        x, y, z = results["x"], results["y"], results["z"]
        print(f"resdis x: {x['resdis'][0]:.1f}µm   {x['resdis'][1]:.1f}µm")
        print(f"resdis y: {y['resdis'][0]:.1f}µm   {y['resdis'][1]:.1f}µm")
        print(f"resdis z: {z['resdis'][0]:.1f}µm   {z['resdis'][1]:.1f}µm")

        print(f"dxy={np.linalg.norm(y['pb'] - x['pb']):.0f}µm  dyz={np.linalg.norm(z['pb'] - y['pb']):.0f}µm  dzx={np.linalg.norm(z['pb'] - x['pb']):.0f}µm")
        print(f"axy={np.degrees(np.arccos(np.clip(np.dot(y['nB'], x['nB']), -1, 1))):.2f}°  "
              f"ayz={np.degrees(np.arccos(np.clip(np.dot(y['nB'], z['nB']), -1, 1))):.2f}°  "
              f"azx={np.degrees(np.arccos(np.clip(np.dot(x['nB'], z['nB']), -1, 1))):.2f}°")

        pB = np.mean([x['pb'], y['pb'], z['pb']], axis=0)
        print(f"pB: {pB[0]:8.0f} {pB[1]:8.0f} {pB[2]:8.0f}")
        for key, res in zip(['x', 'y', 'z'], [x, y, z]):
            delta = res['pb'] - pB
            norm = np.linalg.norm(delta)
            print(f"{key}.sf-pB: {delta[0]:5.0f} {delta[1]:5.0f} {delta[2]:5.0f} norm: {norm:5.0f}")

    @staticmethod
    def combine_axes(results: dict) -> dict:
        pB = np.mean([v["pb"] for v in results.values()], axis=0)
        nB = np.vstack([v["nB"] for v in results.values()])
        return {"pB": pB, "nB": nB}
