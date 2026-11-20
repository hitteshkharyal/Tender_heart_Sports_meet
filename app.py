"""
=====================================================================
  SPORTS MEET 2026 - SMART GUEST GREETER & CROWD COUNTER
  Glassmorphism Single-Screen Dashboard  |  Tender Heart School
=====================================================================
"""
import datetime
import os
import sys
import threading
import time

import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoProcessorBase
    import av
    HAS_WEBRTC = True
except Exception:
    HAS_WEBRTC = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C
from detector import PersonDetector
from stats import VisitorStats
from tracker import CentroidTracker
from voice import VoiceGreeter

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Sports Meet 2026 - Smart Greeter",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== GLASSMORPHISM PROFESSIONAL STYLING ====================
st.markdown("""
<style>
    /* Hide Streamlit default menu, footer, and toolbar while keeping sidebar active */
    #MainMenu, footer, [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Floating gold collapse/expand sidebar controller */
    [data-testid="collapsedControl"] {
        display: flex !important;
        background: rgba(15, 25, 54, 0.9) !important;
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
        border-radius: 8px !important;
        color: #ffd700 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
        top: 0.6rem !important;
        left: 0.6rem !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"]:hover {
        background: rgba(37, 99, 235, 0.7) !important;
        border-color: #ffd700 !important;
    }

    /* Ambient Sports Stadium Background with Luminous Lighting */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background: #060b19 !important;
    }

    [data-testid="stAppViewContainer"], .main {
        background: 
            radial-gradient(circle at 12% 15%, rgba(37, 99, 235, 0.22) 0%, transparent 45%),
            radial-gradient(circle at 88% 18%, rgba(255, 215, 0, 0.14) 0%, transparent 42%),
            radial-gradient(circle at 50% 95%, rgba(0, 220, 130, 0.12) 0%, transparent 55%),
            #060b19 !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        overflow: hidden !important;
    }

    /* Single-Screen Viewport Container with Zero Scroll */
    .main .block-container {
        padding: 0.45rem 1.1rem 0.35rem 1.1rem !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }

    /* Glassmorphism Header Bar */
    .glass-hdr {
        background: rgba(14, 24, 56, 0.65);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-top: 1px solid rgba(255, 255, 255, 0.28);
        border-radius: 12px;
        padding: 6px 18px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .event-title-text {
        margin: 0;
        font-size: 24px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 0.5px;
        text-shadow: 0 0 14px rgba(59, 130, 246, 0.7);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .school-badge {
        background: linear-gradient(135deg, #ffd700 0%, #f59e0b 100%);
        color: #060a1a;
        font-size: 18px;
        font-weight: 900;
        padding: 4px 14px;
        border-radius: 8px;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        box-shadow: 0 2px 12px rgba(245, 158, 11, 0.5);
    }
    
    .clock-text {
        color: #ffffff;
        font-size: 21px;
        font-weight: 800;
        font-variant-numeric: tabular-nums;
        text-align: right;
        margin: 0;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
    }
    
    .date-text {
        color: #ffd700;
        font-size: 11px;
        font-weight: 600;
        margin: 0;
        text-align: right;
    }

    /* Glassmorphism Greeting Pill */
    .glass-greet {
        background: linear-gradient(90deg, rgba(30, 58, 138, 0.55) 0%, rgba(37, 99, 235, 0.42) 50%, rgba(30, 58, 138, 0.55) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 215, 0, 0.45);
        border-radius: 8px;
        padding: 3px 14px;
        margin-bottom: 5px;
        text-align: center;
        color: #ffd700;
        font-size: 13px;
        font-weight: 700;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }

    /* Glassmorphism Card Panels */
    .glass-card {
        background: rgba(15, 25, 54, 0.62);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-top: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 12px;
        padding: 8px 14px;
        margin-bottom: 5px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .card-label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1px;
    }
    
    .card-number {
        font-weight: 900;
        line-height: 1.05;
        margin: 2px 0;
    }
    
    .card-sub {
        color: #64748b;
        font-size: 11px;
        margin: 0;
    }

    /* Glassmorphism Video Viewport */
    [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    [data-testid="stImage"] img,
    div[data-testid="stWebRtc"] video,
    video {
        width: 100% !important;
        max-height: 520px !important;
        object-fit: contain !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.28) !important;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5) !important;
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
    }

    /* Glassmorphism Welcome Banner */
    .glass-popup {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(23, 37, 84, 0.85) 100%);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 2px solid #ffd700;
        border-radius: 12px;
        padding: 8px 16px;
        text-align: center;
        margin-bottom: 4px;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.4);
    }
    
    .popup-title-text {
        color: #ffd700;
        font-size: 18px;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    
    .popup-sub-text {
        color: #00dc82;
        font-size: 14px;
        font-weight: 800;
        margin: 2px 0 3px 0;
    }
    
    .popup-badge-pill {
        display: inline-block;
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        color: #ffffff;
        font-size: 13px;
        font-weight: 800;
        padding: 2px 14px;
        border-radius: 12px;
        border: 1px solid #ffd700;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.5);
    }

    /* Glassmorphism Buttons */
    div.stButton > button {
        background: rgba(18, 30, 66, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.28) !important;
        color: #e2e8f0 !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        padding: 4px 8px !important;
        font-size: 12px !important;
        height: 36px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    
    div.stButton > button:hover {
        background: rgba(37, 99, 235, 0.5) !important;
        border-color: #ffd700 !important;
        color: #ffd700 !important;
        box-shadow: 0 0 18px rgba(255, 215, 0, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    iframe[title="streamlit_components_html.html"],
    div[data-testid="stCustomComponentV1"] {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Modern Glassmorphic Dark Sidebar (Visible in Normal & Fullscreen Mode) */
    section[data-testid="stSidebar"],
    :fullscreen section[data-testid="stSidebar"],
    :-webkit-full-screen section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        background: #080f26 !important;
        border-right: 1px solid rgba(255, 215, 0, 0.3) !important;
        z-index: 1000000 !important;
    }
    section[data-testid="stSidebar"] > div {
        overflow-y: auto !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.6rem !important;
    }

    /* All text inside sidebar is white and clear */
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #ffd700 !important;
        font-weight: 800 !important;
        font-size: 12px !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
    }

    /* Radio buttons in sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: rgba(18, 30, 66, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        margin-bottom: 4px !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(37, 99, 235, 0.35) !important;
        border-color: #ffd700 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] p {
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    /* Selectbox in sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background: rgba(18, 30, 66, 0.95) !important;
        border: 1px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 8px !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    /* Checkbox in sidebar */
    section[data-testid="stSidebar"] label[data-testid="stCheckbox"] span {
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    /* Keep Sidebar Toggle Button visible in Fullscreen */
    [data-testid="collapsedControl"],
    :fullscreen [data-testid="collapsedControl"],
    :-webkit-full-screen [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        background: rgba(15, 25, 54, 0.95) !important;
        border: 1px solid rgba(255, 215, 0, 0.6) !important;
        border-radius: 8px !important;
        color: #ffd700 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6) !important;
        top: 0.6rem !important;
        left: 0.6rem !important;
        z-index: 10000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Native HTML5 Fullscreen Controller
components.html("""
<script>
(function() {
    function setupFullscreen() {
        try {
            var doc = window.parent.document;
            var buttons = doc.querySelectorAll('button');
            buttons.forEach(function(btn) {
                if (btn.textContent && (btn.textContent.indexOf('Fullscreen') !== -1 || btn.textContent.indexOf('⛶') !== -1)) {
                    if (!btn.getAttribute('data-fs-ready')) {
                        btn.setAttribute('data-fs-ready', 'true');
                        btn.addEventListener('click', function(e) {
                            try {
                                if (!doc.fullscreenElement && !doc.webkitFullscreenElement) {
                                    var el = doc.documentElement;
                                    if (el.requestFullscreen) {
                                        el.requestFullscreen();
                                    } else if (el.webkitRequestFullscreen) {
                                        el.webkitRequestFullscreen();
                                    } else if (el.msRequestFullscreen) {
                                        el.msRequestFullscreen();
                                    }
                                } else {
                                    if (doc.exitFullscreen) {
                                        doc.exitFullscreen();
                                    } else if (doc.webkitExitFullscreen) {
                                        doc.webkitExitFullscreen();
                                    } else if (doc.msExitFullscreen) {
                                        doc.msExitFullscreen();
                                    }
                                }
                            } catch(err) {
                                console.log('Fullscreen error:', err);
                            }
                        }, true);
                    }
                }
            });
        } catch(e) {}
    }
    setupFullscreen();
    setInterval(setupFullscreen, 500);

    try {
        var doc = window.parent.document;
        if (!doc._fsListenerAttached) {
            doc._fsListenerAttached = true;
            doc.addEventListener('fullscreenchange', function() {
                var isFs = !!(doc.fullscreenElement || doc.webkitFullscreenElement);
                var btn = doc.querySelector('button[data-fs-ready="true"]');
                if (btn) {
                    var p = btn.querySelector('p') || btn;
                    p.textContent = isFs ? '🗗 Exit Fullscreen' : '⛶ Fullscreen';
                }
            });
        }
    } catch(e) {}
})();
</script>
""", height=0)


# ==================== SINGLETON BACK-END SERVICES ====================
@st.cache_resource
def _init_services():
    s = VisitorStats(C.SAVE_FILE, reset_daily=C.RESET_COUNT_EACH_DAY)
    t = CentroidTracker(
        max_disappeared=C.MAX_DISAPPEARED,
        max_distance=C.MAX_DISTANCE,
        reid_enabled=C.REID_ENABLED,
    )
    d = PersonDetector(C.DETECTOR, C.CONFIDENCE, C.YOLO_MODEL)
    v = VoiceGreeter(
        enabled=C.ENABLE_VOICE,
        rate=C.VOICE_RATE,
        volume=C.VOICE_VOLUME,
        cooldown=C.VOICE_COOLDOWN,
    )
    return s, t, d, v


stats, tracker, detector, voice = _init_services()

# ==================== SESSION STATE ====================
if "camera_on" not in st.session_state:
    st.session_state.camera_on = True
if "popup_time" not in st.session_state:
    st.session_state.popup_time = 0.0
if "popup_guest" not in st.session_state:
    st.session_state.popup_guest = 0
if "popup_title" not in st.session_state:
    st.session_state.popup_title = C.WELCOME_HEADLINE
if "popup_subtitle" not in st.session_state:
    st.session_state.popup_subtitle = C.WELCOME_SUBHEAD
if "show_boxes" not in st.session_state:
    st.session_state.show_boxes = True
if "reset_cooldown" not in st.session_state:
    st.session_state.reset_cooldown = 0.0


# Global thread-safe notification state for WebRTC & OpenCV background workers
POPUP_STATE = {
    "time": 0.0,
    "title": C.WELCOME_HEADLINE,
    "subtitle": C.WELCOME_SUBHEAD,
    "guest_id": 0
}

CAM_DEVICE_LABELS = {
    0: "📷 Camera 0: External Lenovo FHD Cam (Priority)",
    1: "📷 Camera 1: Built-in Laptop Webcam"
}


# ==================== HARDWARE CAMERA SAFE OPEN HELPER ====================
def safe_open_camera(source=None):
    """
    Safely open the specified camera source at native HD resolution.
    Sets MJPG hardware compression and 1280x720 target dimensions BEFORE
    initial frame acquisition to prevent Windows DirectShow from locking to 480p YUY2.
    """
    if source is not None and not isinstance(source, int):
        candidates = [source]
    elif source is not None:
        candidates = [source]
    else:
        primary = C.CAMERA_SOURCE
        candidates = [primary] + [i for i in [0, 1] if i != primary]

    for src in candidates:
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if (isinstance(src, int) and sys.platform.startswith("win")) else [cv2.CAP_ANY]
        for b in backends:
            cap = None
            try:
                cap = cv2.VideoCapture(src, b)
                if cap is not None and cap.isOpened():
                    try:
                        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, C.CAMERA_WIDTH)
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, C.CAMERA_HEIGHT)
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_FPS, 30)
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    except Exception:
                        pass

                    ok, frame = cap.read()
                    if ok and frame is not None and frame.size > 0:
                        return cap
                    cap.release()
            except Exception:
                if cap is not None:
                    try:
                        cap.release()
                    except Exception:
                        pass
    return None

    for src in candidates:
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if (isinstance(src, int) and sys.platform.startswith("win")) else [cv2.CAP_ANY]
        for b in backends:
            cap = None
            try:
                cap = cv2.VideoCapture(src, b)
                if cap is not None and cap.isOpened():
                    try:
                        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, C.CAMERA_WIDTH)
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, C.CAMERA_HEIGHT)
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_FPS, 30)
                    except Exception:
                        pass
                    try:
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    except Exception:
                        pass

                    ok, frame = cap.read()
                    if ok and frame is not None and frame.size > 0:
                        print(f"[camera] Connected to camera {src} at native resolution {frame.shape[1]}x{frame.shape[0]} HD")
                        return cap
                    cap.release()
            except Exception:
                if cap is not None:
                    try:
                        cap.release()
                    except Exception:
                        pass
    return None


# ==================== HEADER STRIP (INDIA STANDARD TIME: GMT +5:30) ====================
now_dt = C.get_ist_now()
time_str = now_dt.strftime("%I:%M:%S %p").lstrip("0") + " IST"
date_str = now_dt.strftime("%A, %d %B %Y")

st.markdown(f"""
<div class="glass-hdr">
  <div class="event-title-text">
    <span>🏆 {C.EVENT_TITLE}</span>
    <span class="school-badge">{C.SCHOOL_NAME}</span>
  </div>
  <div>
    <p class="clock-text">{time_str}</p>
    <p class="date-text">{date_str}</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Time greeting banner
st.markdown(f"""
<div class="glass-greet">✨ {C.get_time_greeting()}  •  {C.WELCOME_HEADLINE}  •  {C.WELCOME_SUBHEAD}</div>
""", unsafe_allow_html=True)


# ==================== LAYOUT: VIDEO (LEFT) | STATS & GRAPH (RIGHT) ====================
# ==================== HELPER: UPDATE ALL STAT CARDS ====================
def update_cards(in_view=0):
    if "total_ph" in globals():
        total_ph.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid #ffd700;">
          <div class="card-label">Total Guests Welcomed Today</div>
          <div class="card-number" style="color:#ffd700; font-size:36px; text-shadow: 0 0 16px rgba(255,215,0,0.45);">{stats.total:,}</div>
          <div class="card-sub">Official Attendee Count</div>
        </div>""", unsafe_allow_html=True)

    if "view_ph" in globals():
        view_ph.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid #38bdf8;">
          <div class="card-label">In View Now</div>
          <div class="card-number" style="color:#38bdf8; font-size:28px; text-shadow: 0 0 12px rgba(56,189,248,0.45);">{in_view}</div>
          <div class="card-sub">Visible in Camera</div>
        </div>""", unsafe_allow_html=True)

    if in_view < 4:
        cl, cc = "CALM", "#00dc82"
    elif in_view < 9:
        cl, cc = "LIVELY", "#ffd700"
    elif in_view < 15:
        cl, cc = "BUSY", "#ff8000"
    else:
        cl, cc = "PACKED!", "#ff3b5c"

    if "crowd_ph" in globals():
        crowd_ph.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid {cc};">
          <div class="card-label">Crowd Status</div>
          <div class="card-number" style="color:{cc}; font-size:24px; text-shadow: 0 0 12px {cc}66;">{cl}</div>
          <div class="card-sub">+{stats.recent_arrivals(600)} in 10m</div>
        </div>""", unsafe_allow_html=True)

    if "chart_ph" in globals():
        bk = stats.buckets(12, 300)
        labels = [f"-{i*5}m" for i in range(11, -1, -1)]
        chart_ph.bar_chart(dict(zip(labels, bk)), height=285, color="#2563eb")


# ==================== SIDEBAR: OPERATOR & CAMERA CONTROLS ====================
with st.sidebar:
    st.markdown("""
    <div style="padding: 0 0 10px;">
      <h3 style="color:#ffd700; font-size:16px; font-weight:900; margin:0; letter-spacing:1px;">
        ⚙️ ARENA CONTROLS
      </h3>
      <p style="color:#94a3b8; font-size:11px; margin:2px 0 0;">Tender Heart High School</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Camera Feed Mode Selector
    cam_modes = ["🎥 Hardware USB Camera", "🌐 Browser Live Camera"] if sys.platform.startswith("win") else ["🌐 Browser Live Camera", "🎥 Hardware USB Camera"]
    cam_mode = st.radio(
        "Camera Feed Mode",
        cam_modes,
        index=0,
        key="arena_feed_mode"
    )

    # 2. Hardware Camera Device Selector (Priority: Camera 0 External Lenovo FHD Cam)
    if cam_mode == "🎥 Hardware USB Camera":
        current_active = st.session_state.get("active_hw_cam_idx", 0)
        chosen_cam_idx = st.selectbox(
            "Select Camera Device",
            options=[0, 1],
            format_func=lambda x: CAM_DEVICE_LABELS.get(x, f"Camera {x}"),
            index=0 if current_active == 0 else 1,
            key="arena_camera_idx"
        )

        if st.session_state.get("active_hw_cam_idx", 0) != chosen_cam_idx:
            st.session_state.active_hw_cam_idx = chosen_cam_idx
            if "cap" in st.session_state and st.session_state["cap"] is not None:
                try:
                    st.session_state["cap"].release()
                except Exception:
                    pass
                st.session_state["cap"] = None
            st.rerun()

    st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.12);'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin:0 0 6px;'>Arena Operations</p>", unsafe_allow_html=True)

    # 3. Action Buttons
    sb1, sb2 = st.columns(2)
    with sb1:
        cam_lbl = "🔴 Camera OFF" if st.session_state.camera_on else "🟢 Camera ON"
        if st.button(cam_lbl, key="cam_btn", use_container_width=True):
            st.session_state.camera_on = not st.session_state.camera_on
            if not st.session_state.camera_on and "cap" in st.session_state and st.session_state["cap"] is not None:
                try:
                    st.session_state["cap"].release()
                except Exception:
                    pass
                st.session_state["cap"] = None
            st.rerun()

    with sb2:
        if st.button("⛶ Fullscreen", key="fs_btn", use_container_width=True):
            pass

    if st.button(f"🔊 Voice Greeter: {'ON' if voice.enabled else 'OFF'}", key="v_btn", use_container_width=True):
        voice.toggle()
        st.rerun()

    if st.button("🎉 Test Welcome (+1)", key="tw_btn", use_container_width=True):
        stats.add(1)
        gid = stats.total
        now = time.time()
        st.session_state.popup_time = now
        st.session_state.popup_title = C.WELCOME_HEADLINE
        st.session_state.popup_subtitle = C.WELCOME_SUBHEAD
        st.session_state.popup_guest = gid
        POPUP_STATE["time"] = now
        POPUP_STATE["title"] = C.WELCOME_HEADLINE
        POPUP_STATE["subtitle"] = C.WELCOME_SUBHEAD
        POPUP_STATE["guest_id"] = gid
        voice.speak("Welcome to Sports Meet 2026! We are happy to have you here!")
        voice.play_chime()

    # INSTANT RESET: Clears all guest counts to 0 without hardware reload lag!
    if st.button("🔄 Reset Count to 0", key="r_btn", use_container_width=True):
        stats.reset()
        tracker.reset()
        st.session_state.popup_time = 0.0
        st.session_state.popup_guest = 0
        POPUP_STATE["time"] = 0.0
        POPUP_STATE["guest_id"] = 0
        st.session_state.reset_cooldown = time.time() + 2.5
        st.toast("✅ Reset complete! All guest counts cleared to 0.")

    st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.12);'>", unsafe_allow_html=True)
    st.session_state.show_boxes = st.checkbox("Show Tracking Boxes", value=st.session_state.get("show_boxes", True), key="chk_boxes")


# ==================== MAIN DASHBOARD: VIDEO (LEFT) | STATS & GRAPH (RIGHT) ====================
col_vid, col_st = st.columns([1.7, 1.0], gap="small")

with col_st:
    # 1. Total Welcomed Card
    total_ph = st.empty()

    # 2. In View Now & Crowd Status Cards
    c1, c2 = st.columns(2)
    view_ph = c1.empty()
    crowd_ph = c2.empty()

    # 3. Large Arrivals Graph (Glassmorphism card, height=285)
    st.markdown("<p style='font-size:11px;font-weight:700;color:#94a3b8;"
                "text-transform:uppercase;margin:8px 0 2px'>📊 Arrivals Trend (Last 60 Min)</p>",
                unsafe_allow_html=True)
    chart_ph = st.empty()

    # Initial stats render
    update_cards(0)


with col_vid:
    popup_ph = st.empty()
    status_ph = st.empty()

    now = time.time()
    in_cooldown = now < st.session_state.get("reset_cooldown", 0.0)

    # --- Live Welcome Popup Banner or Reset Notice ---
    if in_cooldown:
        popup_ph.markdown("""
        <div class="glass-popup" style="border-color: #00dc82;">
          <p class="popup-title-text" style="color: #00dc82;">✨ ATTENDEE COUNT RESET TO 0</p>
          <p class="popup-sub-text" style="color: #ffffff;">Ready to welcome attendees!</p>
        </div>""", unsafe_allow_html=True)
    elif now - st.session_state.popup_time < C.POPUP_SECONDS:
        p_title = st.session_state.get("popup_title", C.WELCOME_HEADLINE)
        p_sub = st.session_state.get("popup_subtitle", C.WELCOME_SUBHEAD)
        popup_ph.markdown(f"""
        <div class="glass-popup">
          <p class="popup-title-text">🎉 {p_title}</p>
          <p class="popup-sub-text">{p_sub}</p>
          <span class="popup-badge-pill">GUEST #{st.session_state.popup_guest:,}</span>
        </div>""", unsafe_allow_html=True)
    else:
        popup_ph.empty()

    if not st.session_state.camera_on:
        # --- Camera OFF Standby ---
        status_ph.markdown(
            "<div style='margin-bottom:4px;'><span style='background:rgba(235,50,60,0.2); border:1px solid #eb323c; color:#eb323c; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● CAMERA OFF</span></div>",
            unsafe_allow_html=True
        )
        off_img = np.zeros((480, 854, 3), dtype=np.uint8)
        off_img[:] = (10, 16, 36)
        cv2.putText(off_img, "CAMERA IS TURNED OFF", (235, 230),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 100, 200), 2)
        cv2.putText(off_img, "Click 'Camera ON' to resume detection", (215, 275),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 150, 180), 1)
        st.image(off_img, channels="RGB", use_container_width=True)

    elif cam_mode == "🌐 Browser Live Camera" and HAS_WEBRTC:
        # --- Mode 1: Browser Live Camera Stream (Native WebRTC & Permission Prompt) ---
        status_ph.markdown(
            f"<div style='margin-bottom:4px;'><span style='background:rgba(0,220,130,0.18); border:1px solid #00dc82; color:#00dc82; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● LIVE — BROWSER WEBCAM ({detector.backend.upper()})</span> <span style='color:#94a3b8; font-size:12px; margin-left:8px;'>Continuous real-time attendee detection</span></div>",
            unsafe_allow_html=True
        )

        class WebRTCProcessor(VideoProcessorBase):
            def __init__(self):
                self.frame_idx = 0
                self.latest_frame = None
                self.lock = threading.Lock()
                self.running = True
                self.worker = threading.Thread(target=self._detection_worker, daemon=True)
                self.worker.start()

            def _detection_worker(self):
                while self.running:
                    target_frame = None
                    with self.lock:
                        if self.latest_frame is not None:
                            target_frame = self.latest_frame.copy()
                            self.latest_frame = None

                    if target_frame is not None and target_frame.size > 0:
                        _now = time.time()
                        _in_cooldown = _now < st.session_state.get("reset_cooldown", 0.0)
                        if not _in_cooldown:
                            try:
                                dets = detector.detect(target_frame)
                                people = tracker.update(dets, target_frame)
                                for p in people.values():
                                    if p.disappeared > 0:
                                        continue

                                    # Case 1: Returning Guest -> Greet, DO NOT Recount!
                                    if p.is_returning and p.guest_number is not None:
                                        if tracker.registry.can_greet_again(p.guest_number, cooldown_seconds=12.0):
                                            tracker.registry.record_greeting(p.guest_number)
                                            now_t = time.time()
                                            POPUP_STATE["time"] = now_t
                                            POPUP_STATE["title"] = "WELCOME BACK!"
                                            POPUP_STATE["subtitle"] = "GREAT TO SEE YOU AGAIN!"
                                            POPUP_STATE["guest_id"] = p.guest_number
                                            voice.speak(f"Welcome back Guest {p.guest_number} to Sports Meet 2026! Great to see you again!")
                                            voice.play_chime()
                                        continue

                                    # Case 2: Genuinely New Attendee -> Register & Count ONCE
                                    if not p.counted:
                                        if p.frames_seen >= C.MIN_FRAMES_TO_COUNT:
                                            p.counted = True
                                            stats.add(1)
                                            new_gid = stats.total
                                            p.guest_number = new_gid
                                            p.label = f"Guest #{new_gid}"
                                            tracker.registry.register(new_gid, p.appearance_sig)

                                            now_t = time.time()
                                            POPUP_STATE["time"] = now_t
                                            POPUP_STATE["title"] = C.WELCOME_HEADLINE
                                            POPUP_STATE["subtitle"] = C.WELCOME_SUBHEAD
                                            POPUP_STATE["guest_id"] = new_gid
                                            voice.speak("Welcome to Sports Meet 2026! We are happy to have you here!")
                                            voice.play_chime()
                            except Exception:
                                pass
                    time.sleep(0.02)

            def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
                img = frame.to_ndarray(format="bgr24")
                self.frame_idx += 1

                # Send newest frame to background detection thread without blocking stream
                if self.frame_idx % max(1, C.DETECT_EVERY_N_FRAMES) == 0:
                    with self.lock:
                        self.latest_frame = img

                # Overlay current tracked bounding boxes immediately (<1ms)
                if st.session_state.get("show_boxes", True):
                    try:
                        for p in tracker.visible():
                            x1, y1, x2, y2 = [int(v) for v in p.box[:4]]
                            col = (0, 220, 130) if p.counted else (0, 215, 255)
                            cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)
                            tag = p.label
                            (tw, tht), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                            cv2.rectangle(img, (x1, y1 - tht - 8), (x1 + tw + 10, y1), col, -1)
                            cv2.putText(img, tag, (x1 + 5, y1 - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 16, 32), 2)
                    except Exception:
                        pass

                return av.VideoFrame.from_ndarray(img, format="bgr24")

            def __del__(self):
                self.running = False

        rtc_config = RTCConfiguration({
            "iceServers": [
                {"urls": [
                    "stun:stun.l.google.com:19302",
                    "stun:stun1.l.google.com:19302",
                    "stun:stun2.l.google.com:19302"
                ]},
                {"urls": [
                    "turn:openrelay.metered.ca:80",
                    "turn:openrelay.metered.ca:443",
                    "turn:openrelay.metered.ca:443?transport=tcp"
                ],
                "username": "openrelayproject",
                "credential": "openrelayproject"}
            ]
        })

        ctx = webrtc_streamer(
            key="sportsmeet_live_preview",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_config,
            video_processor_factory=WebRTCProcessor,
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 1280},
                    "height": {"ideal": 720},
                    "frameRate": {"ideal": 30}
                },
                "audio": False
            },
            async_processing=True,
        )

        if ctx.state.playing:
            while ctx.state.playing:
                n_vis = len(tracker.visible())
                update_cards(n_vis)

                # Live celebratory popup banner
                now = time.time()
                if now - POPUP_STATE.get("time", 0.0) < C.POPUP_SECONDS:
                    p_title = POPUP_STATE.get("title", C.WELCOME_HEADLINE)
                    p_sub = POPUP_STATE.get("subtitle", C.WELCOME_SUBHEAD)
                    p_gid = POPUP_STATE.get("guest_id", stats.total)
                    popup_ph.markdown(f"""
                    <div class="glass-popup">
                      <p class="popup-title-text">🎉 {p_title}</p>
                      <p class="popup-sub-text">{p_sub}</p>
                      <span class="popup-badge-pill">GUEST #{p_gid:,}</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    popup_ph.empty()

                time.sleep(0.15)

    else:
        # --- Mode 2: Hardware USB Camera (Continuous High-FPS DirectShow / OpenCV Loop) ---
        img_ph = st.empty()
        hw_target = st.session_state.get("active_hw_cam_idx", C.CAMERA_SOURCE)
        if ("cap" not in st.session_state or st.session_state["cap"] is None or
            not st.session_state["cap"].isOpened() or
            st.session_state.get("opened_hw_cam_target") != hw_target):
            if "cap" in st.session_state and st.session_state["cap"] is not None:
                try:
                    st.session_state["cap"].release()
                except Exception:
                    pass
            st.session_state["cap"] = safe_open_camera(hw_target)
            st.session_state.opened_hw_cam_target = hw_target

        cap = st.session_state["cap"]
        det_name = detector.backend.upper()
        frame_idx = 0

        try:
            while st.session_state.camera_on:
                frame = None
                connected = False

                if cap is not None and cap.isOpened():
                    try:
                        ok, frame = cap.read()
                        if ok and frame is not None and frame.size > 0:
                            connected = True
                        else:
                            frame = None
                    except Exception:
                        frame = None

                if connected and frame is not None:
                    status_ph.markdown(
                        f"<div style='margin-bottom:4px;'><span style='background:rgba(0,220,130,0.18); border:1px solid #00dc82; color:#00dc82; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● LIVE — {det_name} (CAM {hw_target})</span></div>",
                        unsafe_allow_html=True
                    )

                    if not in_cooldown and (frame_idx % max(1, C.DETECT_EVERY_N_FRAMES) == 0):
                        try:
                            dets = detector.detect(frame)
                            people = tracker.update(dets, frame)
                            for p in people.values():
                                if p.disappeared > 0:
                                    continue
                                if p.is_returning and p.guest_number is not None:
                                    if tracker.registry.can_greet_again(p.guest_number, cooldown_seconds=12.0):
                                        tracker.registry.record_greeting(p.guest_number)
                                        now_t = time.time()
                                        st.session_state.popup_time = now_t
                                        st.session_state.popup_title = "WELCOME BACK!"
                                        st.session_state.popup_subtitle = "GREAT TO SEE YOU AGAIN!"
                                        st.session_state.popup_guest = p.guest_number
                                        POPUP_STATE["time"] = now_t
                                        POPUP_STATE["title"] = "WELCOME BACK!"
                                        POPUP_STATE["subtitle"] = "GREAT TO SEE YOU AGAIN!"
                                        POPUP_STATE["guest_id"] = p.guest_number
                                        voice.speak(f"Welcome back Guest {p.guest_number} to Sports Meet 2026! Great to see you again!")
                                        voice.play_chime()
                                    continue
                                if not p.counted:
                                    if p.frames_seen >= C.MIN_FRAMES_TO_COUNT:
                                        p.counted = True
                                        stats.add(1)
                                        new_gid = stats.total
                                        p.guest_number = new_gid
                                        p.label = f"Guest #{new_gid}"
                                        tracker.registry.register(new_gid, p.appearance_sig)

                                        now_t = time.time()
                                        st.session_state.popup_time = now_t
                                        st.session_state.popup_title = C.WELCOME_HEADLINE
                                        st.session_state.popup_subtitle = C.WELCOME_SUBHEAD
                                        st.session_state.popup_guest = new_gid
                                        POPUP_STATE["time"] = now_t
                                        POPUP_STATE["title"] = C.WELCOME_HEADLINE
                                        POPUP_STATE["subtitle"] = C.WELCOME_SUBHEAD
                                        POPUP_STATE["guest_id"] = new_gid
                                        voice.speak("Welcome to Sports Meet 2026! We are happy to have you here!")
                                        voice.play_chime()
                        except Exception as e:
                            pass

                    vis = tracker.visible()
                    n_vis = len(vis)

                    if st.session_state.show_boxes:
                        for p in vis:
                            x1, y1, x2, y2 = [int(v) for v in p.box[:4]]
                            col = (0, 220, 130) if p.counted else (0, 215, 255)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), col, 2)
                            tag = p.label
                            (tw, tht), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                            cv2.rectangle(frame, (x1, y1 - tht - 8), (x1 + tw + 10, y1), col, -1)
                            cv2.putText(frame, tag, (x1 + 5, y1 - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 16, 32), 2)

                    # Update celebratory banner if active
                    now = time.time()
                    if now - POPUP_STATE.get("time", 0.0) < C.POPUP_SECONDS:
                        p_title = POPUP_STATE.get("title", C.WELCOME_HEADLINE)
                        p_sub = POPUP_STATE.get("subtitle", C.WELCOME_SUBHEAD)
                        p_gid = POPUP_STATE.get("guest_id", stats.total)
                        popup_ph.markdown(f"""
                        <div class="glass-popup">
                          <p class="popup-title-text">🎉 {p_title}</p>
                          <p class="popup-sub-text">{p_sub}</p>
                          <span class="popup-badge-pill">GUEST #{p_gid:,}</span>
                        </div>""", unsafe_allow_html=True)
                    else:
                        popup_ph.empty()

                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_ph.image(rgb, channels="RGB", use_container_width=True)
                    update_cards(n_vis)
                    frame_idx += 1
                else:
                    status_ph.markdown(
                        f"<div style='margin-bottom:4px;'><span style='background:rgba(235,50,60,0.18); border:1px solid #eb323c; color:#eb323c; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● CAMERA {hw_target} NOT RESPONDING</span> <span style='color:#94a3b8; font-size:12px; margin-left:8px;'>Switch device or select 'Browser Live Camera'</span></div>",
                        unsafe_allow_html=True
                    )
                    blank = np.zeros((480, 854, 3), dtype=np.uint8)
                    blank[:] = (12, 18, 38)
                    cv2.putText(blank, f"HARDWARE CAMERA {hw_target} NOT CONNECTED", (110, 220),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (60, 60, 220), 2)
                    cv2.putText(blank, "Check USB cable or choose another camera above",
                                (120, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 200, 235), 1)
                    img_ph.image(blank, channels="RGB", use_container_width=True)
                    update_cards(0)
                    time.sleep(1.5)
                    if cap is None or not cap.isOpened():
                        st.session_state["cap"] = safe_open_camera(hw_target)
                        cap = st.session_state["cap"]

                time.sleep(0.015)
        finally:
            if not st.session_state.camera_on and cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass
                st.session_state["cap"] = None
