import os
import pandas as pd
from pathlib import Path
from typing import Union
from metacell.dataloader._logger import setup_logger

class scMetData(object):
    def __init__(self, file: Union[Path, str],):
        self.file = file
        self.filename = os.path.basename(file)

        self.logger, self.memory_handler = setup_logger()

        self.mz_data = {}
        self.intensity_data = {}
        self.raw_scm_data = pd.DataFrame()
        self.cell_marker_eic = {}
        self.scm_events_index = {}
        self.scm_events = pd.DataFrame()
        self.cell_feature_matrix = pd.DataFrame()
        pass

    # 当调用 mdata.scm_events['marker']时，返回 mdata.raw_scm_data[scm_events[marker]]
