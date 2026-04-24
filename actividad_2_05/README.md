# Activity 2.05 - Traffic Light Detection

## Description

Implementation of a traffic light detector using computer vision that identifies the current state of the traffic light (red, yellow, green, or none).

## Implemented Algorithm

### Technique: Color Detection in HSV Space

The algorithm uses:

1. **HSV Conversion**: Better color separation than BGR/RGB
2. **Calibrated color ranges**:
   - **Red**: Two ranges (0-10° and 160-180° in Hue) because red is at the extremes of the spectrum
   - **Yellow**: 15-35° in Hue
   - **Green**: 40-90° in Hue
3. **Morphology**: OPEN and CLOSE operations to eliminate noise
4. **Position analysis**: Uses vertical position to disambiguate when there are multiple colors
5. **Area analysis**: Prioritizes detections with larger area

### Processing Pipeline

```
BGR Image -> HSV -> Gaussian Blur -> Color Masks -> Morphology -> 
Contour Analysis -> Area and Position Calculation -> Final Decision
```

## Files

- **`main.py`**: `TrafficLightDetection` class with main algorithm
- **`test_traffic_light.py`**: Test script with 3DGS simulator
- **`README.md`**: This documentation

## Usage

### With 3DGS Simulator

1. Start the simulator:
```bash
te3002b-sim
```

2. Run the detector:
```bash
python3 test_traffic_light.py
```

### With a Static Image

```bash
python3 test_traffic_light.py path/to/image.jpg
```

## TrafficLightDetection Class

### Main Method

```python
def detect_state(self, image):
    """
    Detects the traffic light state.
    
    Args:
        image: OpenCV BGR image
        
    Returns:
        str: 'red', 'yellow', 'green', or 'none'
    """
```

### Configurable Parameters

```python
# HSV ranges
self.red_lower1 = np.array([0, 100, 100])
self.red_upper1 = np.array([10, 255, 255])
self.red_lower2 = np.array([160, 100, 100])
self.red_upper2 = np.array([180, 255, 255])

self.yellow_lower = np.array([15, 100, 100])
self.yellow_upper = np.array([35, 255, 255])

self.green_lower = np.array([40, 50, 50])
self.green_upper = np.array([90, 255, 255])

# Minimum area to validate detection
self.min_area = 50
```

## Decision Logic

### Case 1: Single detection
Returns the detected color if the area exceeds the minimum.

### Case 2: Multiple detections
1. Checks vertical position:
   - Red: upper part (y < 40% of height)
   - Yellow: middle part (30% < y < 70%)
   - Green: lower part (y > 50% of height)
2. If position is not conclusive, uses the color with largest area

### Case 3: No detections
Returns `"none"`

## Algorithm Advantages

- **Robust to noise**: Morphology eliminates isolated pixels
- **Adaptable to lighting**: HSV separates color from brightness
- **Ambiguity handling**: Uses vertical position as additional criterion
- **Efficient**: Real-time processing (~40 Hz)

## Possible Improvements

1. **Automatic calibration**: Adjust HSV ranges according to lighting conditions
2. **Shape detection**: Verify that it is circular (real traffic light)
3. **Temporal tracking**: Use previous frames to smooth detection
4. **Adaptive ROI**: Search only in region where traffic light is expected

## Requirements

- Python 3.x
- OpenCV (`cv2`)
- NumPy
- Access to 3DGS simulator (for live testing)

## Notes

- HSV ranges may need adjustment depending on specific simulator conditions
- The algorithm assumes only one traffic light color is on at a time
- Vertical position helps distinguish between lights of a standard vertical traffic light
