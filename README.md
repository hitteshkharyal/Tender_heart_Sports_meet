# Tender_heart_Sports_meet
## Sports Meet 2026 – Smart Guest Greeter & Crowd Counter
### Tender Heart School

A modern **Streamlit Web Dashboard** and computer vision application for stadium entrance displays, event TVs, and projectors. Powered by **YOLOv8** person detection, privacy-preserving duplicate prevention, and background offline text-to-speech voice announcements.

---

## What's New in the Streamlit UI & UX

- **Sleek Modern Web Dashboard**: Responsive dark navy athletic stadium theme with royal blue cards, radiant championship gold metrics, and emerald status badges.
- **YOLOv8 Person Detection**: High-accuracy real-time attendee detection (with automatic OpenCV HOG fallback).
- **Dynamic Time-Based Greetings**:
  - **5:00 AM – 11:59 AM**: `Good Morning!  •  WELCOME TO SPORTS MEET 2026!`
  - **12:00 PM – 4:59 PM**: `Good Afternoon!  •  WELCOME TO SPORTS MEET 2026!`
  - **5:00 PM – 4:59 AM**:  `Good Evening!  •  WELCOME TO SPORTS MEET 2026!`
- **Live Metrics**:
  - **Total Guests Welcomed Today** (large gold counter).
  - **In View Now** (attendees currently standing in front of the camera).
  - **Crowd Status** (CALM, LIVELY, BUSY, PACKED) with colored level indicators.
  - **Recent Influx** (+X in last 10 minutes).
  - **Arrivals Trend (Last 60 Minutes)** (interactive hourly distribution chart).
- **Celebratory Welcome Alerts**:
  - Whenever a new visitor enters, a prominent welcome card and celebratory balloon burst appear:
    - `WELCOME TO SPORTS MEET 2026!`
    - `WE ARE HAPPY TO HAVE YOU HERE!`
    - `GUEST #<TOTAL>`
- **Offline Voice Announcements**:
  - Speaks *"Welcome to Sports Meet 2026! We are happy to have you here!"* in a non-blocking background thread via Windows SAPI5 (`pyttsx3`).
- **Interactive Sidebar Controls**:
  - Toggle live camera on/off.
  - Switch camera source (built-in webcam `0`, external USB camera `1`, or demo clip).
  - Toggle voice announcements and detection bounding boxes.
  - Test Welcome button (simulates guest arrival, alert, and spoken welcome).
  - Manual count adjusters (+1 / -1) and reset with confirmation.
  - Purge temporary Re-ID identity cache.

---

## One-Command Startup

### Windows Launcher
Double-click or run from Command Prompt / PowerShell:
```powershell
.\run_windows.bat
```

### Manual Command
```powershell
python -m streamlit run app.py
```

---

## Project Structure

```
├── app.py                # Glassmorphism Single-Screen Web Dashboard
├── config.py             # Branding, dynamic time greetings & settings
├── detector.py           # YOLOv8 Person Detector (with OpenCV HOG fallback)
├── tracker.py            # HSV Multi-zone Re-ID & Duplicate Prevention Tracker
├── stats.py              # Persistent attendance metrics and arrival timestamps
├── voice.py              # Non-blocking background Windows SAPI5 voice engine
├── requirements.txt      # Dependencies (Streamlit, Ultralytics, OpenCV, pyttsx3)
├── run_windows.bat       # Windows batch launcher
├── yolov8n.pt            # YOLOv8 nano model weights
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── data/
    └── visitor_count.json # Daily attendance JSON store
```
