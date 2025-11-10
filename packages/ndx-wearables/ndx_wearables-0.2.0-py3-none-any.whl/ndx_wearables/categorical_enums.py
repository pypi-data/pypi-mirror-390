from enum import Enum

try:
    # HDMF is where DynamicTable lives
    from hdmf.common import DynamicTable, VectorData
except Exception as e:
    raise ImportError("hdmf is required for meanings table builders") from e

# Concrete constrained subclass examples 
class SleepPhase(str, Enum):
    AWAKE = "awake"
    N1 = "n1"
    N2 = "n2"
    N3 = "n3"
    REM = "rem"

class ActivityClass(str, Enum):
    SITTING = "sitting"
    WALKING = "walking"
    RUNNING = "running"

# Add small, direct functions that build and return the tables 
def build_sleep_phase_meanings():
    """
    Pre-built DynamicTable to store the mapping between sleep-stage category labels and detailed descriptions
    """
    category = VectorData(
        name="category",
        description="Sleep phase label",
        data=[e.value for e in SleepPhase]
    )
    meaning = VectorData(
        name="meaning",
        description="Human-readable description",
        data=[
            "Wakefulness",
            "Non-REM stage 1",
            "Non-REM stage 2",
            "Non-REM stage 3 (deep sleep)",
            "Rapid eye movement (REM) sleep"
        ]
    )
    # TODO: this should probably be explicit NDX-Events `MeaningsTables` eventually
    table = DynamicTable(
        name="SleepPhase_Meanings",
        description="Category definitions for sleep stages",
        columns=[category, meaning],
    )
    return table


def build_activity_class_meanings():
    """
    Pre-built DynamicTable to store the mapping between activity intensity labels and detailed descriptions
    """
    category = VectorData(
        name="category",
        description="Activity label",
        data=[e.value for e in ActivityClass]
    )
    meaning = VectorData(
        name="meaning",
        description="Human-readable description",
        data=[
            "Minimal movement",
            "Ambulatory movement at a comfortable pace",
            "Ambulatory movement at a faster pace"
        ]
    )
    # TODO: this should probably be explicit NDX-Events `MeaningsTables` eventually
    table = DynamicTable(
        name="Activity_Meanings",
        columns=[category, meaning],
        description="Category definitions for activity classes"
    )
    return table


ENUM_MAP = {
    "sleep_phase": SleepPhase,
    "activity_class": ActivityClass
    # Add more
}
