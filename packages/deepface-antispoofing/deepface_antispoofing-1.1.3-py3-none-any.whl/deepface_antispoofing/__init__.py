import requests
from pathlib import Path
import cv2
import numpy as np
import tensorflow as tf
from datetime import datetime

class DeepFaceAntiSpoofing:
    def __init__(self):
        self.models_dir = Path.cwd() / "models"
        self.data_dir = Path.cwd() / "data"
        self.age_gender_model_path = self.models_dir / "age_gender_model.h5"
        self.anti_spoofing_model_path = self.models_dir / "anti_spoofing_model.h5"
        self.printed_detection_model_path = self.models_dir / "printed_detection_model_1.keras"
        self.emotion_model_path = self.models_dir / "emotion_model.h5"
        self.face_mask_model_path = self.models_dir / "face_mask_model.keras"
        self.cascade_path = self.data_dir / "haarcascade_frontalface_default.xml"
        self._ensure_resources()
        self.age_gender_model = self._load_age_gender_model()
        self.anti_spoofing_model = self._load_anti_spoofing_model()
        self.printed_detection_model = self._load_printed_detection_model()
        self.emotion_model = self._load_emotion_model()
        self.face_mask_model = self._load_face_mask_model()
        self.face_cascade = cv2.CascadeClassifier(str(self.cascade_path))
        if self.face_cascade.empty():
            raise Exception("Failed to load Haar Cascade classifier")

        # Emotion labels
        self.labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

    def _ensure_resources(self):
        """Ensure models and Haar Cascade file are available. Downloads them if they don't exist."""
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        if not self.age_gender_model_path.exists():
            print("Downloading age_gender_model.h5...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/age_gender_model.h5")
            if response.status_code == 200:
                with open(self.age_gender_model_path, "wb") as f:
                    f.write(response.content)
                print("age_gender_model.h5 downloaded successfully.")
            else:
                raise Exception("Failed to download age_gender_model.h5")

        if not self.anti_spoofing_model_path.exists():
            print("Downloading anti_spoofing_model.h5...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/anti_spoofing_model.h5")
            if response.status_code == 200:
                with open(self.anti_spoofing_model_path, "wb") as f:
                    f.write(response.content)
                print("anti_spoofing_model.h5 downloaded successfully.")
            else:
                raise Exception("Failed to download anti_spoofing_model.h5")

        # Download printed_detection_model_1.keras
        if not self.printed_detection_model_path.exists():
            print("Downloading printed_detection_model_1.keras...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/printed_detection_model_1.keras")
            if response.status_code == 200:
                with open(self.printed_detection_model_path, "wb") as f:
                    f.write(response.content)
                print("printed_detection_model_1.keras downloaded successfully.")
            else:
                print("Warning: printed_detection_model_1.keras not available for download. Please train the model first.")

        # Download emotion_model.h5
        if not self.emotion_model_path.exists():
            print("Downloading emotion_model.h5...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/emotion_model.h5")
            if response.status_code == 200:
                with open(self.emotion_model_path, "wb") as f:
                    f.write(response.content)
                print("emotion_model.h5 downloaded successfully.")
            else:
                print("Warning: emotion_model.h5 not available for download. Please train the model first.")

        # Download face_mask_model.keras
        if not self.face_mask_model_path.exists():
            print("Downloading face_mask_model.keras...")
            response = requests.get("https://ipsoftechs.pythonanywhere.com/media/face_mask_model.keras")
            if response.status_code == 200:
                with open(self.face_mask_model_path, "wb") as f:
                    f.write(response.content)
                print("face_mask_model.keras downloaded successfully.")
            else:
                print("Warning: face_mask_model.keras not available for download. Please train the model first.")

        if not self.cascade_path.exists():
            print("Downloading haarcascade_frontalface_default.xml...")
            response = requests.get(
                "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            )
            if response.status_code == 200:
                with open(self.cascade_path, "wb") as f:
                    f.write(response.content)
                print("haarcascade_frontalface_default.xml downloaded successfully.")
            else:
                raise Exception("Failed to download haarcascade_frontalface_default.xml")

    def _load_face_mask_model(self):
        """Load the face mask detection model."""
        try:
            model_path = self.models_dir / "face_mask_model.keras"
            if not model_path.exists():
                print("Face mask model not found. Training required.")
                return None
            model = tf.keras.models.load_model(model_path)
            return model
        except Exception as e:
            print(f"Error loading face mask model: {e}")
            return None

    def _load_emotion_model(self):
        """Load the emotion recognition model."""
        try:
            model = tf.keras.models.load_model(self.emotion_model_path, compile=False)
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            return model
        except Exception as e:
            print(f"Warning: Could not load emotion model: {e}")
            return None

    def _load_age_gender_model(self):
        """Load the age and gender model."""
        model = tf.keras.models.load_model(self.age_gender_model_path, compile=False)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss={
                'age': tf.keras.losses.CategoricalCrossentropy(),
                'gender': tf.keras.losses.CategoricalCrossentropy()
            },
            metrics={
                'age': 'accuracy',
                'gender': 'accuracy'
            }
        )
        return model

    def _load_anti_spoofing_model(self):
        """Load the anti-spoofing model."""
        model = tf.keras.models.load_model(self.anti_spoofing_model_path, compile=False)
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        return model

    def _load_printed_detection_model(self):
        """Load the printed detection model."""
        try:
            model = tf.keras.models.load_model(self.printed_detection_model_path, compile=False)
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            return model
        except Exception as e:
            print(f"Warning: Could not load printed detection model: {e}")
            return None

    def _convert_to_serializable(self, data):
        """Convert numpy types to JSON-serializable types."""
        if isinstance(data, dict):
            return {k: self._convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, (np.float32, np.float64)):
            return float(data)
        elif isinstance(data, (np.int32, np.int64)):
            return int(data)
        return data

    def _detect_face(self, file_path: str) -> tuple[bool, str | tuple]:
        """Detect faces in the image using Haar Cascade."""
        try:
            img = cv2.imread(file_path)
            if img is None:
                return False, "Failed to load image"
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            if len(faces) == 1:
                return True, faces[0]
            elif len(faces) == 0:
                return False, "No face detected"
            else:
                return False, "Multiple faces detected"
        except Exception as e:
            return False, str(e)

    def analyze_image(self, file_path: str) -> dict:
        """Analyze an image for age, gender, and spoof detection."""
        face_detected, message_or_coords = self._detect_face(file_path)
        if not face_detected:
            return {"error": message_or_coords}

        try:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Failed to load image")

            img_age_gender = cv2.resize(img, (96, 96))
            img_age_gender = img_age_gender.astype(np.float32) / 255.0
            img_age_gender = np.expand_dims(img_age_gender, axis=0)

            img_anti_spoof = cv2.resize(img, (128, 128))
            img_anti_spoof = img_anti_spoof.astype(np.float32) / 255.0
            img_anti_spoof = np.expand_dims(img_anti_spoof, axis=0)

            age_pred, gender_pred = self.age_gender_model.predict(img_age_gender)
            age = int(np.argmax(age_pred[0]))
            gender_probs = gender_pred[0]
            gender_dict = {'Male': float(gender_probs[0]), 'Female': float(gender_probs[1])}
            dominant_gender = 'Male' if gender_probs[0] > gender_probs[1] else 'Female'

            spoof_pred = self.anti_spoofing_model.predict(img_anti_spoof)
            spoof_prob = float(spoof_pred[0][0])
            is_real = spoof_prob > 0.5
            spoof_dict = {'Fake': 1.0 - spoof_prob, 'Real': spoof_prob}
            dominant_spoof = 'Real' if is_real else 'Fake'

            analysis = {
                "age": age,
                "gender": gender_dict,
                "dominant_gender": dominant_gender,
                "spoof": spoof_dict,
                "dominant_spoof": dominant_spoof,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return self._convert_to_serializable(analysis)
        except Exception as e:
            return {"error": str(e)}

    def analyze_deepface(self, image_path: str) -> dict:
        """Analyze image specifically for printed detection only."""
        face_detected, message_or_coords = self._detect_face(image_path)
        if not face_detected:
            return {"error": message_or_coords}

        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Failed to load image")

            # Preprocess for printed detection (128x128)
            img_printed = cv2.resize(img, (128, 128))
            img_printed = img_printed.astype(np.float32) / 255.0
            img_printed = np.expand_dims(img_printed, axis=0)

            # Predict printed/real
            printed_pred = self.printed_detection_model.predict(img_printed, verbose=0)
            pred = float(printed_pred[0][0])  # prob of printed (class 1)
            printed_prob = 1.0 - pred  # Flip to prob of real (to match original logic)

            # printed_prob is probability of being real (1 = Real, 0 = Printed)
            is_real = printed_prob > 0.5
            printed_dict = {
                'Printed': 1.0 - printed_prob,
                'Real': printed_prob
            }
            dominant_printed = 'Real' if is_real else 'Printed'

            # Confidence score
            confidence = printed_prob if is_real else (1.0 - printed_prob)

            analysis = {
                "printed_analysis": printed_dict,
                "dominant_printed": dominant_printed,
                "confidence": float(confidence),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return self._convert_to_serializable(analysis)
        except Exception as e:
            return {"error": str(e)}

    def analyze_emotion(self, image_path: str) -> dict:
        """Analyze image for emotion recognition."""
        face_detected, message_or_coords = self._detect_face(image_path)
        if not face_detected:
            return {"error": message_or_coords}

        if self.emotion_model is None:
            return {"error": "Emotion model not available"}

        try:
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                raise ValueError("Failed to load image")

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 3)

            if len(faces) == 0:
                return {"error": "No face detected in emotion analysis"}

            # Process only the first face
            x, y, w, h = faces[0]

            # EXACT same preprocessing
            sub_face_img = gray[y:y + h, x:x + w]
            resized = cv2.resize(sub_face_img, (48, 48))
            normalize = resized / 255.0
            reshaped = np.reshape(normalize, (1, 48, 48, 1))

            # Predict emotions
            result = self.emotion_model.predict(reshaped, verbose=0)

            # EXACT same label
            label = np.argmax(result, axis=1)[0]

            # Get the emotion name from dictionary
            dominant_emotion = self.labels_dict[label]

            # Get confidence (probability of predicted emotion)
            confidence = float(result[0][label])

            # Create emotion probabilities dictionary for all emotions
            emotion_probs = result[0]
            emotions_dict = {}
            for i, emotion_name in self.labels_dict.items():
                emotions_dict[emotion_name.lower()] = float(emotion_probs[i])

            analysis = {
                "emotions": emotions_dict,
                "dominant_emotion": dominant_emotion.lower(),
                "confidence": confidence,
                "predicted_label": int(label),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return self._convert_to_serializable(analysis)
        except Exception as e:
            return {"error": str(e)}

    def analyze_face_mask(self, image_path: str) -> dict:
        face_detected, message_or_coords = self._detect_face(image_path)
        if not face_detected:
            return {"error": message_or_coords}
        if self.face_mask_model is None:
            return {"error": "Face mask model not available"}

        try:
            img = tf.keras.preprocessing.image.load_img(
                image_path,
                target_size=(224, 224),  # Must be 224x224
                interpolation='bilinear'
            )
            img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            prediction = self.face_mask_model.predict(img_array, verbose=0)
            mask_prob = float(prediction[0][0])

            has_mask = mask_prob < 0.5
            with_mask_prob = 1.0 - mask_prob
            without_mask_prob = mask_prob
            confidence = with_mask_prob if has_mask else without_mask_prob

            analysis = {
                "has_mask": has_mask,
                "with_mask_prob": float(with_mask_prob),
                "without_mask_prob": float(without_mask_prob),
                "confidence": float(confidence),
                "mask_status": "With Mask" if has_mask else "Without Mask",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return analysis
        except Exception as e:
            return {"error": str(e)}

    def analyze_comprehensive(self, image_path: str) -> dict:
        """Comprehensive analysis including all models."""
        try:
            # Get analysis from all models
            age_gender_result = self.analyze_image(image_path)
            printed_result = self.analyze_deepface(image_path)
            emotion_result = self.analyze_emotion(image_path)
            face_mask_result = self.analyze_face_mask(image_path)

            # Combine results
            comprehensive_result = {
                "age_gender": age_gender_result if "error" not in age_gender_result else {
                    "error": age_gender_result["error"]},
                "printed_detection": printed_result if "error" not in printed_result else {
                    "error": printed_result["error"]},
                "emotion": emotion_result if "error" not in emotion_result else {"error": emotion_result["error"]},
                "face_mask": face_mask_result if "error" not in face_mask_result else {
                    "error": face_mask_result["error"]},
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return comprehensive_result
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    deepface = DeepFaceAntiSpoofing()

    # Test all analyses
    test_image = "path_to_test_image.jpg"

    print("Testing Age/Gender Analysis:")
    result1 = deepface.analyze_image(test_image)
    print(result1)

    print("\nTesting Printed Detection:")
    result2 = deepface.analyze_deepface(test_image)
    print(result2)

    print("\nTesting Emotion Analysis:")
    result3 = deepface.analyze_emotion(test_image)
    print(result3)

    print("\nTesting Face Mask Analysis:")
    result4 = deepface.analyze_face_mask(test_image)
    print(result4)

    print("\nTesting Comprehensive Analysis:")
    result5 = deepface.analyze_comprehensive(test_image)
    print(result5)