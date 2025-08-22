import sys
import os
import time
import random
import threading
import platform
import webbrowser
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

# --- Dependencies ---
try:
    import pyautogui
except Exception as e:
    raise SystemExit("pyautogui is required. Install with:\n  pip install pyautogui pillow") from e

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

# --- Settings ---
pyautogui.PAUSE = 0.25
pyautogui.FAILSAFE = True  # Move mouse to top-left to emergency stop

SYSTEM = platform.system()
IS_WIN = SYSTEM == "Windows"
IS_MAC = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"
KEY_CMD = "command" if IS_MAC else "ctrl"

BING_HOME = "https://www.bing.com"
BING_SIGNIN = "https://login.live.com/"  # Microsoft account sign-in

# -------------------------
# Browser helpers
# -------------------------
def open_browser(prefer_edge=True, url=BING_HOME):
    """
    Try to open Microsoft Edge first (Windows/macOS/Linux),
    otherwise fall back to the default system browser.
    """
    used_edge = False

    if prefer_edge:
        try:
            if IS_WIN:
                # Common Edge paths on Windows
                candidates = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                ]
                for p in candidates:
                    if os.path.isfile(p):
                        webbrowser.register("msedge", None, webbrowser.BackgroundBrowser(p))
                        webbrowser.get("msedge").open(url, new=1)
                        used_edge = True
                        break

            elif IS_MAC:
                # Quote app name; don't construct this string on Windows/Linux
                if os.path.exists("/Applications/Microsoft Edge.app"):
                    webbrowser.get('open -a "Microsoft Edge" %s').open(url, new=1)
                    used_edge = True

            elif IS_LINUX:
                # Try common Edge binaries on Linux
                for name in ("microsoft-edge", "microsoft-edge-stable", "microsoft-edge-beta"):
                    edge_path = shutil.which(name)
                    if edge_path:
                        webbrowser.register("msedge", None, webbrowser.BackgroundBrowser(edge_path))
                        webbrowser.get("msedge").open(url, new=1)
                        used_edge = True
                        break
        except Exception:
            used_edge = False

    if not used_edge:
        webbrowser.open(url, new=1)

# -------------------------
# Permissions / environment preflight
# -------------------------
def check_pyautogui_permissions():
    """
    Try minimal actions that commonly fail when permissions are missing.
    Return (ok: bool, message: str).
    """
    try:
        _ = pyautogui.size()
        _ = pyautogui.position()
        try:
            # Screenshot is a good indicator on macOS/Wayland
            pyautogui.screenshot(region=(0, 0, 1, 1))
        except Exception:
            # Not fatal everywhere; continue
            pass
        return True, "OK"
    except Exception as e:
        msg = str(e)
        tips = []
        if IS_MAC:
            tips += [
                "macOS: System Settings → Privacy & Security:",
                "  • Accessibility: enable Terminal/VS Code (the app running this script)",
                "  • Screen Recording: enable Terminal/VS Code",
            ]
        elif IS_LINUX:
            tips += [
                "Linux: Prefer an X11 session; Wayland often blocks automation.",
                "If on Wayland, try an Xorg session (e.g., 'Ubuntu on Xorg').",
                "Ensure DISPLAY is set (echo $DISPLAY).",
            ]
        elif IS_WIN:
            tips += [
                "Windows: Usually no special permission needed.",
                "If blocked, try running VS Code/Terminal as Administrator.",
            ]
        return False, "PyAutoGUI cannot access the display/controls.\n\nError: {}\n\n{}".format(
            msg, "\n".join(tips)
        )

# -------------------------
# Search worker thread
# -------------------------
class SearchWorker(threading.Thread):
    def __init__(self, words, target_count, on_progress, on_done, on_error, stop_event, pause_event):
        super().__init__(daemon=True)
        self.words = words
        self.target = target_count
        self.on_progress = on_progress
        self.on_done = on_done
        self.on_error = on_error
        self.stop_event = stop_event
        self.pause_event = pause_event

    def run(self):
        if not self.words:
            self.on_error("Your word list is empty.\nPaste your random_words and try again.")
            self.on_done()
            return

        remaining = min(self.target, len(self.words))
        self.on_progress(remaining)

        # Ensure a browser is open
        open_browser(prefer_edge=True, url=BING_HOME)
        time.sleep(3)

        for i in range(remaining):
            if self.stop_event.is_set():
                break

            # Pause loop
            while self.pause_event.is_set() and not self.stop_event.is_set():
                time.sleep(0.1)

            if self.stop_event.is_set():
                break

            try:
                term = random.choice(self.words)
                self.words.remove(term)

                # Focus omnibox/address bar, type query, hit Enter
                pyautogui.hotkey(KEY_CMD, "l")
                time.sleep(0.2)
                pyautogui.typewrite(term, interval=0.02)
                pyautogui.press("enter")

                # Wait for results; add jitter
                time.sleep(2.5 + random.uniform(0.2, 0.8))

                remaining_now = remaining - (i + 1)
                self.on_progress(remaining_now)

            except pyautogui.FailSafeException:
                self.stop_event.set()
                break
            except Exception as e:
                self.stop_event.set()
                self.on_error(f"Automation stopped:\n{e}")
                break

        self.on_done()

# -------------------------
# GUI
# -------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Search")
        self.geometry("420x270")
        self.resizable(False, False)

        # State
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()  # when set → paused
        self.worker = None
        self.countdown_after_id = None
        self.countdown_seconds = 0

        # UI vars
        self.remaining_var = tk.IntVar(value=0)
        self.status_var = tk.StringVar(value="Idle")
        self.countdown_var = tk.StringVar(value="")
        self.pin_var = tk.BooleanVar(value=False)

        frm = ttk.Frame(self, padding=14)
        frm.pack(fill="both", expand=True)

        # Row 0: instructions + Pin
        ttk.Label(frm, text="Press Escape in this window to STOP the search.").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        self.pin_btn = ttk.Checkbutton(frm, text="Pin on top", variable=self.pin_var, command=self.toggle_pin)
        self.pin_btn.grid(row=0, column=2, sticky="e")

        # Row 1: searches spinbox
        ttk.Label(frm, text="Searches:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.spn = ttk.Spinbox(frm, from_=1, to=1000, width=8)
        self.spn.set("30")
        self.spn.grid(row=1, column=1, sticky="w", pady=(10, 0))

        # Row 2: remaining + status
        ttk.Label(frm, text="Remaining:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Label(frm, textvariable=self.remaining_var).grid(row=2, column=1, sticky="w", pady=(8, 0))
        ttk.Label(frm, textvariable=self.status_var, foreground="#555").grid(row=2, column=2, sticky="e", pady=(8, 0))

        # Row 3: countdown display
        ttk.Label(frm, textvariable=self.countdown_var, font=("TkDefaultFont", 10, "bold")).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        # Row 4: buttons
        self.btn_start = ttk.Button(frm, text="Start", command=self.on_start)
        self.btn_pause = ttk.Button(frm, text="Pause", command=self.on_pause, state="disabled")
        self.btn_stop = ttk.Button(frm, text="Stop", command=self.on_stop, state="disabled")
        self.btn_start.grid(row=4, column=0, pady=(16, 0), sticky="we")
        self.btn_pause.grid(row=4, column=1, pady=(16, 0), sticky="we")
        self.btn_stop.grid(row=4, column=2, pady=(16, 0), sticky="we")

        # Grid config
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)

        # Key binding: ESC to stop
        self.bind("<Escape>", lambda e: self.on_stop())

        # Preflight permissions on load
        self.after(100, self.preflight)

    # --- Helpers ---
    def set_buttons(self, running=False, paused=False, during_countdown=False):
        if during_countdown:
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.btn_pause.config(state="disabled", text="Pause")
            return

        if running:
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.btn_pause.config(state="normal")
            self.btn_pause.config(text=("Resume" if paused else "Pause"))
        else:
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_pause.config(state="disabled", text="Pause")

    def toggle_pin(self):
        self.attributes("-topmost", bool(self.pin_var.get()))

    def preflight(self):
        ok, msg = check_pyautogui_permissions()
        if not ok:
            messagebox.showerror("Permission required", msg)
            self.status_var.set("Blocked")
        else:
            self.status_var.set("Ready")

    # Thread-safe UI hooks
    def ui_set_remaining(self, left):
        self.after(0, lambda: self.remaining_var.set(left))

    def ui_on_done(self):
        def finish():
            self.status_var.set("Idle")
            self.countdown_var.set("")
            self.set_buttons(running=False, paused=False)
        self.after(0, finish)

    def ui_error(self, msg):
        self.after(0, lambda: messagebox.showerror("Automation error", msg))

    # --- Countdown ---
    def start_countdown(self, seconds, on_finish):
        self.countdown_seconds = int(seconds)
        self.countdown_var.set(f"Starting in: {self.countdown_seconds}s")
        self.set_buttons(during_countdown=True)
        self.status_var.set("Countdown")

        def tick():
            if self.stop_event.is_set():
                self.countdown_var.set("")
                self.set_buttons(running=False, paused=False)
                return

            self.countdown_seconds -= 1
            if self.countdown_seconds <= 0:
                self.countdown_var.set("Starting…")
                self.countdown_after_id = None
                on_finish()
            else:
                self.countdown_var.set(f"Starting in: {self.countdown_seconds}s")
                self.countdown_after_id = self.after(1000, tick)

        self.countdown_after_id = self.after(1000, tick)

    def cancel_countdown(self):
        if self.countdown_after_id:
            try:
                self.after_cancel(self.countdown_after_id)
            except Exception:
                pass
            self.countdown_after_id = None
        self.countdown_var.set("")

    # --- Callbacks ---
    def on_start(self):
        # Parse desired count
        try:
            count = int(self.spn.get())
        except ValueError:
            count = 30
        if count <= 0:
            messagebox.showwarning("Invalid value", "Please choose at least 1 search.")
            return

        ok, msg = check_pyautogui_permissions()
        if not ok:
            messagebox.showerror("Permission required", msg)
            return

        # Ask Bing login status
        logged_in = messagebox.askyesno(
            "Bing Sign-in",
            "Are you logged into your Bing account?\n\n"
            "Yes → begin with a 5-second countdown\n"
            "No → open the Bing/Microsoft sign-in page"
        )
        if not logged_in:
            self.status_var.set("Sign-in required")
            open_browser(prefer_edge=True, url=BING_SIGNIN)
            return

        # Prepare (5-second countdown)
        if not random_words:
            messagebox.showwarning("No words", "Your random_words list is empty.")
            return

        self.stop_event.clear()
        self.pause_event.clear()
        self.remaining_var.set(min(count, len(random_words)))
        self.start_countdown(5, on_finish=lambda: self._start_worker(count))

    def _start_worker(self, count):
        if self.stop_event.is_set():
            self.set_buttons(running=False, paused=False)
            self.countdown_var.set("")
            return

        self.status_var.set("Running")
        self.set_buttons(running=True, paused=False)
        self.countdown_var.set("")

        self.worker = SearchWorker(
            words=random_words,
            target_count=count,
            on_progress=self.ui_set_remaining,
            on_done=self.ui_on_done,
            on_error=self.ui_error,
            stop_event=self.stop_event,
            pause_event=self.pause_event,
        )
        self.worker.start()

    def on_pause(self):
        if self.worker is None:
            return
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.status_var.set("Running")
            self.set_buttons(running=True, paused=False)
        else:
            self.pause_event.set()
            self.status_var.set("Paused")
            self.set_buttons(running=True, paused=True)

    def on_stop(self):
        # Cancel countdown if pending, and stop worker
        self.stop_event.set()
        self.cancel_countdown()
        self.status_var.set("Stopping...")
        self.set_buttons(running=False, paused=False)

# -------------------------
# Entry
# -------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()