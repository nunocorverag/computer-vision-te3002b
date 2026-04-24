# Computer Vision Activities - TE3002B

Repository for computer vision activities from TE3002B - Implementation of Intelligent Robotics course.

**Author:** Gustavo Nuno  
**Institution:** Tecnologico de Monterrey  
**Course:** TE3002B - Implementation of Intelligent Robotics  
**Date:** April 2026  

---

## Activities Overview

This repository contains implementations of various computer vision techniques applied to autonomous robotics:

### Activity 2.01 - Basic Image Processing
- **Technique:** Fundamental image operations and transformations
- **Application:** Introduction to OpenCV and image manipulation
- **Key Features:** Image loading, display, basic filters
- **Files:** `activity_2_01/`

### Activity 2.02 - Image Transformations
- **Technique:** Geometric transformations and color space conversions
- **Application:** Image preprocessing and feature extraction
- **Key Features:** Rotation, scaling, translation, color space manipulation
- **Files:** `activity_2_02/`

### Activity 2.03 - Advanced CV Techniques
- **Technique:** Edge detection, feature matching, and object recognition
- **Application:** Advanced computer vision algorithms
- **Key Features:** Canny edge detection, Harris corners, template matching
- **Files:** `activity_2_03/`

### Activity 2.04 - Center Line Detection
- **Technique:** ROI cropping, Otsu thresholding, contour filtering
- **Application:** Lane following for autonomous navigation
- **Key Features:** Temporal smoothing, proportional steering control
- **Files:** `activity_2_04/`

### Activity 2.05 - Traffic Light Detection
- **Technique:** HSV color space detection
- **Application:** Traffic light state recognition (red, yellow, green)
- **Key Features:** Morphological operations, position-based disambiguation
- **Files:** `activity_2_05/`

### Activity 2.06 - Traffic Sign Detection
- **Technique:** Dual-approach pipeline (Blur Detection + YOLOv8 CNN)
- **Application:** Real-time traffic sign detection and classification
- **Key Features:** 
  - Approach A: Image quality filtering (Laplacian variance)
  - Approach B: Deep learning with YOLOv8
  - 5 sign classes: Stop, Workers, Go Straight, Turn Left, Turn Right
- **Files:** `activity_2_06/`

---

## Repository Structure

```
Activities/
├── README.md                    <- This file
├── .gitignore                   <- Excludes videos, datasets, temp files
├── activity_2_01/               <- Basic image processing
├── activity_2_02/               <- Image transformations
├── activity_2_03/               <- Advanced CV techniques
├── activity_2_04/               <- Center line detection
│   ├── README.md
│   ├── actividad_2_04.py
│   ├── fulltest.py
│   └── ...
├── activity_2_05/               <- Traffic light detection
│   ├── README.md
│   ├── test_traffic_light.py
│   └── ...
└── activity_2_06/               <- Traffic sign detection (YOLO)
    ├── README.md
    ├── actividad_2_06.py
    ├── detector.py
    ├── yolov8_traffic_signs_kaggle.ipynb
    ├── weights/
    │   └── best.pt
    └── ...
```

---

## Prerequisites

### General Requirements
- Python 3.9+
- TE3002B Simulator (Unity-based)
- Virtual environment recommended

### Python Dependencies

```bash
pip install opencv-python numpy grpcio protobuf ultralytics
```

Or install from individual activity requirements:

```bash
# For Activity 2.04 and 2.05
pip install opencv-python numpy grpcio protobuf

# For Activity 2.06 (additional)
pip install ultralytics
```

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/nunocorverag/computer-vision-te3002b.git
cd computer-vision-te3002b
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # If available
```

### 3. Start Simulator

```bash
te3002b-sim
```

### 4. Run Activities

```bash
# Activity 2.04 - Center Line Detection
cd activity_2_04
python3 actividad_2_04.py

# Activity 2.05 - Traffic Light Detection
cd ../activity_2_05
python3 test_traffic_light.py

# Activity 2.06 - Traffic Sign Detection
cd ../activity_2_06
python3 actividad_2_06.py
```

---

## Technical Details

### Simulator Connection
- **Host:** 127.0.0.1
- **Port:** 7072
- **Protocol:** gRPC

### Image Processing Pipeline

**Activity 2.04:**
```
Camera Frame -> ROI Crop -> Grayscale -> Gaussian Blur -> 
Otsu Threshold -> Morphology -> Contour Detection -> Center Calculation
```

**Activity 2.05:**
```
Camera Frame -> HSV Conversion -> Color Masks (R/Y/G) -> 
Morphology -> Contour Analysis -> Position + Area Decision
```

**Activity 2.06:**
```
Camera Frame -> Blur Detection (Quality Filter) -> 
YOLOv8 CNN Detection -> NMS -> Bounding Boxes + Labels
```

---

## Results

### Activity 2.04
- Real-time lane following
- Proportional steering control
- ~40 Hz processing rate

### Activity 2.05
- Accurate traffic light state detection
- Robust to lighting variations
- Position-based disambiguation

### Activity 2.06
- **Detection Rate:** 5/5 signs detected (100%)
- **Processing:** 15,544 frames tested
- **Signs:** Stop, Workers, Go Straight, Turn Left, Turn Right
- **Model:** YOLOv8n (3M parameters)
- **Training:** Google Colab, 100 epochs, Roboflow dataset

---

## Notes

- Videos are generated automatically and excluded from repository
- Datasets are excluded due to size (can be regenerated)
- Each activity has its own detailed README
- All code is documented with comments explaining the pipeline

---

## License

This project is part of an academic activity.  
Code available for educational purposes only.

---

## Contact

Gustavo Nuno  
TE3002B - Implementation of Intelligent Robotics  
Tecnologico de Monterrey
