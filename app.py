"""
=====================================================================
  SPORTS MEET 2026 - SMART GUEST GREETER & CROWD COUNTER
  Glassmorphism Single-Screen Dashboard  |  Tender Heart School
=====================================================================
"""
import datetime
import os
import sys
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
    initial_sidebar_state="collapsed",
)

# ==================== GLASSMORPHISM PROFESSIONAL STYLING ====================
st.markdown("""
<style>
    /* Completely hide Streamlit Header, Footer, Sidebar, and Toolbar */
    #MainMenu, header, footer,
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Ambient Sports Stadium Background with Luminous Lighting */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
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
        font-size: 22px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 0.5px;
        text-shadow: 0 0 14px rgba(59, 130, 246, 0.7);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .school-badge {
        background: linear-gradient(135deg, #ffd700 0%, #f59e0b 100%);
        color: #060a1a;
        font-size: 11px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 6px;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
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
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
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
</style>
""", unsafe_allow_html=True)


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


# ==================== SAFE CAMERA OPEN HELPER ====================
def safe_open_camera(source=None):
    """
    Safely open any available camera source.
    Scans all device camera indices (0, 1, 2, 3, 4) with both DirectShow and standard backends,
    verifying actual frame readability before returning.
    """
    candidates = []
    if source is not None and not isinstance(source, int):
        candidates.append(source)
    else:
        primary = C.CAMERA_SOURCE if source is None else source
        candidates = [primary] + [i for i in [0, 1, 2, 3, 4] if i != primary]

    for src in candidates:
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if (isinstance(src, int) and sys.platform.startswith("win")) else [cv2.CAP_ANY]
        for b in backends:
            cap = None
            try:
                cap = cv2.VideoCapture(src, b)
                if cap is not None and cap.isOpened():
                    ok, frame = cap.read()
                    if ok and frame is not None and frame.size > 0:
                        try:
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, C.CAMERA_WIDTH)
                        except Exception:
                            pass
                        try:
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, C.CAMERA_HEIGHT)
                        except Exception:
                            pass
                        print(f"[camera] Successfully connected to device camera {src}")
                        return cap
                    cap.release()
            except Exception:
                if cap is not None:
                    try:
                        cap.release()
                    except Exception:
                        pass
    return None


# ==================== HEADER STRIP ====================
now_dt = datetime.datetime.now()
time_str = now_dt.strftime("%I:%M:%S %p").lstrip("0")
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
col_vid, col_st = st.columns([1.7, 1.0], gap="small")

with col_st:
    # 1. Total Welcomed Card
    total_ph = st.empty()

    # 2. In View Now & Crowd Status Cards
    c1, c2 = st.columns(2)
    view_ph = c1.empty()
    crowd_ph = c2.empty()

    # 3. Controls Row 1: Camera ON/OFF & Fullscreen Button
    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
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

    with b2:
        # Seamless Glassmorphism Fullscreen Button
        if st.button("⛶ Fullscreen", key="fs_btn", use_container_width=True):
            pass

    # Controls Row 2: Test, Voice, Reset
    b3, b4, b5 = st.columns(3)
    with b3:
        if st.button("🎉 Test (+1)", key="tw_btn", use_container_width=True):
            stats.add(1)
            gid = stats.total
            st.session_state.popup_time = time.time()
            st.session_state.popup_title = C.WELCOME_HEADLINE
            st.session_state.popup_subtitle = C.WELCOME_SUBHEAD
            st.session_state.popup_guest = gid
            voice.speak("Welcome to Sports Meet 2026! We are happy to have you here!")
            voice.play_chime()

    with b4:
        if st.button(f"🔊 Voice: {'ON' if voice.enabled else 'OFF'}", key="v_btn", use_container_width=True):
            voice.toggle()
            st.rerun()

    with b5:
        # INSTANT RESET: Clears all guest counts to 0 without hardware reload lag!
        if st.button("🔄 Reset 0", key="r_btn", use_container_width=True):
            stats.reset()
            tracker.reset()
            st.session_state.popup_time = 0.0
            st.session_state.popup_guest = 0
            st.session_state.reset_cooldown = time.time() + 2.5
            st.toast("✅ Reset complete! All guest counts cleared to 0.")

    # 4. Large Arrivals Graph (Glassmorphism card, height=215: big, clear & fits comfortably on all screens)
    st.markdown("<p style='font-size:11px;font-weight:700;color:#94a3b8;"
                "text-transform:uppercase;margin:6px 0 2px'>📊 Arrivals Trend (Last 60 Min)</p>",
                unsafe_allow_html=True)
    chart_ph = st.empty()


with col_vid:
    # Camera Source Options: Browser Live Camera (WebRTC) or Local Hardware USB Camera
    cam_options = ["🌐 Browser Live Camera", "🎥 Hardware USB Camera"]

    # Smart default: on Windows with local hardware webcam, default to Hardware USB
    # On Cloud / Linux, default to Browser Live Camera
    default_cam_idx = 0
    if sys.platform.startswith("win"):
        if "has_hw_cam" not in st.session_state:
            _test = safe_open_camera()
            st.session_state.has_hw_cam = (_test is not None)
            if _test is not None:
                st.session_state["cap"] = _test
        if st.session_state.get("has_hw_cam", False):
            default_cam_idx = 1

    cam_mode = st.radio(
        "Camera Mode",
        cam_options,
        index=default_cam_idx,
        horizontal=True,
        key="cam_mode_select",
        label_visibility="collapsed"
    )

    popup_ph = st.empty()
    status_ph = st.empty()
    img_ph = st.empty()


# ==================== TOP-LEVEL JAVASCRIPT FULLSCREEN CONTROLLER ====================
components.html("""
<script>
(function() {
    try {
        var pdoc = window.parent.document;

        function attachFS() {
            var buttons = pdoc.querySelectorAll('button');
            buttons.forEach(function(btn) {
                if (btn.innerText && btn.innerText.includes('Fullscreen')) {
                    if (btn.dataset.fsAttached === 'true') return;
                    btn.dataset.fsAttached = 'true';

                    btn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        var de = pdoc.documentElement;
                        var isFS = Boolean(pdoc.fullscreenElement || pdoc.webkitFullscreenElement || pdoc.mozFullScreenElement);
                        if (!isFS) {
                            if (de.requestFullscreen) de.requestFullscreen();
                            else if (de.webkitRequestFullscreen) de.webkitRequestFullscreen();
                            else if (de.msRequestFullscreen) de.msRequestFullscreen();
                        } else {
                            if (pdoc.exitFullscreen) pdoc.exitFullscreen();
                            else if (pdoc.webkitExitFullscreen) pdoc.webkitExitFullscreen();
                            else if (pdoc.msExitFullscreen) pdoc.msExitFullscreen();
                        }
                    });
                }
            });
        }

        attachFS();
        setInterval(attachFS, 500);

        pdoc.addEventListener('keydown', function(e) {
            if ((e.key === 'f' || e.key === 'F') && !e.ctrlKey && !e.altKey && e.target.tagName !== 'INPUT') {
                var de = pdoc.documentElement;
                var isFS = Boolean(pdoc.fullscreenElement || pdoc.webkitFullscreenElement || pdoc.mozFullScreenElement);
                if (!isFS) {
                    if (de.requestFullscreen) de.requestFullscreen();
                } else {
                    if (pdoc.exitFullscreen) pdoc.exitFullscreen();
                }
            }
        });
    } catch(err) {
        console.error(err);
    }
})();
</script>
""", height=0)


# ==================== HELPER: UPDATE ALL STAT CARDS ====================
def update_cards(in_view=0):
    total_ph.markdown(f"""
    <div class="glass-card" style="border-left: 5px solid #ffd700;">
      <div class="card-label">Total Guests Welcomed Today</div>
      <div class="card-number" style="color:#ffd700; font-size:36px; text-shadow: 0 0 16px rgba(255,215,0,0.45);">{stats.total:,}</div>
      <div class="card-sub">Official Attendee Count</div>
    </div>""", unsafe_allow_html=True)

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
    crowd_ph.markdown(f"""
    <div class="glass-card" style="border-left: 5px solid {cc};">
      <div class="card-label">Crowd Status</div>
      <div class="card-number" style="color:{cc}; font-size:24px; text-shadow: 0 0 12px {cc}66;">{cl}</div>
      <div class="card-sub">+{stats.recent_arrivals(600)} in 10m</div>
    </div>""", unsafe_allow_html=True)

    # Big, Clear Arrivals Chart (height=215: prominent without exceeding viewport height!)
    bk = stats.buckets(12, 300)
    labels = [f"-{i*5}m" for i in range(11, -1, -1)]
    chart_ph.bar_chart(dict(zip(labels, bk)), height=215, color="#2563eb")


# Initial stats cards render
update_cards(0)


# ==================== MAIN CAMERA & VIDEO DISPATCHER ====================
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
    img_ph.image(off_img, channels="RGB", width="stretch")

elif cam_mode == "🌐 Browser Live Camera" and HAS_WEBRTC:
    # --- Mode 1: Browser Live Camera Stream (Native WebRTC & Permission Prompt) ---
    status_ph.markdown(
        f"<div style='margin-bottom:4px;'><span style='background:rgba(0,220,130,0.18); border:1px solid #00dc82; color:#00dc82; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● LIVE — BROWSER WEBCAM ({detector.backend.upper()})</span> <span style='color:#94a3b8; font-size:12px; margin-left:8px;'>Continuous real-time attendee detection</span></div>",
        unsafe_allow_html=True
    )

    class WebRTCProcessor(VideoProcessorBase):
        def __init__(self):
            self.frame_idx = 0

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            self.frame_idx += 1
            now = time.time()
            in_cooldown = now < st.session_state.get("reset_cooldown", 0.0)

            # Continuous Person Detection & Re-ID
            if not in_cooldown and (self.frame_idx % max(1, C.DETECT_EVERY_N_FRAMES) == 0):
                try:
                    dets = detector.detect(img)
                    people = tracker.update(dets, img)
                    for p in people.values():
                        if p.disappeared > 0:
                            continue

                        # Case 1: Returning Guest -> Greet, DO NOT Recount!
                        if p.is_returning and p.guest_number is not None:
                            if tracker.registry.can_greet_again(p.guest_number, cooldown_seconds=12.0):
                                tracker.registry.record_greeting(p.guest_number)
                                st.session_state.popup_time = time.time()
                                st.session_state.popup_title = "WELCOME BACK!"
                                st.session_state.popup_subtitle = "GREAT TO SEE YOU AGAIN!"
                                st.session_state.popup_guest = p.guest_number
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

                                st.session_state.popup_time = time.time()
                                st.session_state.popup_title = C.WELCOME_HEADLINE
                                st.session_state.popup_subtitle = C.WELCOME_SUBHEAD
                                st.session_state.popup_guest = new_gid
                                voice.speak("Welcome to Sports Meet 2026! We are happy to have you here!")
                                voice.play_chime()
                except Exception as e:
                    print(f"[app] WebRTC frame error: {e}")

            # Draw continuous Bounding Boxes with stable Guest Number tags
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

    rtc_config = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}]}
    )

    ctx = webrtc_streamer(
        key="sportsmeet_live_preview",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_config,
        video_processor_factory=WebRTCProcessor,
        media_stream_constraints={"video": {"width": {"ideal": 1280}, "height": {"ideal": 720}}, "audio": False},
        async_processing=True,
    )

    if ctx.state.playing:
        update_cards(len(tracker.visible()))

else:
    # --- Mode 2: Hardware USB Camera (Continuous High-FPS OpenCV Loop) ---
    if "cap" not in st.session_state or st.session_state["cap"] is None or not st.session_state["cap"].isOpened():
        st.session_state["cap"] = safe_open_camera(C.CAMERA_SOURCE)
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
                    f"<div style='margin-bottom:4px;'><span style='background:rgba(0,220,130,0.18); border:1px solid #00dc82; color:#00dc82; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● LIVE — {det_name}</span></div>",
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
                                    st.session_state.popup_time = time.time()
                                    st.session_state.popup_title = "WELCOME BACK!"
                                    st.session_state.popup_subtitle = "GREAT TO SEE YOU AGAIN!"
                                    st.session_state.popup_guest = p.guest_number
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

                                    st.session_state.popup_time = time.time()
                                    st.session_state.popup_title = C.WELCOME_HEADLINE
                                    st.session_state.popup_subtitle = C.WELCOME_SUBHEAD
                                    st.session_state.popup_guest = new_gid
                                    voice.speak("Welcome to Sports Meet 2026! We are happy to have you here!")
                                    voice.play_chime()
                    except Exception as e:
                        print(f"[app] Hardware camera detection error: {e}")

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

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_ph.image(rgb, channels="RGB", width="stretch")
                update_cards(n_vis)
                frame_idx += 1
            else:
                status_ph.markdown(
                    "<div style='margin-bottom:4px;'><span style='background:rgba(235,50,60,0.18); border:1px solid #eb323c; color:#eb323c; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;'>● NO HARDWARE CAMERA DETECTED</span> <span style='color:#94a3b8; font-size:12px; margin-left:8px;'>Switch to 'Browser Live Camera' above!</span></div>",
                    unsafe_allow_html=True
                )
                blank = np.zeros((480, 854, 3), dtype=np.uint8)
                blank[:] = (12, 18, 38)
                cv2.putText(blank, "NO HARDWARE CAMERA FOUND ON HOST", (135, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (60, 60, 220), 2)
                cv2.putText(blank, "Select 'Browser Live Camera' above to use your camera!",
                            (110, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 200, 235), 1)
                img_ph.image(blank, channels="RGB", width="stretch")
                update_cards(0)
                time.sleep(2.0)
                if cap is None or not cap.isOpened():
                    st.session_state["cap"] = safe_open_camera()
                    cap = st.session_state["cap"]

            time.sleep(0.015)
    finally:
        if not st.session_state.camera_on and cap is not None:
            try:
                cap.release()
            except Exception:
                pass
            st.session_state["cap"] = None
