# DeepFace Anti-Spoofing

The **DeepFace Anti-Spoofing** package enables users to perform advanced face recognition, anti-spoofing, deepfake detection, emotion analysis, and face mask detection on images. It provides comprehensive predictions for age, gender, emotions, mask status, and determines whether an image contains a real face, a printed photo, a presentation attack, or an AI-generated deepfake. This package is designed for secure authentication, identity verification, and seamless integration into Python applications, ensuring reliable and efficient image analysis.

## Features

- **Face Analysis**: Predict age and gender from uploaded images using the `analyze_image` method.
- **Anti-Spoofing Detection**: Determine whether a face is real or part of a spoofing attack (e.g., printed photo, or presentation attack) using the `analyze_deepface` method.
- **Deepfake Detection**: Detect AI-generated faces or deepfakes with high accuracy via the `analyze_image` method.
- **Emotion Analysis**: Analyze seven basic emotions (angry, disgust, fear, happy, neutral, sad, surprise) using the `analyze_emotion` method.
- **Face Mask Detection**: Detect whether a person is wearing a face mask using the `analyze_face_mask` method.
- **Comprehensive Analysis**: Get all analysis results in a single call using the `analyze_comprehensive` method.
- **Simple Integration**: Easily integrate into Python applications for robust image analysis.

## Documentation

Comprehensive documentation, guidance, and code examples, including a web interface for testing, are provided at the [DeepFace Anti-Spoofing Documentation](https://ipsoftechsolutions.pythonanywhere.com/deepface-antispoofing-documentation/).

## Installation

To use the DeepFace Anti-Spoofing and Deepfake Analysis package in your Python application, install the required package:

```bash
pip install deepface-antispoofing
```

## Usage Examples

### Example 1: Face Analysis with Age, Gender, and Deepfake Detection
The `analyze_image` method predicts age, gender, and whether the image contains a real or AI-generated face.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_image(file_path)

print(response)
```

**Sample Response**:
```json
{
  "id": 1,
  "age": 30,
  "gender": {
    "Male": 0.85,
    "Female": 0.15
  },
  "dominant_gender": "Male",
  "spoof": {
    "Fake": 0.02,
    "Real": 0.98
  },
  "dominant_spoof": "Real",
  "timestamp": "2025-04-18 12:34:56"
}
```

### Example 2: Anti-Spoofing Detection for Printed, or Presentation Attacks
The `analyze_deepface` method determines whether the face is real or part of a spoofing attack, such as a printed photo, or presentation attack.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_deepface(file_path)

print(response)
```

**Sample Response**:
```json
{
  "confidence": 1.0,
  "is_real": "True",
  "processing_time": 1.03,
  "spoof_type": "Real Face",
  "success": "True"
}
```

### Example 3: Emotion Analysis
The `analyze_emotion` method analyzes seven basic emotions from the facial expression.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_emotion(file_path)

print(response)
```

**Sample Response**:
```json
{
  "emotions": {
    "angry": 2.2382489987649024e-05,
    "disgust": 6.113571515697913e-08,
    "fear": 4.268830161890946e-05,
    "happy": 0.9963662624359131,
    "neutral": 0.0030167356599122286,
    "sad": 3.199426646460779e-05,
    "surprise": 0.0005198476719669998
  },
  "dominant_emotion": "happy",
  "confidence": 0.9963662624359131,
  "predicted_label": 3,
  "timestamp": "2025-11-05 23:24:02"
}
```

### Example 4: Face Mask Detection
The `analyze_face_mask` method detects whether a person is wearing a face mask.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_face_mask(file_path)

print(response)
```

**Sample Response**:
```json
{
  "has_mask": false,
  "with_mask_prob": 0.34883034229278564,
  "without_mask_prob": 0.6511696577072144,
  "confidence": 0.6511696577072144,
  "mask_status": "Without Mask",
  "timestamp": "2025-11-05 23:24:52"
}
```

### Example 5: Comprehensive Analysis
The `analyze_comprehensive` method provides all analysis results in a single call.

```python
from deepface_antispoofing import DeepFaceAntiSpoofing

file_path = "path_to_image.jpg"

deepface = DeepFaceAntiSpoofing()

response = deepface.analyze_comprehensive(file_path)

print(response)
```

**Sample Response**:
```json
{
  "age_gender": {
    "age": 25,
    "gender": {
      "Male": 5.152494122739881e-05,
      "Female": 0.9999485015869141
    },
    "dominant_gender": "Female",
    "spoof": {
      "Fake": 7.748603820800781e-07,
      "Real": 0.9999992251396179
    },
    "dominant_spoof": "Real",
    "timestamp": "2025-11-05 23:25:17"
  },
  "printed_detection": {
    "printed_analysis": {
      "Printed": 0.10731140524148941,
      "Real": 0.8926885947585106
    },
    "dominant_printed": "Real",
    "confidence": 0.8926885947585106,
    "timestamp": "2025-11-05 23:25:18"
  },
  "emotion": {
    "emotions": {
      "angry": 2.2382489987649024e-05,
      "disgust": 6.113571515697913e-08,
      "fear": 4.268830161890946e-05,
      "happy": 0.9963662624359131,
      "neutral": 0.0030167356599122286,
      "sad": 3.199426646460779e-05,
      "surprise": 0.0005198476719669998
    },
    "dominant_emotion": "happy",
    "confidence": 0.9963662624359131,
    "predicted_label": 3,
    "timestamp": "2025-11-05 23:25:19"
  },
  "face_mask": {
    "has_mask": false,
    "with_mask_prob": 0.34883034229278564,
    "without_mask_prob": 0.6511696577072144,
    "confidence": 0.6511696577072144,
    "mask_status": "Without Mask",
    "timestamp": "2025-11-05 23:25:20"
  },
  "timestamp": "2025-11-05 23:25:20"
}
```

## Key Points

- Ensure the uploaded image contains a clear face for accurate analysis.
- Use analyze_image for age, gender, and deepfake detection.
- Use analyze_deepface for detecting spoofing attacks like printed photos, or presentation attacks.
- Use analyze_emotion for emotion analysis across seven basic emotions.
- Use analyze_face_mask for detecting whether a person is wearing a face mask.
- Use analyze_comprehensive for getting all analysis results in a single call.
- Refer to the [official documentation](https://ipsoftechsolutions.pythonanywhere.com/deepface-antispoofing-documentation/) for detailed endpoint specifications, advanced features, and web interface usage.

## Support

For any issues or questions, please contact [ipsoftechsolutions@gmail.com](mailto:ipsoftechsolutions@gmail.com).

---

Thank you for choosing DeepFace Anti-Spoofing for your face recognition, anti-spoofing, and deepfake detection needs!