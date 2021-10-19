import pandas as pd
import numpy as np
from pandas import Timestamp

from dw_squared import PALETTE
from dw_squared.client import DWSquared


class Lines(DWSquared):
    def __init__(self,
                 data: pd.DataFrame = None,
                 title: str = '',
                 source: str = '',
                 prefix_unit: str = '',
                 notes: str = '',
                 graph_start: Timestamp = None,
                 graph_end: Timestamp = None,
                 display_today: bool = True,
                 height: int = None,
                 width: int = None,
                 token: str = None,
                 *args,
                 **kwargs,
                 ):
        super().__init__(title, token, height, width, graph_start, graph_end, source, notes)
        self.frame = data
        self.title = title
        self.source = source
        self.notes = notes
        self.display_today = display_today
        self.prefix_unit = prefix_unit
        self._data = self.reshape_data(self.frame)

    @property
    def chart(self):
        if self._chart is None:
            self._chart = self.dw.create_chart(
                self.title, chart_type='d3-lines', data=self._data)
        return self._chart

    def reshape_data(self, frame: pd.DataFrame):
        self._data = frame.reset_index()
        return self._data

    def update_data(self, frame):
        self._update_data(frame, self.reshape_data)

    def metadata(self):
        palette = {legend: next(PALETTE) for legend in self._data.columns[1:]}
        extra_properties = {
            'data': {
                'column-format': {
                    self._data.columns[1]: {
                        'type': 'auto',
                        'number-append': f' {self.prefix_unit}',
                    }
                }
            },
            'visualize': {
                'x-grid': 'ticks',
                'y-grid': 'on',
                'custom-colors': palette,
                'scale-y': 'linear',
                'labeling': 'top' if self._data.shape[1] > 2 else 'off',
                'base-color': 7,
                'label-colors': True,
                'interpolation': 'linear',
                'show-tooltips': True,
                'y-grid-labels': 'inside',
                "line-symbols": True,
                "line-symbols-on": "last",
                "line-value-labels": True
            }
        }
        extra_properties.update(self.default_publish)
        extra_properties.update(self.initial_properties)
        if self.display_today:
            extra_properties['visualize'].update(self.today_line)
        self.dw.update_metadata(self.chart['id'], extra_properties)
