from dataclasses import dataclass, field
import numpy as np
from typing import Optional, List, Dict
# from torch import tensor
# import torch


@dataclass(frozen=True)
class InputJob:
    ljob_path : str
    image : np.ndarray
    sn : int

if __name__ == "__main__":
    input_job = InputJob(ljob_path="tmp.ljob", image=np.ones((720,1280,3), dtype=np.uint8), sn=0)
    input_job = InputJob(ljob_path="tmp.ljob", image=None, sn=0)
    print(f"{input_job = }")