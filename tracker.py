"""
Sports Meet 2026 - Enhanced Centroid & Appearance Tracker
Features a persistent Guest Registry with multi-zone HSV signature Re-ID.
Ensures every person is counted exactly ONCE today, maintains their permanent Guest #ID,
and greets returning guests without recounting them.
"""
from collections import OrderedDict
import time

import cv2
import numpy as np

import config as C


def compute_iou(boxA, boxB):
    """Compute Intersection over Union (IoU) of two boxes (x1, y1, x2, y2)."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h
    if inter_area == 0:
        return 0.0

    boxA_area = max(1, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxB_area = max(1, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
    iou = inter_area / float(boxA_area + boxB_area - inter_area)
    return max(0.0, min(1.0, iou))


def extract_appearance_signature(frame, box):
    """
    Extracts a multi-zone normalized HSV color appearance signature
    composed of Head, Torso, and Lower-body histograms.
    Highly invariant to illumination shifts and auto-exposure changes.
    """
    if frame is None or len(frame.shape) < 3:
        return None
    fh, fw = frame.shape[:2]
    x1, y1, x2, y2 = [int(v) for v in box[:4]]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(fw, x2), min(fh, y2)
    bw, bh = x2 - x1, y2 - y1
    if bw < 25 or bh < 35:
        return None

    crop = frame[y1:y2, x1:x2]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    # 3 vertical zones:
    # Zone 1 (top 25%): head / hair
    # Zone 2 (mid 45%): torso / shirt / jacket
    # Zone 3 (lower 30%): waist / pants / shorts
    z1 = hsv[0:int(bh * 0.25), :]
    z2 = hsv[int(bh * 0.25):int(bh * 0.70), :]
    z3 = hsv[int(bh * 0.70):, :]

    # 1D Hue histograms (30 bins: 0 to 180) - Hue represents color tone independent of brightness
    h1 = cv2.calcHist([z1], [0], None, [30], [0, 180])
    h2 = cv2.calcHist([z2], [0], None, [30], [0, 180])
    h3 = cv2.calcHist([z3], [0], None, [30], [0, 180])

    # 2D H-S histogram for torso (18 Hue x 8 Saturation bins)
    h2_hs = cv2.calcHist([z2], [0, 1], None, [18, 8], [0, 180, 25, 256])

    # Normalize with L1 norm so sum of bins == 1 (required for Bhattacharyya distance)
    cv2.normalize(h1, h1, 1, 0, cv2.NORM_L1)
    cv2.normalize(h2, h2, 1, 0, cv2.NORM_L1)
    cv2.normalize(h3, h3, 1, 0, cv2.NORM_L1)
    cv2.normalize(h2_hs, h2_hs, 1, 0, cv2.NORM_L1)

    return {
        "h1": h1,
        "h2": h2,
        "h3": h3,
        "h2_hs": h2_hs,
        "aspect_ratio": bh / float(max(1, bw)),
    }


def compare_signatures(sigA, sigB):
    """
    Compare two appearance signatures.
    Returns similarity between 0.0 (completely distinct) and 1.0 (identical person).
    """
    if sigA is None or sigB is None:
        return 0.0

    # Torso Hue (highest weight)
    bhat2 = cv2.compareHist(sigA["h2"], sigB["h2"], cv2.HISTCMP_BHATTACHARYYA)
    corr2 = max(0.0, cv2.compareHist(sigA["h2"], sigB["h2"], cv2.HISTCMP_CORREL))
    sim_torso = 0.5 * max(0.0, 1.0 - bhat2) + 0.5 * corr2

    # Torso 2D H-S
    bhat_hs = cv2.compareHist(sigA["h2_hs"], sigB["h2_hs"], cv2.HISTCMP_BHATTACHARYYA)
    sim_hs = max(0.0, 1.0 - bhat_hs)

    # Head and Lower-body Hue
    bhat1 = cv2.compareHist(sigA["h1"], sigB["h1"], cv2.HISTCMP_BHATTACHARYYA)
    bhat3 = cv2.compareHist(sigA["h3"], sigB["h3"], cv2.HISTCMP_BHATTACHARYYA)
    sim_other = 0.4 * max(0.0, 1.0 - bhat1) + 0.6 * max(0.0, 1.0 - bhat3)

    score = sim_torso * 0.50 + sim_hs * 0.30 + sim_other * 0.20
    return float(max(0.0, min(1.0, score)))


class GuestRegistry:
    """
    Persistent in-memory registry of all guests counted today.
    Holds their permanent guest number and a collection of appearance signatures.
    """
    def __init__(self, match_threshold=0.55):
        self.guests = {}   # guest_number -> dict
        self.match_threshold = match_threshold

    def register(self, guest_number, signature):
        """Register a new counted guest with their initial appearance signature."""
        now = time.time()
        self.guests[guest_number] = {
            "id": guest_number,
            "label": f"Guest #{guest_number}",
            "signatures": [signature] if signature is not None else [],
            "first_seen": now,
            "last_seen": now,
            "greeted_last": now,
            "visit_count": 1,
        }
        print(f"[registry] Registered new attendee: Guest #{guest_number}")

    def add_signature(self, guest_number, signature):
        """Add additional signature sample to enrich guest profile (up to 8 samples)."""
        if guest_number not in self.guests or signature is None:
            return
        g = self.guests[guest_number]
        # Keep up to 8 diverse snapshots
        if len(g["signatures"]) < 8:
            g["signatures"].append(signature)
        g["last_seen"] = time.time()

    def find_match(self, signature):
        """
        Compare signature against all registered guests.
        Returns (guest_number, best_similarity) if similarity >= match_threshold,
        otherwise (None, best_similarity).
        """
        if signature is None or not self.guests:
            return None, 0.0

        best_gid = None
        best_sim = 0.0

        for gid, g in self.guests.items():
            for s in g["signatures"]:
                sim = compare_signatures(signature, s)
                if sim > best_sim:
                    best_sim = sim
                    best_gid = gid

        if best_sim >= self.match_threshold and best_gid is not None:
            return best_gid, best_sim
        return None, best_sim

    def record_greeting(self, guest_number):
        """Update last greeted timestamp for a guest."""
        if guest_number in self.guests:
            self.guests[guest_number]["greeted_last"] = time.time()
            self.guests[guest_number]["visit_count"] += 1

    def can_greet_again(self, guest_number, cooldown_seconds=12.0):
        """Check if enough time has elapsed to greet this returning guest again."""
        if guest_number not in self.guests:
            return True
        return (time.time() - self.guests[guest_number]["greeted_last"]) >= cooldown_seconds

    def clear(self):
        """Clear all registered guest identities."""
        self.guests.clear()


class TrackedPerson:
    def __init__(self, track_id, box, appearance=None, guest_number=None):
        self.track_id = track_id
        self.guest_number = guest_number
        self.label = f"Guest #{guest_number}" if guest_number is not None else "Guest"
        self.box = box
        self.centroid = self._centre(box)
        self.prev_centroid = self.centroid
        self.frames_seen = 1
        self.disappeared = 0
        self.counted = (guest_number is not None)
        self.is_returning = False
        self.appearance_sig = appearance
        self.first_seen = time.time()
        self.last_seen = time.time()

    @staticmethod
    def _centre(box):
        x1, y1, x2, y2 = box[:4]
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def update(self, box, appearance=None):
        self.prev_centroid = self.centroid
        self.box = box
        self.centroid = self._centre(box)
        self.frames_seen += 1
        self.disappeared = 0
        self.last_seen = time.time()
        if appearance is not None:
            self.appearance_sig = appearance


class CentroidTracker:
    def __init__(self, max_disappeared=35, max_distance=180, reid_enabled=True):
        self.next_track_id = 1
        self.people = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.reid_enabled = reid_enabled
        self.registry = GuestRegistry(match_threshold=0.55)

    def reset(self):
        """Reset the tracker and guest registry completely."""
        self.people.clear()
        self.registry.clear()
        self.next_track_id = 1

    def clear_identities(self):
        """Purge stored guest identity appearance signatures."""
        self.registry.clear()
        print("[tracker] Re-ID identity memory cleared.")

    def update(self, detections, frame=None):
        """
        Update tracker with detections [(x1, y1, x2, y2, conf), ...].
        Returns dict track_id -> TrackedPerson.
        """
        # If no detections in this frame
        if not detections:
            for tid in list(self.people):
                self.people[tid].disappeared += 1
                if self.people[tid].disappeared > self.max_disappeared:
                    del self.people[tid]
            return self.people

        # Extract appearance signatures
        det_appearances = []
        if frame is not None and self.reid_enabled:
            for d in detections:
                det_appearances.append(extract_appearance_signature(frame, d))
        else:
            det_appearances = [None] * len(detections)

        det_centres = np.array([((d[0] + d[2]) / 2.0, (d[1] + d[3]) / 2.0) for d in detections])

        # If no currently active tracks, register all detections
        if not self.people:
            for d, app in zip(detections, det_appearances):
                self._register(d, app)
            return self.people

        track_ids = list(self.people.keys())
        obj_centres = np.array([self.people[i].centroid for i in track_ids])

        # Distance matrix (Euclidean)
        dist_matrix = np.linalg.norm(obj_centres[:, None, :] - det_centres[None, :, :], axis=2)

        # Cost matrix: IoU overlap + spatial distance
        cost_matrix = np.zeros_like(dist_matrix)
        for r, tid in enumerate(track_ids):
            pbox = self.people[tid].box
            for c, det_box in enumerate(detections):
                iou = compute_iou(pbox, det_box)
                d = dist_matrix[r, c]
                cost = (d / float(self.max_distance)) * 0.6 + (1.0 - iou) * 0.4
                cost_matrix[r, c] = cost

        used_rows, used_cols = set(), set()
        for flat in np.argsort(cost_matrix, axis=None):
            r, c = divmod(int(flat), cost_matrix.shape[1])
            if r in used_rows or c in used_cols:
                continue

            iou = compute_iou(self.people[track_ids[r]].box, detections[c])
            if dist_matrix[r, c] > self.max_distance and iou < 0.08:
                continue

            tid = track_ids[r]
            self.people[tid].update(detections[c], det_appearances[c])
            # If guest is already confirmed, periodically enrich their signature library
            if self.people[tid].counted and self.people[tid].guest_number is not None:
                self.registry.add_signature(self.people[tid].guest_number, det_appearances[c])

            used_rows.add(r)
            used_cols.add(c)

        # Increment disappeared for unmatched active tracks
        for r, tid in enumerate(track_ids):
            if r not in used_rows:
                self.people[tid].disappeared += 1
                if self.people[tid].disappeared > self.max_disappeared:
                    del self.people[tid]

        # Register unassociated detections
        for c, (d, app) in enumerate(zip(detections, det_appearances)):
            if c not in used_cols:
                self._register(d, app)

        return self.people

    def visible(self):
        """Returns currently visible people (disappeared == 0)."""
        return [p for p in self.people.values() if p.disappeared == 0]

    def _register(self, box, appearance=None):
        """
        Register a new detection.
        First checks if the person matches an existing registered guest (Re-ID).
        If matched, immediately links them to their permanent Guest #ID!
        """
        matched_gid = None
        if self.reid_enabled and appearance is not None:
            matched_gid, sim = self.registry.find_match(appearance)
            if matched_gid is not None:
                print(f"[tracker] Matched returning attendee -> Guest #{matched_gid} (similarity: {sim:.2f})")

        person = TrackedPerson(
            track_id=self.next_track_id,
            box=box,
            appearance=appearance,
            guest_number=matched_gid,
        )

        if matched_gid is not None:
            person.counted = True
            person.is_returning = True
            person.label = f"Guest #{matched_gid}"

        self.people[self.next_track_id] = person
        self.next_track_id += 1
