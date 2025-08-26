import os, sys, time, random, platform, shutil, subprocess, webbrowser, threading
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize, QSettings
from PySide6.QtGui import (
    QPalette, QColor, QFont, QPainter, QLinearGradient, QPen, QPixmap, QIcon
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QGraphicsDropShadowEffect, QGridLayout, QDialog, QCheckBox, QSizePolicy
)

SYSTEM = platform.system()
IS_MAC = SYSTEM == "Darwin"
IS_WIN = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"

# Import pyautogui only on Win/Linux (never on macOS)
if not IS_MAC:
    try:
        import pyautogui
        pyautogui.PAUSE = 0.25
        pyautogui.FAILSAFE = True
    except Exception as e:
        if IS_WIN or IS_LINUX:
            raise SystemExit("Install dependency: pip install pyautogui") from e

BING_HOME = "https://www.bing.com"
BING_SIGNIN = "https://login.live.com/"

random_words = [
    "nebula",     "quasar",     "supernova",     "asteroid",     "galaxy",     "comet",     "orbit",     "pulsar",     "atom",     "molecule",
    "gravity",     "neutron",     "photosynthesis",     "quantum",     "entropy",     "enzyme",     "proton",     "electron",     "isotope",     "plasma",
    "lion",     "tiger",     "leopard",     "cheetah",     "panther",     "jaguar",     "cougar",     "lynx",     "hyena",     "wolf",
    "eagle",     "falcon",     "sparrow",     "swallow",     "albatross",     "pelican",     "heron",     "ibis",     "stork",     "owl",
    "salmon",     "trout",     "carp",     "catfish",     "anchovy",     "sardine",     "tuna",     "mackerel",     "halibut",     "cod",
    "oak",     "maple",     "willow",     "birch",     "cypress",     "cedar",     "aspen",     "baobab",     "spruce",     "fir",
    "rose",     "tulip",     "orchid",     "lily",     "daffodil",     "peony",     "violet",     "magnolia",     "iris",     "sunflower",
    "ruby",     "sapphire",     "emerald",     "topaz",     "amethyst",     "garnet",     "opal",     "quartz",     "diamond",     "beryl",
    "river",     "ocean",     "lagoon",     "harbor",     "island",     "valley",     "canyon",     "plateau",     "delta",     "estuary",
    "desert",     "tundra",     "prairie",     "savanna",     "rainforest",     "wetland",     "moor",     "glacier",     "taiga",     "steppe",
    "breeze",     "thunder",     "lightning",     "hailstorm",     "downpour",     "mist",     "blizzard",     "monsoon",     "cyclone",     "typhoon",
    "sunrise",     "sunset",     "twilight",     "midnight",     "equinox",     "solstice",     "horizon",     "zenith",     "dawn",     "dusk",
    "copper",     "silver",     "gold",     "platinum",     "iron",     "nickel",     "cobalt",     "titanium",     "aluminum",     "mercury",
    "oxygen",     "hydrogen",     "carbon",     "nitrogen",     "sulfur",     "phosphorus",     "chlorine",     "argon",     "neon",     "xenon",
    "triangle",     "square",     "rectangle",     "parallelogram",     "trapezoid",     "rhombus",     "polygon",     "ellipse",     "circle",     "oval",
    "calculus",     "algebra",     "geometry",     "statistics",     "trigonometry",     "topology",     "logic",     "combinatorics",     "theorem",     "lemma",
    "protein",     "lipid",     "carbohydrate",     "nucleus",     "ribosome",     "chloroplast",     "mitochondrion",     "cytoplasm",     "membrane",     "chromosome",
    "bacteria",     "fungus",     "amoeba",     "protozoan",     "alga",     "lichen",     "nematode",     "annelid",     "arthropod",     "crustacean",
    "volcano",     "earthquake",     "tsunami",     "avalanche",     "landslide",     "erosion",     "sediment",     "bedrock",     "mineral",     "fossil",
    "marble",     "granite",     "basalt",     "limestone",     "sandstone",     "shale",     "gneiss",     "schist",     "quartzite",     "slate",
    "hammer",     "chisel",     "wrench",     "pliers",     "screwdriver",     "solder",     "anvil",     "lathe",     "drill",     "saw",
    "canvas",     "easel",     "palette",     "pigment",     "charcoal",     "pastel",     "fresco",     "mosaic",     "etching",     "engraving",
    "violin",     "cello",     "trumpet",     "trombone",     "clarinet",     "oboe",     "bassoon",     "timpani",     "symphony",     "sonata",
    "rhythm",     "melody",     "harmony",     "tempo",     "crescendo",     "glissando",     "staccato",     "vibrato",     "cadence",     "overture",
    "syntax",     "semantics",     "phonology",     "morphology",     "pragmatics",     "lexicon",     "grammar",     "dialect",     "phoneme",     "grapheme",
    "justice",     "freedom",     "equality",     "virtue",     "honesty",     "courage",     "wisdom",     "empathy",     "kindness",     "patience",
    "concept",     "theory",     "hypothesis",     "evidence",     "method",     "analysis",     "synthesis",     "inference",     "experiment",     "observation",
    "battery",     "resistor",     "capacitor",     "inductor",     "transistor",     "diode",     "oscillator",     "antenna",     "circuit",     "sensor",
    "network",     "protocol",     "router",     "switch",     "firewall",     "bandwidth",     "latency",     "throughput",     "algorithm",     "database",
    "compiler",     "interpreter",     "encryption",     "hashing",     "virtualization",     "container",     "notebook",     "journal",     "ledger",     "parchment",
    "ant",     "aardvark",     "baboon",     "badger",     "bat",     "bear",     "beaver",     "bison",     "buffalo",     "camel",
    "capybara",     "caracal",     "chinchilla",     "chimpanzee",     "coyote",     "dingo",     "donkey",     "dromedary",     "elephant",     "ferret",
    "fox",     "gazelle",     "giraffe",     "gorilla",     "groundhog",     "hamster",     "hedgehog",     "hippopotamus",     "horse",     "iguana",
    "impala",     "jackal",     "kangaroo",     "koala",     "lemur",     "llama",     "manatee",     "marmot",     "meerkat",     "mongoose",
    "moose",     "narwhal",     "ocelot",     "octopus",     "opossum",     "orangutan",     "otter",     "panda",     "platypus",     "porcupine",
    "porpoise",     "possum",     "rabbit",     "raccoon",     "reindeer",     "rhinoceros",     "seal",     "serval",     "skunk",     "sloth",
    "tapir",     "walrus",     "warthog",     "weasel",     "wildebeest",     "zebra",     "yak",     "alpaca",     "anteater",     "armadillo",
    "auklet",     "bittern",     "blackbird",     "bluebird",     "bobolink",     "bunting",     "buzzard",     "canary",     "cardinal",     "chickadee",
    "cormorant",     "crane",     "cuckoo",     "curlew",     "dove",     "egret",     "goldfinch",     "goose",     "grouse",     "gull",
    "hawk",     "hoopoe",     "jay",     "kestrel",     "kite",     "kingfisher",     "lark",     "loon",     "magpie",     "mallard",
    "mockingbird",     "nightjar",     "nuthatch",     "oriole",     "osprey",     "ostrich",     "parakeet",     "parrot",     "peacock",     "peafowl",
    "phoebe",     "phoenix",     "pigeon",     "ptarmigan",     "quail",     "raven",     "robin",     "sandpiper",     "sapsucker",     "shrike",
    "snipe",     "starling",     "swift",     "tern",     "thrush",     "titmouse",     "toucan",     "vireo",     "vulture",     "warbler",
    "waxwing",     "woodcock",     "woodpecker",     "wren",     "plover",     "pipit",     "sandgrouse",     "penguin",     "cassowary",     "abalone",
    "barracuda",     "bluegill",     "bonito",     "clownfish",     "eel",     "flounder",     "goby",     "grouper",     "guppy",     "herring",
    "lamprey",     "marlin",     "minnow",     "mollusk",     "moray",     "perch",     "pike",     "pollock",     "ray",     "rockfish",
    "sailfish",     "snapper",     "squid",     "sturgeon",     "sunfish",     "swordfish",     "tarpon",     "tilapia",     "walleye",     "antlion",
    "aphid",     "beetle",     "bollworm",     "butterfly",     "caddisfly",     "cicada",     "cricket",     "damselfly",     "dragonfly",     "earwig",
    "firefly",     "flea",     "grasshopper",     "horntail",     "lacewing",     "ladybug",     "mantis",     "mayfly",     "millipede",     "mite",
    "mosquito",     "moth",     "pillbug",     "scorpion",     "silverfish",     "spider",     "termite",     "tick",     "wasp",     "weevil",
    "woodlouse",     "worm",     "katydid",     "tarantula",     "centipede",     "bumblebee",     "honeybee",     "locust",     "blackfly",     "acacia",
    "alder",     "ash",     "beech",     "bamboo",     "banyan",     "bottlebrush",     "dogwood",     "elm",     "hemlock",     "holly",
    "juniper",     "kapok",     "mahogany",     "mulberry",     "olive",     "palm",     "poplar",     "redwood",     "sequoia",     "sycamore",
    "teak",     "tamarind",     "yew",     "yucca",     "zinnia",     "azalea",     "begonia",     "camellia",     "carnation",     "chrysanthemum",
    "cosmos",     "dahlia",     "gardenia",     "geranium",     "gladiolus",     "hibiscus",     "hydrangea",     "jasmine",     "lavender",     "marigold",
    "morningglory",     "narcissus",     "pansy",     "petunia",     "phlox",     "poinsettia",     "primrose",     "snapdragon",     "anemone",     "aster",
    "camphor",     "caladium",     "clover",     "fennel",     "sage",     "thyme",     "rosemary",     "basil",     "oregano",     "cumin",
    "turmeric",     "ginger",     "horseradish",     "parsley",     "cilantro",     "chive",     "tarragon",     "saffron",     "agate",     "actinolite",
    "alexandrite",     "andalusite",     "apatite",     "aragonite",     "azurite",     "barite",     "benitoite",     "bornite",     "calcite",     "cassiterite",
    "celestine",     "chalcedony",     "chalcopyrite",     "chromite",     "corundum",     "diopside",     "dolomite",     "epidote",     "feldspar",     "fluorite",
    "galena",     "graphite",     "hematite",     "ilmenite",     "jadeite",     "kaolinite",     "kunzite",     "labradorite",     "malachite",     "monazite",
    "obsidian",     "olivine",     "orthoclase",     "peridot",     "petalite",     "pyrite",     "rhodonite",     "rutile",     "scapolite",     "sodalite",
    "spinel",     "sugilite",     "tourmaline",     "uraninite",     "variscite",     "wollastonite",     "zircon",     "zeolite",     "archipelago",     "atoll",
    "bayou",     "butte",     "cape",     "cliff",     "dune",     "fen",     "fjord",     "foothill",     "gorge",     "gulch",
    "inlet",     "isthmus",     "knoll",     "marsh",     "mesa",     "meadow",     "oasis",     "outwash",     "peninsula",     "ravine",
    "ridge",     "scree",     "shoal",     "sound",     "strait",     "summit",     "swale",     "tideland",     "upland",     "watershed",
    "wharf",     "grotto",     "hinterland",     "backwater",     "headland",     "moorland",     "aurora",     "drizzle",     "gust",     "squall",
    "gale",     "zephyr",     "whirlwind",     "cloudburst",     "rainfall",     "overcast",     "sunbeam",     "afterglow",     "downburst",     "microburst",
    "whiteout",     "mistbow",     "rainbow",     "sunshower",     "icefall",     "snowflake",     "icicle",     "sleet",     "graupel",     "snowdrift",
    "thundersnow",     "stormfront",     "updraft",     "downdraft",     "windstorm",     "tempest",     "aphelion",     "perihelion",     "apogee",     "perigee",
    "umbra",     "penumbra",     "syzygy",     "asterism",     "multiverse",     "singularity",     "wormhole",     "planetesimal",     "exoplanet",     "magnetar",
    "nebulosity",     "astronomy",     "astrophysics",     "meteoroid",     "meteorite",     "meteorology",     "heliosphere",     "ionosphere",     "mesosphere",     "stratosphere",
    "troposphere",     "chronology",     "epoch",     "eon",     "millennium",     "bromine",     "iodine",     "cesium",     "barium",     "strontium",
    "calcium",     "potassium",     "sodium",     "lithium",     "beryllium",     "magnesium",     "scandium",     "vanadium",     "manganese",     "chromium",
    "zinc",     "gallium",     "germanium",     "arsenic",     "selenium",     "bismuth",     "polonium",     "radon",     "radium",     "francium",
    "astatine",     "thorium",     "uranium",     "plutonium",     "neptunium",     "americium",     "curium",     "einsteinium",     "fermium",     "mendelevium",
    "nobelium",     "lawrencium",     "rutherfordium",     "dubnium",     "seaborgium",     "bohrium",     "hassium",     "meitnerium",     "roentgenium",     "copernicium",
    "nihonium",     "flerovium",     "moscovium",     "livermorium",     "oganesson",     "axiom",     "proof",     "corollary",     "postulate",     "predicate",
    "quantifier",     "bijection",     "injection",     "surjection",     "isomorphism",     "homomorphism",     "manifold",     "tensor",     "matrix",     "determinant",
    "eigenvalue",     "eigenvector",     "gradient",     "divergence",     "curl",     "integral",     "derivative",     "limit",     "series",     "sequences",
    "congruence",     "modulus",     "prime",     "composite",     "factorial",     "polygonal",     "polyhedron",     "simplex",     "torus",     "knot",
    "graph",     "lattice",     "ring",     "field",     "group",     "momentum",     "inertia",     "impulse",     "friction",     "viscosity",
    "turbulence",     "kinematics",     "dynamics",     "thermodynamics",     "optics",     "acoustics",     "relativity",     "superconductivity",     "spintronics",     "photovoltaics",
    "electrostatics",     "magnetism",     "radiation",     "diffraction",     "interference",     "refraction",     "resonance",     "conductance",     "inductance",     "capacitance",
    "impedance",     "admittance",     "permittivity",     "permeability",     "luminosity",     "allele",     "genotype",     "phenotype",     "epigenetics",     "homeostasis",
    "metabolism",     "catabolism",     "anabolism",     "osmosis",     "diffusion",     "endocytosis",     "exocytosis",     "apoptosis",     "autophagy",     "synapse",
    "axon",     "dendrite",     "neurotransmitter",     "myelin",     "glia",     "photosystem",     "stomata",     "xylem",     "phloem",     "meristem",
    "gametophyte",     "sporophyte",     "zygote",     "blastula",     "gastrula",     "embryo",     "placenta",     "biome",     "ecosystem",     "biosphere",
    "population",     "niche",     "symbiosis",     "mutualism",     "parasitism",     "commensalism",     "predation",     "trophic",     "bioluminescence",     "chlorophyll",
    "carotenoid",     "hemoglobin",     "myoglobin",     "insulin",     "glucagon",     "artery",     "vein",     "capillary",     "atrium",     "ventricle"
]

def open_browser(prefer_edge=True, url=BING_HOME):
    used_edge = False
    if prefer_edge:
        try:
            if IS_WIN:
                for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                          r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
                    if os.path.isfile(p):
                        webbrowser.register("msedge", None, webbrowser.BackgroundBrowser(p))
                        webbrowser.get("msedge").open(url, new=1); used_edge = True; break
            elif IS_MAC and os.path.exists("/Applications/Microsoft Edge.app"):
                webbrowser.get('open -a "Microsoft Edge" %s').open(url, new=1); used_edge = True
            elif IS_LINUX:
                for name in ("microsoft-edge", "microsoft-edge-stable", "microsoft-edge-beta"):
                    edge_path = shutil.which(name)
                    if edge_path:
                        webbrowser.register("msedge", None, webbrowser.BackgroundBrowser(edge_path))
                        webbrowser.get("msedge").open(url, new=1); used_edge = True; break
        except Exception:
            used_edge = False
    if not used_edge:
        webbrowser.open(url, new=1)

# ---------- macOS AppleScript ----------
def _osa(script: str):
    return subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def mac_app_exists(name: str) -> bool:
    return os.path.exists(f"/Applications/{name}.app")

def mac_pick_browser() -> str:
    for app in ("Microsoft Edge", "Google Chrome", "Safari"):
        if mac_app_exists(app): return app
    return "Safari"

def mac_activate(app_name: str):
    _osa(f'tell application "{app_name}" to activate')

def mac_keycode(code: int, with_cmd=False):
    if with_cmd:
        _osa(f'tell application "System Events" to key code {code} using command down')
    else:
        _osa(f'tell application "System Events" to key code {code}')

def mac_focus_omnibox(): mac_keycode(37, with_cmd=True)  # cmd-L
def mac_press_return():  mac_keycode(36, with_cmd=False) # return

def mac_type_human(text: str):
    esc = text.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
    set theText to "{esc}"
    tell application "System Events"
        repeat with i from 1 to (count of theText)
            set c to text i thru i of theText
            keystroke c
            delay (random number from 0.035 to 0.12)
            if ((random number from 1 to 18) is 1) then
                delay (random number from 0.12 to 0.25)
            end if
        end repeat
    end tell
    '''
    _osa(script)

def mac_preflight_access():
    try:
        _osa('tell application "System Events" to count processes'); return True, "OK"
    except subprocess.CalledProcessError:
        return False, ("macOS blocked automation.\n"
                       "Give Accessibility permission to your Terminal/VS Code:\n"
                       "System Settings → Privacy & Security → Accessibility.")
    except FileNotFoundError:
        return False, "osascript not found (unexpected on macOS)."

# ---------- Win/Linux helpers ----------
def wl_preflight():
    try:
        _ = pyautogui.size(); _ = pyautogui.position(); return True, "OK"
    except Exception as e:
        tips = []
        if IS_LINUX:
            tips += ["Run under X11 (Wayland can block automation).",
                     "Switch to an Xorg session or ensure DISPLAY is set."]
        elif IS_WIN:
            tips += ["Try running the terminal/VS Code as Administrator."]
        return False, "Automation access failed.\n\nError: {}\n\n{}".format(str(e), "\n".join(tips))

def human_type_pyautogui(term: str):
    i = 0
    n = len(term)
    while i < n:
        chunk_len = random.choice((1,1,2,3))
        chunk = term[i:i+chunk_len]
        pyautogui.typewrite(chunk, interval=random.uniform(0.01, 0.12))
        i += len(chunk)
        time.sleep(random.uniform(0.03, 0.18))
        if random.random() < 0.06:
            time.sleep(random.uniform(0.12, 0.28))

# ---------- Automation wrapper ----------
class Automator:
    def __init__(self):
        self.browser_mac = mac_pick_browser() if IS_MAC else None

    def open_and_ready(self):
        open_browser(prefer_edge=True, url=BING_HOME)
        time.sleep(2.2)
        if IS_MAC: mac_activate(self.browser_mac)

    def search_once(self, term: str):
        if IS_MAC:
            mac_activate(self.browser_mac)
            time.sleep(0.12)
            mac_focus_omnibox()
            time.sleep(0.08)
            mac_type_human(term)
            mac_press_return()
        else:
            pyautogui.hotkey("ctrl" if (IS_WIN or IS_LINUX) else "command", "l")
            time.sleep(0.06)
            human_type_pyautogui(term)
            pyautogui.press("enter")

# ---------- Worker thread ----------
class SearchWorker(QThread):
    progress = Signal(int)       # remaining
    status   = Signal(str)
    error    = Signal(str)
    done     = Signal()

    def __init__(self, words, target_count):
        super().__init__()
        self.words = words
        self.target = target_count
        self._stop = threading.Event()
        self._pause = threading.Event()
        self.automator = Automator()

    def stop(self): self._stop.set()
    def toggle_pause(self):
        if self._pause.is_set(): self._pause.clear()
        else: self._pause.set()

    def run(self):
        try:
            if not self.words:
                self.error.emit("Your word list is empty. Paste your random_words and try again.")
                self.done.emit(); return

            remaining = min(self.target, len(self.words))
            self.progress.emit(remaining)
            self.status.emit("Opening browser")
            self.automator.open_and_ready()
            self.status.emit("Running")

            for i in range(remaining):
                if self._stop.is_set(): break
                while self._pause.is_set() and not self._stop.is_set(): time.sleep(0.1)
                if self._stop.is_set(): break

                term = random.choice(self.words)
                self.words.remove(term)
                self.automator.search_once(term)
                time.sleep(2.3 + random.uniform(0.25, 0.9))
                self.progress.emit(remaining - (i + 1))
        except Exception as e:
            self.error.emit(f"Automation stopped:\n{e}")
        finally:
            self.done.emit()

# ---------- UI pieces ----------
class GradientWidget(QWidget):
    def paintEvent(self, evt):
        painter = QPainter(self)
        # Vertical deep-blue gradient
        base = QLinearGradient(0, 0, 0, self.height())
        base.setColorAt(0.0, QColor("#0f172a"))   # slate-900
        base.setColorAt(0.5, QColor("#1e3a8a"))   # indigo-800
        base.setColorAt(1.0, QColor("#1d4ed8"))   # blue-700
        painter.fillRect(self.rect(), base)
        # Soft top highlight
        from PySide6.QtGui import QRadialGradient
        highlight = QRadialGradient(self.width()/2, self.height()*0.08, self.height()*0.7)
        highlight.setColorAt(0.0, QColor(255,255,255,38))
        highlight.setColorAt(1.0, QColor(255,255,255,0))
        painter.fillRect(self.rect(), highlight)
        # Bottom vignette
        shade = QLinearGradient(0, 0, 0, self.height())
        shade.setColorAt(0.85, QColor(0,0,0,0))
        shade.setColorAt(1.0, QColor(0,0,0,60))
        painter.fillRect(self.rect(), shade)

class PillLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: rgba(0,0,0,80);
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: 600;
            }
        """)

class TitleLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        f = QFont(); f.setPointSize(24); f.setWeight(QFont.Weight.Black)
        self.setFont(f)
        self.setStyleSheet("color:#ffffff;")
# ---------- Sign-in Dialog ----------
class SigninDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bing sign-in")
        self.setModal(True)
        self.logged_in = None
        self.remember = False

        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(18, 16, 18, 16)
        wrap.setSpacing(10)

        title = QLabel("Start now?")
        f = QFont(); f.setPointSize(14); f.setWeight(QFont.Weight.Bold)
        title.setFont(f); title.setStyleSheet("color:#ffffff;")
        title.setAlignment(Qt.AlignHCenter)

        sub = QLabel("Are you logged into your Bing account?")
        sf = QFont(); sf.setPointSize(11)
        sub.setFont(sf); sub.setStyleSheet("color:#e6f0ff;")
        sub.setAlignment(Qt.AlignHCenter)

        self.chk = QCheckBox("Remember my choice")
        self.chk.setStyleSheet("color:#eaf2ff;")
        self.chk.stateChanged.connect(lambda _: setattr(self, 'remember', self.chk.isChecked()))

        # Buttons
        row = QHBoxLayout(); row.setSpacing(8)
        btn_yes = QPushButton("I'm logged in")
        btn_no  = QPushButton("Sign in")
        for b, c0, c1 in (
            (btn_yes, "#34d399", "#0ea472"),
            (btn_no,  "#3a9bff", "#1e6aff"),
        ):
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(38)
            b.setStyleSheet(f"""
            QPushButton {{ color:white; border:none; border-radius:10px; padding:8px 14px;
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {c0}, stop:1 {c1}); font-weight:600; }}
            QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {c0}, stop:1 {c1}); }}
            QPushButton:pressed {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {c1}, stop:1 {c0}); }}
            """)
        btn_yes.clicked.connect(self._accept_yes)
        btn_no.clicked.connect(self._accept_no)

        row.addStretch(1); row.addWidget(btn_yes); row.addWidget(btn_no); row.addStretch(1)

        # Card look
        frame = QFrame(); frame.setObjectName("dlgcard")
        frame.setStyleSheet("QFrame#dlgcard { background: rgba(10,16,28,230); border-radius: 14px; }")
        inner = QVBoxLayout(frame); inner.setContentsMargins(16, 14, 16, 14); inner.setSpacing(10)
        inner.addWidget(title)
        inner.addWidget(sub)
        inner.addWidget(self.chk, 0, Qt.AlignHCenter)
        inner.addLayout(row)

        wrap.addWidget(frame)
        # Fixed-size dialog (non-resizable)
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint, True)
        self.setFixedSize(self.sizeHint())

    def _accept_yes(self):
        self.logged_in = True
        self.accept()

    def _accept_no(self):
        self.logged_in = False
        self.accept()

class HintLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        f = QFont(); f.setPointSize(10)
        self.setFont(f)
        self.setStyleSheet("color:#e6f0ff;")

class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet("QFrame#card { background: rgba(10,16,28,210); border-radius: 16px; }")
        shadow = QGraphicsDropShadowEffect(blurRadius=26, xOffset=0, yOffset=10, color=QColor(0,0,0,110))
        self.setGraphicsEffect(shadow)


class Stepper(QWidget):
    """Sleek + / − stepper with large buttons and centered value."""
    valueChanged = Signal(int)
    def __init__(self, minimum=1, maximum=2000, value=30, step=1):
        super().__init__()
        self.min = minimum; self.max = maximum; self._value = value; self.step = step
        row = QHBoxLayout(self); row.setContentsMargins(12, 10, 12, 10); row.setSpacing(12)
        self.setStyleSheet("background: rgba(255,255,255,22); border-radius: 14px;")

        self.btn_minus = QPushButton("−"); self.btn_plus = QPushButton("+")
        for b in (self.btn_minus, self.btn_plus):
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumSize(46, 46)
            b.setStyleSheet("""
            QPushButton { color:white; background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5b7cff, stop:1 #2b56f7);
                          border:none; border-radius:12px; font-weight:700; font-size:22px; }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #6b89ff, stop:1 #3a63ff); }
            QPushButton:pressed { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #2b56f7, stop:1 #2148d4); }
            """)
            b.setAutoRepeat(True); b.setAutoRepeatDelay(300); b.setAutoRepeatInterval(60)

        self.lbl = QLabel(str(self._value))
        f = QFont(); f.setPointSize(28); f.setWeight(QFont.Weight.Bold)
        self.lbl.setFont(f); self.lbl.setStyleSheet("color:white;")
        self.lbl.setMinimumWidth(80); self.lbl.setAlignment(Qt.AlignCenter)

        row.addWidget(self.btn_minus)
        row.addWidget(self.lbl, 1)
        row.addWidget(self.btn_plus)

        self.btn_minus.clicked.connect(lambda: self._bump(-self.step))
        self.btn_plus.clicked.connect(lambda: self._bump(+self.step))

    def _bump(self, d):
        v = max(self.min, min(self.max, self._value + d))
        if v != self._value:
            self._value = v
            self.lbl.setText(str(v))
            self.valueChanged.emit(v)

    def value(self): return self._value
    def setValue(self, v):
        v = max(self.min, min(self.max, v))
        if v != self._value:
            self._value = v; self.lbl.setText(str(v)); self.valueChanged.emit(v)

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bing Auto Search")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Tighter footprint
        self.resize(600, 280)
        self.setMinimumSize(580, 276)

        self.worker: SearchWorker | None = None
        self.countdown_timer = QTimer(self); self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self._tick_countdown)
        self.countdown_left = 0
        self.is_pinned = False
        self.count_target = 30

        # Background
        self.bg = GradientWidget()
        self.setCentralWidget(self.bg)
        root = QVBoxLayout(self.bg); root.setContentsMargins(18, 12, 18, 12); root.setSpacing(8)

        # Top bar: left (pin or remaining) | centered title | right (remaining or pin)
        self.title_label = TitleLabel("Bing Auto Search")
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.remaining = PillLabel("Remaining: 0")
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setFixedSize(36, 36)
        self.pin_btn.setCursor(Qt.PointingHandCursor)
        self.pin_btn.setToolTip("Pin on top")
        self.pin_btn.setStyleSheet(
            """
            QPushButton { color:#ffffff; background: rgba(0,0,0,90); border:none; border-radius: 10px; font-size:18px; }
            QPushButton:hover { background: rgba(255,255,255,40); }
            QPushButton:pressed { background: rgba(0,0,0,140); }
            """
        )
        self.pin_btn.clicked.connect(self.toggle_pin)

        # Containers for left/right so we can keep widths balanced
        self.left = QWidget(); self.right = QWidget()
        left_lay = QHBoxLayout(self.left); left_lay.setContentsMargins(0,0,0,0); left_lay.setSpacing(0)
        right_lay = QHBoxLayout(self.right); right_lay.setContentsMargins(0,0,0,0); right_lay.setSpacing(0)

        if IS_WIN:
            left_lay.addWidget(self.pin_btn, 0, Qt.AlignLeft | Qt.AlignVCenter)
            right_lay.addWidget(self.remaining, 0, Qt.AlignRight | Qt.AlignVCenter)
        else:
            left_lay.addWidget(self.remaining, 0, Qt.AlignLeft | Qt.AlignVCenter)
            right_lay.addWidget(self.pin_btn, 0, Qt.AlignRight | Qt.AlignVCenter)

        topbar = QHBoxLayout(); topbar.setContentsMargins(0,0,0,0); topbar.setSpacing(4)
        topbar.addWidget(self.left, 0, Qt.AlignVCenter)
        topbar.addWidget(self.title_label, 1, Qt.AlignVCenter)
        topbar.addWidget(self.right, 0, Qt.AlignVCenter)
        root.addLayout(topbar)

        # Balance side widths so the title is truly centered
        QTimer.singleShot(0, self._balance_side_widths)

        # Countdown label centered
        self.countdown = QLabel("")
        cf = QFont(); cf.setPointSize(12); cf.setWeight(QFont.Weight.DemiBold)
        self.countdown.setFont(cf)
        self.countdown.setStyleSheet("color:#eaf2ff;")
        root.addWidget(self.countdown, alignment=Qt.AlignHCenter)

        # Card: Stepper above Buttons (vertical)
        self.card = Card()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(12)

        # Stepper (narrower)
        self.stepper = Stepper(minimum=1, maximum=2000, value=self.count_target, step=1)
        self.stepper.setMaximumWidth(220)
        self.stepper.valueChanged.connect(self._on_stepper_changed)
        card_layout.addWidget(self.stepper, 0, Qt.AlignHCenter)

        # Buttons row
        buttons_row = QHBoxLayout(); buttons_row.setSpacing(8)
        self.btn_start = self._mk_btn("▶  Start", "#34d399", "#0ea472")
        self.btn_pause = self._mk_btn("⏸  Pause", "#3a9bff", "#1e6aff")
        self.btn_stop  = self._mk_btn("⏹  Stop",  "#f87171", "#ef4444")
        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_stop.clicked.connect(self.on_stop)
        buttons_row.addStretch(1)
        buttons_row.addWidget(self.btn_start)
        buttons_row.addWidget(self.btn_pause)
        buttons_row.addWidget(self.btn_stop)
        buttons_row.addStretch(1)
        card_layout.addLayout(buttons_row)

        root.addWidget(self.card, 0, Qt.AlignHCenter)

        root.addStretch(1)
        hint = HintLabel("Press Esc to stop")
        hint.setAlignment(Qt.AlignHCenter)
        root.addWidget(hint, alignment=Qt.AlignHCenter)

        # Initial visibility: only Start
        self._set_state_idle()

        # Preflight
        if IS_MAC: ok, msg = mac_preflight_access()
        else:      ok, msg = wl_preflight()
        if not ok:
            QMessageBox.critical(self, "Permission required", msg)

        # Compact fixed size based on contents
        self.adjustSize()
        self.setMinimumHeight(self.height())
        self.setMaximumHeight(self.height()+6)

    # --- UI helpers ---
    def _mk_btn(self, text, c0, c1):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(44)
        btn.setStyleSheet(f"""
        QPushButton {{
            color:white; border:none; border-radius:12px; padding:10px 18px;
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {c0}, stop:1 {c1});
            font-weight:600;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {self._lighter(c0)}, stop:1 {self._lighter(c1)});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {self._darker(c0)}, stop:1 {self._darker(c1)});
        }}
        """)
        return btn

    def _lighter(self, hexcol):
        c = QColor(hexcol); return QColor(min(255,int(c.red()*1.1)), min(255,int(c.green()*1.1)), min(255,int(c.blue()*1.1))).name()
    def _darker(self, hexcol):
        c = QColor(hexcol); return QColor(int(c.red()*0.85), int(c.green()*0.85), int(c.blue()*0.85)).name()


    # --- State visibility ---
    def _set_state_idle(self):
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_stop.hide()
        self.remaining.setText("Remaining: 0")
        self.countdown.setText("")

    def _set_state_running(self):
        self.btn_start.hide()
        self.btn_pause.show()
        self.btn_stop.show()

    def _set_state_paused(self):
        self.btn_start.setText("▶  Start")
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_stop.show()

    # --- Events ---
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.on_stop()
        else:
            super().keyPressEvent(e)

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_pinned)
        self.show()
        # Visual feedback on the pin button
        self.pin_btn.setStyleSheet(
            f"""
            QPushButton {{ color:{'#8be9a5' if self.is_pinned else '#ffffff'}; background: rgba(0,0,0,90); border:none; border-radius: 10px; font-size:18px; }}
            QPushButton:hover {{ background: rgba(255,255,255,40); }}
            QPushButton:pressed {{ background: rgba(0,0,0,140); }}
            """
        )
        self.pin_btn.setToolTip("Unpin window" if self.is_pinned else "Pin on top")
        # Subtle indicator in the title itself
        base = "Bing Auto Search"
        self.title_label.setText(base + ("  📌" if self.is_pinned else ""))

    def _on_stepper_changed(self, v):
        self.count_target = int(v)

    def _balance_side_widths(self):
        self.left.adjustSize(); self.right.adjustSize()
        w = max(self.left.sizeHint().width(), self.right.sizeHint().width())
        # Reserve at least a minimal width for stable centering
        w = max(w, 60)
        self.left.setFixedWidth(w)
        self.right.setFixedWidth(w)

    def _update_remaining(self, left):
        self.remaining.setText(f"Remaining: {left}")
        QTimer.singleShot(0, self._balance_side_widths)

    # --- Actions ---
    def on_start(self):
        settings = QSettings("AutoBingSearch", "App")
        pref = settings.value("assume_logged_in", None)
        if pref is None:
            dlg = SigninDialog(self)
            dlg.setStyleSheet("background: transparent;")
            if dlg.exec() == QDialog.Accepted:
                if dlg.remember:
                    settings.setValue("assume_logged_in", "yes" if dlg.logged_in else "no")
                if dlg.logged_in:
                    pass  # proceed
                else:
                    open_browser(prefer_edge=True, url=BING_SIGNIN)
                    return
            else:
                return
        else:
            if str(pref).lower() in ("yes", "true", "1"):
                pass  # proceed
            else:
                open_browser(prefer_edge=True, url=BING_SIGNIN)
                return

        if not random_words:
            QMessageBox.warning(self, "No words", "Your random_words list is empty."); return

        self.remaining.setText(f"Remaining: {min(self.count_target, len(random_words))}")
        QTimer.singleShot(0, self._balance_side_widths)
        self.countdown_left = 5
        self.countdown.setText(f"Starting in: {self.countdown_left}s")
        self.btn_start.hide()
        self.btn_pause.hide()
        self.btn_stop.show()
        self.countdown_timer.start()

    def _tick_countdown(self):
        self.countdown_left -= 1
        if self.countdown_left <= 0:
            self.countdown_timer.stop()
            self.countdown.setText("Starting…")
            self._begin_worker(self.count_target)
        else:
            self.countdown.setText(f"Starting in: {self.countdown_left}s")

    def _begin_worker(self, count):
        # Running: Pause + Stop
        self._set_state_running()
        self.worker = SearchWorker(random_words, count)
        self.worker.progress.connect(self._update_remaining)
        self.worker.error.connect(lambda m: QMessageBox.critical(self, "Automation error", m))
        self.worker.done.connect(self._on_done)
        self.worker.start()

    def on_pause(self):
        if not self.worker: return
        self.worker.toggle_pause()
        # paused shows Start + Stop
        if self.btn_pause.isVisible():
            self._set_state_paused()
        else:
            self._set_state_running()

    def on_stop(self):
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
            self.countdown.setText("")
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        self._set_state_idle()

    def _on_done(self):
        self._set_state_idle()

# ---------- Entry ----------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    if IS_MAC: ok, msg = mac_preflight_access()
    else:      ok, msg = wl_preflight()
    if not ok:
        print("[Automation permission warning]", msg)
    main()