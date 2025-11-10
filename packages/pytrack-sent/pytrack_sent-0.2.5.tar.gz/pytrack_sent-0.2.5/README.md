# **PyTrack -- Efortless Performance Tracking for Python**
Track. Analyze. Improve

* PyTrack is a lightweight, type-safe performance tracker built for developers who want deep insights into their code without the hassle.
* Perfect for Discord bots, APIs, data scripts, or any Python project that needs precise execution metrics.

# **Features**

* Function-level tracking — Measure execution time with a simple decorator

* Session reports — Automatically summarize tracked function performance

* Context managers — Profile any code block in a clean, readable way

* Structured output — Easy-to-parse logs for data visualization

* Type-safe design — Fully typed with Python 3.10+ annotations

* Pluggable system — Extend with custom loggers, filters, or exporters


# **Example**

```py
from pytrack_sent import PyTrack

tracker = PyTrack()
my_dict = {}

@tracker.track
def slow_task():
    for _ in range(10**7):
        my_dict[_] = _
    tracker.event("slow_task_completed")

@tracker.track 
def slowertask():
    for _ in range(4):
        slow_task()

slow_task()
slowertask()
tracker.summary()
```

# **Output**
```
📊 PyTrack Report: default
 - slow_task: 5 calls, avg 1.0056s
 - slowertask: 1 calls, avg 3.8714s

Events:
 - slow_task_completed: 5 times
```

# **Why PyTrack?**
Unlike heavy profilers, PyTrack is developer-friendly, portable, and customizable.
It’s perfect for measuring performance in scripts, bots, or production-ready apps without slowing them down.

# **Installation**
``` pip install pytrack-sent ```

# **GUI Dashboard (coming soon)**
A built-in dashboard for visualizing tracked data in real-time using a simple pytrack dashboard command.

# **Planned Integrations**
* Discord.py command profiling

* Matplotlib and Plotly report generation [ADDED]

* Cloud export support (JSON/CSV)

* AI code profiling insights (experimental)

## Made for developers who care about performance.

>Simple. Typed. Transparent.
See live performance charts, trends, and insights right from your terminal or browser

