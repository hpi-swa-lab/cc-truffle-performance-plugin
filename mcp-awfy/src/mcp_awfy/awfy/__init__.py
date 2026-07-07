from .bounce import Bounce
from .cd import CD
from .deltablue import DeltaBlue
from .havlak import Havlak
from .json import Json
from .list import List
from .mandelbrot import Mandelbrot
from .nbody import NBody
from .permute import Permute
from .queens import Queens
from .richards import Richards
from .sieve import Sieve
from .storage import Storage
from .towers import Towers

BENCHMARKS: dict[str, type] = {
    "bounce": Bounce,
    "cd": CD,
    "deltablue": DeltaBlue,
    "havlak": Havlak,
    "json": Json,
    "list": List,
    "mandelbrot": Mandelbrot,
    "nbody": NBody,
    "permute": Permute,
    "queens": Queens,
    "richards": Richards,
    "sieve": Sieve,
    "storage": Storage,
    "towers": Towers,
}
