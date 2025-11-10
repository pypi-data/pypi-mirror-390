from copy import deepcopy
from ctypes import *
from pathlib import Path

import numpy as np
import pandas as pd


def struct2fields(struct: Structure, substruct: bool = False) -> list:
    output = []
    for obj, t in struct._fields_:
        if isinstance(t, type(c_int)):
            output.append(obj)
        # elif isinstance(t, type(Array)):
        #     for k in range(t._length_):
        #         output.append(f'{var}[{k}]')
        elif isinstance(t, type(Array)):
            nshape = np.asarray(t()).shape
            ndim = len(nshape)
            if ndim == 1:
                for i in range(nshape[0]):
                    output.append(f"{obj}[{i}]")
            elif ndim == 2:
                for i in range(nshape[0]):
                    for j in range(nshape[1]):
                        output.append(f"{obj}[{i}][{j}]")
            elif ndim == 3:
                for i in range(nshape[0]):
                    for j in range(nshape[1]):
                        for k in range(nshape[2]):
                            output.append(f"{obj}[{i}][{j}][{k}]")
        elif substruct and isinstance(t, type(Structure)):
            subobj = struct2fields(getattr(struct, obj), substruct=True)
            output += [f"{obj}.{s}" for s in subobj]
    return output


def struct2array(struct: Structure, substruct: bool = False) -> np.ndarray:
    output = np.zeros(0)
    for var, t in struct._fields_:
        if isinstance(t, type(c_int)):
            output = np.append(output, getattr(struct, var))
        elif isinstance(t, type(Array)):
            output = np.append(output, np.ctypeslib.as_array(getattr(struct, var)))
        # elif substruct and isinstance(t, type(Structure)):
        #     output = np.append(
    return output


def array2dict(name: str, array: np.ndarray) -> dict:
    output = {}
    for k, val in enumerate(array):
        vname = f"{name}[{k}]"
        if len(val.shape) == 0:
            output[vname] = val
        else:
            output.update(array2dict(vname, val))
    return output


def struct2dict(struct: Structure, substruct: bool = False) -> dict:
    output = {}
    for obj, t in struct._fields_:
        if isinstance(t, type(c_int)):
            output[obj] = getattr(struct, obj)
            # bool to int
            # if t._type_ == '?':
            #     output[obj] = int(output[obj])
        elif isinstance(t, type(Array)):
            array = np.ctypeslib.as_array(getattr(struct, obj))
            output.update(array2dict(obj, array))
            # for k, val in enumerate(array):
            #     output[f'{obj}[{k}]'] = val
        elif substruct and isinstance(t, type(Structure)):
            subobj = struct2dict(getattr(struct, obj), substruct=True)
            output.update({f"{obj}.{k}": v for k, v in subobj.items()})
    return output


# def struct2dataframe(struct, substruct=False):
#     return output


def binary2struct(file: Path, datatype: Structure) -> Array[Structure]:
    file = Path(file)
    with open(file, "rb") as f:
        filesize = file.stat().st_size
        if filesize % sizeof(datatype) != 0:
            raise ValueError(f"Wrong binary size!! binary size = {filesize}, type size = {sizeof(datatype)}")
        size = int(filesize / sizeof(datatype))
        structarray = (datatype * size)()
        f.readinto(structarray)
    return deepcopy(structarray)


def structarray2dataframe(structarray, substruct: bool = False) -> pd.DataFrame:
    return pd.DataFrame([struct2dict(s, substruct=substruct) for s in structarray])


def read_binary(file: Path, datatype: Structure, substruct: bool = True) -> pd.DataFrame:
    df = structarray2dataframe(binary2struct(file, datatype), substruct=substruct)
    columns = df.columns[np.where(df.dtypes == bool)[0]]  # noqa: E721
    df[columns] = df[columns].astype(int)
    return df
