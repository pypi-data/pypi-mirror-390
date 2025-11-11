from mellifera.executors.trio import TrioExecutor
try:
    from mellifera.executors.nsmainthread import NSMainThreadExecutor
    HAS_NSMAINTHREAD = True
except ModuleNotFoundError:
    HAS_NSMAINTHREAD = False
