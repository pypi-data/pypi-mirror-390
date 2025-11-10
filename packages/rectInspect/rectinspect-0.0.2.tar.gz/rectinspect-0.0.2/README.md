# rectInspect
A Python library for detecting and highlighting defects in images using customizable width and height rules.
<br>
This is the source code of version 0.0.1, created as a starter project for building a Python package.

## Quickstart
The library provides easy-to-use tools for detecting image defects and manually inspecting them using rectangles.

### Initialize Detector
You can initialize the defect detector with threshold, minimum area, width/height arrays, and optional rectangles to remove.

```python
import rectInspect

# Initialize detector
detector = rectInspect.highlight_defects(
    threshold_ratio=0.2,
    min_area=100,
    width_arr=[1],
    height_arr=[8],
    remove_rec=[(64,35)]  # Width, height to skip
)

```

### Process Image
Process an image to detect defects and get the filtered result.

```python
# Process the image
filtered = detector.process_image("2.jpeg")

```

### Detect Defects
Detect defects based on initialized parameters. Returns the number of detected items.

```python
# Detect defects
detected_items = detector.detect_defects(filtered, detector.merged_contours)

# Print results
detector.print_results(detected_items)


```

### Save Highlighted Image
Save the image with defects highlighted in red rectangles.

```python
# Save the highlighted defects
detector.save_highlited_defect_image(filtered, detected_items)

```

### Draw Rectangles Manually
You can also interactively draw rectangles on an image and see their width, height, and area.
```python
# Draw rectangles interactively
detector.draw_rectangle_with_mouse("final.jpg")


```

### Features
- Detect defects using contour analysis.
- Specify multiple width and height ratios using arrays.
- Optionally remove rectangles that match certain width/height dimensions.
- Interactive rectangle drawing with real-time width, height, and area display.
- Save final images with highlighted defects.

### Installation

```bash
pip install rectInspect
```
# rectInspect
