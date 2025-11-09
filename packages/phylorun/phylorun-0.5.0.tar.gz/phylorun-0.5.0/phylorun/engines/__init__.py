from phylorun.engines.beast2 import BEAST2
from phylorun.engines.lphy import LPhy
from phylorun.engines.beastX import BEASTX
from phylorun.engines.engine import Engine
from phylorun.engines.revBayes import RevBayes

ENGINES: list[Engine] = [BEAST2(), BEASTX(), RevBayes(), LPhy()]
