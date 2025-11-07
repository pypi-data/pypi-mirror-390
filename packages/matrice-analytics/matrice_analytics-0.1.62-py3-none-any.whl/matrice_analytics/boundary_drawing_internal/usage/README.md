# Boundary Drawing Tool Usage Examples

This folder contains ready-to-use launcher scripts for the Matrice Boundary Drawing Tool.

## 📁 Files

### `boundary_drawer_launcher.py`
- **Purpose**: Full-featured launcher with comprehensive error handling
- **Features**: Detailed instructions, multiple fallback methods, airport security zones
- **Best for**: First-time users or when you need detailed guidance

### `simple_boundary_launcher.py`
- **Purpose**: Clean, simple launcher that's easy to customize
- **Features**: Function-based approach, minimal output, customizable zones
- **Best for**: Experienced users or when you want to modify the code

## 🚀 Quick Start

1. **Navigate to this folder**:
   ```bash
   cd python-sdk/src/matrice/deploy/utils/boundary_drawing_internal/usage
   ```

2. **Run a launcher**:
   ```bash
   python boundary_drawer_launcher.py
   # OR
   python simple_boundary_launcher.py
   ```

3. **The tool will**:
   - Check if your video file exists at: `C:\Users\pathi\OneDrive\Desktop\matriceai\matrice-applications\airport-security\door2.mp4`
   - Launch an interactive HTML tool in your browser
   - Allow you to draw boundaries on video frames
   - Generate Python code with zone coordinates

## 🎯 Customization

### Change Video Path
Edit the `VIDEO_PATH` variable in either file:
```python
VIDEO_PATH = r"path\to\your\video.mp4"
```

### Modify Zone Names
Update the zone lists for your specific use case:
```python
# For airport security
SECURITY_ZONES = [
    "entry_door",
    "security_line", 
    "checkpoint",
    "waiting_area",
    "restricted_zone",
    "exit_door"
]

# For retail
RETAIL_ZONES = [
    "entrance",
    "checkout",
    "aisles",
    "customer_service"
]
```

## 🔧 How the Tool Works

1. **Select Zone Type**: Choose from the dropdown menu
2. **Draw Boundaries**: Click points on the video frame
3. **Complete Zone**: Right-click or press Enter
4. **Generate Code**: Click the "Generate Code" button
5. **Copy & Use**: Copy the Python code for your application

## 📤 Output Format

The tool generates Python code like this:
```python
zones = {
    "entry_door": [[100, 200], [300, 200], [300, 400], [100, 400]],
    "security_line": [[350, 150], [500, 150], [500, 350], [350, 350]],
    "checkpoint": [[200, 100], [400, 120], [380, 250], [180, 230]]
}
```

## 🔗 Integration

Use the generated zones with Matrice post-processing:
```python
from matrice_analytics.post_processing import CustomerServiceProcessor

processor = CustomerServiceProcessor(
    customer_areas=zones["waiting_area"],
    staff_areas=zones["restricted_zone"]
)
```

## 🐛 Troubleshooting

- **Import Error**: Make sure you're running from the correct directory
- **Video Not Found**: Check the video path in the script
- **Browser Doesn't Open**: The HTML file path will be printed - open it manually
- **Tool Not Working**: Try the alternative method in `boundary_drawer_launcher.py`

## 💡 Tips

- Use precise boundary drawing for better results
- Save your zone configurations as JSON for reuse
- Test with a short video clip first
- The tool works with MP4, AVI, MOV, JPG, PNG files 