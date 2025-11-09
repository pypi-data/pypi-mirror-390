from pathlib import Path
from typing import Union
import inspect


def get_caller_path(path_or_str: Union[str, Path], up: int = 1) -> Path:
    if isinstance(path_or_str, Path):
        return path_or_str

    frame = inspect.currentframe()
    try:
        # (+1 because the current function itself counts as one frame)
        for _ in range(up + 1):
            if frame is None:
                raise RuntimeError("Frame stack too shallow")
            frame = frame.f_back

        assert frame is not None, "Frame stack too shallow"

        caller_file = Path(inspect.getfile(frame)).resolve()
        caller_dir = caller_file.parent

        return (caller_dir / path_or_str).resolve()
    finally:
        del frame
