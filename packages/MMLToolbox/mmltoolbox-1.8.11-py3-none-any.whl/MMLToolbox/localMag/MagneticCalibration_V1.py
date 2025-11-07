import numpy as np

from scipy.optimize import least_squares
from numpy.linalg import inv

from MMLToolbox.localMag import StoreMagneticAligner
from MMLToolbox.util.types import *


class MagneticCalibration:
    def __init__(self, store:StoreMagneticAligner):
        self.store = store

    def _get_mag_mes_val(self, x, la, K):
        psy, psz, d1, Se, M0 = x
        la_shifted = la + psy
        num = np.sin(np.radians(d1)) * psz + np.cos(np.radians(d1)) * la_shifted
        denom = la_shifted ** 2 + psz ** 2
        return Se * K * num / denom + M0

    def _fitfun(self,x,K,M,lag):
        return self._get_mag_mes_val(x, lag, K) - M

    def _fit_mag_scan_off(self, M, la, I0, psz0, col=0):
        K = 2e-7 * I0 * 1e6
        M = M[:,col].flatten()
        la = la.flatten()
        lag = la * 1e-3
        x0 = np.array([0, psz0 * 1e-3, 45, 1, 0])
        Berrmax = 1e-3

        result = least_squares(self._fitfun,x0,args=(K,M,lag),xtol=1e-15,ftol=1e-15)
        dB = (M - self._get_mag_mes_val(result.x, lag, K)) / I0
        ind = np.abs(dB) < Berrmax

        Mg = M[ind]
        lag = lag[ind]

        result = least_squares(self._fitfun,x0,args=(K,Mg,lag),xtol=1e-15,ftol=1e-15)
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

    def _fit_single_scan(self, orientation, mscan, column):
        mscan_group = f"cal/{orientation}/{mscan}"
        def_group = f"def/{orientation}/{mscan}"

        M = self.store.read(f"{mscan_group}/M")
        la = self.store.read(f"{def_group}/la")
        I0 = self.store.read(f"{mscan_group}/IO")[0]
        psz0 = self.store.read(f"{def_group}/pszc_ideal")[0]

        fit = self._fit_mag_scan_off(M, la, I0, psz0, col=column)
        return self._rotation_and_translation(fit, orientation, mscan)

    def _fit_line_intersect(self, pa: np.ndarray, da: np.ndarray):
        A = np.zeros((3, 3))
        b = np.zeros(3)
        for i in range(len(pa)):
            n = np.eye(3) - np.outer(da[i], da[i])
            A += n
            b += n @ pa[i]
        return np.linalg.solve(A, b)

    def _fit_normal_vec(self, nBequ: np.ndarray, nB_ideal: np.ndarray):
        from scipy.optimize import minimize

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

    def process(self, scan_list: List[str], direction: str) -> Dict[str, np.ndarray]:
        axis_map = {
            "x": {"col": 0, "nBequ": lambda f: np.sin(np.radians(f["d1"])) * f["zc"] + np.cos(np.radians(f["d1"])) * f["yc"]},
            "y": {"col": 1, "nBequ": lambda f: np.sin(np.radians(f["d1"])) * f["xc"] + np.cos(np.radians(f["d1"])) * f["zc"]},
            "z": {"col": 2, "nBequ": lambda f: np.sin(np.radians(f["d1"])) * f["yc"] + np.cos(np.radians(f["d1"])) * f["xc"]},
        }

        axis_conf = axis_map.get(direction, axis_map["z"])
        col = axis_conf["col"]
        compute_nBequ = axis_conf["nBequ"]

        fits = [self._fit_single_scan(*scan.split("."), column=col) for scan in scan_list]
        pb = []
        nBequ = []
        for f in fits:
            pb.append((f["Rcm"][:, 1] * f["psyc"] + f["Rcm"][:, 2] * f["pszc"] + f["tmc"] - f["psad"]))
            nBequ.append(compute_nBequ(f))
        pb = np.array(pb)
        nBequ = np.array(nBequ)
        pa = np.array([f["psad"] for f in fits])
        da = np.array([f["Rcm"][:, 0] for f in fits])
        pb_fit = self._fit_line_intersect(pa, da)
        nB_fit = self._fit_normal_vec(nBequ, np.mean(da, axis=0))
        return {"pb": pb_fit, "nB": nB_fit}

    @staticmethod
    def combine_axes(results: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        pB = np.mean([v["pb"] for v in results.values()], axis=0)
        nB = np.vstack([v["nB"] for v in results.values()])
        return {"pB": pB, "nB": nB}
