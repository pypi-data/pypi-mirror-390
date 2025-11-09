from typing import *

class Scalar:
    """
    Dataclass containing a scalar datapoint. The datapoints fetched from the DB are formatted into this class.
    """
    def __init__(self, run_id: int, epoch: Optional[int], step: int, split: Optional[str], label: str, value: float, wall_time: int, run_rep: int):
        """
        :param run_id: The run identifier.
        :param epoch: The epoch if availalable else None
        :param step: The training step of the datapoint
        :param split: The split (Train, Val, Test, or other) of the datapoint if given else None.
        :param label: The label, usually the metric name (ex: Accuracy).
        :param value: The value of the datapoint
        :param wall_time: The time since the start in seconds
        :param run_rep: The run repetition (When multiple runs are done of the same experiment) else 0.
        """
        self.run_id = run_id
        self.epoch = epoch
        self.step = step
        self.split = split
        self.label = label
        self.value = value
        self.wall_time = wall_time
        self.run_rep = run_rep

    def __str__(self):
        return (f"Scalar(run_id={self.run_id}, epoch={self.epoch}, step={self.step}, split={self.split}, "
                f"label={self.label}, value={self.value}, wall_time={self.wall_time}, run_rep={self.run_rep})")