from typing import Any
from humalab.constants import MetricDimType, GraphType

GRAPH_TO_DIM_TYPE = {
    GraphType.LINE: MetricDimType.ONE_D,
    GraphType.HISTOGRAM: MetricDimType.ONE_D,
    GraphType.BAR: MetricDimType.ONE_D,
    GraphType.GAUSSIAN: MetricDimType.ONE_D,
    GraphType.SCATTER: MetricDimType.TWO_D,
    GraphType.THREE_D_MAP: MetricDimType.THREE_D,
}


class Metrics:
    """Base class for tracking and logging metrics during runs and episodes.

    Metrics provide a flexible way to log time-series data or aggregated values
    during experiments. Data points are collected with optional x-axis values
    and can be visualized using different graph types.

    Subclasses should override _finalize() to implement custom processing logic.

    Attributes:
        graph_type (GraphType): The type of graph used for visualization.
    """
    def __init__(self,
                 graph_type: GraphType=GraphType.LINE) -> None:
        """Initialize a new Metrics instance.

        Args:
            graph_type (GraphType): The type of graph to use for visualization
                (e.g., LINE, BAR, HISTOGRAM, SCATTER). Defaults to LINE.
        """
        self._values = []
        self._x_values = []
        self._step = -1
        self._metric_dim_type = GRAPH_TO_DIM_TYPE.get(graph_type, MetricDimType.ONE_D)
        self._graph_type = graph_type

    @property
    def metric_dim_type(self) -> MetricDimType:
        """The dimensionality of the metric data.

        Returns:
            MetricDimType: The metric dimension type.
        """
        return self._metric_dim_type

    @property
    def graph_type(self) -> GraphType:
        """The type of graph used for visualization.

        Returns:
            GraphType: The graph type.
        """
        return self._graph_type
    
    def log(self, data: Any, x: Any = None, replace: bool = False) -> None:
        """Log a new data point for the metric.

        Args:
            data (Any): The data point to log.
            x (Any | None): The x-axis value associated with the data point.
                If None, uses an auto-incrementing step counter.
            replace (bool): Whether to replace the last logged value. Defaults to False.
        """
        if self._graph_type == GraphType.THREE_D_MAP:
            if len(data) != 3:
                raise ValueError("Data for 3D map metrics must be a list or tuple of three values.")
        elif self._graph_type == GraphType.SCATTER:
            if len(data) != 2:
                raise ValueError("Data for scatter metrics must be a list or tuple of two values.")    
        
        if replace:
            self._values[-1] = data
            if x is not None:
                self._x_values[-1] = x
        else:
            self._values.append(data)
            if x is not None:
                self._x_values.append(x)
            else:
                self._x_values.append(self._step)
                self._step += 1
        
    def finalize(self) -> dict:
        """Finalize the logged data for processing."""
        ret_result = self._finalize()

        return ret_result

    def _finalize(self) -> dict:
        """Process the logged data before submission. To be implemented by subclasses."""
        ret_val = {
            "values": self._values,
            "x_values": self._x_values
        }
        self._values = []
        self._x_values = []
        self._step = -1
        return ret_val    
