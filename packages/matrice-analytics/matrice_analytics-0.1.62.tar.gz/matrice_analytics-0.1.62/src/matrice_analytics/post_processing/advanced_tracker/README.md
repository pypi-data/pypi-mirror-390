# Advanced Tracker Integration Guide

This guide explains how to integrate the `AdvancedTracker` into any post-processing use case to enable object tracking capabilities.

## Overview

The `AdvancedTracker` is a BYTETracker-inspired implementation that can be added to any use case to convert raw detection results into tracking results. This enables persistent object identification across frames and improves downstream processing accuracy.

## Quick Integration

### 1. Import the Tracker

Add this import to your use case file:

```python
from ..advanced_tracker import AdvancedTracker, TrackerConfig
```

### 2. Initialize the Tracker

In your use case class `__init__` method:

```python
def __init__(self):
    super().__init__("your_use_case_name")
    self.category = "your_category"
    
    # Initialize the tracker
    self.tracker = AdvancedTracker(TrackerConfig())
```

### 3. Apply Tracking in Process Method

In your `process` method, **before** any other processing:

```python
def process(self, data, config, context=None, stream_info=None):
    # Apply tracking to raw detections
    tracking_results = self.tracker.update(data)
    
    # Continue with your existing processing logic using tracking_results
    # instead of the original data
    return self._process_tracking_results(tracking_results, config, context)
```

## Configuration Parameters

The `TrackerConfig` class provides several parameters to customize tracking behavior:

### Core Tracking Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_high_thresh` | float | 0.6 | High confidence threshold for primary association |
| `track_low_thresh` | float | 0.1 | Low confidence threshold for secondary association |
| `new_track_thresh` | float | 0.7 | Minimum confidence to create new tracks |
| `match_thresh` | float | 0.8 | IoU threshold for track-detection matching |

### Buffer and Timing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_buffer` | int | 30 | Number of frames to keep lost tracks |
| `max_time_lost` | int | 30 | Maximum frames before removing lost tracks |
| `frame_rate` | int | 30 | Video frame rate (used for timing calculations) |

### Algorithm Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fuse_score` | bool | True | Fuse IoU distance with detection scores |
| `enable_gmc` | bool | True | Enable Generalized Motion Compensation |
| `gmc_method` | str | "sparseOptFlow" | GMC method: "orb", "sift", "ecc", "sparseOptFlow", "none" |
| `gmc_downscale` | int | 2 | Downscale factor for GMC processing |

### Output Format Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_format` | str | "tracking" | Output format: "tracking" or "detection" |

### Smoothing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_smoothing` | bool | True | Enable bounding box smoothing |
| `smoothing_algorithm` | str | "observability" | Smoothing algorithm: "window" or "observability" |
| `smoothing_window_size` | int | 20 | Window size for smoothing |
| `smoothing_cooldown_frames` | int | 5 | Cooldown frames for smoothing |

## Example Configurations

### High-Precision Tracking
```python
config = TrackerConfig(
    track_high_thresh=0.8,
    track_low_thresh=0.3,
    new_track_thresh=0.9,
    match_thresh=0.9,
    track_buffer=50,
    fuse_score=True
)
```

### Real-Time Tracking
```python
config = TrackerConfig(
    track_high_thresh=0.4,
    track_low_thresh=0.1,
    new_track_thresh=0.5,
    match_thresh=0.6,
    track_buffer=20,
    enable_gmc=False,  # Disable for speed
    fuse_score=False   # Disable for speed
)
```

### Robust Tracking (for noisy detections)
```python
config = TrackerConfig(
    track_high_thresh=0.3,
    track_low_thresh=0.05,
    new_track_thresh=0.4,
    match_thresh=0.5,
    track_buffer=60,
    enable_smoothing=True,
    smoothing_algorithm="observability",
    smoothing_window_size=30
)
```

## Input/Output Formats

The `AdvancedTracker` accepts various input formats and returns the same format with additional tracking information. The tracker automatically detects the input format and returns results in the corresponding format.

### Input Format Structures

#### 1. Single Frame Detection (List[Dict])

**Format:** List of detection dictionaries for a single frame

```python
# Input: Single frame detections
detections = [
    {
        "bounding_box": {"xmin": 100, "ymin": 200, "xmax": 150, "ymax": 280},
        "confidence": 0.85,
        "category": "person"
    },
    {
        "bounding_box": {"x": 175, "y": 275, "width": 50, "height": 80},  # Center format
        "confidence": 0.92,
        "category": "car"
    },
    {
        "bounding_box": {"x1": 250, "y1": 300, "x2": 300, "y2": 380},    # Alternative format
        "confidence": 0.78,
        "category": "bicycle"
    }
]
```

**Output:** Same list with added tracking fields
```python
# Output: Single frame with tracking info
tracking_results = [
    {
        "bounding_box": {"xmin": 98, "ymin": 198, "xmax": 148, "ymax": 278},
        "confidence": 0.85,
        "category": "person",
        "track_id": 1,        # ← ADDED: Unique track identifier
        "frame_id": 1         # ← ADDED: Current frame number
    },
    {
        "bounding_box": {"xmin": 172, "ymin": 272, "xmax": 222, "ymax": 352},
        "confidence": 0.92,
        "category": "car",
        "track_id": 2,        # ← ADDED: Unique track identifier
        "frame_id": 1         # ← ADDED: Current frame number
    },
    {
        "bounding_box": {"xmin": 250, "ymin": 300, "xmax": 300, "ymax": 380},
        "confidence": 0.78,
        "category": "bicycle",
        "track_id": 3,        # ← ADDED: Unique track identifier
        "frame_id": 1         # ← ADDED: Current frame number
    }
]
```

#### 2. Multi-Frame Detection (Dict[str, List[Dict]])

**Format:** Dictionary with frame keys and detection lists

```python
# Input: Multi-frame detections
detections = {
    "frame_1": [
        {
            "bounding_box": {"xmin": 100, "ymin": 200, "xmax": 150, "ymax": 280},
            "confidence": 0.85,
            "category": "person"
        },
        {
            "bounding_box": {"xmin": 175, "ymin": 275, "xmax": 225, "ymax": 355},
            "confidence": 0.92,
            "category": "car"
        }
    ],
    "frame_2": [
        {
            "bounding_box": {"xmin": 105, "ymin": 205, "xmax": 155, "ymax": 285},
            "confidence": 0.87,
            "category": "person"
        },
        {
            "bounding_box": {"xmin": 180, "ymin": 280, "xmax": 230, "ymax": 360},
            "confidence": 0.89,
            "category": "car"
        }
    ],
    "frame_3": [
        {
            "bounding_box": {"xmin": 110, "ymin": 210, "xmax": 160, "ymax": 290},
            "confidence": 0.86,
            "category": "person"
        }
    ]
}
```

**Output:** Same dictionary structure with tracking info
```python
# Output: Multi-frame with tracking info
tracking_results = {
    "frame_1": [
        {
            "bounding_box": {"xmin": 100, "ymin": 200, "xmax": 150, "ymax": 280},
            "confidence": 0.85,
            "category": "person",
            "track_id": 1,    # ← ADDED: Same track ID across frames
            "frame_id": 1     # ← ADDED: Frame number
        },
        {
            "bounding_box": {"xmin": 175, "ymin": 275, "xmax": 225, "ymax": 355},
            "confidence": 0.92,
            "category": "car",
            "track_id": 2,    # ← ADDED: Same track ID across frames
            "frame_id": 1     # ← ADDED: Frame number
        }
    ],
    "frame_2": [
        {
            "bounding_box": {"xmin": 105, "ymin": 205, "xmax": 155, "ymax": 285},
            "confidence": 0.87,
            "category": "person",
            "track_id": 1,    # ← ADDED: Same track ID (person from frame_1)
            "frame_id": 2     # ← ADDED: Frame number
        },
        {
            "bounding_box": {"xmin": 180, "ymin": 280, "xmax": 230, "ymax": 360},
            "confidence": 0.89,
            "category": "car",
            "track_id": 2,    # ← ADDED: Same track ID (car from frame_1)
            "frame_id": 2     # ← ADDED: Frame number
        }
    ],
    "frame_3": [
        {
            "bounding_box": {"xmin": 110, "ymin": 210, "xmax": 160, "ymax": 290},
            "confidence": 0.86,
            "category": "person",
            "track_id": 1,    # ← ADDED: Same track ID (person from previous frames)
            "frame_id": 3     # ← ADDED: Frame number
        }
    ]
}
```

#### 3. Supported Bounding Box Formats

The tracker automatically detects and converts between different bounding box formats:

```python
# Format 1: Corner coordinates (xmin, ymin, xmax, ymax)
{
    "bounding_box": {"xmin": 100, "ymin": 200, "xmax": 150, "ymax": 280}
}

# Format 2: Center coordinates (x, y, width, height)
{
    "bounding_box": {"x": 125, "y": 240, "width": 50, "height": 80}
}

# Format 3: Alternative corner format (x1, y1, x2, y2)
{
    "bounding_box": {"x1": 100, "y1": 200, "x2": 150, "y2": 280}
}

# Format 4: List format [xmin, ymin, xmax, ymax]
{
    "bounding_box": [100, 200, 150, 280]
}
```

**Note:** The tracker always returns bounding boxes in `{"xmin": ..., "ymin": ..., "xmax": ..., "ymax": ...}` format.

#### 4. Required and Optional Fields

**Required Fields:**
- `bounding_box`: Bounding box coordinates (any supported format)
- `confidence`: Detection confidence score (float, 0.0-1.0)
- `category`: Object category/class (string)

**Optional Fields:**
- `features`: Feature vector for tracking (numpy array)
- `score`: Alternative to `confidence` (float)
- `class`: Alternative to `category` (string)

**Added Fields (Output Only):**
- `track_id`: Unique identifier for the tracked object (int)
- `frame_id`: Current frame number (int)

### Complete Input/Output Examples

#### Example 1: People Detection
```python
# Input
people_detections = [
    {
        "bounding_box": {"xmin": 50, "ymin": 100, "xmax": 120, "ymax": 200},
        "confidence": 0.95,
        "category": "person"
    },
    {
        "bounding_box": {"xmin": 200, "ymin": 150, "xmax": 280, "ymax": 250},
        "confidence": 0.88,
        "category": "person"
    }
]

# Output
tracked_people = [
    {
        "bounding_box": {"xmin": 50, "ymin": 100, "xmax": 120, "ymax": 200},
        "confidence": 0.95,
        "category": "person",
        "track_id": 1,
        "frame_id": 1
    },
    {
        "bounding_box": {"xmin": 200, "ymin": 150, "xmax": 280, "ymax": 250},
        "confidence": 0.88,
        "category": "person",
        "track_id": 2,
        "frame_id": 1
    }
]
```

#### Example 2: Vehicle Tracking Across Frames
```python
# Input: Frame 1
frame1_detections = {
    "frame_001": [
        {"bounding_box": {"xmin": 100, "ymin": 200, "xmax": 180, "ymax": 280}, "confidence": 0.92, "category": "car"},
        {"bounding_box": {"xmin": 300, "ymin": 250, "xmax": 380, "ymax": 330}, "confidence": 0.85, "category": "truck"}
    ]
}

# Output: Frame 1
frame1_tracked = {
    "frame_001": [
        {"bounding_box": {"xmin": 100, "ymin": 200, "xmax": 180, "ymax": 280}, "confidence": 0.92, "category": "car", "track_id": 1, "frame_id": 1},
        {"bounding_box": {"xmin": 300, "ymin": 250, "xmax": 380, "ymax": 330}, "confidence": 0.85, "category": "truck", "track_id": 2, "frame_id": 1}
    ]
}

# Input: Frame 2 (same vehicles, moved positions)
frame2_detections = {
    "frame_002": [
        {"bounding_box": {"xmin": 110, "ymin": 210, "xmax": 190, "ymax": 290}, "confidence": 0.90, "category": "car"},
        {"bounding_box": {"xmin": 310, "ymin": 260, "xmax": 390, "ymax": 340}, "confidence": 0.87, "category": "truck"}
    ]
}

# Output: Frame 2 (same track IDs maintained)
frame2_tracked = {
    "frame_002": [
        {"bounding_box": {"xmin": 110, "ymin": 210, "xmax": 190, "ymax": 290}, "confidence": 0.90, "category": "car", "track_id": 1, "frame_id": 2},
        {"bounding_box": {"xmin": 310, "ymin": 260, "xmax": 390, "ymax": 340}, "confidence": 0.87, "category": "truck", "track_id": 2, "frame_id": 2}
    ]
}
```

#### Example 3: Mixed Categories
```python
# Input: Mixed object types
mixed_detections = [
    {"bounding_box": {"x": 100, "y": 150, "width": 60, "height": 120}, "confidence": 0.95, "category": "person"},
    {"bounding_box": {"xmin": 200, "ymin": 200, "xmax": 280, "ymax": 280}, "confidence": 0.88, "category": "car"},
    {"bounding_box": [300, 250, 350, 320], "confidence": 0.92, "category": "bicycle"}
]

# Output: All converted to standard format with tracking
mixed_tracked = [
    {"bounding_box": {"xmin": 70, "ymin": 90, "xmax": 130, "ymax": 210}, "confidence": 0.95, "category": "person", "track_id": 1, "frame_id": 1},
    {"bounding_box": {"xmin": 200, "ymin": 200, "xmax": 280, "ymax": 280}, "confidence": 0.88, "category": "car", "track_id": 2, "frame_id": 1},
    {"bounding_box": {"xmin": 300, "ymin": 250, "xmax": 350, "ymax": 320}, "confidence": 0.92, "category": "bicycle", "track_id": 3, "frame_id": 1}
]
```

### Key Features of Input/Output Format

1. **Format Preservation**: Output format matches input format exactly
2. **Automatic Conversion**: Supports multiple bounding box formats
3. **Track ID Consistency**: Same objects get same track IDs across frames
4. **Frame ID Addition**: Each detection gets a frame ID
5. **Standardized Output**: All bounding boxes converted to xmin/ymin/xmax/ymax format

## State Preservation Implementation

### ⚠️ Important: Preserving Tracker State

The `AdvancedTracker` maintains state across multiple frames to enable persistent object tracking. **It's crucial to preserve the tracker instance** rather than creating a new one for each frame.

### Correct Implementation Pattern

```python
class YourUseCase(BaseProcessor):
    def __init__(self):
        super().__init__("your_use_case_name")
        self.category = "your_category"
        
        # Initialize tracker as None - will be created on first use
        self.tracker = None
    
    def process(self, data, config, context=None, stream_info=None):
        # Create tracker instance if it doesn't exist (preserves state across frames)
        if self.tracker is None:
            from ..advanced_tracker import AdvancedTracker, TrackerConfig
            tracker_config = TrackerConfig()
            self.tracker = AdvancedTracker(tracker_config)
            self.logger.info("Initialized AdvancedTracker for tracking")
        
        # Apply tracking (same instance used across frames)
        tracking_results = self.tracker.update(data)
        
        # Continue with your processing logic
        return self._process_results(tracking_results, config, context)
    
    def reset_tracker(self) -> None:
        """
        Reset the tracker instance when needed.
        
        Call this when:
        - Starting a completely new tracking session
        - Switching to a different video/stream
        - Manual reset requested by user
        """
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("AdvancedTracker reset for new tracking session")
```

### ❌ Incorrect Implementation (Don't Do This)

```python
def process(self, data, config, context=None):
    # WRONG: Creates new tracker every time - loses all state!
    tracker = AdvancedTracker(TrackerConfig())  # New instance each call
    tracking_results = tracker.update(data)     # No state preservation
```

### Why State Preservation Matters

1. **Track Continuity**: The same object gets the same `track_id` across frames
2. **Lost Track Recovery**: Objects temporarily occluded can be re-associated
3. **Performance**: No need to re-initialize tracking state for each frame
4. **Accuracy**: Better tracking results with historical context

### Integration Examples

#### Vehicle Monitoring Use Case
```python
class VehicleMonitoringUseCase(BaseProcessor):
    def __init__(self):
        super().__init__("vehicle_monitoring")
        self.category = "traffic"
        
        # Initialize tracker as None - will be created on first use
        self.tracker = None
    
    def process(self, data, config, context=None, stream_info=None):
        # Create tracker instance if it doesn't exist (preserves state across frames)
        if self.tracker is None:
            tracker_config = TrackerConfig(
                track_high_thresh=0.6,
                track_low_thresh=0.2,
                new_track_thresh=0.7,
                track_buffer=40,
                enable_smoothing=True
            )
            self.tracker = AdvancedTracker(tracker_config)
            self.logger.info("Initialized AdvancedTracker for vehicle monitoring")
        
        # Apply tracking (same instance used across frames)
        tracking_results = self.tracker.update(data)
        
        # Process tracking results instead of raw detections
        return self._process_vehicle_monitoring(tracking_results, config, context, stream_info)
    
    def reset_tracker(self) -> None:
        """Reset tracker for new tracking session."""
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("Vehicle monitoring tracker reset")
```

#### People Counting Use Case
```python
class PeopleCountingUseCase(BaseProcessor):
    def __init__(self):
        super().__init__("people_counting")
        self.category = "general"
        
        # Initialize tracker as None - will be created on first use
        self.tracker = None
    
    def process(self, data, config, context=None):
        # Create tracker instance if it doesn't exist (preserves state across frames)
        if self.tracker is None:
            tracker_config = TrackerConfig(
                track_high_thresh=0.5,
                track_low_thresh=0.1,
                new_track_thresh=0.6,
                track_buffer=30,
                enable_smoothing=True,
                smoothing_algorithm="observability"
            )
            self.tracker = AdvancedTracker(tracker_config)
            self.logger.info("Initialized AdvancedTracker for people counting")
        
        # Apply tracking to get persistent people IDs
        tracking_results = self.tracker.update(data)
        
        # Use tracking results for counting and zone analysis
        return self._process_people_counting(tracking_results, config, context)
    
    def reset_tracker(self) -> None:
        """Reset tracker for new tracking session."""
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("People counting tracker reset")
```

#### PPE Compliance Use Case (Real Implementation)
```python
class PPEComplianceUseCase(BaseProcessor):
    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"
        
        # List of violation categories to track
        self.violation_categories = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
        
        # Initialize smoothing tracker
        self.smoothing_tracker = None
        
        # Initialize advanced tracker (will be created on first use)
        self.tracker = None

    def process(self, data, config, context=None, stream_info=None):
        # ... existing preprocessing ...
        
        # Advanced tracking (BYTETracker-like)
        try:
            from ..advanced_tracker import AdvancedTracker
            from ..advanced_tracker.config import TrackerConfig
            
            # Create tracker instance if it doesn't exist (preserves state across frames)
            if self.tracker is None:
                tracker_config = TrackerConfig()
                self.tracker = AdvancedTracker(tracker_config)
                self.logger.info("Initialized AdvancedTracker for PPE compliance tracking")
            
            processed_data = self.tracker.update(processed_data)
        except Exception as e:
            self.logger.warning(f"AdvancedTracker failed: {e}")
        
        # ... continue with processing ...
    
    def reset_tracker(self) -> None:
        """Reset the advanced tracker instance."""
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("AdvancedTracker reset for new tracking session")
```

## Best Practices

### 1. Tracker Initialization
- Initialize the tracker as `None` in `__init__` and create it on first use
- This preserves state across multiple `process()` calls
- Use appropriate configuration based on your use case requirements

### 2. Processing Order
- Always apply tracking **before** any other processing
- Use tracking results for all downstream operations

### 3. Configuration Tuning
- Start with default settings and tune based on your specific use case
- Higher thresholds = more precise but fewer tracks
- Lower thresholds = more tracks but potentially less accurate

### 4. State Management
- The tracker maintains state across calls, so it's suitable for video streams
- Use `tracker.reset()` if you need to start fresh tracking

### 5. Performance Considerations
- Disable GMC (`enable_gmc=False`) for faster processing
- Reduce `track_buffer` for memory efficiency
- Adjust `frame_rate` to match your video source

## Troubleshooting

### Common Issues

1. **No tracks being created**: Lower `new_track_thresh` and `track_high_thresh`
2. **Too many false tracks**: Increase `new_track_thresh` and `match_thresh`
3. **Tracks disappearing quickly**: Increase `track_buffer` and `max_time_lost`
4. **Poor tracking accuracy**: Enable smoothing and adjust thresholds

### Debug Information
The tracker provides debug information through logging:
```python
import logging
logging.getLogger('advanced_tracker').setLevel(logging.DEBUG)
```

## Advanced Usage

### Custom Distance Metrics
You can extend the matching logic by modifying the `matching.py` file to add custom distance metrics for your specific use case.

### Multi-Camera Tracking
For multi-camera scenarios, you can use the `location` attribute in tracks to associate objects across cameras.

### Track Persistence
The tracker maintains track state across calls, making it suitable for long video sequences or real-time streams. 