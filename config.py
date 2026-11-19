"""
=====================================================================
  SPORTS MEET 2026 - SMART GUEST GREETER & CROWD COUNTER
  Tender Heart School
  ---------------------------------------------------------------
  Configuration settings for UI, Detection, Tracking, Voice, and Stats.
=====================================================================
"""
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- Branding ----------------
SCHOOL_NAME = "TENDER HEART SCHOOL"
EVENT_TITLE = "SPORTS MEET 2026"
TAGLINE = "Play Fair  •  Play Hard  •  Play Together"

# Primary welcome messages (shown prominently)
WELCOME_HEADLINE = "WELCOME TO SPORTS MEET 2026!"
WELCOME_SUBHEAD = "WE ARE HAPPY TO HAVE YOU HERE!"

# Rotating event announcements & sports spirit messages
ROTATING_MESSAGES = [
    "Welcome parents, guests, and athletes to Sports Meet 2026!",
    "Tender Heart School welcomes you to an extraordinary day of sport!",
    "Cheer loud, cheer proud for every champion on the field!",
    "Faster  •  Higher  •  Stronger  •  Together",
    "Drinking water, refreshments, and first aid available near Pavilions A & B.",
    "Every champion was once a beginner. Celebrate their effort and spirit!",
    "Please take your seats in the visitors' gallery and enjoy the games!",
]

# Text scrolling across the bottom ticker
TICKER_TEXT = (
    "WELCOME TO SPORTS MEET 2026   ★   TENDER HEART SCHOOL   ★   "
    "PLEASE TAKE YOUR SEATS IN THE VISITORS' GALLERY   ★   "
    "FIRST AID & REFRESHMENTS AT PAVILION B   ★   "
    "FAIR PLAY, RESPECT, AND EXCELLENCE FOR ALL ATHLETES   ★   "
    "THANK YOU FOR JOINING US TODAY!   ★   "
)


# ---------------- Timezone (India Standard Time: GMT +5:30) ----------------
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30), name="IST")


def get_ist_now():
    """Returns current datetime in Indian Standard Time (GMT +5:30)."""
    return datetime.datetime.now(IST)


def get_time_greeting(hour=None):
    """
    Returns time-based greeting according to Indian Standard Time (IST):
      - 5:00 AM to 11:59 AM: Good Morning!
      - 12:00 PM to 4:59 PM: Good Afternoon!
      - 5:00 PM to 4:59 AM:  Good Evening!
    """
    if hour is None:
        hour = get_ist_now().hour
    if 5 <= hour < 12:
        return "Good Morning!"
    elif 12 <= hour < 17:
        return "Good Afternoon!"
    else:
        return "Good Evening!"


# ---------------- Voice / Text-to-Speech ----------------
ENABLE_VOICE = True            # Offline TTS via pyttsx3 (SAPI5 on Windows)
VOICE_RATE = 155               # Spoken speed (words per minute, natural tempo)
VOICE_VOLUME = 1.0             # Volume 0.0 - 1.0
VOICE_COOLDOWN = 3.0           # Minimum seconds between spoken welcomes
PLAY_SOUND = True              # Optional pleasant chime alongside voice

# ---------------- Camera / Video Feed ----------------
# 0 = built-in webcam, 1 = second (USB) camera,
# or a path / URL, e.g. "demo.mp4" or "rtsp://..."
CAMERA_SOURCE = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
MIRROR_CAMERA = False          # Flip horizontally (helpful for front-facing gate cameras)
LOOP_VIDEO_FILE = True         # Replay video file if using demo clip
CAMERA_RETRY_INTERVAL = 2.5    # Seconds between reconnect attempts when disconnected

# ---------------- Detection ----------------
# "auto" -> YOLO if 'ultralytics' is installed, otherwise OpenCV HOG
# "yolo" -> force YOLO (recommended)
# "hog"  -> force OpenCV HOG (built-in, lightweight)
DETECTOR = "auto"
YOLO_MODEL = os.path.join(BASE_DIR, "yolov8n.pt")
CONFIDENCE = 0.45
DETECT_EVERY_N_FRAMES = 1      # Raise to 2 or 3 on low-power devices

# ---------------- Counting & Tracking ----------------
# "unique" -> Person counted once when entering & seen for MIN_FRAMES_TO_COUNT frames.
# "line"   -> Person counted when their path crosses the virtual entry line.
COUNT_MODE = "unique"
MIN_FRAMES_TO_COUNT = 6
LINE_ORIENTATION = "horizontal"  # "horizontal" or "vertical"
LINE_POSITION = 0.55             # 0.0 - 1.0 across frame
ENTRY_DIRECTION = "down"         # horizontal: "down"/"up"; vertical: "right"/"left"

# Tracker & Duplicate Prevention Tuning
MAX_DISAPPEARED = 45             # Retain lost track for 45 frames (~1.8s) to survive occlusions
MAX_DISTANCE = 150               # Max centroid pixel jump between frames
IOU_THRESHOLD = 0.25             # Bounding box IoU overlap weighting

# Local Appearance-Based Person Re-Identification (Re-ID)
REID_ENABLED = True              # Compare multi-zone color histogram against recently counted guests
REID_SIMILARITY_THRESHOLD = 0.80 # High confidence threshold (0.0 to 1.0, higher = stricter)
REID_MEMORY_SECONDS = 180        # Retain appearance profile of departed guests for 3 minutes

# ---------------- Crowd Level Indicators ----------------
# (minimum people in view, label, RGB colour)
CROWD_LEVELS = [
    (0, "CALM", (0, 212, 190)),       # Teal
    (4, "LIVELY", (255, 200, 0)),     # Gold
    (9, "BUSY", (255, 130, 45)),      # Amber Orange
    (15, "PACKED!", (255, 60, 120)),  # Vivid Coral Red
]

# ---------------- Display & Theme ----------------
START_FULLSCREEN = True
SHOW_DETECTION_BOXES = True
POPUP_SECONDS = 3.4
CONFETTI = True

# Professional Sports Theme Palette (RGB)
NAVY_BG_TOP = (8, 14, 32)
NAVY_BG_BOTTOM = (14, 24, 52)
CARD_BG = (16, 26, 56)
CARD_BORDER = (35, 75, 160)
ROYAL_BLUE = (25, 95, 210)
GOLD = (255, 215, 0)
GOLD_LIGHT = (255, 240, 150)
WHITE = (255, 255, 255)
SOFT_BLUE = (180, 200, 235)
TEAL_GREEN = (0, 220, 130)
ALERT_RED = (235, 50, 60)

# ---------------- Persistence ----------------
SAVE_FILE = os.path.join(BASE_DIR, "data", "visitor_count.json")
RESET_COUNT_EACH_DAY = True      # Start from 0 on a new date (resumes if same date)
