from __future__ import annotations
import time
import json
from typing import Any,Callable,Dict,Optional,TypeVar,cast
from functools import wraps
from .pytrack_types import TrackStats
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import csv

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

    def plot_performance(self,save_path: Optional[str] = None) -> None:
        """Generate and optionally save performance visualization plots.
            Args:
                save_path: Optional path to save the plot. If None, displays plot instead.
        """
        if not self.functions:
            print("No performance data to plot")
            return
        
        fig, (ax1,ax2) = plt.subplots(2,1,figsize=(10,10))
        fig.suptitle(f'PyTrack Performance Report: {self.name}')

        names = list(self.functions.keys())
        calls = [data['calls'] for data in self.functions.values()]
        avg_times = [data['avg_time'] for data in self.functions.values()]

        ax1.bar(names,calls)
        ax1.set_title('Function Calls')
        ax1.set_xticklabels(names,rotation=45)
        ax1.set_ylabel('Number of Calls')

        ax2.bar(names,avg_times)
        ax2.set_title('Average Exec. Time')
        ax2.set_xticklabels(names,rotation=45)
        ax2.set_ylabel('Time (seconds)')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def export_cloud(self,path: str, format: str = "json") -> None:
        """
        Export the report for cloud usage in JSON or CSV format.

        Args:
            path: Destination file path.
            format: 'json' or 'csv'.
        """
        report = self.report()

        if format.lower() == "json":
            with open(path,"w",encoding="utf-8") as f:
                json.dump(report,f,indent=4)
        elif format.lower() == "csv":
            path_obj = Path(path)
            #Export funcs
            with open(path_obj.with_suffix(".functions.csv"),"w",newline="",encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Function","Calls","Total Time","Average Time"])
                for func,data in report["functions"].items():
                    writer.writerow([func,data["calls"],data["total_time"],data["avg_time"]])
            #Export events
            with open(path_obj.with_suffix(".events.csv"),"w",newline="",encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Event","Count"])
                for event,counts in report["events"].items():
                    writer.writerow([event,counts])
        else:
            raise ValueError("Unsupported format. use 'json' or 'csv'.")