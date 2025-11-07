from typing import Any, Dict, List, Optional
from dataclasses import asdict, dataclass, field
import time
from datetime import datetime, timezone
import copy
import tempfile
import os
from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    count_objects_by_category,
    count_objects_in_zones,
    calculate_counting_summary,
    match_results_structure,
    bbox_smoothing,
    BBoxSmoothingConfig,
    BBoxSmoothingTracker
)
# External dependencies
import cv2
import numpy as np
#import torch
import re
from collections import Counter, defaultdict
import sys
import subprocess
import logging
import asyncio
import urllib
import urllib.request
import base64
# Get the major and minor version numbers
major_version = sys.version_info.major
minor_version = sys.version_info.minor
print(f"Python version: {major_version}.{minor_version}")
os.environ["ORT_LOG_SEVERITY_LEVEL"] = "3"


# Lazy import mechanism for LicensePlateRecognizer
_OCR_IMPORT_SOURCE = None
_LicensePlateRecognizerClass = None

def _get_license_plate_recognizer_class():
    """Lazy load LicensePlateRecognizer with automatic installation fallback."""
    global _OCR_IMPORT_SOURCE, _LicensePlateRecognizerClass
    
    if _LicensePlateRecognizerClass is not None:
        return _LicensePlateRecognizerClass
    
    # Try to import from local repo first
    try:
        from ..ocr.fast_plate_ocr_py38 import LicensePlateRecognizer
        _OCR_IMPORT_SOURCE = "local_repo"
        _LicensePlateRecognizerClass = LicensePlateRecognizer
        logging.info("Successfully imported LicensePlateRecognizer from local repo")
        return _LicensePlateRecognizerClass
    except ImportError as e:
        logging.debug(f"Could not import from local repo: {e}")
    
    # Try to import from installed package
    try:
        from fast_plate_ocr import LicensePlateRecognizer  # type: ignore
        _OCR_IMPORT_SOURCE = "installed_package"
        _LicensePlateRecognizerClass = LicensePlateRecognizer
        logging.info("Successfully imported LicensePlateRecognizer from installed package")
        return _LicensePlateRecognizerClass
    except ImportError as e:
        logging.warning(f"Could not import from installed package: {e}")
    
    # Try to install with GPU support first
    logging.info("Attempting to install fast-plate-ocr with GPU support...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "fast-plate-ocr[onnx-gpu]", "--no-cache-dir"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            logging.info("Successfully installed fast-plate-ocr[onnx-gpu]")
            try:
                from fast_plate_ocr import LicensePlateRecognizer  # type: ignore
                _OCR_IMPORT_SOURCE = "installed_package_gpu"
                _LicensePlateRecognizerClass = LicensePlateRecognizer
                logging.info("Successfully imported LicensePlateRecognizer after GPU installation")
                return _LicensePlateRecognizerClass
            except ImportError as e:
                logging.warning(f"Installation succeeded but import failed: {e}")
        else:
            logging.warning(f"GPU installation failed: {result.stderr}")
    except Exception as e:
        logging.warning(f"Error during GPU installation: {e}")
    
    # Try to install with CPU support as fallback
    logging.info("Attempting to install fast-plate-ocr with CPU support...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "fast-plate-ocr[onnx]", "--no-cache-dir"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            logging.info("Successfully installed fast-plate-ocr[onnx]")
            try:
                from fast_plate_ocr import LicensePlateRecognizer  # type: ignore
                _OCR_IMPORT_SOURCE = "installed_package_cpu"
                _LicensePlateRecognizerClass = LicensePlateRecognizer
                logging.info("Successfully imported LicensePlateRecognizer after CPU installation")
                return _LicensePlateRecognizerClass
            except ImportError as e:
                logging.error(f"Installation succeeded but import failed: {e}")
        else:
            logging.error(f"CPU installation failed: {result.stderr}")
    except Exception as e:
        logging.error(f"Error during CPU installation: {e}")
    
    # Return None if all attempts failed
    logging.error("All attempts to load or install LicensePlateRecognizer failed")
    _OCR_IMPORT_SOURCE = "unavailable"
    return None

# Internal utilities that are still required
from ..ocr.preprocessing import ImagePreprocessor
from ..core.config import BaseConfig, AlertConfig, ZoneConfig

try:
    from  matrice_common.session import Session
    HAS_MATRICE_SESSION = True
except ImportError:
    HAS_MATRICE_SESSION = False
    logging.warning("Matrice session not available")

@dataclass
class LicensePlateMonitorConfig(BaseConfig):
    """Configuration for License plate detection use case in License plate monitoring."""
    enable_smoothing: bool = False
    smoothing_algorithm: str = "observability"  # "window" or "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5
    confidence_threshold: float = 0.5
    frame_skip: int = 1
    fps: Optional[float] = None
    bbox_format: str = "auto"
    usecase_categories: List[str] = field(default_factory=lambda: ['license_plate'])
    target_categories: List[str] = field(default_factory=lambda: ['license_plate'])
    alert_config: Optional[AlertConfig] = None
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {0: "license_plate"})
    language: List[str] = field(default_factory=lambda: ['en'])
    country: str = field(default_factory=lambda: 'us')
    ocr_mode:str = field(default_factory=lambda: "numeric") # "alphanumeric" or "numeric" or "alphabetic"
    session: Optional[Session] = None
    lpr_server_id: Optional[str] = None  # Optional LPR server ID for remote logging
    plate_log_cooldown: float = 30.0  # Cooldown period in seconds for logging same plate
    
    def validate(self) -> List[str]:
        """Validate configuration parameters."""
        errors = super().validate()
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if self.frame_skip <= 0:
            errors.append("frame_skip must be positive")
        if self.bbox_format not in ["auto", "xmin_ymin_xmax_ymax", "x_y_width_height"]:
            errors.append("bbox_format must be one of: auto, xmin_ymin_xmax_ymax, x_y_width_height")
        if self.smoothing_window_size <= 0:
            errors.append("smoothing_window_size must be positive")
        if self.smoothing_cooldown_frames < 0:
            errors.append("smoothing_cooldown_frames cannot be negative")
        if self.smoothing_confidence_range_factor <= 0:
            errors.append("smoothing_confidence_range_factor must be positive")
        return errors

class LicensePlateMonitorLogger:
    def __init__(self):
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.lpr_server_id = None
        self.server_info = None
        self.plate_log_timestamps: Dict[str, float] = {}  # Track last log time per plate
        self.server_base_url = None
        self.public_ip = self._get_public_ip()

    def initialize_session(self, config: LicensePlateMonitorConfig) -> None:
        """Initialize session and fetch server connection info if lpr_server_id is provided."""
        print("[LP_LOGGING] ===== INITIALIZING LP LOGGER SESSION =====")
        print(f"[LP_LOGGING] Config lpr_server_id: {config.lpr_server_id}")
        self.logger.info("[LP_LOGGING] ===== INITIALIZING LP LOGGER SESSION =====")
        self.logger.info(f"[LP_LOGGING] Config lpr_server_id: {config.lpr_server_id}")
        
        # Use existing session if provided, otherwise create new one
        if self.session and self.server_info and self.server_base_url:
            self.logger.info("[LP_LOGGING] Session already initialized with server info, skipping re-initialization")
            self.logger.info(f"[LP_LOGGING] Using existing server: {self.server_base_url}")
            return
        elif self.session:
            self.logger.info("[LP_LOGGING] Session exists but server info missing, continuing initialization...")
        else:
            self.logger.info("[LP_LOGGING] No existing session, initializing from scratch...")
        
        if config.session:
            self.session = config.session
            self.logger.info("[LP_LOGGING]  Using provided session from config")
        
        if not self.session:
            # Initialize Matrice session
            if not HAS_MATRICE_SESSION:
                self.logger.error("[LP_LOGGING]  Matrice session module not available")
                raise ImportError("Matrice session is required for License Plate Monitoring")
            try:
                self.logger.info("[LP_LOGGING] Creating new Matrice session from environment variables...")
                account_number = os.getenv("MATRICE_ACCOUNT_NUMBER", "")
                access_key_id = os.getenv("MATRICE_ACCESS_KEY_ID", "")
                secret_key = os.getenv("MATRICE_SECRET_ACCESS_KEY", "")
                project_id = os.getenv("MATRICE_PROJECT_ID", "")
                
                self.logger.info(f"[LP_LOGGING] Account Number: {'SET' if account_number else 'NOT SET'}")
                self.logger.info(f"[LP_LOGGING] Access Key ID: {'SET' if access_key_id else 'NOT SET'}")
                self.logger.info(f"[LP_LOGGING] Secret Key: {'SET' if secret_key else 'NOT SET'}")
                self.logger.info(f"[LP_LOGGING] Project ID: {'SET' if project_id else 'NOT SET'}")
                
                self.session = Session(
                    account_number=account_number,
                    access_key=access_key_id,
                    secret_key=secret_key,
                    project_id=project_id,
                )
                self.logger.info("[LP_LOGGING]  Successfully initialized new Matrice session")
            except Exception as e:
                self.logger.error(f"[LP_LOGGING]  Failed to initialize Matrice session: {e}", exc_info=True)
                raise
        
        # Fetch server connection info if lpr_server_id is provided
        if config.lpr_server_id:
            self.lpr_server_id = config.lpr_server_id
            self.logger.info(f"[LP_LOGGING] Fetching LPR server connection info for server ID: {self.lpr_server_id}")
            try:
                self.server_info = self.get_server_connection_info()
                if self.server_info:
                    self.logger.info(f"[LP_LOGGING]  Successfully fetched LPR server info")
                    self.logger.info(f"[LP_LOGGING]   - Name: {self.server_info.get('name', 'Unknown')}")
                    self.logger.info(f"[LP_LOGGING]   - Host: {self.server_info.get('host', 'Unknown')}")
                    self.logger.info(f"[LP_LOGGING]   - Port: {self.server_info.get('port', 'Unknown')}")
                    self.logger.info(f"[LP_LOGGING]   - Status: {self.server_info.get('status', 'Unknown')}")
                    self.logger.info(f"[LP_LOGGING]   - Project ID: {self.server_info.get('projectID', 'Unknown')}")
                    
                    # Compare server host with public IP to determine if it's localhost
                    server_host = self.server_info.get('host', 'localhost')
                    server_port = self.server_info.get('port', 8200)
                    
                    if server_host == self.public_ip:
                        self.server_base_url = f"http://localhost:{server_port}"
                        self.logger.info(f"[LP_LOGGING] Server host matches public IP ({self.public_ip}), using localhost: {self.server_base_url}")
                    else:
                        self.server_base_url = f"http://{server_host}:{server_port}"
                        self.logger.info(f"[LP_LOGGING] LPR server base URL configured: {self.server_base_url}")
                        
                    self.session.update(self.server_info.get('projectID', ''))
                    self.logger.info(f"[LP_LOGGING]  Updated Matrice session with project ID: {self.server_info.get('projectID', '')}")
                else:
                    self.logger.error("[LP_LOGGING]  Failed to fetch LPR server connection info - server_info is None")
                    self.logger.error("[LP_LOGGING] This will prevent plate logging from working!")
            except Exception as e:
                self.logger.error(f"[LP_LOGGING]  Error fetching LPR server connection info: {e}", exc_info=True)
                self.logger.error("[LP_LOGGING] This will prevent plate logging from working!")
        else:
            self.logger.warning("[LP_LOGGING] No lpr_server_id provided in config, skipping server connection info fetch")
        
        print("[LP_LOGGING] ===== LP LOGGER SESSION INITIALIZATION COMPLETE =====")
        self.logger.info("[LP_LOGGING] ===== LP LOGGER SESSION INITIALIZATION COMPLETE =====")
    
    def _get_public_ip(self) -> str:
        """Get the public IP address of this machine."""
        self.logger.info("Fetching public IP address...")
        try:
            public_ip = urllib.request.urlopen("https://v4.ident.me", timeout=120).read().decode("utf8").strip()
            self.logger.info(f"Successfully fetched external IP: {public_ip}")
            return public_ip
        except Exception as e:
            self.logger.error(f"Error fetching external IP: {e}", exc_info=True)
            return "localhost"

    def get_server_connection_info(self) -> Optional[Dict[str, Any]]:
        """Fetch server connection info from RPC."""
        if not self.lpr_server_id:
            self.logger.warning("No lpr_server_id set, cannot fetch server connection info")
            return None
        
        try:
            endpoint = f"/v1/actions/lpr_servers/{self.lpr_server_id}"
            self.logger.info(f"Sending GET request to: {endpoint}")
            response = self.session.rpc.get(endpoint)
            self.logger.info(f"Received response: success={response.get('success')}, code={response.get('code')}, message={response.get('message')}")
            
            if response.get("success", False) and response.get("code") == 200:
                # Response format:
                # {'success': True,
                # 'code': 200,
                # 'message': 'Success',
                # 'serverTime': '2025-10-19T04:58:04Z',
                # 'data': {'id': '68f07e515cd5c6134a075384',
                # 'name': 'lpr-server-1',
                # 'host': '106.219.122.19',
                # 'port': 8200,
                # 'status': 'created',
                # 'accountNumber': '3823255831182978487149732',
                # 'projectID': '68ca6372ab79ba13ef699ba6',
                # 'region': 'United States',
                # 'isShared': False}}
                data = response.get("data", {})
                self.logger.info(f"Server connection info retrieved: name={data.get('name')}, host={data.get('host')}, port={data.get('port')}, status={data.get('status')}")
                return data
            else:
                self.logger.warning(f"Failed to fetch server info: {response.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            self.logger.error(f"Exception while fetching server connection info: {e}", exc_info=True)
            return None

    def should_log_plate(self, plate_text: str, cooldown: float) -> bool:
        """Check if enough time has passed since last log for this plate."""
        current_time = time.time()
        last_log_time = self.plate_log_timestamps.get(plate_text, 0)
        time_since_last_log = current_time - last_log_time
        
        if time_since_last_log >= cooldown:
            print(f"[LP_LOGGING] ✓ Plate '{plate_text}' ready to log ({time_since_last_log:.1f}s since last)")
            self.logger.info(f"[LP_LOGGING] OK - Plate '{plate_text}' ready to log (last logged {time_since_last_log:.1f}s ago, cooldown={cooldown}s)")
            return True
        else:
            print(f"[LP_LOGGING] ⊗ Plate '{plate_text}' in cooldown ({cooldown - time_since_last_log:.1f}s remaining)")
            self.logger.info(f"[LP_LOGGING] SKIP - Plate '{plate_text}' in cooldown period ({time_since_last_log:.1f}s elapsed, {cooldown - time_since_last_log:.1f}s remaining)")
            return False
    
    def update_log_timestamp(self, plate_text: str) -> None:
        """Update the last log timestamp for a plate."""
        self.plate_log_timestamps[plate_text] = time.time()
        self.logger.debug(f"Updated log timestamp for plate: {plate_text}")
    
    def _format_timestamp_rfc3339(self, timestamp: str) -> str:
        """Convert timestamp to RFC3339 format (2006-01-02T15:04:05Z).
        
        Handles various input formats:
        - "YYYY-MM-DD-HH:MM:SS.ffffff UTC"
        - "YYYY:MM:DD HH:MM:SS"
        - Unix timestamp (float/int)
        """
        try:
            # If already in RFC3339 format, return as is
            if 'T' in timestamp and timestamp.endswith('Z'):
                return timestamp
            
            # Try to parse common formats
            dt = None
            
            # Format: "2025-08-19-04:22:47.187574 UTC"
            if '-' in timestamp and 'UTC' in timestamp:
                timestamp_clean = timestamp.replace(' UTC', '')
                dt = datetime.strptime(timestamp_clean, '%Y-%m-%d-%H:%M:%S.%f')
            # Format: "2025:10:23 14:30:45"
            elif ':' in timestamp and ' ' in timestamp:
                dt = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
            # Format: numeric timestamp
            elif timestamp.replace('.', '').isdigit():
                dt = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
            
            if dt is None:
                # Fallback to current time
                dt = datetime.now(timezone.utc)
            else:
                # Ensure timezone is UTC
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            
            # Format to RFC3339: 2006-01-02T15:04:05Z
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            
        except Exception as e:
            self.logger.warning(f"Failed to parse timestamp '{timestamp}': {e}. Using current time.")
            return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    async def log_plate(self, plate_text: str, timestamp: str, stream_info: Dict[str, Any], 
                       image_data: Optional[str] = None, cooldown: float = 30.0) -> bool:
        """Log plate to RPC server with cooldown period.
        
        Args:
            plate_text: The license plate text
            timestamp: Capture timestamp
            stream_info: Stream information dict
            image_data: Base64-encoded JPEG image of the license plate crop
            cooldown: Cooldown period in seconds
        """
        print(f"[LP_LOGGING] ===== PLATE LOG REQUEST START =====")
        print(f"[LP_LOGGING] Plate: '{plate_text}', Timestamp: {timestamp}")
        self.logger.info(f"[LP_LOGGING] ===== PLATE LOG REQUEST START =====")
        self.logger.info(f"[LP_LOGGING] Plate: '{plate_text}', Timestamp: {timestamp}")
        
        # Check cooldown
        if not self.should_log_plate(plate_text, cooldown):
            print(f"[LP_LOGGING] Plate '{plate_text}' NOT SENT - cooldown")
            self.logger.info(f"[LP_LOGGING]  Plate '{plate_text}' NOT SENT - skipped due to cooldown period")
            self.logger.info(f"[LP_LOGGING] ===== PLATE LOG REQUEST END (SKIPPED) =====")
            return False
        
        try:
            camera_info = stream_info.get("camera_info", {})
            camera_name = camera_info.get("camera_name", "")
            location = camera_info.get("location", "")
            frame_id = stream_info.get("frame_id", "")
            
            print(f"[LP_LOGGING] Camera: '{camera_name}', Location: '{location}'")
            self.logger.info(f"[LP_LOGGING] Stream Info - Camera: '{camera_name}', Location: '{location}', Frame ID: '{frame_id}'")
            
            # Get project ID from server_info
            project_id = self.server_info.get('projectID', '') if self.server_info else ''
            self.logger.info(f"[LP_LOGGING] Project ID: '{project_id}'")
            
            # Format timestamp to RFC3339 format (2006-01-02T15:04:05Z)
            rfc3339_timestamp = self._format_timestamp_rfc3339(timestamp)
            self.logger.info(f"[LP_LOGGING] Formatted timestamp: {timestamp} -> {rfc3339_timestamp}")
            
            payload = {
                'licensePlate': plate_text,
                'frameId': frame_id,
                'location': location,
                'camera': camera_name,
                'captureTimestamp': rfc3339_timestamp,
                'projectId': project_id,
                'imageData': image_data if image_data else ""
            }
            
            # Add projectId as query parameter
            endpoint = f'/v1/lpr-server/detections?projectId={project_id}'
            full_url = f"{self.server_base_url}{endpoint}"
            print(f"[LP_LOGGING] Sending POST to: {full_url}")
            self.logger.info(f"[LP_LOGGING] Sending POST request to: {full_url}")
            self.logger.info(f"[LP_LOGGING] Payload: licensePlate='{plate_text}', frameId='{frame_id}', location='{location}', camera='{camera_name}', imageData length={len(image_data) if image_data else 0}")
            
            response = await self.session.rpc.post_async(endpoint, payload=payload, base_url=self.server_base_url)
            
            print(f"[LP_LOGGING] Response: {response}")
            self.logger.info(f"[LP_LOGGING]  API Response received: {response}")
            
            # Update timestamp after successful log
            self.update_log_timestamp(plate_text)
            print(f"[LP_LOGGING] ✓ Plate '{plate_text}' SUCCESSFULLY SENT")
            self.logger.info(f"[LP_LOGGING]  Plate '{plate_text}' SUCCESSFULLY SENT at {rfc3339_timestamp}")
            self.logger.info(f"[LP_LOGGING] ===== PLATE LOG REQUEST END (SUCCESS) =====")
            return True
            
        except Exception as e:
            print(f"[LP_LOGGING] ✗ Plate '{plate_text}' FAILED - {e}")
            self.logger.error(f"[LP_LOGGING]  Plate '{plate_text}' NOT SENT - Exception occurred: {e}", exc_info=True)
            self.logger.info(f"[LP_LOGGING] ===== PLATE LOG REQUEST END (FAILED) =====")
            return False
        
class LicensePlateMonitorUseCase(BaseProcessor):
    CATEGORY_DISPLAY = {"license_plate": "license_plate"}
    
    def __init__(self):
        super().__init__("license_plate_monitor")
        self.category = "license_plate_monitor"
        self.target_categories = ['license_plate']
        self.CASE_TYPE: Optional[str] = 'license_plate_monitor'
        self.CASE_VERSION: Optional[str] = '1.3'
        self.smoothing_tracker = None
        self.tracker = None
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self._tracking_start_time = None
        self._track_aliases: Dict[Any, Any] = {}
        self._canonical_tracks: Dict[Any, Dict[str, Any]] = {}
        self._track_merge_iou_threshold: float = 0.05
        self._track_merge_time_window: float = 7.0
        self._ascending_alert_list: List[int] = []
        self.current_incident_end_timestamp: str = "N/A"
        self._seen_plate_texts = set()
        # CHANGE: Added _tracked_plate_texts to store the longest plate_text per track_id
        self._tracked_plate_texts: Dict[Any, str] = {}
        # Containers for text stability & uniqueness
        self._unique_plate_texts: Dict[str, str] = {}  # cleaned_text -> original (longest)
        # NEW: track-wise frequency of cleaned texts to pick the dominant variant per track
        self._track_text_counts: Dict[Any, Counter] = defaultdict(Counter)  # track_id -> Counter(cleaned_text -> count)
        # Helper dictionary to keep history of plate texts per track
        self.helper: Dict[Any, List[str]] = {}
        # Map of track_id -> current dominant plate text
        self.unique_plate_track: Dict[Any, str] = {}
        self.image_preprocessor = ImagePreprocessor()
        # OCR model will be lazily initialized when first used
        self.ocr_model = None
        self._ocr_initialization_attempted = False
        # OCR text history for stability checks (text  consecutive frame count)
        self._text_history: Dict[str, int] = {}

        self.start_timer = None
        #self.reset_timer = "2025-08-19-04:22:47.187574 UTC"

        # Minimum length for a valid plate (after cleaning)
        self._min_plate_len = 5
        # number of consecutive frames a plate must appear to be considered "stable"
        self._stable_frames_required = 3
        self._non_alnum_regex = re.compile(r"[^A-Za-z0-9]+")
        self._ocr_mode = None
        #self.jpeg = TurboJPEG()
        
        # Initialize plate logger (optional, only used if lpr_server_id is provided)
        self.plate_logger: Optional[LicensePlateMonitorLogger] = None
        self._logging_enabled = True
        self._plate_logger_initialized = False  # Track if plate logger has been initialized
        

    def reset_tracker(self) -> None:
        """Reset the advanced tracker instance."""
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("AdvancedTracker reset for new tracking session")

    def reset_plate_tracking(self) -> None:
        """Reset plate tracking state."""
        self._seen_plate_texts = set()
        # CHANGE: Reset _tracked_plate_texts
        self._tracked_plate_texts = {}
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self._text_history = {}
        self._unique_plate_texts = {}
        self.helper = {}
        self.unique_plate_track = {}
        self.logger.info("Plate tracking state reset")

    def reset_all_tracking(self) -> None:
        """Reset both advanced tracker and plate tracking state."""
        self.reset_tracker()
        self.reset_plate_tracking()
        self.logger.info("All plate tracking state reset")
    
    def _initialize_plate_logger(self, config: LicensePlateMonitorConfig) -> bool:
        """Initialize the plate logger if lpr_server_id is provided. Returns True if successful."""
        self.logger.info(f"[LP_LOGGING] _initialize_plate_logger called with lpr_server_id: {config.lpr_server_id}")
        
        if not config.lpr_server_id:
            self._logging_enabled = False
            self._plate_logger_initialized = False
            self.logger.warning("[LP_LOGGING] Plate logging disabled: no lpr_server_id provided")
            return False
        
        try:
            if self.plate_logger is None:
                self.logger.info("[LP_LOGGING] Creating new LicensePlateMonitorLogger instance")
                self.plate_logger = LicensePlateMonitorLogger()
            else:
                self.logger.info("[LP_LOGGING] Using existing LicensePlateMonitorLogger instance")
            
            self.logger.info("[LP_LOGGING] Initializing session for plate logger")
            self.plate_logger.initialize_session(config)
            self._logging_enabled = True
            self._plate_logger_initialized = True
            self.logger.info(f"[LP_LOGGING] SUCCESS - Plate logging ENABLED with server ID: {config.lpr_server_id}")
            return True
        except Exception as e:
            self.logger.error(f"[LP_LOGGING] ERROR - Failed to initialize plate logger: {e}", exc_info=True)
            self._logging_enabled = False
            self._plate_logger_initialized = False
            self.logger.error(f"[LP_LOGGING] Plate logging has been DISABLED due to initialization failure")
            return False
    
    async def _log_detected_plates(self, detections: List[Dict[str, Any]], config: LicensePlateMonitorConfig, 
                            stream_info: Optional[Dict[str, Any]], image_bytes: Optional[bytes] = None) -> None:
        """Log all detected plates to RPC server with cooldown."""
        # Enhanced logging for diagnostics
        print(f"[LP_LOGGING] Starting plate logging check - detections count: {len(detections)}")
        self.logger.info(f"[LP_LOGGING] Starting plate logging check - detections count: {len(detections)}")
        self.logger.info(f"[LP_LOGGING] Logging enabled: {self._logging_enabled}, Plate logger exists: {self.plate_logger is not None}, Stream info exists: {stream_info is not None}")
        
        if not self._logging_enabled:
            print("[LP_LOGGING] Plate logging is DISABLED")
            self.logger.warning("[LP_LOGGING] Plate logging is DISABLED - logging_enabled flag is False")
            return
        
        if not self.plate_logger:
            print("[LP_LOGGING] Plate logging SKIPPED - plate_logger not initialized")
            self.logger.warning("[LP_LOGGING] Plate logging SKIPPED - plate_logger is not initialized (lpr_server_id may not be configured)")
            return
        
        if not stream_info:
            print("[LP_LOGGING] Plate logging SKIPPED - stream_info is None")
            self.logger.warning("[LP_LOGGING] Plate logging SKIPPED - stream_info is None")
            return
        
        print("[LP_LOGGING] All pre-conditions met, proceeding with plate logging")
        self.logger.info(f"[LP_LOGGING] All pre-conditions met, proceeding with plate logging")
        
        # Get current timestamp
        current_timestamp = self._get_current_timestamp_str(stream_info, precision=True)
        
        # Encode the full frame image as base64 JPEG
        image_data = ""
        if image_bytes:
            try:
                # Decode image bytes
                image_array = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if image is not None:
                    # Encode as JPEG with 85% quality
                    success, jpeg_buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 99])
                    if success:
                        # Convert to base64
                        image_data = base64.b64encode(jpeg_buffer.tobytes()).decode('utf-8')
                        self.logger.info(f"[LP_LOGGING] Encoded frame image as base64, length: {len(image_data)}")
                    else:
                        self.logger.warning(f"[LP_LOGGING] Failed to encode JPEG image")
                else:
                    self.logger.warning(f"[LP_LOGGING] Failed to decode image bytes")
            except Exception as e:
                self.logger.error(f"[LP_LOGGING] Exception while encoding frame image: {e}", exc_info=True)
        else:
            self.logger.info(f"[LP_LOGGING] No image_bytes provided, sending without image")
        
        # Collect all unique plates from current detections
        plates_to_log = set()
        detections_without_text = 0
        for det in detections:
            plate_text = det.get('plate_text')
            if not plate_text:
                detections_without_text += 1
                continue
            plates_to_log.add(plate_text)
        
        print(f"[LP_LOGGING] Collected {len(plates_to_log)} unique plates to log: {plates_to_log}")
        self.logger.info(f"[LP_LOGGING] Collected {len(plates_to_log)} unique plates to log: {plates_to_log}")
        if detections_without_text > 0:
            self.logger.warning(f"[LP_LOGGING] {detections_without_text} detections have NO plate_text (OCR may have failed or not run yet)")
        
        # Log each unique plate directly with await (respecting cooldown)
        if plates_to_log:
            print(f"[LP_LOGGING] Logging {len(plates_to_log)} plates with cooldown={config.plate_log_cooldown}s")
            self.logger.info(f"[LP_LOGGING] Logging {len(plates_to_log)} plates with cooldown={config.plate_log_cooldown}s")
            try:
                # Call log_plate directly with await for each plate
                for plate_text in plates_to_log:
                    print(f"[LP_LOGGING] Processing plate: {plate_text}")
                    self.logger.info(f"[LP_LOGGING] Processing plate: {plate_text}")
                    try:
                        result = await self.plate_logger.log_plate(
                            plate_text=plate_text,
                            timestamp=current_timestamp,
                            stream_info=stream_info,
                            image_data=image_data,
                            cooldown=config.plate_log_cooldown
                        )
                        status = "SENT" if result else "SKIPPED (cooldown)"
                        print(f"[LP_LOGGING] Plate {plate_text}: {status}")
                        self.logger.info(f"[LP_LOGGING] Plate {plate_text}: {status}")
                    except Exception as e:
                        print(f"[LP_LOGGING] ERROR - Plate {plate_text} failed: {e}")
                        self.logger.error(f"[LP_LOGGING] Plate {plate_text} raised exception: {e}", exc_info=True)
                
                print("[LP_LOGGING] Plate logging complete")
                self.logger.info(f"[LP_LOGGING] Plate logging complete")
            except Exception as e:
                print(f"[LP_LOGGING] CRITICAL ERROR during plate logging: {e}")
                self.logger.error(f"[LP_LOGGING] CRITICAL ERROR during plate logging: {e}", exc_info=True)
        else:
            print("[LP_LOGGING] No plates to log")
            self.logger.info(f"[LP_LOGGING] No plates to log (plates_to_log is empty)")

    async def process(self, data: Any, config: ConfigProtocol, input_bytes: Optional[bytes] = None, 
                context: Optional[ProcessingContext] = None, stream_info: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        processing_start = time.time()
        try:
            if not isinstance(config, LicensePlateMonitorConfig):
                return self.create_error_result("Invalid configuration type for license plate monitoring",
                                               usecase=self.name, category=self.category, context=context)
            
            if context is None:
                context = ProcessingContext()
            
            if not input_bytes:
                return self.create_error_result("input_bytes (video/image) is required for license plate monitoring",
                                               usecase=self.name, category=self.category, context=context)
            
            # Initialize plate logger once if lpr_server_id is provided (optional flow)
            if not self._plate_logger_initialized and config.lpr_server_id:
                self.logger.info(f"[LP_LOGGING] First-time initialization - lpr_server_id: {config.lpr_server_id}")
                success = self._initialize_plate_logger(config)
                if success:
                    self.logger.info(f"[LP_LOGGING] Plate logger initialized successfully and ready to send plates")
                else:
                    self.logger.error(f"[LP_LOGGING] Plate logger initialization FAILED - plates will NOT be sent")
            elif self._plate_logger_initialized:
                self.logger.debug(f"[LP_LOGGING] Plate logger already initialized, skipping re-initialization")
            elif not config.lpr_server_id:
                if self._total_frame_counter == 0:  # Only log once at start
                    self.logger.warning(f"[LP_LOGGING] Plate logging will be DISABLED - no lpr_server_id provided in config")
            
            # Normalize alert_config if provided as a plain dict (JS JSON)
            if isinstance(getattr(config, 'alert_config', None), dict):
                try:
                    config.alert_config = AlertConfig(**config.alert_config)  # type: ignore[arg-type]
                except Exception:
                    pass

            # OCR model will be lazily initialized when _run_ocr is first called
            # No need to initialize here
            
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold
            self._ocr_mode = config.ocr_mode
            self.logger.info(f"Processing license plate monitoring with format: {input_format.value}")
            
            # Step 1: Apply confidence filtering 1
            # print("---------CONFIDENCE FILTERING",config.confidence_threshold)
            # print("---------DATA1--------------",data)
            processed_data = filter_by_confidence(data, config.confidence_threshold)
            #self.logger.debug(f"Applied confidence filtering with threshold {config.confidence_threshold}")
            
            # Step 2: Apply category mapping if provided
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                #self.logger.debug("Applied category mapping")
            #print("---------DATA2--------------",processed_data)
            # Step 3: Filter to target categories (handle dict or list)
            if isinstance(processed_data, dict):
                processed_data = processed_data.get("detections", [])
            # Accept case-insensitive category values and allow overriding via config
            effective_targets = getattr(config, 'target_categories', self.target_categories) or self.target_categories
            targets_lower = {str(cat).lower() for cat in effective_targets}
            processed_data = [d for d in processed_data if str(d.get('category', '')).lower() in targets_lower]
            #self.logger.debug("Applied category filtering")
            
            raw_processed_data = [copy.deepcopy(det) for det in processed_data]
            #print("---------DATA2--------------",processed_data)
            # Step 4: Apply bounding box smoothing if enabled
            if config.enable_smoothing:
                if self.smoothing_tracker is None:
                    smoothing_config = BBoxSmoothingConfig(
                        smoothing_algorithm=config.smoothing_algorithm,
                        window_size=config.smoothing_window_size,
                        cooldown_frames=config.smoothing_cooldown_frames,
                        confidence_threshold=config.confidence_threshold,
                        confidence_range_factor=config.smoothing_confidence_range_factor,
                        enable_smoothing=True
                    )
                    self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)
                processed_data = bbox_smoothing(processed_data, self.smoothing_tracker.config, self.smoothing_tracker)
            
            # Step 5: Apply advanced tracking
            try:
                from ..advanced_tracker import AdvancedTracker
                from ..advanced_tracker.config import TrackerConfig
                if self.tracker is None:
                    tracker_config = TrackerConfig(
                        track_high_thresh=float(config.confidence_threshold),
                        track_low_thresh=max(0.05, float(config.confidence_threshold) / 2),
                        new_track_thresh=float(config.confidence_threshold)
                    )
                    self.tracker = AdvancedTracker(tracker_config)
                    self.logger.info(f"Initialized AdvancedTracker with thresholds: high={tracker_config.track_high_thresh}, "
                                     f"low={tracker_config.track_low_thresh}, new={tracker_config.new_track_thresh}")
                processed_data = self.tracker.update(processed_data)
            except Exception as e:
                self.logger.warning(f"AdvancedTracker failed: {e}")
            #print("---------DATA3--------------",processed_data)
            # Step 6: Update tracking state
            self._update_tracking_state(processed_data)
            #print("---------DATA4--------------",processed_data)
            # Step 7: Attach masks to detections
            processed_data = self._attach_masks_to_detections(processed_data, raw_processed_data)
            #print("---------DATA5--------------",processed_data)
            # Step 8: Perform OCR on media
            ocr_analysis = self._analyze_ocr_in_media(processed_data, input_bytes, config)
            self.logger.info(f"[LP_LOGGING] OCR analysis completed, found {len(ocr_analysis)} results")
            ocr_plates_found = [r.get('plate_text') for r in ocr_analysis if r.get('plate_text')]
            if ocr_plates_found:
                self.logger.info(f"[LP_LOGGING] OCR detected plates: {ocr_plates_found}")
            else:
                self.logger.warning(f"[LP_LOGGING] OCR did not detect any valid plate texts")
            
            # Step 9: Update plate texts
            processed_data = self._update_detections_with_ocr(processed_data, ocr_analysis)
            self._update_plate_texts(processed_data)
            
            # Log final detection state before sending
            final_plates = [d.get('plate_text') for d in processed_data if d.get('plate_text')]
            self.logger.info(f"[LP_LOGGING] After OCR update, {len(final_plates)} detections have plate_text: {final_plates}")
            
            # Step 9.5: Log detected plates to RPC (optional, only if lpr_server_id is provided)
            # Direct await since process is now async
            await self._log_detected_plates(processed_data, config, stream_info, input_bytes)
            
            # Step 10: Update frame counter
            self._total_frame_counter += 1
            
            # Step 11: Extract frame information
            frame_number = None
            if stream_info:
                input_settings = stream_info.get("input_settings", {})
                start_frame = input_settings.get("start_frame")
                end_frame = input_settings.get("end_frame")
                if start_frame is not None and end_frame is not None and start_frame == end_frame:
                    frame_number = start_frame
            
            # Step 12: Calculate summaries
            counting_summary = self._count_categories(processed_data, config)
            counting_summary['total_counts'] = self.get_total_counts()
            
            # Step 13: Generate alerts and summaries
            alerts = self._check_alerts(counting_summary, frame_number, config)
            incidents_list = self._generate_incidents(counting_summary, alerts, config, frame_number, stream_info)
            tracking_stats_list = self._generate_tracking_stats(counting_summary, alerts, config, frame_number, stream_info)
            business_analytics_list = []
            summary_list = self._generate_summary(counting_summary, incidents_list, tracking_stats_list, business_analytics_list, alerts)
            
            # Step 14: Build result
            incidents = incidents_list[0] if incidents_list else {}
            tracking_stats = tracking_stats_list[0] if tracking_stats_list else {}
            business_analytics = business_analytics_list[0] if business_analytics_list else {}
            summary = summary_list[0] if summary_list else {}
            # Build LPR_dict (per-track history) and counter (dominant in last 50%)
            LPR_dict = {}
            counter = {}
            for tid, history in self.helper.items():
                if not history:
                    continue
                LPR_dict[str(tid)] = list(history)
                # dominant from last 50%
                half = max(1, len(history) // 2)
                window = history[-half:]
                from collections import Counter as _Ctr
                dom, cnt = _Ctr(window).most_common(1)[0]
                counter[str(tid)] = {"plate": dom, "count": cnt}

            agg_summary = {str(frame_number): {
                "incidents": incidents,
                "tracking_stats": tracking_stats,
                "business_analytics": business_analytics,
                "alerts": alerts,
                "human_text": summary
            }}
            
            context.mark_completed()
            result = self.create_result(
                data={"agg_summary": agg_summary},
                usecase=self.name,
                category=self.category,
                context=context
            )
            proc_time = time.time() - processing_start
            processing_latency_ms = proc_time * 1000.0
            processing_fps = (1.0 / proc_time) if proc_time > 0 else None
            # Log the performance metrics using the module-level logger
            print("latency in ms:",processing_latency_ms,"| Throughput fps:",processing_fps,"| Frame_Number:",self._total_frame_counter)

            return result
            
        except Exception as e:
            self.logger.error(f"License plate monitoring failed: {str(e)}", exc_info=True)
            if context:
                context.mark_completed()
            return self.create_error_result(str(e), type(e).__name__, usecase=self.name, category=self.category, context=context)

    def _is_video_bytes(self, media_bytes: bytes) -> bool:
        """Determine if bytes represent a video file."""
        video_signatures = [
            b'\x00\x00\x00\x20ftypmp4',  # MP4
            b'\x00\x00\x00\x18ftypmp4',  # MP4 variant
            b'RIFF',  # AVI
            b'\x1aE\xdf\xa3',  # MKV/WebM
            b'ftyp',  # General MP4 family
        ]
        for signature in video_signatures:
            if media_bytes.startswith(signature) or signature in media_bytes[:50]:
                return True
        return False

    def _analyze_ocr_in_media(self, data: Any, media_bytes: bytes, config: LicensePlateMonitorConfig) -> List[Dict[str, Any]]:
        """Analyze OCR of license plates in video frames or images."""
        return self._analyze_ocr_in_image(data, media_bytes, config)


    def _analyze_ocr_in_image(self, data: Any, image_bytes: bytes, config: LicensePlateMonitorConfig) -> List[Dict[str, Any]]:
        """Analyze OCR in a single image."""
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        #image = self.jpeg.decode(image_bytes, pixel_format=TJPF_RGB) #cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
        
        if image is None:
            raise RuntimeError("Failed to decode image from bytes")
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ocr_analysis = []
        detections = self._get_frame_detections(data, "0")

        #print("OCR-detections", detections)
        
        for detection in detections:
            #print("---------OCR DETECTION",detection)
            if detection.get("confidence", 1.0) < config.confidence_threshold:
                continue

            bbox = detection.get("bounding_box", detection.get("bbox"))
            #print("---------OCR BBOX",bbox)
            if not bbox:
                continue

            crop = self._crop_bbox(rgb_image, bbox, config.bbox_format)
            #print("---------OCR CROP SIZEE",crop.size)
            if crop.size == 0:
                continue
            
            plate_text_raw = self._run_ocr(crop)
            #print("---------OCR PLATE TEXT",plate_text_raw)
            plate_text = plate_text_raw if plate_text_raw else None

            ocr_record = {
                "frame_id": "0",
                "timestamp": 0.0,
                "category": detection.get("category", ""),
                "confidence": round(detection.get("confidence", 0.0), 3),
                "plate_text": plate_text,
                "bbox": bbox,
                "detection_id": detection.get("id", f"det_{len(ocr_analysis)}"),
                "track_id": detection.get("track_id")
            }
            ocr_analysis.append(ocr_record)
        
        return ocr_analysis

    def _crop_bbox(self, image: np.ndarray, bbox: Dict[str, Any], bbox_format: str) -> np.ndarray:
        """Crop bounding box region from image."""
        h, w = image.shape[:2]
        
        if bbox_format == "auto":
            if "xmin" in bbox:
                bbox_format = "xmin_ymin_xmax_ymax"
            elif "x" in bbox:
                bbox_format = "x_y_width_height"
            else:
                return np.zeros((0, 0, 3), dtype=np.uint8)
                
        if bbox_format == "xmin_ymin_xmax_ymax":
            xmin = max(0, int(bbox["xmin"]))
            ymin = max(0, int(bbox["ymin"]))
            xmax = min(w, int(bbox["xmax"]))
            ymax = min(h, int(bbox["ymax"]))
        elif bbox_format == "x_y_width_height":
            xmin = max(0, int(bbox["x"]))
            ymin = max(0, int(bbox["y"]))
            xmax = min(w, int(bbox["x"] + bbox["width"]))
            ymax = min(h, int(bbox["y"] + bbox["height"]))
        else:
            return np.zeros((0, 0, 3), dtype=np.uint8)
            
        return image[ymin:ymax, xmin:xmax]

    # ------------------------------------------------------------------
    # Fast OCR helpers
    # ------------------------------------------------------------------
    def _ensure_ocr_model_loaded(self) -> bool:
        """Lazy initialization of OCR model. Returns True if model is available."""
        if self.ocr_model is not None:
            return True
        
        if self._ocr_initialization_attempted:
            return False
        
        self._ocr_initialization_attempted = True
        
        # Try to get the LicensePlateRecognizer class
        LicensePlateRecognizerClass = _get_license_plate_recognizer_class()
        
        if LicensePlateRecognizerClass is None:
            self.logger.error("OCR module not available. LicensePlateRecognizer will not function.")
            return False
        
        # Try to initialize the OCR model
        try:
            self.ocr_model = LicensePlateRecognizerClass('cct-s-v1-global-model')
            source_msg = {
                "local_repo": "from local repo",
                "installed_package": "from installed package",
                "installed_package_gpu": "from installed package (GPU)",
                "installed_package_cpu": "from installed package (CPU)"
            }.get(_OCR_IMPORT_SOURCE, "from unknown source")
            self.logger.info(f"LicensePlateRecognizer loaded successfully {source_msg}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize LicensePlateRecognizer: {e}", exc_info=True)
            self.ocr_model = None
            return False
    
    def _clean_text(self, text: str) -> str:
        """Sanitise OCR output to keep only alphanumerics and uppercase."""
        if not text:
            return ""
        return self._non_alnum_regex.sub('', text).upper()

    def _run_ocr(self, crop: np.ndarray) -> str:
        """Run OCR on a cropped plate image and return cleaned text or empty string."""
        if crop is None or crop.size == 0:
            return ""
        
        # Lazy load OCR model on first use
        if not self._ensure_ocr_model_loaded():
            return ""
        
        # Double-check model is available
        if self.ocr_model is None:
            return ""
        
        # Check if we have a valid OCR model with run method
        if not hasattr(self.ocr_model, 'run'):
            return ""
            
        try:
            # fast_plate_ocr LicensePlateRecognizer has a run() method
            res = self.ocr_model.run(crop)
            
            if isinstance(res, list):
                res = res[0] if res else ""
            cleaned_text = self._clean_text(str(res))
            if cleaned_text and len(cleaned_text) >= self._min_plate_len:
                if self._ocr_mode == "numeric":
                    response = all(ch.isdigit() for ch in cleaned_text) 
                elif self._ocr_mode == "alphabetic":
                    response = all(ch.isalpha() for ch in cleaned_text)
                elif self._ocr_mode == "alphanumeric":
                    response = True
                else:
                    response = False
                
                if response:
                    return cleaned_text
            return ""
        except Exception as exc:
            # Only log at debug level to avoid spam
            self.logger.warning(f"OCR failed: {exc}")
            return ""

    def _get_frame_detections(self, data: Any, frame_key: str) -> List[Dict[str, Any]]:
        """Extract detections for a specific frame from data."""
        if isinstance(data, dict):
            return data.get(frame_key, [])
        elif isinstance(data, list):
            return data
        else:
            return []

    def _update_detections_with_ocr(self, detections: List[Dict[str, Any]], ocr_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update detections with OCR results using track_id or bounding box for matching."""
        #print("---------UPDATE DETECTIONS WITH OCR",ocr_analysis)
        ocr_dict = {}
        for rec in ocr_analysis:
            if rec.get("plate_text"):
                # Primary key: track_id
                track_id = rec.get("track_id")
                if track_id is not None:
                    ocr_dict[track_id] = rec["plate_text"]
                # Fallback key: bounding box as tuple
                else:
                    bbox_key = tuple(sorted(rec["bbox"].items())) if rec.get("bbox") else None
                    if bbox_key:
                        ocr_dict[bbox_key] = rec["plate_text"]
                #self.logger.info(f"OCR record: track_id={track_id}, plate_text={rec.get('plate_text')}, bbox={rec.get('bbox')}")
        
        #print("---------UPDATE DETECTIONS WITH OCR -II",ocr_dict)
        for det in detections:
            track_id = det.get("track_id")
            bbox_key = tuple(sorted(det.get("bounding_box", det.get("bbox", {})).items())) if det.get("bounding_box") or det.get("bbox") else None
            plate_text = None
            if track_id is not None and track_id in ocr_dict:
                plate_text = ocr_dict[track_id]
            elif bbox_key and bbox_key in ocr_dict:
                plate_text = ocr_dict[bbox_key]
            det["plate_text"] = plate_text
            #self.logger.info(f"Detection track_id={track_id}, bbox={det.get('bounding_box')}: Assigned plate_text={plate_text}")
        return detections

    def _count_categories(self, detections: List[Dict], config: LicensePlateMonitorConfig) -> Dict[str, Any]:
        """Count unique licence-plate texts per frame and attach detections."""
        unique_texts: set = set()
        valid_detections: List[Dict[str, Any]] = []

        # Group detections by track_id for per-track dominance
        tracks: Dict[Any, List[Dict[str, Any]]] = {}
        for det in detections:
            if not all(k in det for k in ['category', 'confidence', 'bounding_box']):
                continue
            tid = det.get('track_id')
            if tid is None:
                # If no track id, treat as its own pseudo-track keyed by bbox
                tid = (det.get("bounding_box") or det.get("bbox"))
            tracks.setdefault(tid, []).append(det)

        for tid, dets in tracks.items():
            # Pick a representative bbox (first occurrence)
            rep = dets[0]
            cat = rep.get('category', '')
            bbox = rep.get('bounding_box')
            conf = rep.get('confidence')
            frame_id = rep.get('frame_id')

            # Compute dominant text for this track from last 50% of history
            dominant_text = None
            history = self.helper.get(tid, [])
            if history:
                half = max(1, len(history) // 2)
                window = history[-half:]
                from collections import Counter as _Ctr
                dominant_text, _ = _Ctr(window).most_common(1)[0]
            elif rep.get('plate_text'):
                candidate = self._clean_text(rep.get('plate_text', ''))
                if self._min_plate_len <= len(candidate) <= 6:
                    dominant_text = candidate

            # Fallback to already computed per-track mapping
            if not dominant_text:
                dominant_text = self.unique_plate_track.get(tid)

            # Enforce length 56 and uniqueness per frame
            if dominant_text and self._min_plate_len <= len(dominant_text) <= 6:
                unique_texts.add(dominant_text)
                valid_detections.append({
                    "bounding_box": bbox,
                    "category": cat,
                    "confidence": conf,
                    "track_id": rep.get('track_id'),
                    "frame_id": frame_id,
                    "masks": rep.get("masks", []),
                    "plate_text": dominant_text
                })

        counts = {"License_Plate": len(unique_texts)} if unique_texts else {}

        return {
            "total_count": len(unique_texts),
            "per_category_count": counts,
            "detections": valid_detections
        }

    def _generate_tracking_stats(self, counting_summary: Dict, alerts: Any, config: LicensePlateMonitorConfig,
                                frame_number: Optional[int] = None, stream_info: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Generate structured tracking stats with frame-based keys."""
        tracking_stats = []
        total_detections = counting_summary.get("total_count", 0)
        total_counts = counting_summary.get("total_counts", {})
        cumulative_total = sum(set(total_counts.values())) if total_counts else 0
        per_category_count = counting_summary.get("per_category_count", {})
        track_ids_info = self._get_track_ids_info(counting_summary.get("detections", []))
        current_timestamp = self._get_current_timestamp_str(stream_info, precision=False)
        start_timestamp = self._get_start_timestamp_str(stream_info, precision=False)
        high_precision_start_timestamp = self._get_current_timestamp_str(stream_info, precision=True)
        high_precision_reset_timestamp = self._get_start_timestamp_str(stream_info, precision=True)
        camera_info = self.get_camera_info_from_stream(stream_info)
        
        human_text_lines = []
        #print("counting_summary", counting_summary)
        human_text_lines.append(f"CURRENT FRAME @ {current_timestamp}:")
        if total_detections > 0:
            category_counts = [f"{count} {cat}" for cat, count in per_category_count.items()]
            detection_text = category_counts[0] + " detected" if len(category_counts) == 1 else f"{', '.join(category_counts[:-1])}, and {category_counts[-1]} detected"
            human_text_lines.append(f"\t- {detection_text}")
            # Show dominant per-track license plates for current frame
            seen = set()
            display_texts = []
            for det in counting_summary.get("detections", []):
                t = det.get("track_id")
                dom = det.get("plate_text")
                if not dom or not (self._min_plate_len <= len(dom) <= 6):
                    continue
                if t in seen:
                    continue
                seen.add(t)
                display_texts.append(dom)
            if display_texts:
                human_text_lines.append(f"\t- License Plates: {', '.join(display_texts)}")
        else:
            human_text_lines.append(f"\t- No detections")
        
        human_text_lines.append("")
        human_text_lines.append(f"TOTAL SINCE {start_timestamp}:")
        human_text_lines.append(f"\t- Total Detected: {cumulative_total}")

        if self._unique_plate_texts:
            human_text_lines.append("\t- Unique License Plates:")
            for text in sorted(self._unique_plate_texts.values()):
                human_text_lines.append(f"\t\t- {text}")

        current_counts = [{"category": cat, "count": count} for cat, count in per_category_count.items() if count > 0 or total_detections > 0]
        total_counts_list = [{"category": cat, "count": count} for cat, count in total_counts.items() if count > 0 or cumulative_total > 0]
        
        human_text = "\n".join(human_text_lines)
        detections = []
        for detection in counting_summary.get("detections", []):
            dom = detection.get("plate_text", "")
            if not dom:
                dom = "license_plate"
            bbox = detection.get("bounding_box", {})
            category = detection.get("category", "license_plate")
            segmentation = detection.get("masks", detection.get("segmentation", detection.get("mask", [])))
            detection_obj = self.create_detection_object(category, bbox, segmentation=None, plate_text=dom)
            detections.append(detection_obj)
        
        alert_settings = []
        # Build alert settings tolerating dict or dataclass for alert_config
        if config.alert_config:
            alert_cfg = config.alert_config
            alert_type = getattr(alert_cfg, 'alert_type', None) if not isinstance(alert_cfg, dict) else alert_cfg.get('alert_type')
            alert_value = getattr(alert_cfg, 'alert_value', None) if not isinstance(alert_cfg, dict) else alert_cfg.get('alert_value')
            count_thresholds = getattr(alert_cfg, 'count_thresholds', None) if not isinstance(alert_cfg, dict) else alert_cfg.get('count_thresholds')
            alert_type = alert_type if isinstance(alert_type, list) else (list(alert_type) if alert_type is not None else ['Default'])
            alert_value = alert_value if isinstance(alert_value, list) else (list(alert_value) if alert_value is not None else ['JSON'])
            alert_settings.append({
                "alert_type": alert_type,
                "incident_category": self.CASE_TYPE,
                "threshold_level": count_thresholds or {},
                "ascending": True,
                "settings": {t: v for t, v in zip(alert_type, alert_value)}
            })
        
        if alerts:
            human_text_lines.append(f"Alerts: {alerts[0].get('settings', {})}")
        else:
            human_text_lines.append("Alerts: None")
        
        human_text = "\n".join(human_text_lines)
        reset_settings = [{"interval_type": "daily", "reset_time": {"value": 9, "time_unit": "hour"}}]
        
        tracking_stat = self.create_tracking_stats(
            total_counts=total_counts_list,
            current_counts=current_counts,
            detections=detections,
            human_text=human_text,
            camera_info=camera_info,
            alerts=alerts,
            alert_settings=alert_settings,
            reset_settings=reset_settings,
            start_time=high_precision_start_timestamp,
            reset_time=high_precision_reset_timestamp
        )
        tracking_stats.append(tracking_stat)
        return tracking_stats

    def _check_alerts(self, summary: Dict, frame_number: Any, config: LicensePlateMonitorConfig) -> List[Dict]:
        """Check if any alert thresholds are exceeded."""
        def get_trend(data, lookback=900, threshold=0.6):
            window = data[-lookback:] if len(data) >= lookback else data
            if len(window) < 2:
                return True
            increasing = sum(1 for i in range(1, len(window)) if window[i] >= window[i - 1])
            return increasing / (len(window) - 1) >= threshold

        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        alerts = []
        total_detections = summary.get("total_count", 0)
        total_counts_dict = summary.get("total_counts", {})
        cumulative_total = sum(total_counts_dict.values()) if total_counts_dict else 0
        per_category_count = summary.get("per_category_count", {})

        if not config.alert_config:
            return alerts

        # Extract thresholds regardless of dict/dataclass
        _alert_cfg = config.alert_config
        _thresholds = getattr(_alert_cfg, 'count_thresholds', None) if not isinstance(_alert_cfg, dict) else _alert_cfg.get('count_thresholds')
        _types = getattr(_alert_cfg, 'alert_type', None) if not isinstance(_alert_cfg, dict) else _alert_cfg.get('alert_type')
        _values = getattr(_alert_cfg, 'alert_value', None) if not isinstance(_alert_cfg, dict) else _alert_cfg.get('alert_value')
        _types = _types if isinstance(_types, list) else (list(_types) if _types is not None else ['Default'])
        _values = _values if isinstance(_values, list) else (list(_values) if _values is not None else ['JSON'])
        if _thresholds:
            for category, threshold in _thresholds.items():
                if category == "all" and total_detections > threshold:
                    alerts.append({
                        "alert_type": _types,
                        "alert_id": f"alert_{category}_{frame_key}",
                        "incident_category": self.CASE_TYPE,
                        "threshold_level": threshold,
                        "ascending": get_trend(self._ascending_alert_list),
                        "settings": {t: v for t, v in zip(_types, _values)}
                    })
                elif category in per_category_count and per_category_count[category] > threshold:
                    alerts.append({
                        "alert_type": _types,
                        "alert_id": f"alert_{category}_{frame_key}",
                        "incident_category": self.CASE_TYPE,
                        "threshold_level": threshold,
                        "ascending": get_trend(self._ascending_alert_list),
                        "settings": {t: v for t, v in zip(_types, _values)}
                    })
        return alerts

    def _generate_incidents(self, counting_summary: Dict, alerts: List, config: LicensePlateMonitorConfig,
                           frame_number: Optional[int] = None, stream_info: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Generate structured incidents."""
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        incidents = []
        total_detections = counting_summary.get("total_count", 0)
        current_timestamp = self._get_current_timestamp_str(stream_info, precision=False)
        camera_info = self.get_camera_info_from_stream(stream_info)
        
        self._ascending_alert_list = self._ascending_alert_list[-900:] if len(self._ascending_alert_list) > 900 else self._ascending_alert_list

        if total_detections > 0:
            level = "low"
            intensity = 5.0
            start_timestamp = self._get_start_timestamp_str(stream_info, precision=False)
            if start_timestamp and self.current_incident_end_timestamp == 'N/A':
                self.current_incident_end_timestamp = 'Incident still active'
            elif start_timestamp and self.current_incident_end_timestamp == 'Incident still active':
                if len(self._ascending_alert_list) >= 15 and sum(self._ascending_alert_list[-15:]) / 15 < 1.5:
                    self.current_incident_end_timestamp = current_timestamp
            elif self.current_incident_end_timestamp != 'Incident still active' and self.current_incident_end_timestamp != 'N/A':
                self.current_incident_end_timestamp = 'N/A'
                
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 15)
                intensity = min(10.0, (total_detections / threshold) * 10)
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
            else:
                if total_detections > 30:
                    level = "critical"
                    intensity = 10.0
                    self._ascending_alert_list.append(3)
                elif total_detections > 25:
                    level = "significant"
                    intensity = 9.0
                    self._ascending_alert_list.append(2)
                elif total_detections > 15:
                    level = "medium"
                    intensity = 7.0
                    self._ascending_alert_list.append(1)
                else:
                    level = "low"
                    intensity = min(10.0, total_detections / 3.0)
                    self._ascending_alert_list.append(0)

            human_text_lines = [f"INCIDENTS DETECTED @ {current_timestamp}:"]
            human_text_lines.append(f"\tSeverity Level: {(self.CASE_TYPE, level)}")
            human_text = "\n".join(human_text_lines)

            alert_settings = []
            if config.alert_config:
                _alert_cfg = config.alert_config
                _types = getattr(_alert_cfg, 'alert_type', None) if not isinstance(_alert_cfg, dict) else _alert_cfg.get('alert_type')
                _values = getattr(_alert_cfg, 'alert_value', None) if not isinstance(_alert_cfg, dict) else _alert_cfg.get('alert_value')
                _thresholds = getattr(_alert_cfg, 'count_thresholds', None) if not isinstance(_alert_cfg, dict) else _alert_cfg.get('count_thresholds')
                _types = _types if isinstance(_types, list) else (list(_types) if _types is not None else ['Default'])
                _values = _values if isinstance(_values, list) else (list(_values) if _values is not None else ['JSON'])
                alert_settings.append({
                    "alert_type": _types,
                    "incident_category": self.CASE_TYPE,
                    "threshold_level": _thresholds or {},
                    "ascending": True,
                    "settings": {t: v for t, v in zip(_types, _values)}
                })
        
            event = self.create_incident(
                incident_id=f"{self.CASE_TYPE}_{frame_key}",
                incident_type=self.CASE_TYPE,
                severity_level=level,
                human_text=human_text,
                camera_info=camera_info,
                alerts=alerts,
                alert_settings=alert_settings,
                start_time=start_timestamp,
                end_time=self.current_incident_end_timestamp,
                level_settings={"low": 1, "medium": 3, "significant": 4, "critical": 7}
            )
            incidents.append(event)
        else:
            self._ascending_alert_list.append(0)
            incidents.append({})

        return incidents

    def _generate_summary(self, summary: Dict, incidents: List, tracking_stats: List, business_analytics: List, alerts: List) -> List[str]:
        """Generate a human-readable summary."""
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

    def _update_tracking_state(self, detections: List[Dict]):
        """Track unique track_ids per category."""
        if not hasattr(self, "_per_category_total_track_ids"):
            self._per_category_total_track_ids = {cat: set() for cat in self.target_categories}
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

    def _update_plate_texts(self, detections: List[Dict]):
        """Update set of seen plate texts and track the longest plate_text per track_id."""
        for det in detections:
            raw_text = det.get('plate_text')
            track_id = det.get('track_id')
            if not raw_text or track_id is None:
                continue

            cleaned = self._clean_text(raw_text)

            # Enforce plate length 5 or 6 characters ("greater than 4 and less than 7")
            if not (self._min_plate_len <= len(cleaned) <= 6):
                continue

            # Append to per-track rolling history (keep reasonable size)
            history = self.helper.get(track_id)
            if history is None:
                history = []
                self.helper[track_id] = history
            history.append(cleaned)
            if len(history) > 200:
                del history[: len(history) - 200]

            # Update per-track frequency counter (all-time)
            self._track_text_counts[track_id][cleaned] += 1

            # Update consecutive frame counter for stability across whole video
            self._text_history[cleaned] = self._text_history.get(cleaned, 0) + 1

            # Once stable, decide dominant text from LAST 50% of history
            if self._text_history[cleaned] >= self._stable_frames_required:
                half = max(1, len(history) // 2)
                window = history[-half:]
                from collections import Counter as _Ctr
                dominant, _ = _Ctr(window).most_common(1)[0]

                # Update per-track mapping to dominant
                self._tracked_plate_texts[track_id] = dominant
                self.unique_plate_track[track_id] = dominant

                # Maintain global unique mapping with dominant only
                if dominant not in self._unique_plate_texts:
                    self._unique_plate_texts[dominant] = dominant

        # Reset counters for texts NOT seen in this frame (to preserve stability requirement)
        current_frame_texts = {self._clean_text(det.get('plate_text', '')) for det in detections if det.get('plate_text')}
        for t in list(self._text_history.keys()):
            if t not in current_frame_texts:
                self._text_history[t] = 0

    def get_total_counts(self):
        """Return total unique license plate texts encountered so far."""
        return {'License_Plate': len(self._unique_plate_texts)}

    def _get_track_ids_info(self, detections: List[Dict]) -> Dict[str, Any]:
        """Get detailed information about track IDs."""
        frame_track_ids = {det.get('track_id') for det in detections if det.get('track_id') is not None}
        total_track_ids = set()
        for s in getattr(self, '_per_category_total_track_ids', {}).values():
            total_track_ids.update(s)
        return {
            "total_count": len(total_track_ids),
            "current_frame_count": len(frame_track_ids),
            "total_unique_track_ids": len(total_track_ids),
            "current_frame_track_ids": list(frame_track_ids),
            "last_update_time": time.time(),
            "total_frames_processed": getattr(self, '_total_frame_counter', 0)
        }

    def _compute_iou(self, box1: Any, box2: Any) -> float:
        """Compute IoU between two bounding boxes."""
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

    def _format_timestamp_for_stream(self, timestamp: float) -> str:
        """Format timestamp for streams (YYYY:MM:DD HH:MM:SS format)."""
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime('%Y:%m:%d %H:%M:%S')

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
    
    def _get_tracking_start_time(self) -> str:
        """Get the tracking start time, formatted as a string."""
        if self._tracking_start_time is None:
            return "N/A"
        return self._format_timestamp(self._tracking_start_time)

    def _set_tracking_start_time(self) -> None:
        """Set the tracking start time to the current time."""
        self._tracking_start_time = time.time()

    def _attach_masks_to_detections(self, processed_detections: List[Dict[str, Any]], raw_detections: List[Dict[str, Any]], 
                                    iou_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Attach segmentation masks from raw detections to processed detections."""
        if not processed_detections or not raw_detections:
            for det in processed_detections:
                det.setdefault("masks", [])
            return processed_detections

        used_raw_indices = set()
        for det in processed_detections:
            best_iou = 0.0
            best_idx = None
            for idx, raw_det in enumerate(raw_detections):
                if idx in used_raw_indices:
                    continue
                iou = self._compute_iou(det.get("bounding_box"), raw_det.get("bounding_box"))
                if iou > best_iou:
                    best_iou = iou
                    best_idx = idx
            if best_idx is not None and best_iou >= iou_threshold:
                raw_det = raw_detections[best_idx]
                masks = raw_det.get("masks", raw_det.get("mask"))
                if masks is not None:
                    det["masks"] = masks
                used_raw_indices.add(best_idx)
            else:
                det.setdefault("masks", ["EMPTY"])
        return processed_detections