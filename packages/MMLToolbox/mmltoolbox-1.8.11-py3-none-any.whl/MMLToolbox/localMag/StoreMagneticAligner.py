import h5py
import numpy as np
import os

from abc import ABC
from MMLToolbox.util.types import *

#TODO: save res from MagneticCalibration

class StoreMagneticAligner(ABC):
  def __init__(self, fileName:str,stpm_offset:ndarray=None,IO:int=None) -> None:
    if stpm_offset is None: stpm_offset=np.array([536,-263,-45089])
    if IO is None: IO = 15
    self.fileName = fileName
    self.stpm_offset = stpm_offset
    self.IO = IO
    self._init_groups()

  ################## Private Functions ################## 
  def _init_groups(self) -> None:
    if os.path.exists(f"{self.fileName}.h5"):
        return  # Avoid overwriting existing data

    with h5py.File(f"{self.fileName}.h5", "w") as hf:
      for or_groups in ["or1","or2","or3","or4"]:
        or_group = hf.create_group(f"def/{or_groups}")

        # Optical scan group (oscan)
        oscan_group = or_group.create_group("oscan")
        oscan_group.create_dataset("startpos", data=np.zeros(3))
        oscan_group.create_dataset("xc", data=np.zeros(3))
        oscan_group.create_dataset("yc", data=np.zeros(3))

        # Magnetic scan group (mscan)
        for mscan in ["mscan1", "mscan2"]:
          mscan_group = or_group.create_group(mscan)
          mscan_group.create_dataset("startpos", data=np.zeros(3))
          mscan_group.create_dataset("ds_ideal", data=np.zeros(3))
          mscan_group.create_dataset("pszc_ideal", data=np.array([0.0]))
          mscan_group.create_dataset("IO", data=np.array([self.IO]))

      # Cal group
      for or_groups in ["or1","or2","or3","or4"]:
        or_group = hf.create_group(f"cal/{or_groups}")

        # Optic scan group
        oscan_group = or_group.create_group("oscan")
        oscan_group.create_dataset("pc", data=np.zeros(3))
        oscan_group.create_dataset("dc", data=np.zeros(3))

        # Magnetic scan group
        for mscan in ["mscan1", "mscan2"]:
          mscan_group = or_group.create_group(mscan)
          mscan_group.create_dataset("ds", data=np.zeros(3))
          mscan_group.create_dataset("M", shape=(0, 3), maxshape=(None, 3), dtype="f")
          mscan_group.create_dataset("startpos", data=np.zeros(3))
          mscan_group.create_dataset("IO", data=np.zeros(1))

  def init_orientation(self,orientation):
    if orientation == "or1": call_func = self.init_orientation_1
    elif orientation == "or2": call_func = self.init_orientation_2
    #elif orientation == "or3": call_func = self.init_orientation_3
    elif orientation == "or4": call_func = self.init_orientation_4
    else: 
      ValueError("Orientation not defined")

    call_func()

  ################## Public Functions ################## 
  def init_orientation_1(self,scan_steps:int=100,ostartpos:ndarray=None,mstartpos1:ndarray=None,mla1:int=3000,mstartpos2:ndarray=None,mla2:int=3000)-> None:
    if ostartpos is None: ostartpos=np.array([-36937.3,15083.3,-97613.7])
    if mstartpos1 is None: mstartpos1=np.array([33227.3,-27224.2,-111445.2])
    if mstartpos2 is None: mstartpos2=np.array([33227.3,-23536.5,-114074.3])
    
    with h5py.File(f"{self.fileName}.h5", "a") as hf:
      hf["def/or1/oscan/startpos"][:] = ostartpos
      hf["def/or1/oscan/xc"][:] = np.array([1,0,0])
      hf["def/or1/oscan/yc"][:] = np.array([0,1,0])

      hf["def/or1/mscan1/startpos"][:] = mstartpos1
      hf["def/or1/mscan1"].create_dataset(name="la",data=np.linspace(-mla1*1.5/2,mla1*1.5/2,scan_steps))
      hf["def/or1/mscan1/ds_ideal"][:] = np.array([0,1,0])
      hf["def/or1/mscan1/pszc_ideal"][:] = mla1

      hf["def/or1/mscan2/startpos"][:] = mstartpos2
      hf["def/or1/mscan2"].create_dataset(name="la",data=np.linspace(-mla2*1.5/2,mla2*1.5/2,scan_steps))
      hf["def/or1/mscan2/ds_ideal"][:] = np.array([0,0,-1])
      hf["def/or1/mscan2/pszc_ideal"][:] = mla2

  def init_orientation_2(self,scan_steps:int=100,ostartpos:ndarray=None,mstartpos1:ndarray=None,mla1:int=2800,mstartpos2:ndarray=None,mla2:int=4500)-> None:
    if ostartpos is None: ostartpos=np.array([-37036.6,22719.7,-97646.7])
    if mstartpos1 is None: mstartpos1=np.array([32207.1,-26101,-111445.2])
    if mstartpos2 is None: mstartpos2=np.array([28135.8,-26101,-114074.3])
    
    with h5py.File(f"{self.fileName}.h5", "a") as hf:
      hf["def/or2/oscan/startpos"][:] = ostartpos
      hf["def/or2/oscan/xc"][:] = np.array([0,-1,0])
      hf["def/or2/oscan/yc"][:] = np.array([1,0,0])

      hf["def/or2/mscan1/startpos"][:] = mstartpos1
      hf["def/or2/mscan1"].create_dataset(name="la",data=np.linspace(-mla1*1.5/2,mla1*1.5/2,scan_steps))
      hf["def/or2/mscan1/ds_ideal"][:] = np.array([1,0,0])
      hf["def/or2/mscan1/pszc_ideal"][:] = mla1

      hf["def/or2/mscan2/startpos"][:] = mstartpos2
      hf["def/or2/mscan2"].create_dataset(name="la",data=np.linspace(-mla2*1.5/2,mla2*1.5/2,scan_steps)) # orig:20 steps
      hf["def/or2/mscan2/ds_ideal"][:] = np.array([0,0,1])
      hf["def/or2/mscan2/pszc_ideal"][:] = mla2

  def init_orientation_3(self,scan_steps:int=100,ostartpos:ndarray=None,mstartpos1:ndarray=None,mla1:int=4000,mstartpos2:ndarray=None,mla2:int=2000)-> None:
    # Dont use this, not adjusted
    return None
    if ostartpos is None: ostartpos=np.array([-37652,14718,-27550])
    if mstartpos1 is None: mstartpos1=np.array([37713,-27625,-793])+np.array([500,0,500]) + self.stpm_offset
    if mstartpos2 is None: mstartpos2=np.array([34853,-24544,-3652]) + np.array([0,500,0]) + self.stpm_offset
    
    with h5py.File(f"{self.fileName}.h5", "a") as hf:
      hf["def/or3/oscan/startpos"][:] = ostartpos
      hf["def/or3/oscan/xc"][:] = np.array([1/np.sqrt(2),0,-1/np.sqrt(2)])
      hf["def/or3/oscan/yc"][:] = np.array([0,1,0])

      hf["def/or3/mscan1/startpos"][:] = mstartpos1
      hf["def/or3/mscan1"].create_dataset(name="la",data=np.linspace(-mla1,mla1,20))
      hf["def/or3/mscan1/ds_ideal"][:] = np.array([0,1,0])
      hf["def/or3/mscan1/pszc_ideal"][:] = mla1

      hf["def/or3/mscan2/startpos"][:] = mstartpos2
      hf["def/or3/mscan2"].create_dataset(name="la",data=np.linspace(-mla2,mla2,scan_steps))
      hf["def/or3/mscan2/ds_ideal"][:] = np.array([-1/np.sqrt(2),0,-1/np.sqrt(2)])
      hf["def/or3/mscan2/pszc_ideal"][:] = 3000

  def init_orientation_4(self,scan_steps:int=100,ostartpos:ndarray=None,mstartpos1:ndarray=None,mla1:int=3000,mstartpos2:ndarray=None,mla2:int=4500)-> None:
    if ostartpos is None: ostartpos=np.array([-36857.6,19935,-30569.2])
    if mstartpos1 is None: mstartpos1=np.array([32156.5,-19063.5,-45580.7])
    if mstartpos2 is None: mstartpos2=np.array([36658.1,-21291,-50093.9])
    
    with h5py.File(f"{self.fileName}.h5", "a") as hf:
      hf["def/or4/oscan/startpos"][:] = ostartpos
      hf["def/or4/oscan/xc"][:] = np.array([0,1/np.sqrt(2),-1/np.sqrt(2)])
      hf["def/or4/oscan/yc"][:] = np.array([-1,0,0])

      hf["def/or4/mscan1/startpos"][:] = mstartpos1
      hf["def/or4/mscan1"].create_dataset(name="la",data=np.linspace(-mla1*1.5/2,mla1*1.5/2,scan_steps))
      hf["def/or4/mscan1/ds_ideal"][:] = np.array([-1,0,0])
      hf["def/or4/mscan1/pszc_ideal"][:] = mla1

      hf["def/or4/mscan2/startpos"][:] = mstartpos2
      hf["def/or4/mscan2"].create_dataset(name="la",data=np.linspace(-mla2*1.5/2,mla2*1.5/2,scan_steps)) # orig:20 steps
      hf["def/or4/mscan2/ds_ideal"][:] = np.array([0,1/np.sqrt(2),1/np.sqrt(2)])
      hf["def/or4/mscan2/pszc_ideal"][:] = mla2

  ################## write ################## 
  def save2cal(self,orientation,pc,dc,ds1,M1,new_stpm1,IO_mes1,ds2,M2,new_stpm2,IO_mes2):
    with h5py.File(f"{self.fileName}.h5", "a") as hf:
      hf[f"cal/{orientation}/oscan/dc"][:] = dc
      hf[f"cal/{orientation}/oscan/pc"][:] = pc

      dset_m1 = hf[f"cal/{orientation}/mscan1/M"]
      dset_m1.resize((M1.shape[0], 3))
      dset_m1[:] = M1
      hf[f"cal/{orientation}/mscan1/ds"][:] = ds1
      hf[f"cal/{orientation}/mscan1/startpos"][:] = new_stpm1
      hf[f"cal/{orientation}/mscan1/IO"][:] = IO_mes1

      dset_m2 = hf[f"cal/{orientation}/mscan2/M"]
      dset_m2.resize((M2.shape[0], 3))
      dset_m2[:] = M2
      hf[f"cal/{orientation}/mscan2/ds"][:] = ds2
      hf[f"cal/{orientation}/mscan2/startpos"][:] = new_stpm2
      hf[f"cal/{orientation}/mscan2/IO"][:] = IO_mes2

  ################## READ ################## 
  def read(self,name):
    with h5py.File(f"{self.fileName}.h5", "r") as hf:
      return hf[name][:]
    

  ################## Store Results ################## 
  def save_result(self, pB: np.ndarray, nB: np.ndarray):
    with h5py.File(f"{self.fileName}.h5", "a") as hf:
      if "result" not in hf:
        res_group = hf.create_group("result")
      else:
        res_group = hf["result"]

      if "pB" in res_group:
        del res_group["pB"]
      res_group.create_dataset("pB", data=pB)

      if "nB" in res_group:
        del res_group["nB"]
      res_group.create_dataset("nB", data=nB)

