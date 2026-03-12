import os
from pathlib import Path
from typing import Iterable, List


def load_dotenv(dotenv_paths: Iterable[str] = (".env", ".env.example")) -> List[Path]:
    loaded_paths = []
    for dotenv_path in dotenv_paths:
        path = Path(dotenv_path)
        if not path.exists():
            continue

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

        loaded_paths.append(path)

    return loaded_paths
