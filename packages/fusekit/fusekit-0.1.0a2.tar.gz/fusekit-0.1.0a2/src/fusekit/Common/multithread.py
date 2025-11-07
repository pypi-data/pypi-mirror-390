import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
import time
import queue
import threading
import traceback
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Tuple

class APIThreadPool:
    """
    A thread pool with rate limiting for API calls

    Class wraps THreadPoolExecutor wiht logic to enforce a rate limit
    Tasks are processed concurrently but never exceed the number of calls within the time window
    
    Attributes:
        max_workers (int): The maximum number of worker threads in the pool.
        rate_limit (int): The maximum number of allowed API calls within the time window.
        time_window (int): The duration (in seconds) within which a maximum of `rate_limit`
                           calls may be made.
        request_times (queue.Queue): A queue that stores timestamps of the most recent calls.
        executor (ThreadPoolExecutor): The underlying ThreadPoolExecutor.
        _lock (threading.Lock): A lock used to protect rate-limiting operations.
    """
    # def __init__(self, max_workers: int = 4, rate_limit: int = 10, time_window: int = 60):
    #     self.max_workers = max_workers
    #     self.rate_limit = rate_limit
    #     self.time_window = time_window
    #     self.request_times = queue.Queue()
    #     self.executor = ThreadPoolExecutor(max_workers=max_workers)
    #     self._lock = threading.Lock()
    # def _check_rate_limit(self):
    #     """Implement rate limiting for API calls"""
    #     current_time = time.time()
        
    #     # Remove old requests from the queue
    #     while not self.request_times.empty():
    #         request_time = self.request_times.queue[0]
    #         if current_time - request_time > self.time_window:
    #             self.request_times.get()
    #         else:
    #             break

    #     # Check if we're within rate limits
    #     if self.request_times.qsize() >= self.rate_limit:
    #         oldest_request = self.request_times.queue[0]
    #         sleep_time = self.time_window - (current_time - oldest_request)
    #         if sleep_time > 0:
    #             time.sleep(sleep_time)

    #     self.request_times.put(current_time)

    # def submit_task(self, fn: Callable, *args, **kwargs) -> Any:
    #     """Submit a task to the thread pool with rate limiting"""
    #     with self._lock:
    #         self._check_rate_limit()
    #     return self.executor.submit(fn, *args, **kwargs)

    # def process_batch(self, tasks: List[Dict[str, Any]], 
    #                  process_fn: Callable) -> List[Any]:
    #     """Process a batch of tasks using the thread pool"""
    #     futures = []
    #     results = []

    #     for task in tasks:
    #         future = self.submit_task(process_fn, task)
    #         futures.append((task, future))

    #     for task, future in futures:
    #         try:
    #             result = future.result()
    #             print(f"multithread.py: Tokens used: {result}")
    #             results.append(result)
    #         except Exception as e:
    #             print({
    #                 #"question": task,
    #                 f"ERROR: {str(e)}",
    #                 #"status": "error"
    #             })

    #     return results

    def __init__(self, *,
                 max_workers: int = 4,
                 rate_limit: int = 5_000,
                 time_window: int = 60):
        self.max_workers   = max_workers
        self.rate_limit    = rate_limit
        self.time_window   = time_window

        self.executor      = ThreadPoolExecutor(max_workers=max_workers)
        self._lock         = threading.Lock()                # protects ledger below
        self._ledger: deque[Tuple[float, int]] = deque()      # (timestamp, tokens)
        self._tokens_in_window = 0                            # running sum

    # ---------- internal helpers ----------
    def _prune_ledger(self, now: float) -> None:
        """Drop entries that are older than the sliding time window."""
        while self._ledger and (now - self._ledger[0][0] > self.time_window):
            _, expired_tokens = self._ledger.popleft()
            self._tokens_in_window -= expired_tokens

    def _wait_for_quota(self, tokens_needed: int) -> None:
        """
        Block until `tokens_needed` more tokens will fit under the limit.
        Must be called with self._lock **already held**.
        """
        if tokens_needed > self.rate_limit:
            raise ValueError(
                f"tokens_needed {tokens_needed} exceeds rate limit {self.rate_limit}"
            )
        while True:
            now = time.time()
            self._prune_ledger(now)

            if tokens_needed > self.rate_limit:
                raise ValueError(f'Task needs {tokens_needed} which is larger than the rate limit {self.rate_limit}')
            #print(self._tokens_in_window, tokens_needed, self.rate_limit)
            if self._tokens_in_window + tokens_needed <= self.rate_limit:
                # we’re good—reserve the quota and return
                self._ledger.append((now, tokens_needed))
                self._tokens_in_window += tokens_needed
                return
            if not self._ledger:
                # ledger empty and we’re over the limit—wait before retrying
                self._lock.release()
                time.sleep(self.time_window)
                self._lock.acquire()
                continue

            # not enough room yet—sleep until the oldest entry rolls off
            sleep_for = 0
            #if len(self._ledger) > 0:
            oldest_time, _ = self._ledger[0]
            sleep_for = self.time_window - (now - oldest_time)
            if sleep_for > 0:
                # release the lock while sleeping so other threads aren’t blocked
                self._lock.release()
                time.sleep(sleep_for)
                self._lock.acquire()
            else:
                # should never happen, but guard against busy‑loop
                time.sleep(0.01)

    def _rate_limited_wrapper(self, process_fn: Callable, task: Dict[str, Any]) -> int:
        """
        Worker wrapper:
          1. Run the user‐supplied `process_fn`.
          2. Atomically register its token usage, blocking if necessary.
        """
        tokens_used = process_fn(task)          # CALL THE API
        if not isinstance(tokens_used, int):
            raise ValueError("process_fn must return an int (tokens used)")

        if tokens_used < 0:
            tokens_used=1

        with self._lock:
            self._wait_for_quota(tokens_used)   # register usage / block if needed
        return tokens_used

    # ---------- public API ----------
    def submit_task(self, fn: Callable, *args, **kwargs):
        """
        Submit a single task.  `fn` must return the token count.
        The wrapper enforces the token rate‑limit transparently.
        """
        wrapped = lambda *a, **kw: self._rate_limited_wrapper(fn, *a, **kw)
        return self.executor.submit(wrapped, *args, **kwargs)

    def process_batch(self,
                      tasks: List[Dict[str, Any]],
                      process_fn: Callable) -> List[int]:
        """
        Concurrently process a batch of tasks, honoring the token limit.
        Returns a list of per‑task token counts.
        """
        futures = [self.submit_task(process_fn, t) for t in tasks]

        results: List[int] = []
        for fut in futures:
            try:
                tokens = fut.result()
                #print(f"multithread.py: tokens used: {tokens}")
                results.append(tokens)
            except Exception as e:
                print(f"ERROR {str(e)}")
                print("".join(traceback.format_exception(type(e), e, e.__traceback__)))

        return results

    def __del__(self):
        
        self.executor.shutdown(wait=True)