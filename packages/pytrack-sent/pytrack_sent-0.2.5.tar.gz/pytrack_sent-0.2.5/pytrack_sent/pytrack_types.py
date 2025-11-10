from typing import Callable,Any,Dict,TypedDict
import time

class TrackStats(TypedDict):
    calls: int
    total_time: float
    avg_time: float

TrackedFunc = Callable[...,Any]