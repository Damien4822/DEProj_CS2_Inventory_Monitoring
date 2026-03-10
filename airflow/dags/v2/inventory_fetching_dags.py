import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(ROOT))

from versions.v2_distributed.pipelines.inventory_fetching import dag