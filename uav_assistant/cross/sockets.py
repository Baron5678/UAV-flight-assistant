from typing import Callable, Dict, Any

TraceEvent = Dict[str, Any]
TraceFn = Callable[[TraceEvent], None]