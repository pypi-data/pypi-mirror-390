from __future__ import annotations
import time
import json
from typing import Any,Callable,Dict,Optional,TypeVar,cast
from functools import wraps
from pytrack_types import TrackStats,TrackedFunc

T = TypeVar("T",bound=Callable[...,Any])

class PyTrack:
    """General purpose performance and event tracker."""

    def __init__(self,name: str = "default") -> None:
        self.name: str = name
        self.functions: Dict[str,TrackStats] = {}
        self.events: Dict[str,int] = {}

    def track(self,func: T) -> T:
        """Decorator to measure execution time and count calls"""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start: float = time.perf_counter()
            result: Any = func(*args,**kwargs)
            end: float = time.perf_counter()
            elapsed: float = end - start

            name = func.__qualname__
            if name not in self.functions:
                self.functions[name] = {"calls": 0,"total_time": 0.0,"avg_time": 0.0}

            data = self.functions[name]
            data["calls"] += 1
            data["total_time"] += elapsed
            data["avg_time"] = data["total_time"] / data["calls"]
            return result
        return cast(T,wrapper)
    
    def event(self,name: str) -> None:
        """Manually track a named event."""
        self.events[name] = self.events.get(name,0) + 1

    def report(self) -> Dict[str,Any]:
        """Return a combined report of functions and events"""
        return {
            "name": self.name,
            "functions": self.functions,
            "events": self.events
        }
    
    def save(self,path: str) -> None:
        """Save the report as a JSON"""
        with open(path,"w",encoding="utf-8") as f:
            json.dump(self.report(),f,indent=4)

    def summary(self) -> None:
        """Print a readable summary."""
        print(f"📊 PyTrack Report: {self.name}")
        for func,data in self.functions.items():
            print(f" - {func}: {data['calls']} calls, avg {data['avg_time']:.4f}s")
        if self.events:
            print("\nEvents:")
            for event,count in self.events.items():
                print(f" - {event}: {count} times")