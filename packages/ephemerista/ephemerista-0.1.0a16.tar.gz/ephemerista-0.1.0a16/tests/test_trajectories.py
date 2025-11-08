import numpy as np

from ephemerista.coords.trajectories import Trajectory


def test_from_csv(resources):
    trajectory = Trajectory.from_csv(resources.joinpath("lunar/lunar_transfer.csv"))
    assert isinstance(trajectory, Trajectory)
    assert isinstance(trajectory.states, np.ndarray) and trajectory.states.shape[0] == 2367
