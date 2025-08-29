import os, sys, time, random, platform, shutil, subprocess, webbrowser, threading
from urllib.parse import quote_plus
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize, QSettings, QAbstractNativeEventFilter, QAbstractEventDispatcher
from PySide6.QtGui import (
    QPalette, QColor, QFont, QPainter, QLinearGradient, QPen, QPixmap, QIcon, QShortcut, QKeySequence
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QGraphicsDropShadowEffect, QDialog, QCheckBox, QSizePolicy
)

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None

def mac_open_input_monitoring():
    if IS_MAC:
        try:
            subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent"], check=False)
        except Exception:
            pass
def mac_open_automation():
    if IS_MAC:
        try:
            subprocess.run([
                "open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"
            ], check=False)
        except Exception:
            pass

def mac_open_accessibility():
    if IS_MAC:
        try:
            subprocess.run([
                "open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
            ], check=False)
        except Exception:
            pass

SYSTEM = platform.system()
IS_MAC = SYSTEM == "Darwin"
IS_WIN = SYSTEM == "Windows"


IS_LINUX = SYSTEM == "Linux"

# --- Focus browser helpers for Win/Linux ---
def win_focus_browser():
    if not IS_WIN:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        SW_SHOW = 5
        SW_RESTORE = 9
        SW_SHOWMAXIMIZED = 3
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        browsers = {"msedge.exe", "chrome.exe", "firefox.exe", "brave.exe", "opera.exe"}
        GetWindowThreadProcessId = user32.GetWindowThreadProcessId
        GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
        QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        QueryFullProcessImageNameW.restype = wintypes.BOOL
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        targets = []
        @EnumWindowsProc
        def enum_proc(hwnd, lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            pid = wintypes.DWORD(0)
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
            exe = ""
            if h:
                buf = ctypes.create_unicode_buffer(260)
                size = wintypes.DWORD(260)
                if QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                    exe = os.path.basename(buf.value).lower()
                kernel32.CloseHandle(h)
            if exe in browsers:
                targets.append(hwnd)
                return False
            return True
        user32.EnumWindows(enum_proc, 0)
        if not targets:
            return False
        hwnd = targets[0]
        class POINT(ctypes.Structure):
            _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
        class RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
        class WINDOWPLACEMENT(ctypes.Structure):
            _fields_ = [("length", wintypes.UINT), ("flags", wintypes.UINT), ("showCmd", wintypes.UINT), ("ptMinPosition", POINT), ("ptMaxPosition", POINT), ("rcNormalPosition", RECT)]
        wp = WINDOWPLACEMENT()
        wp.length = ctypes.sizeof(WINDOWPLACEMENT)
        if user32.GetWindowPlacement(hwnd, ctypes.byref(wp)):
            if wp.showCmd == 2:
                user32.ShowWindow(hwnd, SW_RESTORE)
            elif wp.showCmd == SW_SHOWMAXIMIZED:
                user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)
            else:
                user32.ShowWindow(hwnd, SW_SHOW)
        try:
            fg = user32.GetForegroundWindow()
            ctid = kernel32.GetCurrentThreadId()
            tid = user32.GetWindowThreadProcessId(fg, None)
            user32.AttachThreadInput(ctid, tid, True)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.AttachThreadInput(ctid, tid, False)
        except Exception:
            pass
        if user32.GetForegroundWindow() != hwnd:
            VK_MENU = 0x12
            KEYEVENTF_KEYUP = 0x0002
            user32.keybd_event(VK_MENU, 0, 0, 0)
            user32.SetForegroundWindow(hwnd)
            user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        return user32.GetForegroundWindow() == hwnd
    except Exception:
        return False

def linux_focus_browser():
    if not IS_LINUX:
        return False
    try:
        devnull = open(os.devnull, "wb")
        for cmd in (["wmctrl","-xa","microsoft-edge"], ["wmctrl","-xa","google-chrome"], ["wmctrl","-xa","firefox"], ["wmctrl","-xa","brave"]):
            if shutil.which(cmd[0]) and subprocess.call(cmd, stdout=devnull, stderr=devnull) == 0:
                return True
        if shutil.which("xdotool"):
            for cls in ("microsoft-edge", "google-chrome", "firefox", "brave"):
                subprocess.call(["xdotool","search","--class",cls,"windowactivate"], stdout=devnull, stderr=devnull)
                return True
    except Exception:
        pass
    try:
        import pyautogui
        pyautogui.hotkey("alt","tab")
        time.sleep(0.12)
        return True
    except Exception:
        return False

def wl_focus_browser():
    if IS_WIN:
        return win_focus_browser()
    if IS_LINUX:
        return linux_focus_browser()
    return False

APP_USER_MODEL_ID = "com.autobingsearch.app"

def _resource_root():
    return getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))

def get_app_icon_path():
    root = _resource_root()
    if IS_WIN:
        p = os.path.join(root, "assets", "app.ico")
    elif IS_MAC:
        p = os.path.join(root, "assets", "app.icns")
    else:
        p = os.path.join(root, "assets", "app.png")
    return p if os.path.exists(p) else None

if IS_WIN:
    import ctypes
    from ctypes import wintypes  # noqa: F401
    _user32 = ctypes.windll.user32
    _LR_DEFAULTSIZE = 0x00000040
    _LR_LOADFROMFILE = 0x00000010
    _IMAGE_ICON = 1
    _WM_SETICON = 0x0080
    _ICON_SMALL = 0
    _ICON_BIG = 1

    def _win_set_window_icons(hwnd: int, ico_path: str):
        try:
            hicon_big = _user32.LoadImageW(None, ico_path, _IMAGE_ICON, 0, 0, _LR_LOADFROMFILE | _LR_DEFAULTSIZE)
            hicon_small = _user32.LoadImageW(None, ico_path, _IMAGE_ICON, 16, 16, _LR_LOADFROMFILE)
            if hicon_big:
                _user32.SendMessageW(hwnd, _WM_SETICON, _ICON_BIG, hicon_big)
            if hicon_small:
                _user32.SendMessageW(hwnd, _WM_SETICON, _ICON_SMALL, hicon_small)
        except Exception:
            pass

if IS_MAC:
    try:
        from AppKit import NSEvent
        try:
            from AppKit import NSEventMaskKeyDown as _NSEventMaskKeyDown
        except Exception:
            _NSEventMaskKeyDown = 1 << 10  # fallback mask for keyDown
    except Exception:
        NSEvent = None
        _NSEventMaskKeyDown = 1 << 10
else:
    NSEvent = None
    _NSEventMaskKeyDown = 1 << 10

if not IS_MAC:
    try:
        import pyautogui
        pyautogui.PAUSE = 0.25
        pyautogui.FAILSAFE = True
    except Exception as e:
        if IS_WIN or IS_LINUX:
            raise SystemExit("Install dependency: pip install pyautogui") from e

BING_HOME   = "https://www.bing.com"
BING_SIGNIN = "https://login.live.com/"

random_words = [
    "nebula", "quasar", "supernova", "asteroid", "galaxy", "comet", "orbit", "pulsar", "atom", "molecule",
    "gravity", "neutron", "photosynthesis", "quantum", "entropy", "enzyme", "proton", "electron", "isotope", "plasma",
    "lion", "tiger", "leopard", "cheetah", "panther", "jaguar", "cougar", "lynx", "hyena", "wolf",
    "eagle", "falcon", "sparrow", "swallow", "albatross", "pelican", "heron", "ibis", "stork", "owl",
    "salmon", "trout", "carp", "catfish", "anchovy", "sardine", "tuna", "mackerel", "halibut", "cod",
    "oak", "maple", "willow", "birch", "cypress", "cedar", "aspen", "baobab", "spruce", "fir",
    "rose", "tulip", "orchid", "lily", "daffodil", "peony", "violet", "magnolia", "iris", "sunflower",
    "ruby", "sapphire", "emerald", "topaz", "amethyst", "garnet", "opal", "quartz", "diamond", "beryl",
    "river", "ocean", "lagoon", "harbor", "island", "valley", "canyon", "plateau", "delta", "estuary",
    "desert", "tundra", "prairie", "savanna", "rainforest", "wetland", "moor", "glacier", "taiga", "steppe",
    "breeze", "thunder", "lightning", "hailstorm", "downpour", "mist", "blizzard", "monsoon", "cyclone", "typhoon",
    "sunrise", "sunset", "twilight", "midnight", "equinox", "solstice", "horizon", "zenith", "dawn", "dusk",
    "copper", "silver", "gold", "platinum", "iron", "nickel", "cobalt", "titanium", "aluminum", "mercury",
    "oxygen", "hydrogen", "carbon", "nitrogen", "sulfur", "phosphorus", "chlorine", "argon", "neon", "xenon",
    "triangle", "square", "rectangle", "parallelogram", "trapezoid", "rhombus", "polygon", "ellipse", "circle", "oval",
    "calculus", "algebra", "geometry", "statistics", "trigonometry", "topology", "logic", "combinatorics", "theorem", "lemma",
    "protein", "lipid", "carbohydrate", "nucleus", "ribosome", "chloroplast", "mitochondrion", "cytoplasm", "membrane", "chromosome",
    "bacteria", "fungus", "amoeba", "protozoan", "alga", "lichen", "nematode", "annelid", "arthropod", "crustacean",
    "volcano", "earthquake", "tsunami", "avalanche", "landslide", "erosion", "sediment", "bedrock", "mineral", "fossil",
    "marble", "granite", "basalt", "limestone", "sandstone", "shale", "gneiss", "schist", "quartzite", "slate",
    "hammer", "chisel", "wrench", "pliers", "screwdriver", "solder", "anvil", "lathe", "drill", "saw",
    "canvas", "easel", "palette", "pigment", "charcoal", "pastel", "fresco", "mosaic", "etching", "engraving",
    "violin", "cello", "trumpet", "trombone", "clarinet", "oboe", "bassoon", "timpani", "symphony", "sonata",
    "rhythm", "melody", "harmony", "tempo", "crescendo", "glissando", "staccato", "vibrato", "cadence", "overture",
    "syntax", "semantics", "phonology", "morphology", "pragmatics", "lexicon", "grammar", "dialect", "phoneme", "grapheme",
    "justice", "freedom", "equality", "virtue", "honesty", "courage", "wisdom", "empathy", "kindness", "patience",
    "concept", "theory", "hypothesis", "evidence", "method", "analysis", "synthesis", "inference", "experiment", "observation",
    "battery", "resistor", "capacitor", "inductor", "transistor", "diode", "oscillator", "antenna", "circuit", "sensor",
    "network", "protocol", "router", "switch", "firewall", "bandwidth", "latency", "throughput", "algorithm", "database",
    "compiler", "interpreter", "encryption", "hashing", "virtualization", "container", "notebook", "journal", "ledger", "parchment",
    "ant", "aardvark", "baboon", "badger", "bat", "bear", "beaver", "bison", "buffalo", "camel",
    "capybara", "caracal", "chinchilla", "chimpanzee", "coyote", "dingo", "donkey", "dromedary", "elephant", "ferret",
    "fox", "gazelle", "giraffe", "gorilla", "groundhog", "hamster", "hedgehog", "hippopotamus", "horse", "iguana",
    "impala", "jackal", "kangaroo", "koala", "lemur", "llama", "manatee", "marmot", "meerkat", "mongoose",
    "moose", "narwhal", "ocelot", "octopus", "opossum", "orangutan", "otter", "panda", "platypus", "porcupine",
    "porpoise", "possum", "rabbit", "raccoon", "reindeer", "rhinoceros", "seal", "serval", "skunk", "sloth",
    "tapir", "walrus", "warthog", "weasel", "wildebeest", "zebra", "yak", "alpaca", "anteater", "armadillo",
    "auklet", "bittern", "blackbird", "bluebird", "bobolink", "bunting", "buzzard", "canary", "cardinal", "chickadee",
    "cormorant", "crane", "cuckoo", "curlew", "dove", "egret", "goldfinch", "goose", "grouse", "gull",
    "hawk", "hoopoe", "jay", "kestrel", "kite", "kingfisher", "lark", "loon", "magpie", "mallard",
    "mockingbird", "nightjar", "nuthatch", "oriole", "osprey", "ostrich", "parakeet", "parrot", "peacock", "peafowl",
    "phoebe", "phoenix", "pigeon", "ptarmigan", "quail", "raven", "robin", "sandpiper", "sapsucker", "shrike",
    "snipe", "starling", "swift", "tern", "thrush", "titmouse", "toucan", "vireo", "vulture", "warbler",
    "waxwing", "woodcock", "woodpecker", "wren", "plover", "pipit", "sandgrouse", "penguin", "cassowary", "abalone",
    "barracuda", "bluegill", "bonito", "clownfish", "eel", "flounder", "goby", "grouper", "guppy", "herring",
    "lamprey", "marlin", "minnow", "mollusk", "moray", "perch", "pike", "pollock", "ray", "rockfish",
    "sailfish", "snapper", "squid", "sturgeon", "sunfish", "swordfish", "tarpon", "tilapia", "walleye", "antlion",
    "aphid", "beetle", "bollworm", "butterfly", "caddisfly", "cicada", "cricket", "damselfly", "dragonfly", "earwig",
    "firefly", "flea", "grasshopper", "horntail", "lacewing", "ladybug", "mantis", "mayfly", "millipede", "mite",
    "mosquito", "moth", "pillbug", "scorpion", "silverfish", "spider", "termite", "tick", "wasp", "weevil",
    "woodlouse", "worm", "katydid", "tarantula", "centipede", "bumblebee", "honeybee", "locust", "blackfly", "acacia",
    "alder", "ash", "beech", "bamboo", "banyan", "bottlebrush", "dogwood", "elm", "hemlock", "holly",
    "juniper", "kapok", "mahogany", "mulberry", "olive", "palm", "poplar", "redwood", "sequoia", "sycamore",
    "teak", "tamarind", "yew", "yucca", "zinnia", "azalea", "begonia", "camellia", "carnation", "chrysanthemum",
    "cosmos", "dahlia", "gardenia", "geranium", "gladiolus", "hibiscus", "hydrangea", "jasmine", "lavender", "marigold",
    "morningglory", "narcissus", "pansy", "petunia", "phlox", "poinsettia", "primrose", "snapdragon", "anemone", "aster",
    "camphor", "caladium", "clover", "fennel", "sage", "thyme", "rosemary", "basil", "oregano", "cumin",
    "turmeric", "ginger", "horseradish", "parsley", "cilantro", "chive", "tarragon", "saffron", "agate", "actinolite",
    "alexandrite", "andalusite", "apatite", "aragonite", "azurite", "barite", "benitoite", "bornite", "calcite", "cassiterite",
    "celestine", "chalcedony", "chalcopyrite", "chromite", "corundum", "diopside", "dolomite", "epidote", "feldspar", "fluorite",
    "galena", "graphite", "hematite", "ilmenite", "jadeite", "kaolinite", "kunzite", "labradorite", "malachite", "monazite",
    "obsidian", "olivine", "orthoclase", "peridot", "petalite", "pyrite", "rhodonite", "rutile", "scapolite", "sodalite",
    "spinel", "sugilite", "tourmaline", "uraninite", "variscite", "wollastonite", "zircon", "zeolite", "archipelago", "atoll",
    "bayou", "butte", "cape", "cliff", "dune", "fen", "fjord", "foothill", "gorge", "gulch",
    "inlet", "isthmus", "knoll", "marsh", "mesa", "meadow", "oasis", "outwash", "peninsula", "ravine",
    "ridge", "scree", "shoal", "sound", "strait", "summit", "swale", "tideland", "upland", "watershed",
    "wharf", "grotto", "hinterland", "backwater", "headland", "moorland", "aurora", "drizzle", "gust", "squall",
    "gale", "zephyr", "whirlwind", "cloudburst", "rainfall", "overcast", "sunbeam", "afterglow", "downburst", "microburst",
    "whiteout", "mistbow", "rainbow", "sunshower", "icefall", "snowflake", "icicle", "sleet", "graupel", "snowdrift",
    "thundersnow", "stormfront", "updraft", "downdraft", "windstorm", "tempest", "aphelion", "perihelion", "apogee", "perigee",
    "umbra", "penumbra", "syzygy", "asterism", "multiverse", "singularity", "wormhole", "planetesimal", "exoplanet", "magnetar",
    "nebulosity", "astronomy", "astrophysics", "meteoroid", "meteorite", "meteorology", "heliosphere", "ionosphere", "mesosphere", "stratosphere",
    "troposphere", "chronology", "epoch", "eon", "millennium", "bromine", "iodine", "cesium", "barium", "strontium",
    "calcium", "potassium", "sodium", "lithium", "beryllium", "magnesium", "scandium", "vanadium", "manganese", "chromium",
    "zinc", "gallium", "germanium", "arsenic", "selenium", "bismuth", "polonium", "radon", "radium", "francium",
    "astatine", "thorium", "uranium", "plutonium", "neptunium", "americium", "curium", "einsteinium", "fermium", "mendelevium",
    "nobelium", "lawrencium", "rutherfordium", "dubnium", "seaborgium", "bohrium", "hassium", "meitnerium", "roentgenium", "copernicium",
    "nihonium", "flerovium", "moscovium", "livermorium", "oganesson", "axiom", "proof", "corollary", "postulate", "predicate",
    "quantifier", "bijection", "injection", "surjection", "isomorphism", "homomorphism", "manifold", "tensor", "matrix", "determinant",
    "eigenvalue", "eigenvector", "gradient", "divergence", "curl", "integral", "derivative", "limit", "series", "sequences",
    "congruence", "modulus", "prime", "composite", "factorial", "polygonal", "polyhedron", "simplex", "torus", "knot",
    "graph", "lattice", "ring", "field", "group", "momentum", "inertia", "impulse", "friction", "viscosity",
    "turbulence", "kinematics", "dynamics", "thermodynamics", "optics", "acoustics", "relativity", "superconductivity", "spintronics", "photovoltaics",
    "electrostatics", "magnetism", "radiation", "diffraction", "interference", "refraction", "resonance", "conductance", "inductance", "capacitance",
    "impedance", "admittance", "permittivity", "permeability", "luminosity", "allele", "genotype", "phenotype", "epigenetics", "homeostasis",
    "metabolism", "catabolism", "anabolism", "osmosis", "diffusion", "endocytosis", "exocytosis", "apoptosis", "autophagy", "synapse",
    "axon", "dendrite", "neurotransmitter", "myelin", "glia", "photosystem", "stomata", "xylem", "phloem", "meristem",
    "gametophyte", "sporophyte", "zygote", "blastula", "gastrula", "embryo", "placenta", "biome", "ecosystem", "biosphere",
    "population", "niche", "symbiosis", "mutualism", "parasitism", "commensalism", "predation", "trophic", "bioluminescence", "chlorophyll",
    "carotenoid", "hemoglobin", "myoglobin", "insulin", "glucagon", "artery", "vein", "capillary", "atrium", "ventricle"
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

def _osa(script: str):
    try:
        return subprocess.run(["osascript", "-e", script], check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
        if "Not authorized" in err or "not authorized" in err or "Not permitted" in err:
            mac_open_automation()
        raise RuntimeError(err or "AppleScript failed") from e

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

def mac_focus_omnibox(): mac_keycode(37, with_cmd=True)     # cmd-L
def mac_press_return():  mac_keycode(36, with_cmd=False)

# Click near the top-center of the main display to focus Bing's search box (macOS)
def mac_click_focus_region():
    try:
        import Quartz, time as _t
        bounds = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
        x = int(bounds.size.width * 0.5)
        y = int(bounds.size.height * 0.22)
        pos = (x, y)
        ev = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, pos, Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, ev)
        _t.sleep(0.01)
        ev = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, pos, Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, ev)
    except Exception:
        pass

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

# Try to focus Bing's on-page search box on Win/Linux
def _focus_bing_box_win_linux():
    try:
        # click near the top-center within the active window; adjust Y so it hits the results-page box too
        win = getattr(pyautogui, "getActiveWindow", lambda: None)()
        if win and getattr(win, "box", None):
            x, y, w, h = win.left, win.top, win.width, win.height
            # place click around ~14% of window height from the top, clamped sensibly
            pyautogui.click(x + w // 2, y + int(min(190, max(110, h * 0.14))))
        else:
            sw, sh = pyautogui.size()
            pyautogui.click(sw // 2, int(sh * 0.22))
        time.sleep(0.15)
        # select-all and clear once in case selection didn't stick
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.press('backspace')
        time.sleep(0.04)
    except Exception:
        pass

class Automator:
    def __init__(self):
        self.browser_mac = mac_pick_browser() if IS_MAC else None
        self._first = True
        self._launched = False
        self._first_search = True

    def _refocus_browser(self):
        if IS_MAC:
            mac_activate(self.browser_mac)
            time.sleep(0.08)
        else:
            wl_focus_browser()
            time.sleep(0.08)

    def open_and_ready(self):
        if not self._launched:
            open_browser(prefer_edge=True, url=BING_HOME)
            self._launched = True
            # give the first page a moment to settle
            time.sleep(2.4)
            if IS_MAC:
                mac_activate(self.browser_mac)
        self._refocus_browser()

    def _focus_bing_box_mac(self) -> bool:
        try:
            _osa(
                f'''
                tell application "{self.browser_mac}"
                    if (count of windows) = 0 then return
                    tell front window's active tab to do javascript (
                        "(function(){{var el=document.getElementById('sb_form_q')||document.querySelector('input[name=q],input[type=search]'); if(el){{el.focus(); el.select(); try{{el.value='';}}catch(e){{}}}} return true;}})()"
                    )
                end tell
                '''
            )
            return True
        except Exception:
            pass
        try:
            mac_activate(self.browser_mac)
            time.sleep(0.1)
            mac_click_focus_region()
            time.sleep(0.15)
            _osa('tell application "System Events" to keystroke "a" using command down')
            _osa('tell application "System Events" to key code 51')
            return True
        except Exception:
            return False

    def _mac_set_front_url(self, url: str):
        try:
            if self.browser_mac == "Safari":
                _osa(f'set URL of front document of application "Safari" to "{url}"')
            else:
                _osa(
                    f'tell application "{self.browser_mac}" to tell front window to set URL of active tab to "{url}"'
                )
            return True
        except Exception:
            return False

    def _bing_url(self, term: str) -> str:
        return f"{BING_HOME}/search?q={quote_plus(term)}"

    def search_once(self, term: str):
        """Type into Bing's search box in the SAME TAB. For the first search, ensure focus; thereafter use the results-page auto-focus behavior (any letter focuses the box), then Ctrl/Cmd+A and type. Falls back to direct URL if something goes wrong."""
        self._refocus_browser()
        if IS_MAC:
            try:
                mac_activate(self.browser_mac)
                time.sleep(0.10)
                if self._first_search:
                    if not self._focus_bing_box_mac():
                        mac_activate(self.browser_mac)
                        time.sleep(0.2)
                        mac_click_focus_region()
                        time.sleep(0.15)
                        _osa('tell application "System Events" to keystroke "a" using command down')
                        _osa('tell application "System Events" to key code 51')
                    mac_type_human(term)
                    mac_press_return()
                    self._first_search = False
                    return
                # On Bing results pages, any letter focuses the box. Then Cmd+A to clear, type, Enter.
                _osa('tell application "System Events" to keystroke "a"')
                _osa('tell application "System Events" to keystroke "a" using command down')
                mac_type_human(term)
                mac_press_return()
                return
            except Exception:
                # Fallback: same-tab navigation to the results URL
                try:
                    self._mac_set_front_url(self._bing_url(term))
                    self._first_search = False
                    return
                except Exception:
                    open_browser(prefer_edge=True, url=self._bing_url(term))
                    self._first_search = False
                    return

        try:
            if self._first_search:
                _focus_bing_box_win_linux()
                human_type_pyautogui(term)
                pyautogui.press('enter')
                self._first_search = False
                return
            # Results-page trick: any letter focuses the box, then Ctrl+A, type, Enter
            pyautogui.typewrite('a')
            time.sleep(0.05)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            human_type_pyautogui(term)
            pyautogui.press('enter')
        except Exception:
            # Same-tab fallback via Ctrl+L -> results URL
            try:
                from urllib.parse import quote_plus as _qp
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.08)
                pyautogui.typewrite(f"{BING_HOME}/search?q={_qp(term)}", interval=0.02)
                pyautogui.press('enter')
                self._first_search = False
            except Exception:
                pass

class SearchWorker(QThread):
    progress = Signal(int)
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
                self.error.emit("Your word list is empty.")
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
                # spacing between searches, interruptible by stop
                if self._stop.wait(10.0):
                    break
                self.progress.emit(remaining - (i + 1))
        except Exception as e:
            self.error.emit(f"Automation stopped:\n{e}")
        finally:
            self.done.emit()

class GlobalEsc:
    def __init__(self, callback):
        self.callback = callback
        self.listener = None

    def start(self):
        if pynput_keyboard is None:
            return False, "pynput not installed"
        def on_press(key):
            try:
                if key == pynput_keyboard.Key.esc:
                    QTimer.singleShot(0, self.callback)
            except Exception:
                pass
        def on_release(key):
            try:
                if key == pynput_keyboard.Key.esc:
                    QTimer.singleShot(0, self.callback)
            except Exception:
                pass
        try:
            self.listener = pynput_keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
                suppress=False
            )
            self.listener.daemon = True
            self.listener.start()
            return True, "OK"
        except Exception as e:
            return False, str(e)

    def stop(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

class MacGlobalEsc:
    def __init__(self, callback):
        self.callback = callback
        self.globalMonitor = None

    def start(self):
        if not IS_MAC or NSEvent is None:
            return False, "AppKit not available"
        def handler(evt):
            try:
                # Escape keycode is 53
                if int(evt.keyCode()) == 53:
                    QTimer.singleShot(0, self.callback)
            except Exception:
                pass
        try:
            self.globalMonitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(_NSEventMaskKeyDown, handler)
            return True, "OK"
        except Exception as e:
            return False, str(e)

    def stop(self):
        if self.globalMonitor and NSEvent is not None:
            try:
                NSEvent.removeMonitor_(self.globalMonitor)
            except Exception:
                pass
            self.globalMonitor = None

# Quartz event tap global ESC listener for macOS
class MacEventTapEsc:
    def __init__(self, callback):
        self.callback = callback
        self.tap = None
        self.source = None
        self._rl = None
        self.thread = None
        self._ready = threading.Event()
        self._ok = False

    def start(self):
        if not IS_MAC:
            return False, "Mac only"
        try:
            import Quartz
        except Exception as e:
            return False, str(e)

        def loop():
            try:
                mask = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
                def handler(proxy, type_, event, refcon):
                    try:
                        if type_ == Quartz.kCGEventKeyDown:
                            kc = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
                            if int(kc) == 53:
                                QTimer.singleShot(0, self.callback)
                    except Exception:
                        pass
                    return event
                cb = Quartz.CGEventTapCallBack(handler)
                self.tap = Quartz.CGEventTapCreate(
                    Quartz.kCGHIDEventTap,
                    Quartz.kCGHeadInsertEventTap,
                    Quartz.kCGEventTapOptionListenOnly,
                    mask,
                    cb,
                    None
                )
                self._ok = bool(self.tap)
                self._ready.set()
                if not self.tap:
                    return
                self.source = Quartz.CFMachPortCreateRunLoopSource(None, self.tap, 0)
                self._rl = Quartz.CFRunLoopGetCurrent()
                Quartz.CFRunLoopAddSource(self._rl, self.source, Quartz.kCFRunLoopCommonModes)
                Quartz.CGEventTapEnable(self.tap, True)
                Quartz.CFRunLoopRun()
            except Exception:
                if not self._ready.is_set():
                    self._ok = False
                    self._ready.set()
                pass

        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
        self._ready.wait(1.0)
        if not self._ok:
            return False, "Input Monitoring not granted"
        return True, "OK"

    def stop(self):
        if not IS_MAC:
            return
        try:
            import Quartz
            if self._rl is not None:
                Quartz.CFRunLoopStop(self._rl)
                self._rl = None
            if self.tap:
                Quartz.CGEventTapEnable(self.tap, False)
                self.tap = None
        except Exception:
            pass

# Replacement: Ctrl+Alt+Q hotkey for Windows
class WindowsCtrlAltQHotkey:
    def __init__(self, callback):
        self.callback = callback
        self.thread = None
        self.thread_id = None
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._ok = False

    def start(self):
        if not IS_WIN:
            return False, "Windows only"
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        MOD_ALT = 0x0001
        MOD_CONTROL = 0x0002
        VK_Q = 0x51
        WM_HOTKEY = 0x0312
        HOTKEY_ID = 1
        def loop():
            self.thread_id = kernel32.GetCurrentThreadId()
            ok = user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_Q)
            self._ok = bool(ok)
            self._ready.set()
            if not ok:
                return
            msg = wintypes.MSG()
            while not self._stop.is_set() and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    QTimer.singleShot(0, self.callback)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            user32.UnregisterHotKey(None, HOTKEY_ID)
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
        self._ready.wait(1.0)
        return (self._ok, "OK" if self._ok else "RegisterHotKey failed")

    def stop(self):
        if not IS_WIN:
            return
        try:
            import ctypes
            user32 = ctypes.windll.user32
            WM_QUIT = 0x0012
            self._stop.set()
            if self.thread_id:
                user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
        except Exception:
            pass

# WindowsLLCtrlAltQHook: fallback low-level hook for Ctrl+Alt+Q
class WindowsLLCtrlAltSHook:
    def __init__(self, callback):
        self.callback = callback
        self.hooked = None
        self.thread = None
        self.thread_id = None
        self._stop = threading.Event()
        self.ctrl = False
        self.alt = False
        self._ready = threading.Event()
        self._ok = False

    def start(self):
        if not IS_WIN:
            return False, "Windows only"
        try:
            import ctypes
            from ctypes import wintypes
        except Exception as e:
            return False, str(e)
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        WM_SYSKEYDOWN = 0x0104
        WM_SYSKEYUP = 0x0105
        VK_S = 0x53
        VK_CONTROL = 0x11
        VK_LCONTROL = 0xA2
        VK_RCONTROL = 0xA3
        VK_MENU = 0x12

        ULONG_PTR = getattr(wintypes, "ULONG_PTR", ctypes.c_size_t)
        LRESULT = getattr(wintypes, "LRESULT", ctypes.c_ssize_t)
        WPARAM = getattr(wintypes, "WPARAM", ctypes.c_size_t)
        LPARAM = getattr(wintypes, "LPARAM", ctypes.c_ssize_t)
        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [("vkCode", wintypes.DWORD),
                        ("scanCode", wintypes.DWORD),
                        ("flags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ULONG_PTR)]
        LowLevelKeyboardProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)
        state = self

        @LowLevelKeyboardProc
        def hook_proc(nCode, wParam, lParam):
            try:
                if nCode >= 0:
                    kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    msg = wParam
                    vk = kb.vkCode
                    if msg in (WM_KEYDOWN, WM_SYSKEYDOWN):
                        if vk in (VK_LCONTROL, VK_RCONTROL, VK_CONTROL):
                            state.ctrl = True
                        elif vk == VK_MENU:
                            state.alt = True
                        elif vk == VK_S and state.ctrl and state.alt:
                            QTimer.singleShot(0, state.callback)
                    elif msg in (WM_KEYUP, WM_SYSKEYUP):
                        if vk in (VK_LCONTROL, VK_RCONTROL, VK_CONTROL):
                            state.ctrl = False
                        elif vk == VK_MENU:
                            state.alt = False
            except Exception:
                pass
            return user32.CallNextHookEx(state.hooked, nCode, wParam, lParam)

        self.hook_proc = hook_proc

        def loop():
            self.thread_id = kernel32.GetCurrentThreadId()
            self.hooked = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self.hook_proc, kernel32.GetModuleHandleW(None), 0)
            self._ok = bool(self.hooked)
            self._ready.set()
            if not self.hooked:
                return
            msg = wintypes.MSG()
            while not self._stop.is_set() and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            if self.hooked:
                user32.UnhookWindowsHookEx(self.hooked)
                self.hooked = None

        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
        self._ready.wait(1.0)
        return (self._ok, "OK" if self._ok else "Hook failed")

    def stop(self):
        if not IS_WIN:
            return
        try:
            import ctypes
            user32 = ctypes.windll.user32
            WM_QUIT = 0x0012
            self._stop.set()
            if self.thread_id:
                user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
        except Exception:
            pass

class WindowsGlobalEsc:
    def __init__(self, callback):
        self.callback = callback
        self.hooked = None
        self.thread = None
        self.thread_id = None
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._ok = False

    def start(self):
        if not IS_WIN:
            return False, "Windows only"
        try:
            import ctypes
            from ctypes import wintypes
        except Exception as e:
            return False, str(e)
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_SYSKEYDOWN = 0x0104
        VK_ESCAPE = 0x1B

        ULONG_PTR = getattr(wintypes, "ULONG_PTR", ctypes.c_size_t)
        LRESULT = getattr(wintypes, "LRESULT", ctypes.c_ssize_t)
        WPARAM = getattr(wintypes, "WPARAM", ctypes.c_size_t)
        LPARAM = getattr(wintypes, "LPARAM", ctypes.c_ssize_t)
        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [("vkCode", wintypes.DWORD),
                        ("scanCode", wintypes.DWORD),
                        ("flags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ULONG_PTR)]
        LowLevelKeyboardProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)

        @LowLevelKeyboardProc
        def hook_proc(nCode, wParam, lParam):
            try:
                if nCode >= 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
                    kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    if kb.vkCode == VK_ESCAPE:
                        QTimer.singleShot(0, self.callback)
            except Exception:
                pass
            return user32.CallNextHookEx(self.hooked, nCode, wParam, lParam)

        self.hook_proc = hook_proc

        def loop():
            self.thread_id = kernel32.GetCurrentThreadId()
            self.hooked = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self.hook_proc, kernel32.GetModuleHandleW(None), 0)
            self._ok = bool(self.hooked)
            self._ready.set()
            if not self.hooked:
                return
            msg = wintypes.MSG()
            while not self._stop.is_set() and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            if self.hooked:
                user32.UnhookWindowsHookEx(self.hooked)
                self.hooked = None

        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
        self._ready.wait(1.0)
        return (self._ok, "OK" if self._ok else "Hook failed")

# --- WindowsPynputCtrlAltQ ---

class WindowsPynputCtrlAltS:
    def __init__(self, callback):
        self.callback = callback
        self.listener = None
        self.ctrl = False
        self.alt = False
    def start(self):
        if not IS_WIN or pynput_keyboard is None:
            return False, "Unavailable"
        def on_press(key):
            try:
                if key in (pynput_keyboard.Key.ctrl, pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r):
                    self.ctrl = True
                elif key in (pynput_keyboard.Key.alt, pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r):
                    self.alt = True
                elif isinstance(key, pynput_keyboard.KeyCode) and key.char and key.char.lower() == 's' and self.ctrl and self.alt:
                    QTimer.singleShot(0, self.callback)
            except Exception:
                pass
        def on_release(key):
            try:
                if key in (pynput_keyboard.Key.ctrl, pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r):
                    self.ctrl = False
                elif key in (pynput_keyboard.Key.alt, pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r):
                    self.alt = False
            except Exception:
                pass
        try:
            self.listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release, suppress=False)
            self.listener.daemon = True
            self.listener.start()
            return True, "OK"
        except Exception as e:
            return False, str(e)
    def stop(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None


# --- WinHotkeyFilter for native event handling on Windows ---
class WinHotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    def nativeEventFilter(self, eventType, message):
        try:
            if eventType not in (b"windows_generic_MSG", b"windows_dispatcher_MSG"):
                return False, 0
            import ctypes
            from ctypes import wintypes
            class POINT(ctypes.Structure):
                _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
            class MSG(ctypes.Structure):
                _fields_ = [("hwnd", wintypes.HWND),
                            ("message", wintypes.UINT),
                            ("wParam", wintypes.WPARAM),
                            ("lParam", wintypes.LPARAM),
                            ("time", wintypes.DWORD),
                            ("pt", POINT)]
            msg = MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == 1:
                QTimer.singleShot(0, self.callback)
            return False, 0
        except Exception:
            return False, 0

class GradientWidget(QWidget):
    def paintEvent(self, evt):
        painter = QPainter(self)
        base = QLinearGradient(0, 0, 0, self.height())
        base.setColorAt(0.0, QColor("#0f172a"))
        base.setColorAt(0.5, QColor("#1e3a8a"))
        base.setColorAt(1.0, QColor("#1d4ed8"))
        painter.fillRect(self.rect(), base)
        from PySide6.QtGui import QRadialGradient
        highlight = QRadialGradient(self.width()/2, self.height()*0.08, self.height()*0.7)
        highlight.setColorAt(0.0, QColor(255,255,255,38))
        highlight.setColorAt(1.0, QColor(255,255,255,0))
        painter.fillRect(self.rect(), highlight)
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

class SigninDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bing sign-in")
        self.setModal(True)
        self.logged_in = None

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
        self.chk.setStyleSheet(
            """
            QCheckBox { color:#e6f0ff; }
            QCheckBox::indicator { width:16px; height:16px; }
            """
        )
        self.chk.setCursor(Qt.PointingHandCursor)

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
        btn_yes.clicked.connect(lambda: (setattr(self, "logged_in", True),  self.accept()))
        btn_no.clicked.connect(lambda: (setattr(self, "logged_in", False), self.accept()))

        row = QHBoxLayout(); row.setSpacing(8)
        row.addStretch(1); row.addWidget(btn_yes); row.addWidget(btn_no); row.addStretch(1)

        frame = QFrame(); frame.setObjectName("dlgcard")
        frame.setStyleSheet("QFrame#dlgcard { background: rgba(10,16,28,230); border-radius: 14px; }")
        inner = QVBoxLayout(frame); inner.setContentsMargins(16, 14, 16, 14); inner.setSpacing(10)
        inner.addWidget(title)
        inner.addWidget(sub)
        inner.addWidget(self.chk, 0, Qt.AlignHCenter)
        inner.addLayout(row)

        wrap.addWidget(frame)
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint, True)
        self.setFixedSize(self.sizeHint())

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Bing Search")
        ip = get_app_icon_path()
        if ip:
            self.setWindowIcon(QIcon(ip))
            if IS_WIN:
                try:
                    _win_set_window_icons(int(self.winId()), ip)
                except Exception:
                    pass
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.resize(540, 270)
        self.setMinimumSize(520, 264)

        self.worker: SearchWorker | None = None
        self.countdown_timer = QTimer(self); self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self._tick_countdown)
        self.countdown_left = 0
        self.is_pinned = False
        self.count_target = 30

        self.bg = GradientWidget()
        self.setCentralWidget(self.bg)

        self.global_esc = None

        self._win_hotkey_filter = None
        self._HOTKEY_ID = 1

        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.on_stop)

        root = QVBoxLayout(self.bg); root.setContentsMargins(18, 12, 18, 12); root.setSpacing(8)

        self.title_label = TitleLabel("Auto Bing Search")
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

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

        self.left = QWidget(); self.right = QWidget()
        left_lay = QHBoxLayout(self.left); left_lay.setContentsMargins(0,0,0,0); left_lay.setSpacing(0)
        right_lay = QHBoxLayout(self.right); right_lay.setContentsMargins(0,0,0,0); right_lay.setSpacing(0)

        if IS_WIN:
            left_lay.addWidget(self.pin_btn, 0, Qt.AlignLeft | Qt.AlignVCenter)
            self.remember_chk = QCheckBox()
            self.remember_chk.setObjectName("rememberTop")
            self.remember_chk.setToolTip("Remember login choice")
            self.remember_chk.setCursor(Qt.PointingHandCursor)
            self.remember_chk.setFixedSize(36, 36)
            self.remember_chk.setStyleSheet("""
                QCheckBox#rememberTop { background: rgba(0,0,0,90); border-radius: 10px; }
                QCheckBox#rememberTop::indicator { width:18px; height:18px; margin:9px; border-radius:4px;
                    border:1px solid rgba(255,255,255,70); background: rgba(255,255,255,16); }
                QCheckBox#rememberTop::indicator:hover { background: rgba(255,255,255,28); }
                QCheckBox#rememberTop::indicator:checked {
                    border:1px solid #8be9a5;
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #34d399, stop:1 #0ea472);
                }
            """)
            right_lay.addWidget(self.remember_chk, 0, Qt.AlignRight | Qt.AlignVCenter)
        else:
            self.remember_chk = QCheckBox()
            self.remember_chk.setObjectName("rememberTop")
            self.remember_chk.setToolTip("Remember login choice")
            self.remember_chk.setCursor(Qt.PointingHandCursor)
            self.remember_chk.setFixedSize(36, 36)
            self.remember_chk.setStyleSheet("""
                QCheckBox#rememberTop { background: rgba(0,0,0,90); border-radius: 10px; }
                QCheckBox#rememberTop::indicator { width:18px; height:18px; margin:9px; border-radius:4px;
                    border:1px solid rgba(255,255,255,70); background: rgba(255,255,255,16); }
                QCheckBox#rememberTop::indicator:hover { background: rgba(255,255,255,28); }
                QCheckBox#rememberTop::indicator:checked {
                    border:1px solid #8be9a5;
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #34d399, stop:1 #0ea472);
                }
            """)
            left_lay.addWidget(self.remember_chk, 0, Qt.AlignLeft | Qt.AlignVCenter)
            right_lay.addWidget(self.pin_btn, 0, Qt.AlignRight | Qt.AlignVCenter)

        topbar = QHBoxLayout(); topbar.setContentsMargins(0,0,0,0); topbar.setSpacing(1)
        topbar.addWidget(self.left, 0, Qt.AlignVCenter)
        topbar.addWidget(self.title_label, 1, Qt.AlignVCenter)
        topbar.addWidget(self.right, 0, Qt.AlignVCenter)
        root.addLayout(topbar)

        settings_top = QSettings("AutoBingSearch", "App")
        remember_state = settings_top.value("remember_choice", "1")
        self.remember_chk.setChecked(str(remember_state).lower() in ("1","true","yes"))
        self.remember_chk.stateChanged.connect(
            lambda _: settings_top.setValue("remember_choice", "1" if self.remember_chk.isChecked() else "0")
        )

        QTimer.singleShot(0, self._balance_side_widths)

        self.countdown = QLabel("")
        cf = QFont(); cf.setPointSize(12); cf.setWeight(QFont.Weight.DemiBold)
        self.countdown.setFont(cf)
        self.countdown.setStyleSheet("color:#eaf2ff;")
        root.addWidget(self.countdown, alignment=Qt.AlignHCenter)

        self.card = Card()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(12)

        center_wrap = QWidget()
        center_v = QVBoxLayout(center_wrap)
        center_v.setContentsMargins(0, 0, 0, 0)
        center_v.setSpacing(6)

        self.stepper = Stepper(minimum=1, maximum=2000, value=self.count_target, step=1)
        self.stepper.setMaximumWidth(220)
        self.stepper.valueChanged.connect(self._on_stepper_changed)
        center_v.addWidget(self.stepper, 0, Qt.AlignHCenter)

        self.remaining_center = PillLabel("Remaining: 0")
        self.remaining_center.hide()
        center_v.addWidget(self.remaining_center, 0, Qt.AlignHCenter)

        card_layout.addWidget(center_wrap, 0, Qt.AlignHCenter)

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
        hint_text = "Press Ctrl+Alt+S to stop" if IS_WIN else "Press Esc to stop"
        hint = HintLabel(hint_text)
        hint.setAlignment(Qt.AlignHCenter)
        root.addWidget(hint, alignment=Qt.AlignHCenter)

        self._set_state_idle()

        if IS_MAC:
            self._show_mac_permissions_once()
        else:
            ok, msg = wl_preflight()
            if not ok and IS_LINUX:
                self._ensure_linux_requirements(msg)
            elif not ok:
                QMessageBox.critical(self, "Permission required", msg)

        if self.global_esc is None:
            if IS_MAC:
                try:
                    self.global_esc = MacEventTapEsc(self.on_stop)
                    esc_ok, esc_msg = self.global_esc.start()
                except Exception:
                    esc_ok, esc_msg = False, "event tap failed"
                if not esc_ok and NSEvent is not None:
                    self.global_esc = MacGlobalEsc(self.on_stop)
                    esc_ok, esc_msg = self.global_esc.start()
                if not esc_ok:
                    self.global_esc = GlobalEsc(self.on_stop)
                    esc_ok, esc_msg = self.global_esc.start()
            elif IS_WIN:
                self.global_esc = None
            else:
                self.global_esc = GlobalEsc(self.on_stop)
                esc_ok, esc_msg = self.global_esc.start()

        self._win_hotkey_registered = False
        if IS_WIN:
            QTimer.singleShot(0, self._init_win_hotkey)

        self.adjustSize()
        self.setFixedSize(self.size())


    def _init_win_hotkey(self):
        ok = self._setup_win_hotkey()
        if ok:
            return
        try:
            self.global_esc = WindowsLLCtrlAltSHook(self.on_stop)
            esc_ok, _ = self.global_esc.start()
            if not esc_ok and pynput_keyboard is not None:
                self.global_esc = WindowsPynputCtrlAltS(self.on_stop)
                self.global_esc.start()
        except Exception:
            pass

    def _setup_win_hotkey(self):
        if not IS_WIN:
            return False
        try:
            import ctypes
            from ctypes import wintypes
            self._win_hotkey_filter = WinHotkeyFilter(self.on_stop)
            QAbstractEventDispatcher.instance().installNativeEventFilter(self._win_hotkey_filter)
            user32 = ctypes.windll.user32
            MOD_ALT = 0x0001
            MOD_CONTROL = 0x0002
            VK_S = 0x53
            ok = user32.RegisterHotKey(wintypes.HWND(int(self.winId())), self._HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_S)
            self._win_hotkey_registered = bool(ok)
            return self._win_hotkey_registered
        except Exception:
            self._win_hotkey_filter = None
            self._win_hotkey_registered = False
            return False

    def _show_mac_permissions_once(self):
        settings = QSettings("AutoBingSearch", "App")
        if settings.value("mac_perm_prompt_shown", "0") == "1":
            return
        while True:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle("Setup macOS permissions")
            box.setText("Enable Accessibility, Input Monitoring, and Automation for your Terminal/VS Code or the packaged app in System Settings → Privacy & Security.")
            btn_acc = box.addButton("Open Accessibility", QMessageBox.ActionRole)
            btn_inp = box.addButton("Open Input Monitoring", QMessageBox.ActionRole)
            btn_auto = box.addButton("Open Automation", QMessageBox.ActionRole)
            btn_done = box.addButton("Done", QMessageBox.AcceptRole)
            box.exec()
            if box.clickedButton() is btn_acc:
                mac_open_accessibility()
                continue
            if box.clickedButton() is btn_inp:
                mac_open_input_monitoring()
                continue
            if box.clickedButton() is btn_auto:
                mac_open_automation()
                continue
            settings.setValue("mac_perm_prompt_shown", "1")
            break

    def _ensure_linux_requirements(self, msg):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Automation requirements")
        box.setText(msg)
        box.addButton("OK", QMessageBox.AcceptRole)
        box.exec()

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

    def _set_state_idle(self):
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_stop.hide()
        self.remaining_center.setText("Remaining: 0")
        self.remaining_center.hide()
        self.stepper.show()
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

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.on_stop()
        else:
            super().keyPressEvent(e)

    def closeEvent(self, e):
        # Ensure worker is stopped/joined and hotkeys are cleaned up
        try:
            self.on_stop()
        finally:
            try:
                if getattr(self, "global_esc", None):
                    self.global_esc.stop()
            finally:
                if IS_WIN:
                    try:
                        import ctypes
                        from ctypes import wintypes
                        user32 = ctypes.windll.user32
                        user32.UnregisterHotKey(wintypes.HWND(int(self.winId())), self._HOTKEY_ID)
                    except Exception:
                        pass
                    try:
                        if getattr(self, "_win_hotkey_filter", None):
                            QAbstractEventDispatcher.instance().removeNativeEventFilter(self._win_hotkey_filter)
                    except Exception:
                        pass
                super().closeEvent(e)

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_pinned)
        self.show()
        pinned_bg = "background: rgba(40,160,95,0.45);" if self.is_pinned else "background: rgba(0,0,0,90);"
        self.pin_btn.setStyleSheet(
            f"""
            QPushButton {{ color:{'#eaffef' if self.is_pinned else '#ffffff'}; {pinned_bg}
                           border: 1px solid {'#8be9a5' if self.is_pinned else 'transparent'};
                           border-radius: 10px; font-size:18px; }}
            QPushButton:hover {{ background: rgba(255,255,255,40); }}
            QPushButton:pressed {{ background: rgba(0,0,0,140); }}
            """
        )
        self.pin_btn.setToolTip("Unpin window" if self.is_pinned else "Pin on top")

    def _on_stepper_changed(self, v):
        self.count_target = int(v)

    def _balance_side_widths(self):
        self.left.adjustSize(); self.right.adjustSize()
        w = max(self.left.sizeHint().width(), self.right.sizeHint().width())
        w = min(max(w, 36), 84)
        self.left.setFixedWidth(w)
        self.right.setFixedWidth(w)

    def _update_remaining(self, left):
        self.remaining_center.setText(f"Remaining: {left}")
        QTimer.singleShot(0, self._balance_side_widths)

    def on_start(self):
        force_prompt = bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)
        settings = QSettings("AutoBingSearch", "App")

        remember_ui = self.remember_chk.isChecked()
        pref = settings.value("assume_logged_in", None)

        need_prompt = force_prompt or (not remember_ui) or (pref is None)

        if need_prompt:
            dlg = SigninDialog(self)
            dlg.setStyleSheet("background: transparent;")
            dlg.chk.setChecked(remember_ui)

            if dlg.exec() == QDialog.Accepted:
                remember_choice = dlg.chk.isChecked() or remember_ui
                settings.setValue("remember_choice", "1" if remember_choice else "0")
                self.remember_chk.setChecked(remember_choice)

                if remember_choice:
                    settings.setValue("assume_logged_in", "yes" if dlg.logged_in else "no")

                if not dlg.logged_in:
                    open_browser(prefer_edge=True, url=BING_SIGNIN)
                    return
            else:
                return
        else:
            if str(pref).lower() not in ("yes", "true", "1"):
                open_browser(prefer_edge=True, url=BING_SIGNIN)
                return

        if not random_words:
            QMessageBox.warning(self, "No words", "Your random_words list is empty."); return

        start_left = min(self.count_target, len(random_words))
        self.remaining_center.setText(f"Remaining: {start_left}")
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
        self._set_state_running()
        self.stepper.hide()
        self.remaining_center.show()

        self.worker = SearchWorker(random_words, count)
        self.worker.progress.connect(self._update_remaining)
        self.worker.error.connect(lambda m: QMessageBox.critical(self, "Automation error", m))
        self.worker.done.connect(self._on_done)
        self.worker.start()

    def on_pause(self):
        if not self.worker: return
        self.worker.toggle_pause()
        if self.btn_pause.isVisible():
            self._set_state_paused()
        else:
            self._set_state_running()

    def on_stop(self):
        # Stop countdown if pending
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
            self.countdown.setText("")
        # Stop and join worker if running
        if self.worker:
            try:
                self.worker.stop()
                if self.worker.isRunning():
                    self.worker.wait(5000)
            finally:
                self.worker = None
        # Reset UI to idle
        self.stepper.show()
        self.remaining_center.hide()
        self._set_state_idle()

    def _on_done(self):
        self.stepper.show()
        self.remaining_center.hide()
        self._set_state_idle()
        self.worker = None

def main():
    if IS_WIN:
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
        except Exception:
            pass
    app = QApplication(sys.argv)
    ip = get_app_icon_path()
    if ip:
        app.setWindowIcon(QIcon(ip))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
