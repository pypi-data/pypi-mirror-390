from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Any

from drive.utilities.parser.phenotype_descriptions_parser import PhecodesMapper

from .networks import Network_Interface


@dataclass
class RuntimeState:
    """main class to hold the data from the network analysis and the different pvalues"""

    networks: List[Network_Interface]
    output_path: Path
    carriers: Dict[str, Dict[str, Set[str]]]
    phenotype_descriptions: PhecodesMapper
    config_options: dict[str, Any] = field(default_factory=dict)
