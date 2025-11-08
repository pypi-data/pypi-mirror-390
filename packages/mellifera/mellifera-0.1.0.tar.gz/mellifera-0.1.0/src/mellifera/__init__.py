from mellifera.orchestrators.parent import ParentOrchestrator
from mellifera.orchestrators.trio import TrioOrchestrator

try:
    from mellifera.orchestrators.nsmainthread import NSMainThreadOrchestrator
    HAS_NSMAINTHREAD = True
except ModuleNotFoundError:
    HAS_NSMAINTHREAD = False

def Orchestrator():
    orchestrator = ParentOrchestrator()
    orchestrator.add_orchestrator(TrioOrchestrator())
    if HAS_NSMAINTHREAD:
        orchestrator.add_orchestrator(NSMainThreadOrchestrator())
    return orchestrator
