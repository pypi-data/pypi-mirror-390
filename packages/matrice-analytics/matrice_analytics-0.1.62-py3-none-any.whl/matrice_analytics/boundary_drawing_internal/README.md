# 🎯 Boundary Drawing Tool

A comprehensive tool for creating interactive boundary definitions from video frames or images. Perfect for defining zones like queues, staff areas, entry/exit points, security zones, and more for computer vision applications.

## 📋 Features

- **Multi-format Support**: Works with videos (MP4, AVI, MOV, etc.) and images (JPG, PNG, etc.)
- **Interactive HTML Interface**: User-friendly drag-and-drop interface with real-time visualization
- **Multiple Zone Types**: Pre-defined zone types with custom tag support
- **Drawing Modes**: Support for both polygons and lines
- **Grid Reference**: Optional grid overlay for precise coordinate placement
- **Code Generation**: Automatic Python code generation ready for use in applications
- **Save/Load Configurations**: Export and import zone configurations as JSON
- **Real-time Preview**: Live preview of drawn zones with color coding
- **Browser-based**: No additional software required - works in any modern web browser

## 🚀 Quick Start

### Easy Import and Use (Recommended)

The simplest way to use the boundary drawing tool:

```python
# One-line usage for any video or image
from matrice_analytics.boundary_drawing_internal import quick_boundary_tool

# Creates tool and opens in browser automatically
quick_boundary_tool("my_video.mp4", zones_needed=["queue", "staff", "exit"])
```

Or use the class for more control:

```python
from matrice_analytics.boundary_drawing_internal import EasyBoundaryTool

# Initialize with custom settings
tool = EasyBoundaryTool(auto_open_browser=True, grid_step=50)

# Create from video (auto-extracts first frame)
html_path = tool.create_from_video("security_camera.mp4")

# Or create from image
html_path = tool.create_from_image("frame.jpg")

# Auto-detect file type
html_path = tool.quick_setup("any_file.mp4", zones_needed=["queue", "staff"])
```

Create a standalone drag & drop tool:

```python
from matrice_analytics.boundary_drawing_internal import create_standalone_tool

# Creates a tool that accepts any uploaded file
create_standalone_tool("my_boundary_tool.html")
```

### Command Line Usage

```bash
# Process a video file
python boundary_drawing_internal.py --input video.mp4

# Process an image with custom grid spacing
python boundary_drawing_internal.py --input frame.jpg --grid-step 25

# Create tool without opening browser automatically
python boundary_drawing_internal.py --input video.mp4 --no-browser

# Specify output directory
python boundary_drawing_internal.py --input video.mp4 --output ./boundaries/
```

### Programmatic Usage

```python
from matrice_analytics.boundary_drawing_internal import BoundaryDrawingTool

# Initialize the tool
tool = BoundaryDrawingTool()

# Process a video file
results = tool.process_input_file(
    input_path="video.mp4",
    output_dir="./boundaries/",
    grid_step=50,
    open_browser=True,
    embed_image=True
)

# Or just extract first frame
frame_path = tool.extract_first_frame("video.mp4", "first_frame.jpg")

# Create grid reference
grid_path = tool.create_grid_reference_image("first_frame.jpg", "grid.jpg")

# Create interactive HTML tool
html_path = tool.create_interactive_html("grid.jpg", "tool.html")
```

## 🎨 Zone Types

The tool comes with pre-defined zone types, each with distinct colors:

- 🏃 **Queue Area** (Green) - Customer queue zones
- 👥 **Staff Area** (Teal) - Staff working areas  
- 🚪 **Entry Zone** (Yellow) - Entry points
- 🚶 **Exit Zone** (Red) - Exit points
- 🚫 **Restricted** (Purple) - Restricted access areas
- ⏰ **Waiting Area** (Orange) - General waiting areas
- 🛎️ **Service Area** (Mint) - Customer service zones
- 🔒 **Security Zone** (Dark Gray) - Security checkpoints

You can also create **custom zone types** by typing in the custom tag input field.

## 🖱️ How to Use the Interactive Tool

### 1. Load Your File
- **Drag & Drop**: Drag a video or image file onto the upload area
- **Click to Browse**: Click the upload area to select a file
- **Supported Formats**: JPG, PNG, MP4, AVI, MOV, MKV, WMV, FLV, WEBM

### 2. Select Zone Type
- Click on one of the pre-defined zone type buttons
- Or enter a custom zone name in the text field and click "Add"

### 3. Choose Drawing Mode
- **📐 Polygon**: For area definitions (requires minimum 3 points)
- **📏 Line**: For boundary lines (requires exactly 2 points)

### 4. Draw Your Zones
- **Click** on the image to add points
- **Right-click** or press **Enter** to complete the current zone
- **Press Escape** to cancel the current zone
- **Ctrl+Z** to undo the last point

### 5. Export Your Work
- **📋 Generate Code**: Creates Python code ready for use
- **💾 Save Config**: Download configuration as JSON file
- **📁 Load Config**: Load previously saved configurations

## 📝 Generated Code Format

The tool generates Python code in the following format:

```python
# Generated boundary definitions
zones = {
    "queue": [[100, 200], [300, 200], [300, 400], [100, 400]],
    "staff": [[500, 100], [700, 100], [700, 300], [500, 300]],
    "entry": [[50, 50], [150, 100]]
}

# Usage examples:
# For post-processing configuration:
# config.customer_service.customer_areas = zones["queue"]
# config.advanced_tracking.boundary_config = { "points": zones["entry"] }

# Individual zone coordinates:
# queue polygon (4 points):
queue_1 = [[100, 200], [300, 200], [300, 400], [100, 400]]
# staff polygon (4 points):
staff_1 = [[500, 100], [700, 100], [700, 300], [500, 300]]
```

## 🔧 Integration with Matrice SDK

### Customer Service Processor

```python
from matrice_analytics.post_processing import CustomerServiceProcessor

# Use your defined zones
processor = CustomerServiceProcessor(
    customer_areas=zones["queue"],
    staff_areas=zones["staff"],
    service_areas=zones["service"]
)
```

### Advanced Tracking Processor

```python
from matrice_analytics.post_processing import AdvancedTrackingProcessor
from matrice_analytics.post_processing.config import AdvancedTrackingConfig

config = AdvancedTrackingConfig(
    boundary_config={
        "points": zones["entry"],
        "type": "line"
    }
)

processor = AdvancedTrackingProcessor(config)
```

### Counting Processor

```python
from matrice_analytics.post_processing import CountingProcessor

# Count objects in specific zones
results = processor.count_in_zones(
    results=detection_results,
    zones=zones
)
```

## 📁 Output Files

When you run the tool, it creates several files:

- **`*_first_frame.jpg`**: Extracted first frame (for videos)
- **`*_grid_reference.jpg`**: Frame with grid overlay for coordinate reference
- **`*_boundary_tool.html`**: Interactive HTML tool for drawing zones
- **`boundary_config.json`**: Saved zone configurations (when exported)

## ⚙️ Command Line Options

```bash
python boundary_drawing_internal.py [OPTIONS]

Options:
  --input, -i TEXT        Input video or image file [required]
  --output, -o TEXT       Output directory for generated files
  --grid-step INTEGER     Grid line spacing in pixels (default: 50)
  --no-browser           Do not open the tool in browser automatically
  --no-embed             Do not embed image as base64 in HTML
  --help                 Show this message and exit
```

## 🌐 Browser Compatibility

The tool works in all modern web browsers:
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## 📚 Use Cases

### Airport Security
- Define security zones with different threat levels
- Create passenger flow boundaries
- Mark restricted access areas

### Retail Analytics
- Queue management for checkout counters
- Customer flow analysis
- Staff monitoring zones

### Healthcare Facilities
- Patient waiting areas
- Staff-only zones
- Emergency access routes

### Manufacturing
- Worker safety zones
- Quality control areas
- Equipment boundaries

## 🔍 Tips & Best Practices

1. **Use Grid Reference**: Enable grid overlay for precise coordinate placement
2. **Start with Large Areas**: Define major zones first, then refine with smaller areas
3. **Save Frequently**: Export configurations regularly to avoid losing work
4. **Test Different Grid Sizes**: Smaller grid steps (25-30px) for detailed work, larger (75-100px) for quick layouts
5. **Color Coding**: Use the color-coded zones to quickly identify different area types
6. **Custom Tags**: Create meaningful custom zone names for specific use cases

## 🐛 Troubleshooting

### Video Won't Load
- Ensure the video format is supported (MP4, AVI, MOV, etc.)
- Try converting to MP4 if using an uncommon format
- Check that the video file isn't corrupted

### HTML Tool Not Opening
- Check if popup blockers are enabled in your browser
- Manually open the generated HTML file
- Ensure JavaScript is enabled in your browser

### Coordinates Look Wrong
- Verify the grid scale matches your requirements
- Check that you're clicking on the correct positions
- Use the mouse tracker in the bottom-right corner for real-time coordinates

## 📄 License

This tool is part of the Matrice AI SDK and follows the same licensing terms.

## 🤝 Contributing

To contribute to this tool:
1. Follow the existing code style
2. Add tests for new features
3. Update documentation for any changes
4. Submit a pull request with a clear description

## 📞 Support

For support with the boundary drawing tool:
- Check the troubleshooting section above
- Review the examples in the Matrice SDK documentation
- Contact the development team for technical issues 