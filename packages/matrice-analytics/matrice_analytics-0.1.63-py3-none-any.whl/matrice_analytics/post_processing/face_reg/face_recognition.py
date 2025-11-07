"""
Face Recognition with Local Embedding Search Optimization

This module uses local similarity search for face recognition to achieve high performance:

Performance Optimization Strategy:
1. EmbeddingManager loads all staff embeddings from API at startup (~1 API call)
2. Embeddings are cached in memory as a normalized numpy matrix
3. Face recognition uses fast local cosine similarity search (~1-5ms per face)
4. API calls are avoided during normal operation (2000x speedup vs API calls)
5. Background refresh updates embeddings periodically (configurable TTL)

Processing Flow:
1. TemporalIdentityManager receives face embedding from detection
2. Uses EmbeddingManager._find_best_local_match() for fast local similarity search
3. Returns best match if similarity >= threshold, otherwise returns "Unknown"
4. Only falls back to API if EmbeddingManager unavailable (rare)

Configuration options:
- enable_track_id_cache: Enable/disable track-level caching
- cache_max_size: Maximum number of cached track IDs (default: 3000)
- cache_ttl: Cache time-to-live in seconds (default: 3600)
 - background_refresh_interval: Embedding refresh interval (default: 43200s = 12h)
- similarity_threshold: Minimum similarity for recognition (default: 0.45)
"""
import subprocess
import logging
import asyncio
import os
log_file = open("pip_jetson_btii.log", "w")
cmd = ["pip", "install", "httpx"]
subprocess.run(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        #preexec_fn=os.setpgrp   
    )
log_file.close()

from typing import Any, Dict, List, Optional, Tuple
import time
import base64
import cv2
import numpy as np
import threading
from datetime import datetime, timezone
from collections import deque

from ..core.base import (
    BaseProcessor,
    ProcessingContext,
    ProcessingResult,
    ConfigProtocol,
)
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    calculate_counting_summary,
    match_results_structure,
)
from dataclasses import dataclass, field
from ..core.config import BaseConfig, AlertConfig
from .face_recognition_client import FacialRecognitionClient
from .people_activity_logging import PeopleActivityLogging
from .embedding_manager import EmbeddingManager, EmbeddingConfig


# ---- Lightweight identity tracking and temporal smoothing (adapted from compare_similarity.py) ---- #
from collections import deque, defaultdict




def _normalize_embedding(vec: List[float]) -> List[float]:
    """Normalize an embedding vector to unit length (L2). Returns float32 list."""
    arr = np.asarray(vec, dtype=np.float32)
    if arr.size == 0:
        return []
    n = np.linalg.norm(arr)
    if n > 0:
        arr = arr / n
    return arr.tolist()


## Removed FaceTracker fallback (using AdvancedTracker only)


class TemporalIdentityManager:
    """
    Maintains stable identity labels per tracker ID using temporal smoothing and embedding history.

    Adaptation for production: _compute_best_identity uses EmbeddingManager for local similarity
    search first (fast), then falls back to API only if needed (slow).
    """

    def __init__(
        self,
        face_client: FacialRecognitionClient,
        embedding_manager = None,
        recognition_threshold: float = 0.35,
        history_size: int = 20,
        unknown_patience: int = 7,
        switch_patience: int = 5,
        fallback_margin: float = 0.05,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.face_client = face_client
        self.embedding_manager = embedding_manager
        self.threshold = float(recognition_threshold)
        self.history_size = int(history_size)
        self.unknown_patience = int(unknown_patience)
        self.switch_patience = int(switch_patience)
        self.fallback_margin = float(fallback_margin)
        self.tracks: Dict[Any, Dict[str, object]] = {}

    def _ensure_track(self, track_id: Any) -> None:
        if track_id not in self.tracks:
            self.tracks[track_id] = {
                "stable_staff_id": None,
                "stable_person_name": None,
                "stable_employee_id": None,
                "stable_score": 0.0,
                "stable_staff_details": {},
                "label_votes": defaultdict(int),  # staff_id -> votes
                "embedding_history": deque(maxlen=self.history_size),
                "unknown_streak": 0,
                "streaks": defaultdict(int),  # staff_id -> consecutive frames
            }

    async def _compute_best_identity(self, emb: List[float], location: str = "", timestamp: str = "") -> Tuple[Optional[str], str, float, Optional[str], Dict[str, Any], str]:
        """
        Find best identity match using local similarity search (fast) with optional API fallback.
        Returns (staff_id, person_name, score, employee_id, staff_details, detection_type).
        
        Performance optimization: Uses EmbeddingManager for local similarity search to avoid
        slow API calls (~2000ms). Only falls back to API if local search is unavailable.
        """
        if not emb or not isinstance(emb, list):
            return None, "Unknown", 0.0, None, {}, "unknown"
        
        st10 = time.time()
        
        # PRIMARY PATH: Local similarity search using EmbeddingManager (FAST - ~1-5ms)
        if self.embedding_manager:
            # Defensive check: ensure embeddings are loaded before attempting search
            if not self.embedding_manager.is_ready():
                status = self.embedding_manager.get_status()
                self.logger.error(f"EmbeddingManager not ready for search - status: {status}")
                print(f"ERROR: _compute_best_identity - embeddings not ready. Status: {status}")
                return None, "Unknown", 0.0, None, {}, "unknown"
                
            try:
                local_match = self.embedding_manager._find_best_local_match(emb)
                
                if local_match:
                    staff_embedding, similarity_score = local_match
                    
                    # Extract person name from staff details
                    person_name = "Unknown"
                    staff_details = staff_embedding.staff_details if isinstance(staff_embedding.staff_details, dict) else {}
                    
                    if staff_details:
                        first_name = staff_details.get("firstName")
                        last_name = staff_details.get("lastName")
                        name = staff_details.get("name")
                        if name:
                            person_name = str(name)
                        elif first_name or last_name:
                            person_name = f"{first_name or ''} {last_name or ''}".strip() or "Unknown"
                    
                    # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY (LOCAL)----------------------------")
                    # print("LATENCY:",(time.time() - st10)*1000,"| Throughput fps:",(1.0 / (time.time() - st10)) if (time.time() - st10) > 0 else None)
                    # print(f"LOCAL MATCH: staff_id={staff_embedding.staff_id}, similarity={similarity_score:.3f}")
                    # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY (LOCAL)----------------------------")
                    
                    self.logger.info(f"Local embedding match - staff_id={staff_embedding.staff_id}, person_name={person_name}, score={similarity_score:.3f}")
                    
                    return (
                        str(staff_embedding.staff_id),
                        person_name,
                        float(similarity_score),
                        str(staff_embedding.employee_id),
                        staff_details,
                        "known"
                    )
                else:
                    # No local match found; log best similarity for observability
                    best_sim = 0.0
                    try:
                        best_sim = float(self.embedding_manager.get_best_similarity(emb))
                    except Exception:
                        pass
                    self.logger.debug(f"No local match found - best_similarity={best_sim:.3f}, threshold={self.threshold:.3f}")
                    # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY (LOCAL - NO MATCH)----------------------------")
                    # print("LATENCY:",(time.time() - st10)*1000,"| Throughput fps:",(1.0 / (time.time() - st10)) if (time.time() - st10) > 0 else None)
                    # print(f"BEST_SIM={best_sim:.3f} THRESH={self.threshold:.3f}")
                    # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY (LOCAL - NO MATCH)----------------------------")
                    
                    return None, "Unknown", 0.0, None, {}, "unknown"
                    
            except Exception as e:
                self.logger.warning(f"Local similarity search failed, falling back to API: {e}")
                # Fall through to API call below
        
        # FALLBACK PATH: API call (SLOW - ~2000ms) - only if embedding manager not available
        # This path should rarely be used in production
        try:
            self.logger.warning("Using slow API fallback for identity search - consider checking embedding manager initialization")
            resp = await self.face_client.search_similar_faces(
                face_embedding=emb,
                threshold=0.01,  # low threshold to always get top-1
                limit=1,
                collection="staff_enrollment",
                location=location,
                timestamp=timestamp,
            )
            # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY (API FALLBACK)----------------------------")
            # print("LATENCY:",(time.time() - st10)*1000,"| Throughput fps:",(1.0 / (time.time() - st10)) if (time.time() - st10) > 0 else None)
            # print("WARNING: Using slow API fallback!")
            # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY (API FALLBACK)----------------------------")

        except Exception as e:
            self.logger.error(f"API ERROR: Failed to search similar faces in _compute_best_identity: {e}", exc_info=True)
            return None, "Unknown", 0.0, None, {}, "unknown"

        try:
            results: List[Any] = []
            self.logger.debug('API Response received for identity search')
            if isinstance(resp, dict):
                if isinstance(resp.get("data"), list):
                    results = resp.get("data", [])
                elif isinstance(resp.get("results"), list):
                    results = resp.get("results", [])
                elif isinstance(resp.get("items"), list):
                    results = resp.get("items", [])
            elif isinstance(resp, list):
                results = resp

            if not results:
                self.logger.debug("No identity match found from API")
                return None, "Unknown", 0.0, None, {}, "unknown"

            item = results[0] if isinstance(results, list) else results
            self.logger.debug(f'Top-1 match from API: {item}')
            # Be defensive with keys and types
            staff_id = item.get("staffId") if isinstance(item, dict) else None
            employee_id = str(item.get("_id")) if isinstance(item, dict) and item.get("_id") is not None else None
            score = float(item.get("score", 0.0)) if isinstance(item, dict) else 0.0
            detection_type = str(item.get("detectionType", "unknown")) if isinstance(item, dict) else "unknown"
            staff_details = item.get("staffDetails", {}) if isinstance(item, dict) else {}
            # Extract a person name from staff_details
            person_name = "Unknown"
            if isinstance(staff_details, dict) and staff_details:
                first_name = staff_details.get("firstName")
                last_name = staff_details.get("lastName")
                name = staff_details.get("name")
                if name:
                    person_name = str(name)
                else:
                    if first_name or last_name:
                        person_name = f"{first_name or ''} {last_name or ''}".strip() or "UnknowNN" #TODO:ebugging change to normal once done
            # If API says unknown or missing staff_id, treat as unknown
            if not staff_id: #or detection_type == "unknown"
                self.logger.debug(f"API returned unknown or missing staff_id - score={score}, employee_id={employee_id}")
                return None, "Unknown", float(score), employee_id, staff_details if isinstance(staff_details, dict) else {}, "unknown"
            self.logger.info(f"API identified face - staff_id={staff_id}, person_name={person_name}, score={score:.3f}")
            return str(staff_id), person_name, float(score), employee_id, staff_details if isinstance(staff_details, dict) else {}, "known"
        except Exception as e:
            self.logger.error(f"Error parsing API response in _compute_best_identity: {e}", exc_info=True)
            return None, "Unknown", 0.0, None, {}, "unknown"

    async def _compute_best_identity_from_history(self, track_state: Dict[str, object], location: str = "", timestamp: str = "") -> Tuple[Optional[str], str, float, Optional[str], Dict[str, Any], str]:
        hist: deque = track_state.get("embedding_history", deque())  # type: ignore
        if not hist:
            return None, "Unknown", 0.0, None, {}, "unknown"
        try:
            self.logger.debug(f"Computing identity from embedding history - history_size={len(hist)}")
            proto = np.mean(np.asarray(list(hist), dtype=np.float32), axis=0)
            proto_list = proto.tolist() if isinstance(proto, np.ndarray) else list(proto)
        except Exception as e:
            self.logger.error(f"Error computing prototype from history: {e}", exc_info=True)
            proto_list = []
        return await self._compute_best_identity(proto_list, location=location, timestamp=timestamp)

    async def update(
        self,
        track_id: Any,
        emb: List[float],
        eligible_for_recognition: bool,
        location: str = "",
        timestamp: str = "",
    ) -> Tuple[Optional[str], str, float, Optional[str], Dict[str, Any], str]:
        """
        Update temporal identity state for a track and return a stabilized identity.
        Returns (staff_id, person_name, score, employee_id, staff_details, detection_type).
        """
        st7=time.time()
        self._ensure_track(track_id)
        s = self.tracks[track_id]

        # Update embedding history
        if emb:
            try:
                history: deque = s["embedding_history"]  # type: ignore
                history.append(_normalize_embedding(emb))
            except Exception:
                pass

        # Defaults for return values
        stable_staff_id = s.get("stable_staff_id")
        stable_person_name = s.get("stable_person_name")
        stable_employee_id = s.get("stable_employee_id")
        stable_score = float(s.get("stable_score", 0.0))
        stable_staff_details = s.get("stable_staff_details", {}) if isinstance(s.get("stable_staff_details"), dict) else {}
        
        # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - STABLE VALUES----------------------------")
        # print("LATENCY:",(time.time() - st7)*1000,"| Throughput fps:",(1.0 / (time.time() - st7)) if (time.time() - st7) > 0 else None)
        # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - STABLE VALUES----------------------------")

        if eligible_for_recognition and emb:
            st8=time.time()
            staff_id, person_name, inst_score, employee_id, staff_details, det_type = await self._compute_best_identity(
                emb, location=location, timestamp=timestamp
            )
            # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY_I----------------------------")
            # print("LATENCY:",(time.time() - st8)*1000,"| Throughput fps:",(1.0 / (time.time() - st8)) if (time.time() - st8) > 0 else None)
            # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY_I----------------------------")

            is_inst_known = staff_id is not None and inst_score >= self.threshold
            if is_inst_known:
                s["label_votes"][staff_id] += 1  # type: ignore
                s["streaks"][staff_id] += 1  # type: ignore
                s["unknown_streak"] = 0

                # Initialize stable if not set
                if stable_staff_id is None:
                    s["stable_staff_id"] = staff_id
                    s["stable_person_name"] = person_name
                    s["stable_employee_id"] = employee_id
                    s["stable_score"] = float(inst_score)
                    s["stable_staff_details"] = staff_details
                    return staff_id, person_name, float(inst_score), employee_id, staff_details, "known"

                # If same as stable, keep it and update score
                if staff_id == stable_staff_id:
                    s["stable_score"] = float(inst_score)
                    # prefer latest name/details if present
                    if person_name and person_name != stable_person_name:
                        s["stable_person_name"] = person_name
                    if isinstance(staff_details, dict) and staff_details:
                        s["stable_staff_details"] = staff_details
                    if employee_id:
                        s["stable_employee_id"] = employee_id
                    return staff_id, s.get("stable_person_name") or person_name, float(inst_score), s.get("stable_employee_id") or employee_id, s.get("stable_staff_details", {}), "known"

                # Competing identity: switch only if sustained and with margin & votes ratio (local parity)
                if s["streaks"][staff_id] >= self.switch_patience:  # type: ignore
                    try:
                        prev_votes = s["label_votes"].get(stable_staff_id, 0) if stable_staff_id is not None else 0  # type: ignore
                        cand_votes = s["label_votes"].get(staff_id, 0)  # type: ignore
                    except Exception:
                        prev_votes, cand_votes = 0, 0
                    if cand_votes >= max(2, 0.75 * prev_votes) and float(inst_score) >= (self.threshold + 0.02):
                        s["stable_staff_id"] = staff_id
                        s["stable_person_name"] = person_name
                        s["stable_employee_id"] = employee_id
                        s["stable_score"] = float(inst_score)
                        s["stable_staff_details"] = staff_details
                        # reset other streaks
                        try:
                            for k in list(s["streaks"].keys()):  # type: ignore
                                if k != staff_id:
                                    s["streaks"][k] = 0  # type: ignore
                        except Exception:
                            pass
                        return staff_id, person_name, float(inst_score), employee_id, staff_details, "known"

                # Do not switch yet; keep stable but return instant score/name
                return stable_staff_id, stable_person_name or person_name, float(inst_score), stable_employee_id or employee_id, stable_staff_details, "known" if stable_staff_id else "unknown"

            # Instantaneous is unknown or low score
            s["unknown_streak"] = int(s.get("unknown_streak", 0)) + 1
            if stable_staff_id is not None and s["unknown_streak"] <= self.unknown_patience:  # type: ignore
                return stable_staff_id, stable_person_name or "Unknown", float(inst_score), stable_employee_id, stable_staff_details, "known"

            # Fallback: use prototype from history
            st9=time.time()
            fb_staff_id, fb_name, fb_score, fb_employee_id, fb_details, fb_type = await self._compute_best_identity_from_history(s, location=location, timestamp=timestamp)
            # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY FROM HISTORY----------------------------")
            # print("LATENCY:",(time.time() - st9)*1000,"| Throughput fps:",(1.0 / (time.time() - st9)) if (time.time() - st9) > 0 else None)
            # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE - COMPUTE BEST IDENTITY FROM HISTORY----------------------------")

            if fb_staff_id is not None and fb_score >= max(0.0, self.threshold - self.fallback_margin):
                s["label_votes"][fb_staff_id] += 1  # type: ignore
                s["stable_staff_id"] = fb_staff_id
                s["stable_person_name"] = fb_name
                s["stable_employee_id"] = fb_employee_id
                s["stable_score"] = float(fb_score)
                s["stable_staff_details"] = fb_details
                s["unknown_streak"] = 0
                return fb_staff_id, fb_name, float(fb_score), fb_employee_id, fb_details, "known"

            # No confident identity
            s["stable_staff_id"] = stable_staff_id
            s["stable_person_name"] = stable_person_name
            s["stable_employee_id"] = stable_employee_id
            s["stable_score"] = float(stable_score)
            s["stable_staff_details"] = stable_staff_details
            return None, "Unknown", float(inst_score), None, {}, "unknown"

        # Not eligible or no embedding; keep stable if present
        if stable_staff_id is not None:
            return stable_staff_id, stable_person_name or "Unknown", float(stable_score), stable_employee_id, stable_staff_details, "known"
        return None, "Unknown", 0.0, None, {}, "unknown"


@dataclass
class FaceRecognitionEmbeddingConfig(BaseConfig):
    """Configuration for face recognition with embeddings use case."""

    # Smoothing configuration
    enable_smoothing: bool = False
    smoothing_algorithm: str = "observability"  # "window" or "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5

    # Base confidence threshold (separate from embedding similarity threshold)
    similarity_threshold: float = 0.2  # Lowered to match local code - 0.45 was too conservative
    # Base confidence threshold (separate from embedding similarity threshold)
    confidence_threshold: float = 0.1  # Detection confidence threshold
    
    # Face recognition optional features
    enable_face_tracking: bool = True  # Enable BYTE TRACKER advanced face tracking -- KEEP IT TRUE ALWAYS


    enable_auto_enrollment: bool = False  # Enable auto-enrollment of unknown faces
    enable_face_recognition: bool = (
        True  # Enable face recognition (requires credentials)
    )
    enable_unknown_face_processing: bool = (
        False  # TODO: Unable when we will be saving unkown faces # Enable unknown face cropping/uploading (requires frame data)
    )
    enable_people_activity_logging: bool = True  # Enable logging of known face activities

    usecase_categories: List[str] = field(default_factory=lambda: ["face"])

    target_categories: List[str] = field(default_factory=lambda: ["face"])

    alert_config: Optional[AlertConfig] = None

    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {0: "face"}
    )

    facial_recognition_server_id: str = ""
    session: Any = None  # Matrice session for face recognition client
    deployment_id: Optional[str] = None  # deployment ID for update_deployment call
    
    # Embedding configuration
    embedding_config: Optional[Any] = None  # Will be set to EmbeddingConfig instance
    
    
    # Track ID cache optimization settings
    enable_track_id_cache: bool = True
    cache_max_size: int = 3000
    cache_ttl: int = 3600  # Cache time-to-live in seconds (1 hour)
    
    # Search settings
    search_limit: int = 5
    search_collection: str = "staff_enrollment"


class FaceRecognitionEmbeddingUseCase(BaseProcessor):
    # Human-friendly display names for categories
    CATEGORY_DISPLAY = {"face": "face"}

    def __init__(self, config: Optional[FaceRecognitionEmbeddingConfig] = None):
        super().__init__("face_recognition")
        self.category = "security"

        self.CASE_TYPE: Optional[str] = "face_recognition"
        self.CASE_VERSION: Optional[str] = "1.0"
        # List of categories to track
        self.target_categories = ["face"]

        # Initialize smoothing tracker
        self.smoothing_tracker = None

        # Initialize advanced tracker (will be created on first use)
        self.tracker = None
        # Initialize tracking state variables
        self._total_frame_counter = 0
        self._global_frame_offset = 0

        # Track start time for "TOTAL SINCE" calculation
        self._tracking_start_time = datetime.now(
            timezone.utc
        )  # Store as datetime object for UTC

        self._track_aliases: Dict[Any, Any] = {}
        self._canonical_tracks: Dict[Any, Dict[str, Any]] = {}
        # Tunable parameters – adjust if necessary for specific scenarios
        self._track_merge_iou_threshold: float = 0.05  # IoU ≥ 0.05 →
        self._track_merge_time_window: float = 7.0  # seconds within which to merge

        self._ascending_alert_list: List[int] = []
        self.current_incident_end_timestamp: str = "N/A"

        # Session totals tracked per unique internal track id (thread-safe)
        self._recognized_track_ids = set()
        self._unknown_track_ids = set()
        self._tracking_lock = threading.Lock()

        # Person tracking: {person_id: [{"camera_id": str, "timestamp": str}, ...]}
        self.person_tracking: Dict[str, List[Dict[str, str]]] = {}

        self.face_client = None

        # Initialize PeopleActivityLogging without face client initially
        self.people_activity_logging = None

        # Initialize EmbeddingManager - will be configured in process method
        self.embedding_manager = None
        # Temporal identity manager for API-based top-1 identity smoothing
        self.temporal_identity_manager = None
        # Removed lightweight face tracker fallback; we always use AdvancedTracker
        # Optional gating similar to compare_similarity
        self._track_first_seen: Dict[int, int] = {}
        self._probation_frames: int = 30  # Reduced from 260 - only for "Unknown" label suppression, not recognition
        self._min_face_w: int = 30
        self._min_face_h: int = 30

        self.start_timer = None
        
        # Store config for async initialization
        self._default_config = config
        self._initialized = False
        
        # Don't call asyncio.run() in __init__ - it will fail if called from async context
        # Initialization must be done by calling await initialize(config) after instantiation
        # This is handled in PostProcessor._get_use_case_instance()

    async def initialize(self, config: Optional[FaceRecognitionEmbeddingConfig] = None) -> None:
        """
        Async initialization method to set up face client and all components.
        Must be called after __init__ before process() can be called.
        
        CRITICAL INITIALIZATION SEQUENCE:
        1. Initialize face client and update deployment
        2. Create EmbeddingManager (does NOT load embeddings yet)
        3. Synchronously load embeddings with _load_staff_embeddings() - MUST succeed
        4. Verify embeddings are actually loaded (fail-fast if not)
        5. Start background refresh thread (only after successful load)
        6. Initialize TemporalIdentityManager with loaded EmbeddingManager
        7. Final verification of all components
        
        This sequence ensures:
        - No race conditions between main load and background thread
        - Fail-fast behavior if embeddings can't be loaded
        - All components have verified embeddings before use
        
        Args:
            config: Optional config to use. If not provided, uses config from __init__.
            
        Raises:
            RuntimeError: If embeddings fail to load or verification fails
        """
        print("=============== INITIALIZE() CALLED ===============")
        if self._initialized:
            self.logger.debug("Use case already initialized, skipping")
            print("=============== ALREADY INITIALIZED, SKIPPING ===============")
            return
            
        # Use provided config or fall back to default config from __init__
        init_config = config or self._default_config
        
        if not init_config:
            raise ValueError("No config provided for initialization - config is required")
            
        # Validate config type
        if not isinstance(init_config, FaceRecognitionEmbeddingConfig):
            raise TypeError(f"Invalid config type for initialization: {type(init_config)}, expected FaceRecognitionEmbeddingConfig")
            
        self.logger.info("Initializing face recognition use case with provided config")
        # print("=============== STEP 1: INITIALIZING FACE CLIENT ===============")
        
        # Initialize face client (includes deployment update)
        try:
            self.face_client = await self._get_facial_recognition_client(init_config)
            # print(f"=============== FACE CLIENT INITIALIZED: {self.face_client is not None} ===============")
            
            # Initialize People activity logging if enabled
            if init_config.enable_people_activity_logging:
                self.people_activity_logging = PeopleActivityLogging(self.face_client)
                # PeopleActivityLogging starts its background thread in __init__
                self.logger.info("People activity logging enabled and started")
            
            # Initialize EmbeddingManager
            # print("=============== STEP 2: INITIALIZING EMBEDDING MANAGER ===============")
            if not init_config.embedding_config:
                # print("=============== CREATING EMBEDDING CONFIG ===============")
                init_config.embedding_config = EmbeddingConfig(
                    similarity_threshold=init_config.similarity_threshold,
                    confidence_threshold=init_config.confidence_threshold,
                    enable_track_id_cache=init_config.enable_track_id_cache,
                    cache_max_size=init_config.cache_max_size,
                    cache_ttl=3600,
                    background_refresh_interval=43200,
                    staff_embeddings_cache_ttl=43200,
                )
            self.embedding_manager = EmbeddingManager(init_config.embedding_config, self.face_client)
            # print(f"=============== EMBEDDING MANAGER CREATED: {self.embedding_manager is not None} ===============")
            self.logger.info("Embedding manager initialized")
            
            # Load staff embeddings immediately for fast startup (avoid race conditions)
            # This MUST succeed before we can proceed - fail fast if it doesn't
            # print("=============== STEP 3: CALLING _load_staff_embeddings() ===============")
            embeddings_loaded = await self.embedding_manager._load_staff_embeddings()
            # print(f"=============== EMBEDDINGS LOADED: {embeddings_loaded} ===============")
            
            if not embeddings_loaded:
                error_msg = "CRITICAL: Failed to load staff embeddings at initialization - cannot proceed without embeddings"
                print(f"=============== {error_msg} ===============")
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Verify embeddings are actually loaded using is_ready() method
            if not self.embedding_manager.is_ready():
                status = self.embedding_manager.get_status()
                error_msg = f"CRITICAL: Embeddings not ready after load - status: {status}"
                print(f"=============== {error_msg} ===============")
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # print(f"=============== STAFF EMBEDDINGS COUNT: {len(self.embedding_manager.staff_embeddings)} ===============")
            # print(f"=============== EMBEDDINGS MATRIX SHAPE: {self.embedding_manager.embeddings_matrix.shape} ===============")
            # print(f"=============== EMBEDDINGS LOADED FLAG: {self.embedding_manager._embeddings_loaded} ===============")
            self.logger.info(f"Successfully loaded {len(self.embedding_manager.staff_embeddings)} staff embeddings at initialization")
            
            # NOW start background refresh after successful initial load (prevents race conditions)
            if init_config.embedding_config.enable_background_refresh:
                # print("=============== STEP 4: STARTING BACKGROUND REFRESH ===============")
                self.embedding_manager.start_background_refresh()
                self.logger.info("Background embedding refresh started after successful initial load")
            
            # Initialize TemporalIdentityManager with EmbeddingManager for fast local search
            # print("=============== STEP 5: INITIALIZING TEMPORAL IDENTITY MANAGER ===============")
            self.temporal_identity_manager = TemporalIdentityManager(
                face_client=self.face_client,
                embedding_manager=self.embedding_manager,
                recognition_threshold=float(init_config.similarity_threshold),
                history_size=20,
                unknown_patience=7,
                switch_patience=5,
                fallback_margin=0.05,
            )
            self.logger.info("Temporal identity manager initialized with embedding manager for local similarity search")
            
            # Final verification before marking as initialized
            # print("=============== STEP 6: FINAL VERIFICATION ===============")
            if not self.embedding_manager.is_ready():
                status = self.embedding_manager.get_status()
                error_msg = f"CRITICAL: Final verification failed - embeddings not ready. Status: {status}"
                print(f"=============== {error_msg} ===============")
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Log detailed status for debugging
            status = self.embedding_manager.get_status()
            # print(f"=============== FINAL CHECKS PASSED ===============")
            # print(f"  - Face client: {self.face_client is not None}")
            # print(f"  - Embedding manager: {self.embedding_manager is not None}")
            # print(f"  - Embedding manager status: {status}")
            # print(f"  - Temporal identity manager: {self.temporal_identity_manager is not None}")
            
            self._initialized = True
            self.logger.info("Face recognition use case fully initialized and verified")
            # print("=============== INITIALIZATION COMPLETE ===============")
            
        except Exception as e:
            self.logger.error(f"Error during use case initialization: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize face recognition use case: {e}") from e

    async def _get_facial_recognition_client(
        self, config: FaceRecognitionEmbeddingConfig
    ) -> FacialRecognitionClient:
        """Get facial recognition client and update deployment"""
        # Initialize face recognition client if not already done
        if self.face_client is None:
            self.logger.info(
                f"Initializing face recognition client with server ID: {config.facial_recognition_server_id}"
            )
            self.face_client = FacialRecognitionClient(
                server_id=config.facial_recognition_server_id, session=config.session
            )
            self.logger.info("Face recognition client initialized")
            
            # Call update_deployment if deployment_id is provided
            if config.deployment_id:
                try:
                    self.logger.info(f"Updating deployment with ID: {config.deployment_id}")
                    response = await self.face_client.update_deployment(config.deployment_id)
                    if response.get('success', False):
                        self.logger.info(f"Successfully updated deployment {config.deployment_id}")
                    else:
                        self.logger.warning(f"Failed to update deployment: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    self.logger.error(f"Exception while updating deployment: {e}", exc_info=True)
            else:
                self.logger.debug("No deployment_id provided, skipping deployment update")

        return self.face_client

    async def process(
        self,
        data: Any,
        config: ConfigProtocol,
        input_bytes: Optional[bytes] = None,
        context: Optional[ProcessingContext] = None,
        stream_info: Optional[Dict[str, Any]] = None,
    ) -> ProcessingResult:
        """
        Main entry point for face recognition with embeddings post-processing.
        Applies all standard processing plus face recognition and auto-enrollment.
        
        Thread-safe: Uses local variables for per-request state and locks for global totals.
        Order-preserving: Processes detections sequentially to maintain input order.
        """
        processing_start = time.time()
        # Ensure config is correct type
        if not isinstance(config, FaceRecognitionEmbeddingConfig):
            return self.create_error_result(
                "Invalid config type",
                usecase=self.name,
                category=self.category,
                context=context,
            )
        if context is None:
            context = ProcessingContext()
        
        # Defensive check: Ensure context is ProcessingContext object (production safety)
        # This handles edge cases where parameter mismatch might pass a dict as context
        if not isinstance(context, ProcessingContext):
            self.logger.warning(
                f"Context parameter is not ProcessingContext (got {type(context).__name__}, {context}). "
                "Creating new ProcessingContext. This may indicate a parameter mismatch in the caller."
            )
            context = ProcessingContext()

        # Lazy initialization on first process() call (similar to tracker initialization pattern)
        if not self._initialized:
            self.logger.info("Initializing face recognition use case on first process() call...")
            try:
                await self.initialize(config)
                self.logger.info("Face recognition use case initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize face recognition use case: {e}", exc_info=True)
                return self.create_error_result(
                    f"Initialization failed: {e}",
                    usecase=self.name,
                    category=self.category,
                    context=context,
                )

        # Ensure confidence threshold is set
        if not config.confidence_threshold:
            config.confidence_threshold = 0.35

        
        # Detect input format and store in context
        input_format = match_results_structure(data)
        context.input_format = input_format

        context.confidence_threshold = config.confidence_threshold

        # Parse face recognition model output format (with embeddings)
        processed_data = self._parse_face_model_output(data)
        # Normalize embeddings early for consistency (local parity)
        for _det in processed_data:
            try:
                emb = _det.get("embedding", []) or []
                if emb:
                    _det["embedding"] = _normalize_embedding(emb)
            except Exception:
                pass
        # Ignore any pre-existing track_id on detections (we rely on our own tracker)
        for _det in processed_data:
            if isinstance(_det, dict) and "track_id" in _det:
                try:
                    del _det["track_id"]
                except Exception:
                    _det["track_id"] = None

        # Apply standard confidence filtering
        if config.confidence_threshold is not None:
            processed_data = filter_by_confidence(
                processed_data, config.confidence_threshold
            )
            self.logger.debug(
                f"Applied confidence filtering with threshold {config.confidence_threshold}"
            )
        else:
            self.logger.debug(
                "Did not apply confidence filtering since threshold not provided"
            )

        # Apply category mapping if provided
        if config.index_to_category:
            processed_data = apply_category_mapping(
                processed_data, config.index_to_category
            )
            self.logger.debug("Applied category mapping")

        # Apply category filtering
        if config.target_categories:
            processed_data = filter_by_categories(
                processed_data, config.target_categories
            )
            self.logger.debug("Applied category filtering")

        # print("------------------TILL TRACKER MS----------------------------")
        # print(self._initialized,"LATENCY:",(time.time() - processing_start)*1000,"| Throughput fps:",(1.0 / (time.time() - processing_start)) if (time.time() - processing_start) > 0 else None)
        # print("------------------TILL TRACKER MS----------------------------")
        # Advanced tracking (BYTETracker-like) - only if enabled
        if config.enable_face_tracking:
            from ..advanced_tracker import AdvancedTracker
            from ..advanced_tracker.config import TrackerConfig

            # Create tracker instance if it doesn't exist (preserves state across frames)
            if self.tracker is None:
                tracker_config = TrackerConfig(
                                track_high_thresh=0.5,
                                track_low_thresh=0.05,
                                new_track_thresh=0.5,
                                match_thresh=0.8,
                                track_buffer=int(600),  # Increased to match local code - allows longer occlusions
                                max_time_lost=int(300),  # Increased to match local code
                                fuse_score=True,
                                enable_gmc=False,
                                frame_rate=int(20)
                )

                self.tracker = AdvancedTracker(tracker_config)
                self.logger.info(
                    "Initialized AdvancedTracker for Face Recognition with thresholds: "
                    f"high={tracker_config.track_high_thresh}, "
                    f"low={tracker_config.track_low_thresh}, "
                    f"new={tracker_config.new_track_thresh}"
                )

            # The tracker expects the data in the same format as input
            # It will add track_id and frame_id to each detection (we rely ONLY on these)
            processed_data = self.tracker.update(processed_data)
        else:
            self.logger.debug("Advanced face tracking disabled; continuing without external track IDs")

        # Initialize local recognition summary variables
        current_recognized_count = 0
        current_unknown_count = 0
        recognized_persons = {}
        current_frame_staff_details = {}

        # print("------------------TRACKER INIT END----------------------------")
        # print("LATENCY:",(time.time() - processing_start)*1000,"| Throughput fps:",(1.0 / (time.time() - processing_start)) if (time.time() - processing_start) > 0 else None)
        # print("------------------TRACKER INIT END----------------------------")

        # Process face recognition for each detection (if enabled)
        if config.enable_face_recognition:
            # Additional safety check: verify embeddings are still loaded and ready
            if not self.embedding_manager or not self.embedding_manager.is_ready():
                status = self.embedding_manager.get_status() if self.embedding_manager else {}
                error_msg = f"CRITICAL: Cannot process face recognition - embeddings not ready. Status: {status}"
                self.logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                return self.create_error_result(
                    error_msg,
                    usecase=self.name,
                    category=self.category,
                    context=context,
                )
            
            face_recognition_result = await self._process_face_recognition(
                processed_data, config, stream_info, input_bytes
            )
            processed_data, current_recognized_count, current_unknown_count, recognized_persons, current_frame_staff_details = face_recognition_result
        else:
            # Just add default face recognition fields without actual recognition
            for detection in processed_data:
                detection["person_id"] = None
                detection["person_name"] = "Unknown"
                detection["recognition_status"] = "disabled"
                detection["enrolled"] = False

        # print("------------------FACE RECONG CONFIG ENABLED----------------------------")
        # print("LATENCY:",(time.time() - processing_start)*1000,"| Throughput fps:",(1.0 / (time.time() - processing_start)) if (time.time() - processing_start) > 0 else None)
        # print("------------------FACE RECONG CONFIG ENABLED----------------------------")

        # Update tracking state for total count per label
        self._update_tracking_state(processed_data)

        # Update frame counter
        self._total_frame_counter += 1

        # Extract frame information from stream_info
        frame_number = None
        if stream_info:
            input_settings = stream_info.get("input_settings", {})
            start_frame = input_settings.get("start_frame")
            end_frame = input_settings.get("end_frame")
            # If start and end frame are the same, it's a single frame
            if (
                start_frame is not None
                and end_frame is not None
                and start_frame == end_frame
            ):
                frame_number = start_frame

        # Compute summaries and alerts
        general_counting_summary = calculate_counting_summary(data)
        counting_summary = self._count_categories(processed_data, config)
        # Add total unique counts after tracking using only local state
        total_counts = self.get_total_counts()
        counting_summary["total_counts"] = total_counts

        # NEW: Add face recognition summary
        counting_summary.update(self._get_face_recognition_summary(
            current_recognized_count, current_unknown_count, recognized_persons
        ))

        # print("------------------TILL FACE RECOG SUMMARY----------------------------")
        # print("LATENCY:",(time.time() - processing_start)*1000,"| Throughput fps:",(1.0 / (time.time() - processing_start)) if (time.time() - processing_start) > 0 else None)
        # print("------------------TILL FACE RECOG SUMMARY----------------------------")

        # Add detections to the counting summary (standard pattern for detection use cases)
        # Ensure display label is present for UI (does not affect logic/counters)
        for _d in processed_data:
            if "display_name" not in _d:
                name = _d.get("person_name")
                # Use person_name only if recognized; otherwise leave empty to honor probation logic
                _d["display_name"] = name if _d.get("recognition_status") == "known" else (_d.get("display_name", "") or "")
        counting_summary["detections"] = processed_data

        alerts = self._check_alerts(counting_summary, frame_number, config)

        # Step: Generate structured incidents, tracking stats and business analytics with frame-based keys
        incidents_list = self._generate_incidents(
            counting_summary, alerts, config, frame_number, stream_info
        )
        tracking_stats_list = self._generate_tracking_stats(
            counting_summary, alerts, config, frame_number, stream_info, current_frame_staff_details
        )
        business_analytics_list = self._generate_business_analytics(
            counting_summary, alerts, config, stream_info, is_empty=True
        )
        summary_list = self._generate_summary(incidents_list, tracking_stats_list, business_analytics_list)

        # Extract frame-based dictionaries from the lists
        incidents = incidents_list[0] if incidents_list else {}
        tracking_stats = tracking_stats_list[0] if tracking_stats_list else {}
        business_analytics = (
            business_analytics_list[0] if business_analytics_list else {}
        )
        summary = summary_list[0] if summary_list else {}

        # print("------------------TILL TRACKING STATS----------------------------")
        # print("LATENCY:",(time.time() - processing_start)*1000,"| Throughput fps:",(1.0 / (time.time() - processing_start)) if (time.time() - processing_start) > 0 else None)
        # print("------------------TILL TRACKING STATS----------------------------")


        agg_summary = {
            str(frame_number): {
                "incidents": incidents,
                "tracking_stats": tracking_stats,
                "business_analytics": business_analytics,
                "alerts": alerts,
                "human_text": summary,
                "person_tracking": self.get_person_tracking_summary(),
            }
        }

        context.mark_completed()

        # Build result object following the standard pattern - same structure as people counting
        result = self.create_result(
            data={"agg_summary": agg_summary},
            usecase=self.name,
            category=self.category,
            context=context,
        )
        proc_time = time.time() - processing_start
        processing_latency_ms = proc_time * 1000.0
        processing_fps = (1.0 / proc_time) if proc_time > 0 else None
        # Log the performance metrics using the module-level logger
        print("latency in ms:",processing_latency_ms,"| Throughput fps:",processing_fps,"| Frame_Number:",self._total_frame_counter)

        return result

    def _parse_face_model_output(self, data: Any) -> List[Dict]:
        """Parse face recognition model output to standard detection format, preserving embeddings"""
        processed_data = []

        if isinstance(data, dict):
            # Handle frame-based format: {"0": [...], "1": [...]}
            for frame_id, frame_detections in data.items():
                if isinstance(frame_detections, list):
                    for detection in frame_detections:
                        if isinstance(detection, dict):
                            # Convert to standard format but preserve face-specific fields
                            standard_detection = {
                                "category": detection.get("category", "face"),
                                "confidence": detection.get("confidence", 0.0),
                                "bounding_box": detection.get("bounding_box", {}),
                                "track_id": detection.get("track_id", ""),
                                "frame_id": detection.get("frame_id", frame_id),
                                # Preserve face-specific fields
                                "embedding": detection.get("embedding", []),
                                "landmarks": detection.get("landmarks", None),
                                "fps": detection.get("fps", 30),
                            }
                            processed_data.append(standard_detection)
        elif isinstance(data, list):
            # Handle list format
            for detection in data:
                if isinstance(detection, dict):
                    # Convert to standard format and ensure all required fields exist
                    standard_detection = {
                        "category": detection.get("category", "face"),
                        "confidence": detection.get("confidence", 0.0),
                        "bounding_box": detection.get("bounding_box", {}),
                        "track_id": detection.get("track_id", ""),
                        "frame_id": detection.get("frame_id", 0),
                        # Preserve face-specific fields
                        "embedding": detection.get("embedding", []),
                        "landmarks": detection.get("landmarks", None),
                        "fps": detection.get("fps", 30),
                        "metadata": detection.get("metadata", {}),
                    }
                    processed_data.append(standard_detection)

        return processed_data

    def _extract_frame_from_data(self, input_bytes: bytes) -> Optional[np.ndarray]:
        """
        Extract frame from original model data

        Args:
            original_data: Original data from model (same format as model receives)

        Returns:
            np.ndarray: Frame data or None if not found
        """
        try:
            try:
                if isinstance(input_bytes, str):
                    frame_bytes = base64.b64decode(input_bytes)
                else:
                    frame_bytes = input_bytes
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return frame
            except Exception as e:
                self.logger.debug(f"Could not decode direct frame data: {e}")

            return None

        except Exception as e:
            self.logger.debug(f"Error extracting frame from data: {e}")
            return None

    # Removed unused _calculate_bbox_area_percentage (not referenced)

    async def _process_face_recognition(
        self,
        detections: List[Dict],
        config: FaceRecognitionEmbeddingConfig,
        stream_info: Optional[Dict[str, Any]] = None,
        input_bytes: Optional[bytes] = None,
    ) -> List[Dict]:
        """Process face recognition for each detection with embeddings"""

        # Face client is initialized in initialize(); if absent, this indicates a prior init failure
        if not self.face_client:
            self.logger.error("Face client not initialized; initialize() must succeed before processing")
            return []

        # Initialize unknown faces storage if not exists
        if not hasattr(self, "unknown_faces_storage"):
            self.unknown_faces_storage = {}

        # Initialize frame availability warning flag to avoid spam
        if not hasattr(self, "_frame_warning_logged"):
            self._frame_warning_logged = False

        # Initialize per-request tracking (thread-safe)
        current_recognized_count = 0
        current_unknown_count = 0
        recognized_persons = {}
        current_frame_staff_details = {}  # Store staff details for current frame

        # Extract frame from original data for cropping unknown faces
        current_frame = (
            self._extract_frame_from_data(input_bytes) if input_bytes else None
        )

        # Log frame availability once per session
        if current_frame is None and not self._frame_warning_logged:
            if config.enable_unknown_face_processing:
                self.logger.info(
                    "Frame data not available in model output - unknown face cropping/uploading will be skipped. "
                    "To disable this feature entirely, set enable_unknown_face_processing=False"
                )
            self._frame_warning_logged = True

        # Get location from stream_info
        location = (
            stream_info.get("camera_location", "unknown") if stream_info else "unknown"
        )

        # Generate current timestamp
        current_timestamp = datetime.now(timezone.utc).isoformat()

        final_detections = []
        # Process detections sequentially to preserve order
        for detection in detections:
            
            # Process each detection sequentially with await to preserve order
            st1=time.time()
            processed_detection = await self._process_face(
                detection, current_frame, location, current_timestamp, config,
                current_recognized_count, current_unknown_count, 
                recognized_persons, current_frame_staff_details
            )
            # print("------------------WHOLE FACE RECOG PROCESSING DETECTION----------------------------")
            # print("LATENCY:",(time.time() - st1)*1000,"| Throughput fps:",(1.0 / (time.time() - st1)) if (time.time() - st1) > 0 else None)
            # print("------------------WHOLE FACE RECOG PROCESSING DETECTION----------------------------")

            # Include both known and unknown faces in final detections (maintains original order)
            if processed_detection:
                final_detections.append(processed_detection)
                # Update local counters based on processed detection
                if processed_detection.get("recognition_status") == "known":
                    staff_id = processed_detection.get("person_id")
                    if staff_id:
                        current_frame_staff_details[staff_id] = processed_detection.get("person_name", "Unknown")
                        current_recognized_count += 1
                        recognized_persons[staff_id] = recognized_persons.get(staff_id, 0) + 1
                elif processed_detection.get("recognition_status") == "unknown":
                    current_unknown_count += 1

        return final_detections, current_recognized_count, current_unknown_count, recognized_persons, current_frame_staff_details

    async def _process_face(
        self,
        detection: Dict,
        current_frame: np.ndarray,
        location: str = "",
        current_timestamp: str = "",
        config: FaceRecognitionEmbeddingConfig = None,
        current_recognized_count: int = 0,
        current_unknown_count: int = 0,
        recognized_persons: Dict = None,
        current_frame_staff_details: Dict = None,
    ) -> Dict:

        # Extract and validate embedding using EmbeddingManager
        st2=time.time()
        detection, embedding = self.embedding_manager.extract_embedding_from_detection(detection)
        if not embedding:
            return None

        # Internal tracker-provided ID (from AdvancedTracker; ignore upstream IDs entirely)
        track_id = detection.get("track_id")
        # print("------------------FACE RECOG EMBEDDING EXTRACTION----------------------------")
        # print("LATENCY:",(time.time() - st2)*1000,"| Throughput fps:",(1.0 / (time.time() - st2)) if (time.time() - st2) > 0 else None)
        # print("------------------FACE RECOG EMBEDDING EXTRACTION----------------------------")

        # Determine if detection is eligible for recognition (similar to compare_similarity gating)
        bbox = detection.get("bounding_box", {}) or {}
        x1 = int(bbox.get("xmin", bbox.get("x1", 0)))
        y1 = int(bbox.get("ymin", bbox.get("y1", 0)))
        x2 = int(bbox.get("xmax", bbox.get("x2", 0)))
        y2 = int(bbox.get("ymax", bbox.get("y2", 0)))
        w_box = max(1, x2 - x1)
        h_box = max(1, y2 - y1)
        frame_id = detection.get("frame_id", None) #TODO: Maybe replace this with stream_info frame_id

        # Track probation age strictly by internal tracker id
        if track_id is not None:
            if track_id not in self._track_first_seen:
                try:
                    self._track_first_seen[track_id] = int(frame_id) if frame_id is not None else self._total_frame_counter
                except Exception:
                    self._track_first_seen[track_id] = self._total_frame_counter
            age_frames = (int(frame_id) if frame_id is not None else self._total_frame_counter) - int(self._track_first_seen.get(track_id, 0)) + 1
        else:
            age_frames = 1

        # Eligible for recognition if face is large enough (lowered threshold to match local code behavior)
        eligible_for_recognition = (w_box >= self._min_face_w and h_box >= self._min_face_h)

        # Primary: API-based identity smoothing via TemporalIdentityManager
        staff_id = None
        person_name = ""
        similarity_score = 0.0
        employee_id = None
        staff_details: Dict[str, Any] = {}
        detection_type = "unknown"
        try:
            if self.temporal_identity_manager:
                track_key = track_id if track_id is not None else f"no_track_{id(detection)}"
                if not eligible_for_recognition:
                    # Mirror compare_similarity: when not eligible, keep stable label if present
                    s = self.temporal_identity_manager.tracks.get(track_key, {})
                    if isinstance(s, dict):
                        stable_staff_id = s.get("stable_staff_id")
                        stable_person_name = s.get("stable_person_name") or "Unknown"
                        stable_employee_id = s.get("stable_employee_id")
                        stable_score = float(s.get("stable_score", 0.0))
                        stable_staff_details = s.get("stable_staff_details") if isinstance(s.get("stable_staff_details"), dict) else {}
                        if stable_staff_id is not None:
                            staff_id = stable_staff_id
                            person_name = stable_person_name
                            employee_id = stable_employee_id
                            similarity_score = stable_score
                            staff_details = stable_staff_details
                            detection_type = "known"
                        else:
                            detection_type = "unknown"
                    # Also append embedding to history for temporal smoothing
                    if embedding:
                        try:
                            
                            self.temporal_identity_manager._ensure_track(track_key)
                            hist = self.temporal_identity_manager.tracks[track_key]["embedding_history"]  # type: ignore
                            hist.append(_normalize_embedding(embedding))  # type: ignore
                        except Exception:
                            pass
                else: #if eligible for recognition
                    st3=time.time()
                    staff_id, person_name, similarity_score, employee_id, staff_details, detection_type = await self.temporal_identity_manager.update(
                        track_id=track_key,
                        emb=embedding,
                        eligible_for_recognition=True,
                        location=location,
                        timestamp=current_timestamp,
                    )
                    # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE----------------------------")
                    # print("LATENCY:",(time.time() - st3)*1000,"| Throughput fps:",(1.0 / (time.time() - st3)) if (time.time() - st3) > 0 else None)
                    # print("------------------FACE RECOG TEMPORAL IDENTITY MANAGER UPDATE----------------------------")
        except Exception as e:
            self.logger.warning(f"TemporalIdentityManager update failed: {e}")

        # # Fallback: if still unknown and we have an EmbeddingManager, use local search
        # if (staff_id is None or detection_type == "unknown") and self.embedding_manager is not None:
        #     try:
        #         search_result = await self.embedding_manager.search_face_embedding(
        #             embedding=embedding,
        #             track_id=track_id,
        #             location=location,
        #             timestamp=current_timestamp,
        #         )
        #         if search_result:
        #             employee_id = search_result.employee_id
        #             staff_id = search_result.staff_id
        #             detection_type = search_result.detection_type
        #             staff_details = search_result.staff_details
        #             person_name = search_result.person_name
        #             similarity_score = search_result.similarity_score
        #     except Exception as e:
        #         self.logger.warning(f"Local embedding search fallback failed: {e}")

        # Update detection object directly (avoid relying on SearchResult type)
        detection = detection.copy()
        detection["person_id"] = staff_id
        detection["person_name"] = person_name or ""
        detection["recognition_status"] = "known" if staff_id else "unknown"
        detection["employee_id"] = employee_id
        detection["staff_details"] = staff_details if isinstance(staff_details, dict) else {}
        detection["similarity_score"] = float(similarity_score)
        detection["enrolled"] = bool(staff_id)
        # Display label policy: ALWAYS show identified faces immediately, only suppress "Unknown" during probation
        is_identified = (staff_id is not None and detection_type == "known")
        if is_identified:
            # Identified faces: show name immediately (no probation delay)
            detection["display_name"] = person_name
        else:
            # Unknown faces: only show "Unknown" label after probation period to avoid flicker
            show_unknown_label = (age_frames >= self._probation_frames)
            detection["display_name"] = "" if show_unknown_label else "" #TODO: Maybe replace this with "Unknown" bec probationif fail we show unknown.
        # Preserve original category (e.g., 'face') for tracking/counting

        # Update global tracking per unique internal track id to avoid double-counting within a frame
        # Determine unknown strictly by recognition_status (display label never affects counters)
        is_truly_unknown = (detection.get("recognition_status") == "unknown")

        try:
            internal_tid = detection.get("track_id")
        except Exception:
            internal_tid = None

        if not is_truly_unknown and detection_type == "known":
            # Mark recognized and ensure it is not counted as unknown anymore
            self._track_person(staff_id)
            with self._tracking_lock:
                if internal_tid is not None:
                    self._unknown_track_ids.discard(internal_tid)
                    self._recognized_track_ids.add(internal_tid)
        else:
            # Only count as unknown in session totals if probation has been exceeded and still unknown
            matured_unknown = (age_frames >= self._probation_frames)
            if matured_unknown:
                with self._tracking_lock:
                    if internal_tid is not None:
                        # If it later becomes recognized, we'll remove it from unknown set above
                        self._unknown_track_ids.add(internal_tid)

        # Enqueue detection for background logging with all required parameters
        try:
            # Log known faces for activity tracking (skip any employee_id starting with "unknown_")
            if (
                detection["recognition_status"] == "known"
                and self.people_activity_logging
                and config
                and getattr(config, 'enable_people_activity_logging', True)
                and employee_id
                and not str(employee_id).startswith("unknown_")
            ):
                st4=time.time()
                await self.people_activity_logging.enqueue_detection(
                    detection=detection,
                    current_frame=current_frame,
                    location=location,
                )
                # print("------------------FACE RECOG ENQUEUEING DETECTION FOR ACTIVITY LOGGING----------------------------")
                # print("LATENCY:",(time.time() - st4)*1000,"| Throughput fps:",(1.0 / (time.time() - st4)) if (time.time() - st4) > 0 else None)
                # print("------------------FACE RECOG ENQUEUEING DETECTION FOR ACTIVITY LOGGING----------------------------")

                self.logger.debug(f"Enqueued known face detection for activity logging: {detection.get('person_name', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error enqueueing detection for activity logging: {e}")
        # print("------------------PROCESS FACE LATENCY TOTAL----------------------------")
        #print("LATENCY:",(time.time() - st2)*1000,"| Throughput fps:",(1.0 / (time.time() - st2)) if (time.time() - st2) > 0 else None)
        # print("------------------PROCESS FACE LATENCY TOTAL----------------------------")

        return detection



    def _return_error_detection(
        self,
        detection: Dict,
        person_id: str,
        person_name: str,
        recognition_status: str,
        enrolled: bool,
        category: str,
        error: str,
    ) -> Dict:
        """Return error detection"""
        detection["person_id"] = person_id
        detection["person_name"] = person_name
        detection["recognition_status"] = recognition_status
        detection["enrolled"] = enrolled
        detection["category"] = category
        detection["error"] = error
        return detection

    def _track_person(self, person_id: str) -> None:
        """Track person with camera ID and UTC timestamp"""
        if person_id not in self.person_tracking:
            self.person_tracking[person_id] = []

        # Add current detection
        detection_record = {
            "camera_id": "test_camera_001",  # TODO: Get from stream_info in production
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self.person_tracking[person_id].append(detection_record)

    def get_person_tracking_summary(self) -> Dict:
        """Get summary of tracked persons with camera IDs and timestamps"""
        return dict(self.person_tracking)

    def get_unknown_faces_storage(self) -> Dict[str, bytes]:
        """Get stored unknown face images as bytes"""
        if self.people_activity_logging:
            return self.people_activity_logging.get_unknown_faces_storage()
        return {}

    def clear_unknown_faces_storage(self) -> None:
        """Clear stored unknown face images"""
        if self.people_activity_logging:
            self.people_activity_logging.clear_unknown_faces_storage()

    def _get_face_recognition_summary(self, current_recognized_count: int, current_unknown_count: int, recognized_persons: Dict) -> Dict:
        """Get face recognition summary for current frame"""
        recognition_rate = 0.0
        total_current = current_recognized_count + current_unknown_count
        if total_current > 0:
            recognition_rate = (current_recognized_count / total_current) * 100

        # Get thread-safe global totals
        with self._tracking_lock:
            total_recognized = len(self._recognized_track_ids)
            total_unknown = len(self._unknown_track_ids)

        return {
            "face_recognition_summary": {
                "current_frame": {
                    "recognized": current_recognized_count,
                    "unknown": current_unknown_count,
                    "total": total_current,
                    "recognized_persons": dict(recognized_persons),
                    "recognition_rate": round(recognition_rate, 1),
                },
                "session_totals": {
                    "total_recognized": total_recognized,
                    "total_unknown": total_unknown,
                    "total_processed": total_recognized + total_unknown,
                },
                "person_tracking": self.get_person_tracking_summary(),
            }
        }

    def _check_alerts(
        self, summary: dict, frame_number: Any, config: FaceRecognitionEmbeddingConfig
    ) -> List[Dict]:
        """
        Check if any alert thresholds are exceeded and return alert dicts.
        """

        def get_trend(data, lookback=900, threshold=0.6):
            window = data[-lookback:] if len(data) >= lookback else data
            if len(window) < 2:
                return True  # not enough data to determine trend
            increasing = 0
            total = 0
            for i in range(1, len(window)):
                if window[i] >= window[i - 1]:
                    increasing += 1
                total += 1
            ratio = increasing / total
            if ratio >= threshold:
                return True
            elif ratio <= (1 - threshold):
                return False

        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        alerts = []
        total_detections = summary.get("total_count", 0)
        face_summary = summary.get("face_recognition_summary", {})
        current_unknown = face_summary.get("current_frame", {}).get("unknown", 0)

        if not config.alert_config:
            return alerts

        if (
            hasattr(config.alert_config, "count_thresholds")
            and config.alert_config.count_thresholds
        ):
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "unknown_faces" and current_unknown > threshold:
                    alerts.append(
                        {
                            "alert_type": (
                                getattr(config.alert_config, "alert_type", ["Default"])
                                if hasattr(config.alert_config, "alert_type")
                                else ["Default"]
                            ),
                            "alert_id": f"alert_unknown_faces_{frame_key}",
                            "incident_category": "unknown_face_detection",
                            "threshold_level": threshold,
                            "current_count": current_unknown,
                            "ascending": get_trend(
                                self._ascending_alert_list, lookback=900, threshold=0.8
                            ),
                            "settings": {
                                t: v
                                for t, v in zip(
                                    (
                                        getattr(
                                            config.alert_config,
                                            "alert_type",
                                            ["Default"],
                                        )
                                        if hasattr(config.alert_config, "alert_type")
                                        else ["Default"]
                                    ),
                                    (
                                        getattr(
                                            config.alert_config, "alert_value", ["JSON"]
                                        )
                                        if hasattr(config.alert_config, "alert_value")
                                        else ["JSON"]
                                    ),
                                )
                            },
                        }
                    )
                elif category == "all" and total_detections > threshold:
                    alerts.append(
                        {
                            "alert_type": (
                                getattr(config.alert_config, "alert_type", ["Default"])
                                if hasattr(config.alert_config, "alert_type")
                                else ["Default"]
                            ),
                            "alert_id": "alert_" + category + "_" + frame_key,
                            "incident_category": self.CASE_TYPE,
                            "threshold_level": threshold,
                            "ascending": get_trend(
                                self._ascending_alert_list, lookback=900, threshold=0.8
                            ),
                            "settings": {
                                t: v
                                for t, v in zip(
                                    (
                                        getattr(
                                            config.alert_config,
                                            "alert_type",
                                            ["Default"],
                                        )
                                        if hasattr(config.alert_config, "alert_type")
                                        else ["Default"]
                                    ),
                                    (
                                        getattr(
                                            config.alert_config, "alert_value", ["JSON"]
                                        )
                                        if hasattr(config.alert_config, "alert_value")
                                        else ["JSON"]
                                    ),
                                )
                            },
                        }
                    )

        return alerts

    def _generate_tracking_stats(
        self,
        counting_summary: Dict,
        alerts: List,
        config: FaceRecognitionEmbeddingConfig,
        frame_number: Optional[int] = None,
        stream_info: Optional[Dict[str, Any]] = None,
        current_frame_staff_details: Dict = None,
    ) -> List[Dict]:
        """Generate structured tracking stats matching eg.json format with face recognition data."""
        camera_info = self.get_camera_info_from_stream(stream_info)
        tracking_stats = []

        total_detections = counting_summary.get("total_count", 0)
        total_counts_dict = counting_summary.get("total_counts", {})
        cumulative_total = sum(total_counts_dict.values()) if total_counts_dict else 0
        per_category_count = counting_summary.get("per_category_count", {})
        face_summary = counting_summary.get("face_recognition_summary", {})

        current_timestamp = self._get_current_timestamp_str(
            stream_info, precision=False
        )
        start_timestamp = self._get_start_timestamp_str(stream_info, precision=False)

        # Create high precision timestamps for input_timestamp and reset_timestamp
        high_precision_start_timestamp = self._get_current_timestamp_str(
            stream_info, precision=True
        )
        high_precision_reset_timestamp = self._get_start_timestamp_str(
            stream_info, precision=True
        )

        # Build total_counts array in expected format
        total_counts = []
        for cat, count in total_counts_dict.items():
            if count > 0:
                total_counts.append({"category": cat, "count": count})

        # Add face recognition specific total counts
        session_totals = face_summary.get("session_totals", {})
        total_counts.extend(
            [
                {
                    "category": "recognized_faces",
                    "count": session_totals.get("total_recognized", 0),
                },
                {
                    "category": "unknown_faces",
                    "count": session_totals.get("total_unknown", 0),
                },
            ]
        )

        # Build current_counts array in expected format
        current_counts = []
        for cat, count in per_category_count.items():
            if count > 0 or total_detections > 0:
                current_counts.append({"category": cat, "count": count})

        # Add face recognition specific current counts
        current_frame = face_summary.get("current_frame", {})
        current_counts.extend(
            [
                {
                    "category": "recognized_faces",
                    "count": current_frame.get("recognized", 0),
                },
                {"category": "unknown_faces", "count": current_frame.get("unknown", 0)},
            ]
        )

        # Prepare detections with face recognition info
        detections = []
        for detection in counting_summary.get("detections", []):
            bbox = detection.get("bounding_box", {})
            category = detection.get("display_name", "")

            detection_obj = self.create_detection_object(category, bbox)
            # Add face recognition specific fields
            detection_obj.update(
                {
                    "person_id": detection.get("person_id"),
                    # Use display_name for front-end label suppression policy
                    "person_name": detection.get("display_name", ""),
                    # Explicit label field for UI overlays
                    "label": detection.get("display_name", ""),
                    "recognition_status": detection.get(
                        "recognition_status", "unknown"
                    ),
                    "enrolled": detection.get("enrolled", False),
                }
            )
            detections.append(detection_obj)

        # Build alert_settings array in expected format
        alert_settings = []
        if config.alert_config and hasattr(config.alert_config, "alert_type"):
            alert_settings.append(
                {
                    "alert_type": (
                        getattr(config.alert_config, "alert_type", ["Default"])
                        if hasattr(config.alert_config, "alert_type")
                        else ["Default"]
                    ),
                    "incident_category": self.CASE_TYPE,
                    "threshold_level": (
                        config.alert_config.count_thresholds
                        if hasattr(config.alert_config, "count_thresholds")
                        else {}
                    ),
                    "ascending": True,
                    "settings": {
                        t: v
                        for t, v in zip(
                            (
                                getattr(config.alert_config, "alert_type", ["Default"])
                                if hasattr(config.alert_config, "alert_type")
                                else ["Default"]
                            ),
                            (
                                getattr(config.alert_config, "alert_value", ["JSON"])
                                if hasattr(config.alert_config, "alert_value")
                                else ["JSON"]
                            ),
                        )
                    },
                }
            )

    
        human_text_lines = [f"CURRENT FRAME @ {current_timestamp}"]

        current_recognized = current_frame.get("recognized", 0)
        current_unknown = current_frame.get("unknown", 0)
        recognized_persons = current_frame.get("recognized_persons", {})
        total_current = current_recognized + current_unknown

        # Show staff names and IDs being recognized in current frame (with tabs)
        human_text_lines.append(f"\tCurrent Total Faces: {total_current}")
        human_text_lines.append(f"\tCurrent Recognized: {current_recognized}")
        
        if recognized_persons:
            for person_id in recognized_persons.keys():
                # Get actual staff name from current frame processing
                staff_name = (current_frame_staff_details or {}).get(
                    person_id, f"Staff {person_id}"
                )
                human_text_lines.append(f"\tName: {staff_name} (ID: {person_id})")
        human_text_lines.append(f"\tCurrent Unknown: {current_unknown}")

        # Show current frame counts only (with tabs)
        human_text_lines.append("")
        human_text_lines.append(f"TOTAL SINCE @ {start_timestamp}")
        human_text_lines.append(f"\tTotal Faces: {cumulative_total}")
        human_text_lines.append(f"\tRecognized: {face_summary.get('session_totals',{}).get('total_recognized', 0)}")  
        human_text_lines.append(f"\tUnknown: {face_summary.get('session_totals',{}).get('total_unknown', 0)}")
        # Additional counts similar to compare_similarity HUD
        # try:
        #     human_text_lines.append(f"\tCurrent Faces (detections): {total_detections}")
        #     human_text_lines.append(f"\tTotal Unique Tracks: {cumulative_total}")
        # except Exception:
        #     pass

        human_text = "\n".join(human_text_lines)

        if alerts:
            for alert in alerts:
                human_text_lines.append(
                    f"Alerts: {alert.get('settings', {})} sent @ {current_timestamp}"
                )
        else:
            human_text_lines.append("Alerts: None")

        human_text = "\n".join(human_text_lines)
        reset_settings = [
            {"interval_type": "daily", "reset_time": {"value": 9, "time_unit": "hour"}}
        ]

        tracking_stat = self.create_tracking_stats(
            total_counts=total_counts,
            current_counts=current_counts,
            detections=detections,
            human_text=human_text,
            camera_info=camera_info,
            alerts=alerts,
            alert_settings=alert_settings,
            reset_settings=reset_settings,
            start_time=high_precision_start_timestamp,
            reset_time=high_precision_reset_timestamp,
        )

        tracking_stats.append(tracking_stat)
        return tracking_stats

    # Copy all other methods from face_recognition.py but add face recognition info to human text
    def _generate_incidents(
        self,
        counting_summary: Dict,
        alerts: List,
        config: FaceRecognitionEmbeddingConfig,
        frame_number: Optional[int] = None,
        stream_info: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        """Generate structured incidents for the output format with frame-based keys."""

        incidents = []
        total_detections = counting_summary.get("total_count", 0)
        face_summary = counting_summary.get("face_recognition_summary", {})
        current_frame = face_summary.get("current_frame", {})

        current_timestamp = self._get_current_timestamp_str(stream_info)
        camera_info = self.get_camera_info_from_stream(stream_info)

        self._ascending_alert_list = (
            self._ascending_alert_list[-900:]
            if len(self._ascending_alert_list) > 900
            else self._ascending_alert_list
        )

        if total_detections > 0:
            # Determine event level based on unknown faces ratio
            level = "low"
            intensity = 5.0
            start_timestamp = self._get_start_timestamp_str(stream_info)
            if start_timestamp and self.current_incident_end_timestamp == "N/A":
                self.current_incident_end_timestamp = "Incident still active"
            elif (
                start_timestamp
                and self.current_incident_end_timestamp == "Incident still active"
            ):
                if (
                    len(self._ascending_alert_list) >= 15
                    and sum(self._ascending_alert_list[-15:]) / 15 < 1.5
                ):
                    self.current_incident_end_timestamp = current_timestamp
            elif (
                self.current_incident_end_timestamp != "Incident still active"
                and self.current_incident_end_timestamp != "N/A"
            ):
                self.current_incident_end_timestamp = "N/A"

            # Base intensity on unknown faces
            current_unknown = current_frame.get("unknown", 0)
            unknown_ratio = (
                current_unknown / total_detections if total_detections > 0 else 0
            )
            intensity = min(10.0, unknown_ratio * 10 + (current_unknown / 3))

            if intensity >= 9:
                level = "critical"
                self._ascending_alert_list.append(3)
            elif intensity >= 7:
                level = "significant"
                self._ascending_alert_list.append(2)
            elif intensity >= 5:
                level = "medium"
                self._ascending_alert_list.append(1)
            else:
                level = "low"
                self._ascending_alert_list.append(0)

            # Generate human text in new format with face recognition info
            current_recognized = current_frame.get("recognized", 0)
            human_text_lines = [f"FACE RECOGNITION INCIDENTS @ {current_timestamp}:"]
            human_text_lines.append(f"\tSeverity Level: {(self.CASE_TYPE,level)}")
            human_text_lines.append(f"\tRecognized Faces: {current_recognized}")
            human_text_lines.append(f"\tUnknown Faces: {current_unknown}")
            human_text_lines.append(f"\tTotal Faces: {total_detections}")
            human_text = "\n".join(human_text_lines)

            alert_settings = []
            if config.alert_config and hasattr(config.alert_config, "alert_type"):
                alert_settings.append(
                    {
                        "alert_type": (
                            getattr(config.alert_config, "alert_type", ["Default"])
                            if hasattr(config.alert_config, "alert_type")
                            else ["Default"]
                        ),
                        "incident_category": self.CASE_TYPE,
                        "threshold_level": (
                            config.alert_config.count_thresholds
                            if hasattr(config.alert_config, "count_thresholds")
                            else {}
                        ),
                        "ascending": True,
                        "settings": {
                            t: v
                            for t, v in zip(
                                (
                                    getattr(
                                        config.alert_config, "alert_type", ["Default"]
                                    )
                                    if hasattr(config.alert_config, "alert_type")
                                    else ["Default"]
                                ),
                                (
                                    getattr(
                                        config.alert_config, "alert_value", ["JSON"]
                                    )
                                    if hasattr(config.alert_config, "alert_value")
                                    else ["JSON"]
                                ),
                            )
                        },
                    }
                )

            event = self.create_incident(
                incident_id=self.CASE_TYPE + "_" + str(frame_number),
                incident_type=self.CASE_TYPE,
                severity_level=level,
                human_text=human_text,
                camera_info=camera_info,
                alerts=alerts,
                alert_settings=alert_settings,
                start_time=start_timestamp,
                end_time=self.current_incident_end_timestamp,
                level_settings={"low": 1, "medium": 3, "significant": 4, "critical": 7},
            )
            incidents.append(event)

        else:
            self._ascending_alert_list.append(0)
            incidents.append({})

        return incidents

    def _generate_business_analytics(
        self,
        counting_summary: Dict,
        alerts: Any,
        config: FaceRecognitionEmbeddingConfig,
        stream_info: Optional[Dict[str, Any]] = None,
        is_empty=False,
    ) -> List[Dict]:
        """Generate standardized business analytics for the agg_summary structure."""
        if is_empty:
            return []
        return []

    def _generate_summary(self, incidents: List, tracking_stats: List, business_analytics: List) -> List[str]:
        """
        Generate a human_text string for the tracking_stat, incident, business analytics and alerts.
        """
        lines = []
        lines.append("Application Name: "+self.CASE_TYPE)
        lines.append("Application Version: "+self.CASE_VERSION)
        if len(incidents) > 0:
            lines.append("Incidents: "+f"\n\t{incidents[0].get('human_text', 'No incidents detected')}")
        if len(tracking_stats) > 0:
            lines.append("Tracking Statistics: "+f"\t{tracking_stats[0].get('human_text', 'No tracking statistics detected')}")
        if len(business_analytics) > 0:
            lines.append("Business Analytics: "+f"\t{business_analytics[0].get('human_text', 'No business analytics detected')}")

        if len(incidents) == 0 and len(tracking_stats) == 0 and len(business_analytics) == 0:
            lines.append("Summary: "+"No Summary Data")

        return ["\n".join(lines)]

    # Include all the standard helper methods from face_recognition.py...
    def _count_categories(
        self, detections: list, config: FaceRecognitionEmbeddingConfig
    ) -> dict:
        """
        Count the number of detections per category and return a summary dict.
        The detections list is expected to have 'track_id' (from tracker), 'category', 'bounding_box', etc.
        Output structure will include 'track_id' for each detection as per AdvancedTracker output.
        """
        counts = {}
        for det in detections:
            cat = det.get("category", "unknown")
            counts[cat] = counts.get(cat, 0) + 1
        # Each detection dict will now include 'track_id' and face recognition fields
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": [
                {
                    "bounding_box": det.get("bounding_box"),
                    "category": det.get("category"),
                    "confidence": det.get("confidence"),
                    "track_id": det.get("track_id"),
                    "frame_id": det.get("frame_id"),
                    # Face recognition fields
                    "person_id": det.get("person_id"),
                    "person_name": det.get("person_name"),
                    "label": det.get("display_name", ""),
                    "recognition_status": det.get("recognition_status"),
                    "enrolled": det.get("enrolled"),
                    "embedding": det.get("embedding", []),
                    "landmarks": det.get("landmarks"),
                    "staff_details": det.get(
                        "staff_details"
                    ),  # Full staff information from API
                }
                for det in detections
            ],
        }

    # Removed unused _extract_predictions (counts and outputs are built elsewhere)

    # Copy all standard tracking, IoU, timestamp methods from face_recognition.py
    def _update_tracking_state(self, detections: list):
        """Track unique categories track_ids per category for total count after tracking."""
        if not hasattr(self, "_per_category_total_track_ids"):
            self._per_category_total_track_ids = {
                cat: set() for cat in self.target_categories
            }
        self._current_frame_track_ids = {cat: set() for cat in self.target_categories}

        for det in detections:
            cat = det.get("category")
            raw_track_id = det.get("track_id")
            if cat not in self.target_categories or raw_track_id is None:
                continue
            bbox = det.get("bounding_box", det.get("bbox"))
            canonical_id = self._merge_or_register_track(raw_track_id, bbox)
            det["track_id"] = canonical_id

            self._per_category_total_track_ids.setdefault(cat, set()).add(canonical_id)
            self._current_frame_track_ids[cat].add(canonical_id)

    def get_total_counts(self):
        """Return total unique track_id count for each category."""
        return {
            cat: len(ids)
            for cat, ids in getattr(self, "_per_category_total_track_ids", {}).items()
        }

    def _format_timestamp_for_stream(self, timestamp: float) -> str:
        """Format timestamp for streams (YYYY:MM:DD HH:MM:SS format)."""
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y:%m:%d %H:%M:%S")

    def _format_timestamp_for_video(self, timestamp: float) -> str:
        """Format timestamp for video chunks (HH:MM:SS.ms format)."""
        hours = int(timestamp // 3600)
        minutes = int((timestamp % 3600) // 60)
        seconds = round(float(timestamp % 60), 2)
        return f"{hours:02d}:{minutes:02d}:{seconds:.1f}"

    def _format_timestamp(self, timestamp: Any) -> str:
        """Format a timestamp to match the current timestamp format: YYYY:MM:DD HH:MM:SS.

        The input can be either:
        1. A numeric Unix timestamp (``float`` / ``int``) – it will be converted to datetime.
        2. A string in the format ``YYYY-MM-DD-HH:MM:SS.ffffff UTC``.

        The returned value will be in the format: YYYY:MM:DD HH:MM:SS (no milliseconds, no UTC suffix).

        Example
        -------
        >>> self._format_timestamp("2025-10-27-19:31:20.187574 UTC")
        '2025:10:27 19:31:20'
        """

        # Convert numeric timestamps to datetime first
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp, timezone.utc)
            return dt.strftime('%Y:%m:%d %H:%M:%S')

        # Ensure we are working with a string from here on
        if not isinstance(timestamp, str):
            return str(timestamp)

        # Remove ' UTC' suffix if present
        timestamp_clean = timestamp.replace(' UTC', '').strip()

        # Remove milliseconds if present (everything after the last dot)
        if '.' in timestamp_clean:
            timestamp_clean = timestamp_clean.split('.')[0]

        # Parse the timestamp string and convert to desired format
        try:
            # Handle format: YYYY-MM-DD-HH:MM:SS
            if timestamp_clean.count('-') >= 2:
                # Replace first two dashes with colons for date part, third with space
                parts = timestamp_clean.split('-')
                if len(parts) >= 4:
                    # parts = ['2025', '10', '27', '19:31:20']
                    formatted = f"{parts[0]}:{parts[1]}:{parts[2]} {'-'.join(parts[3:])}"
                    return formatted
        except Exception:
            pass

        # If parsing fails, return the cleaned string as-is
        return timestamp_clean

    def _get_current_timestamp_str(self, stream_info: Optional[Dict[str, Any]], precision=False, frame_id: Optional[str]=None) -> str:
        """Get formatted current timestamp based on stream type."""
        
        if not stream_info:
            return "00:00:00.00"
        if precision:
            if stream_info.get("input_settings", {}).get("start_frame", "na") != "na":
                if frame_id:
                    start_time = int(frame_id)/stream_info.get("input_settings", {}).get("original_fps", 30)
                else:
                    start_time = stream_info.get("input_settings", {}).get("start_frame", 30)/stream_info.get("input_settings", {}).get("original_fps", 30)
                stream_time_str = self._format_timestamp_for_video(start_time)
                
                return self._format_timestamp(stream_info.get("input_settings", {}).get("stream_time", "NA"))
            else:
                return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")

        if stream_info.get("input_settings", {}).get("start_frame", "na") != "na":
            if frame_id:
                start_time = int(frame_id)/stream_info.get("input_settings", {}).get("original_fps", 30)
            else:
                start_time = stream_info.get("input_settings", {}).get("start_frame", 30)/stream_info.get("input_settings", {}).get("original_fps", 30)

            stream_time_str = self._format_timestamp_for_video(start_time)
           

            return self._format_timestamp(stream_info.get("input_settings", {}).get("stream_time", "NA"))
        else:
            stream_time_str = stream_info.get("input_settings", {}).get("stream_info", {}).get("stream_time", "")
            if stream_time_str:
                try:
                    timestamp_str = stream_time_str.replace(" UTC", "")
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H:%M:%S.%f")
                    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
                    return self._format_timestamp_for_stream(timestamp)
                except:
                    return self._format_timestamp_for_stream(time.time())
            else:
                return self._format_timestamp_for_stream(time.time())

    def _get_start_timestamp_str(self, stream_info: Optional[Dict[str, Any]], precision=False) -> str:
        """Get formatted start timestamp for 'TOTAL SINCE' based on stream type."""
        if not stream_info:
            return "00:00:00"
        
        if precision:
            if self.start_timer is None:
                candidate = stream_info.get("input_settings", {}).get("stream_time")
                if not candidate or candidate == "NA":
                    candidate = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
                self.start_timer = candidate
                return self._format_timestamp(self.start_timer)
            elif stream_info.get("input_settings", {}).get("start_frame", "na") == 1:
                candidate = stream_info.get("input_settings", {}).get("stream_time")
                if not candidate or candidate == "NA":
                    candidate = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
                self.start_timer = candidate
                return self._format_timestamp(self.start_timer)
            else:
                return self._format_timestamp(self.start_timer)

        if self.start_timer is None:
            # Prefer direct input_settings.stream_time if available and not NA
            candidate = stream_info.get("input_settings", {}).get("stream_time")
            if not candidate or candidate == "NA":
                # Fallback to nested stream_info.stream_time used by current timestamp path
                stream_time_str = stream_info.get("input_settings", {}).get("stream_info", {}).get("stream_time", "")
                if stream_time_str:
                    try:
                        timestamp_str = stream_time_str.replace(" UTC", "")
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H:%M:%S.%f")
                        self._tracking_start_time = dt.replace(tzinfo=timezone.utc).timestamp()
                        candidate = datetime.fromtimestamp(self._tracking_start_time, timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
                    except:
                        candidate = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
                else:
                    candidate = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
            self.start_timer = candidate
            return self._format_timestamp(self.start_timer)
        elif stream_info.get("input_settings", {}).get("start_frame", "na") == 1:
            candidate = stream_info.get("input_settings", {}).get("stream_time")
            if not candidate or candidate == "NA":
                stream_time_str = stream_info.get("input_settings", {}).get("stream_info", {}).get("stream_time", "")
                if stream_time_str:
                    try:
                        timestamp_str = stream_time_str.replace(" UTC", "")
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H:%M:%S.%f")
                        ts = dt.replace(tzinfo=timezone.utc).timestamp()
                        candidate = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
                    except:
                        candidate = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
                else:
                    candidate = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S.%f UTC")
            self.start_timer = candidate
            return self._format_timestamp(self.start_timer)
        
        else:
            if self.start_timer is not None and self.start_timer != "NA":
                return self._format_timestamp(self.start_timer)

            if self._tracking_start_time is None:
                stream_time_str = stream_info.get("input_settings", {}).get("stream_info", {}).get("stream_time", "")
                if stream_time_str:
                    try:
                        timestamp_str = stream_time_str.replace(" UTC", "")
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H:%M:%S.%f")
                        self._tracking_start_time = dt.replace(tzinfo=timezone.utc).timestamp()
                    except:
                        self._tracking_start_time = time.time()
                else:
                    self._tracking_start_time = time.time()

            dt = datetime.fromtimestamp(self._tracking_start_time, tz=timezone.utc)
            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt.strftime('%Y:%m:%d %H:%M:%S')

    
    def _compute_iou(self, box1: Any, box2: Any) -> float:
        """Compute IoU between two bounding boxes which may be dicts or lists."""

        def _bbox_to_list(bbox):
            if bbox is None:
                return []
            if isinstance(bbox, list):
                return bbox[:4] if len(bbox) >= 4 else []
            if isinstance(bbox, dict):
                if "xmin" in bbox:
                    return [bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]]
                if "x1" in bbox:
                    return [bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]]
                values = [v for v in bbox.values() if isinstance(v, (int, float))]
                return values[:4] if len(values) >= 4 else []
            return []

        l1 = _bbox_to_list(box1)
        l2 = _bbox_to_list(box2)
        if len(l1) < 4 or len(l2) < 4:
            return 0.0
        x1_min, y1_min, x1_max, y1_max = l1
        x2_min, y2_min, x2_max, y2_max = l2

        x1_min, x1_max = min(x1_min, x1_max), max(x1_min, x1_max)
        y1_min, y1_max = min(y1_min, y1_max), max(y1_min, y1_max)
        x2_min, x2_max = min(x2_min, x2_max), max(x2_min, x2_max)
        y2_min, y2_max = min(y2_min, y2_max), max(y2_min, y2_max)

        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)

        inter_w = max(0.0, inter_x_max - inter_x_min)
        inter_h = max(0.0, inter_y_max - inter_y_min)
        inter_area = inter_w * inter_h

        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = area1 + area2 - inter_area

        return (inter_area / union_area) if union_area > 0 else 0.0

    def _merge_or_register_track(self, raw_id: Any, bbox: Any) -> Any:
        """Return a stable canonical ID for a raw tracker ID."""
        if raw_id is None or bbox is None:
            return raw_id

        now = time.time()

        if raw_id in self._track_aliases:
            canonical_id = self._track_aliases[raw_id]
            track_info = self._canonical_tracks.get(canonical_id)
            if track_info is not None:
                track_info["last_bbox"] = bbox
                track_info["last_update"] = now
                track_info["raw_ids"].add(raw_id)
            return canonical_id

        for canonical_id, info in self._canonical_tracks.items():
            if now - info["last_update"] > self._track_merge_time_window:
                continue
            iou = self._compute_iou(bbox, info["last_bbox"])
            if iou >= self._track_merge_iou_threshold:
                self._track_aliases[raw_id] = canonical_id
                info["last_bbox"] = bbox
                info["last_update"] = now
                info["raw_ids"].add(raw_id)
                return canonical_id

        canonical_id = raw_id
        self._track_aliases[raw_id] = canonical_id
        self._canonical_tracks[canonical_id] = {
            "last_bbox": bbox,
            "last_update": now,
            "raw_ids": {raw_id},
        }
        return canonical_id

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, "people_activity_logging") and self.people_activity_logging:
                self.people_activity_logging.stop_background_processing()
        except:
            pass
        
        try:
            if hasattr(self, "embedding_manager") and self.embedding_manager:
                self.embedding_manager.stop_background_refresh()
        except:
            pass