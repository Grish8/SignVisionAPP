from flask import Flask, render_template, Response, jsonify, request
from collections import deque
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os
# Suppress TensorFlow oneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# Fix Windows encoding issues
if os.name == 'nt':  # Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'
import cv2
import pyaudio
import numpy as np
import mediapipe as mp  
import threading
import time
import pickle
import tensorflow as tf
import pyttsx3
import cvlib as cv
import speech_recognition as sr
import numpy as np
import threading
import time
import os
from pathlib import Path
from collections import deque
from nltk.tokenize import RegexpTokenizer
from difflib import SequenceMatcher

from flask import Flask, render_template, Response, jsonify, request, session, redirect

app = Flask(__name__)

app.secret_key = 'my-secret-key'

# Constants
ASSETS_FOLDER = "static/assets"
SIGN_PATH = "static/assets"
SIMILARITY_RATIO = 0.9

# Global variables
# For sign-to-voice
engine = None
current_character = ""
is_running_sign = False

# For text-to-sign
current_video_path_text = ""
is_playing_text = False
current_frame_text = None

# For voice-to-sign
is_listening = False
current_video_path_voice = ""
current_frame_voice = None
recognized_text = ""
speech_client = None

recognized_queue = deque()  # Queue to hold recognized texts
is_playing_sequence = False  # Flag to control video sequence playback
recognized_history = []     #List to store all recognized texts
current_playing_index = -1  #Index of currently playing text


word_buffer = []  # Buffer to accumulate words
SIGN_TRIGGER_COUNT = 3  # Number of words to accumulate before showing signs

#after initialization - settings part
app.config["MONGO_URI"] = "mongodb://localhost:27017/Sign-Vision"
mongo = PyMongo(app)

#settings model
class UserSettings:
    _cache = {}  # Class-level cache

    @staticmethod
    def get_settings(user_id, force_refresh=False):
        if not force_refresh and user_id in UserSettings._cache:
            return UserSettings._cache[user_id]
        
        settings = mongo.db.settings.find_one({"user_id": user_id}) or {}
        if 'recognized_texts' not in settings:
            settings['recognized_texts'] = []
        UserSettings._cache[user_id] = settings
        return settings
    
    @staticmethod
    def update_settings(user_id, updates):
        mongo.db.settings.update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True
        )
        # Invalidate cache
        if user_id in UserSettings._cache:
            del UserSettings._cache[user_id]
    
    @staticmethod
    def append_recognized_text(user_id, text):
        mongo.db.settings.update_one(
            {"user_id": user_id},
            {"$push": {"recognized_texts": text}},
            upsert=True
        )
        # Invalidate cache
        if user_id in UserSettings._cache:
            del UserSettings._cache[user_id]

#AR headset display words
class ARHeadsetDisplay:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")
            
        # Set window properties
        self.window_name = "AR Headset Simulation"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text display variables
        self.current_text = "Say something..."
        self.listening = True
        self.status = "Ready"
        
        # AR display parameters
        self.hud_color = (0, 255, 100)  # AR green
        self.corner_size = 150
        self.corner_thickness = 3
        
        # Sign language configuration
        self.signs_folder = "static/assets"
        self.sign_videos = self._load_sign_videos()
        self.word_buffer = deque()
        self.current_sign_frame = None
        self.video_playing = False
        self.video_thread = None
        self.last_word_time = 0
        self.word_timeout = 2.0
        
        # Sign display area
        self.sign_width = 100
        self.sign_height = 100
        self.sign_x = 30
        self.sign_y = 0
        
        # Calibrate microphone
        print("Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complete")
        
    def listen_thread(self):
        """Continuous speech recognition in background"""
        while self.listening:
            try:
                with self.microphone as source:
                    self.status = "Listening..."
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                self.current_text = text
                UserSettings.append_recognized_text("current_user", text)
                new_words = text.split()
                for word in new_words:
                    self.word_buffer.append(word)
                    self.last_word_time = time.time()
                self.status = "Ready"
            except sr.WaitTimeoutError:
                self.status = "Ready"
            except sr.UnknownValueError:
                self.current_text = "Could not understand sound"
                self.status = "Error"
            except Exception as e:
                self.current_text = f"Error: {str(e)}"
                self.status = "Error"
                self.listening = False
                
    def draw_ar_corners(self, frame):
        """Draw AR headset corner markers"""
        height, width = frame.shape[:2]
        
        # Top-left corner
        cv2.line(frame, (0, 0), (self.corner_size, 0), self.hud_color, self.corner_thickness)
        cv2.line(frame, (0, 0), (0, self.corner_size), self.hud_color, self.corner_thickness)
        
        # Top-right corner
        cv2.line(frame, (width, 0), (width - self.corner_size, 0), self.hud_color, self.corner_thickness)
        cv2.line(frame, (width, 0), (width, self.corner_size), self.hud_color, self.corner_thickness)
        
        # Bottom-left corner
        cv2.line(frame, (0, height), (self.corner_size, height), self.hud_color, self.corner_thickness)
        cv2.line(frame, (0, height), (0, height - self.corner_size), self.hud_color, self.corner_thickness)
        
        # Bottom-right corner
        cv2.line(frame, (width, height), (width - self.corner_size, height), self.hud_color, self.corner_thickness)
        cv2.line(frame, (width, height), (width, height - self.corner_size), self.hud_color, self.corner_thickness)
        
        return frame
    
    def draw_status_indicator(self, frame):
        """Draw status indicator in top-right corner"""
        height, width = frame.shape[:2]
        indicator_size = 20
        margin = 30
        
        if self.status == "Listening":
            color = (0, 255, 255)  # Yellow
        elif self.status == "Error":
            color = (0, 0, 255)    # Red
        else:
            color = (0, 255, 0)     # Green
            
        cv2.circle(frame, (width - margin, margin), indicator_size, color, -1)
        
        # Add status text
        cv2.putText(frame, self.status, (width - margin - 100, margin + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
        return frame
    
    def get_frame(self):
        """Get a single frame with all AR overlays"""
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Apply AR effects
        frame = self.draw_ar_corners(frame)
        frame = self.draw_status_indicator(frame)
        frame = self.draw_sign_language(frame)
        
        # Split text into multiple lines if too long
        words = self.current_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) < 25:  # Characters per line
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
        
        # Calculate starting Y position (centered vertically)
        line_height = 50
        total_text_height = len(lines) * line_height
        start_y = (height - total_text_height) // 2
        
        # Display each line centered horizontally
        for i, line in enumerate(lines):
            text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = start_y + (i * line_height)
            
            # Add stroke/border to make text more readable
            cv2.putText(frame, line, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4, cv2.LINE_AA)
            # Actual text
            cv2.putText(frame, line, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, self.hud_color, 2, cv2.LINE_AA)
        
        return frame

    def apply_settings(self, settings):
        """Apply new settings dynamically"""
        if settings.get('high_contrast', False):
            self.hud_color = (255, 255, 0)  # Yellow for high contrast
        else:
            self.hud_color = (0, 255, 100)  # Default green
            
        self.sign_width = settings.get('sign_size', 100)
        self.sign_height = settings.get('sign_size', 100)
        
        print("Applied new headset settings")
        
    def _load_sign_videos(self):
        sign_videos = {}
        signs_path = Path(self.signs_folder)
        
        if not signs_path.exists():
            print(f"Warning: Signs folder '{self.signs_folder}' not found!")
            return sign_videos
            
        for video_file in signs_path.glob("*.*"):
            sign_name = video_file.stem.lower()
            sign_videos[sign_name] = str(video_file)
            print(f"Loaded sign: {sign_name} => {video_file}")
            
        return sign_videos
        
    def find_sign_video(self, word):
        word = word.lower()
        
        # Exact match
        if word in self.sign_videos:
            return self.sign_videos[word]
            
        # Common variations
        variations = {
            "thank you": "thanks",
            "you're welcome": "welcome",
            "good morning": "morning",
            "good night": "night"
        }
        
        if word in variations:
            return self.sign_videos.get(variations[word], None)
            
        # Partial matches
        for sign_name in self.sign_videos:
            if word in sign_name or sign_name in word:
                return self.sign_videos[sign_name]
                
        # Individual letters
        if len(word) == 1:
            return self.sign_videos.get(word, None)
            
        return None
        
    def _play_video(self, path):
        """Internal video player that runs in a separate thread"""
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"Failed to open video: {path}")
            self.video_playing = False
            return
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30
            
        frame_delay = 1/fps
        
        while self.video_playing and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            self.current_sign_frame = cv2.resize(frame, (self.sign_width, self.sign_height))
            time.sleep(frame_delay)
            
        cap.release()
        self.video_playing = False
        self.current_sign_frame = None
        
    def play_sign_video(self, path):
        """Start video playback in a separate thread"""
        if not os.path.exists(path):
            print(f"Video file not found: {path}")
            return
            
        if self.video_playing:
            self.video_playing = False
            if self.video_thread:
                self.video_thread.join()
                
        self.video_playing = True
        self.video_thread = threading.Thread(target=self._play_video, args=(path,))
        self.video_thread.daemon = True
        self.video_thread.start()
        
    def process_words(self):
        while self.listening or self.word_buffer:
            if self.word_buffer:
                word = self.word_buffer.popleft()
                print(f"Processing word: {word}")
                
                video_path = self.find_sign_video(word)
                if video_path:
                    print(f"Playing sign for: {word}")
                    self.play_sign_video(video_path)
                else:
                    print(f"No sign found for: {word}")
                    
                self.last_word_time = time.time()
            else:
                if time.time() - self.last_word_time > self.word_timeout:
                    self.current_sign_frame = None
                time.sleep(0.1)
                
    def draw_sign_language(self, frame):
        if self.current_sign_frame is not None:
            height, width = frame.shape[:2]
            
            # Position in bottom left corner
            x = self.sign_x
            y = height - self.sign_height - self.sign_y
            
            try:
                # Resize the sign frame if needed
                sign_frame = cv2.resize(self.current_sign_frame, (self.sign_width, self.sign_height))
                
                # Get the region of interest in the main frame
                roi = frame[y:y+self.sign_height, x:x+self.sign_width]
                
                # Handle transparency if present (for PNGs with alpha channel)
                if sign_frame.shape[2] == 4:
                    # Extract the alpha channel and create 3-channel alpha
                    alpha = sign_frame[:, :, 3] / 255.0
                    alpha = cv2.merge([alpha, alpha, alpha])
                    
                    # Extract the RGB channels
                    foreground = sign_frame[:, :, :3].astype(float)
                    background = roi.astype(float)
                    
                    # Blend the images
                    blended = cv2.multiply(alpha, foreground) + cv2.multiply(1.0 - alpha, background)
                    roi[:] = blended.astype(np.uint8)
                else:
                    # No transparency - just overlay the image
                    roi[:] = sign_frame
                
                # Draw a border around the sign
                cv2.rectangle(frame, (x, y), (x+self.sign_width, y+self.sign_height), self.hud_color, 2)
                
            except Exception as e:
                print(f"Error overlaying sign: {e}")
                
        return frame

# Global AR headset instance
ar_headset = None


#AR display signs

class ARSignLanguageDisplay:
    def __init__(self, signs_folder="static/assets"):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")

         # Load settings
        self.settings = UserSettings.get_settings("current_user")  # Replace with actual user ID
        
          # Apply settings
        self.sign_width = self.settings.get('sign_size', 200)
        self.sign_height = self.settings.get('sign_size', 200)

        
        # Set window properties
        self.window_name = "AR Sign Language Display"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Sign language configuration
        self.signs_folder = signs_folder
        self.sign_videos = self._load_sign_videos()
        self.word_buffer = deque()
        self.current_sign_frame = None
        self.is_listening = True
        self.status = "Ready"
        self.SIGN_TRIGGER_COUNT = 1
        
        # Video playback control
        self.video_playing = False
        self.video_thread = None
        self.last_word_time = 0
        self.word_timeout = 2.0
        
        # AR display parameters
        self.hud_color = (0, 255, 100)
        self.corner_size = 150
        self.corner_thickness = 3
        
          # Sign display area - adjust these values as needed
        self.sign_width = 100  # Reduced width for better visibility
        self.sign_height = 100  # Reduced height
        self.sign_x = 30       # Position from left edge
        self.sign_y = 0       # Position from bottom edge
        
        # Calibrate microphone
        print("Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complete")
        
    def _load_sign_videos(self):
        sign_videos = {}
        signs_path = Path(self.signs_folder)
        
        if not signs_path.exists():
            print(f"Warning: Signs folder '{self.signs_folder}' not found!")
            return sign_videos
            
        for video_file in signs_path.glob("*.*"):
            sign_name = video_file.stem.lower()
            sign_videos[sign_name] = str(video_file)
            print(f"Loaded sign: {sign_name} => {video_file}")
            
        return sign_videos
        
    def find_sign_video(self, word):
        word = word.lower()
        
        # Exact match
        if word in self.sign_videos:
            return self.sign_videos[word]
            
        # Common variations
        variations = {
            "thank you": "thanks",
            "you're welcome": "welcome",
            "good morning": "morning",
            "good night": "night"
        }
        
        if word in variations:
            return self.sign_videos.get(variations[word], None)
            
        # Partial matches
        for sign_name in self.sign_videos:
            if word in sign_name or sign_name in word:
                return self.sign_videos[sign_name]
                
        # Individual letters
        if len(word) == 1:
            return self.sign_videos.get(word, None)
            
        return None
        
    def _play_video(self, path):
        """Internal video player that runs in a separate thread"""
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"Failed to open video: {path}")
            self.video_playing = False
            return
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30
            
        frame_delay = 1/fps
        
        while self.video_playing and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            self.current_sign_frame = cv2.resize(frame, (self.sign_width, self.sign_height))
            time.sleep(frame_delay)
            
        cap.release()
        self.video_playing = False
        self.current_sign_frame = None
        
    def play_sign_video(self, path):
        """Start video playback in a separate thread"""
        if not os.path.exists(path):
            print(f"Video file not found: {path}")
            return
            
        if self.video_playing:
            self.video_playing = False
            if self.video_thread:
                self.video_thread.join()
                
        self.video_playing = True
        self.video_thread = threading.Thread(target=self._play_video, args=(path,))
        self.video_thread.daemon = True
        self.video_thread.start()
        
    def process_words(self):
        while self.is_listening or self.word_buffer:
            if self.word_buffer:
                word = self.word_buffer.popleft()
                print(f"Processing word: {word}")
                
                video_path = self.find_sign_video(word)
                if video_path:
                    print(f"Playing sign for: {word}")
                    self.play_sign_video(video_path)
                else:
                    print(f"No sign found for: {word}")
                    
                self.last_word_time = time.time()
            else:
                if time.time() - self.last_word_time > self.word_timeout:
                    self.current_sign_frame = None
                time.sleep(0.1)
        
    def listen_thread(self):
        with self.microphone as source:
            while self.is_listening:
                try:
                    self.status = "Listening..."
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio)
                    
                    if "stop" in text.lower():
                        self.is_listening = False
                        break
                    
                    new_words = text.split()
                    for word in new_words:
                        self.word_buffer.append(word)
                        self.last_word_time = time.time()
                    
                    print(f"Recognized: {text}")
                    self.status = "Processing"
                    
                except sr.WaitTimeoutError:
                    self.status = "Ready"
                except sr.UnknownValueError:
                    self.status = "Error: No speech"
                except Exception as e:
                    self.status = f"Error: {str(e)}"
                    self.is_listening = False
                    
    def draw_ar_corners(self, frame):
        height, width = frame.shape[:2]
        
        # Top-left corner
        cv2.line(frame, (0, 0), (self.corner_size, 0), self.hud_color, self.corner_thickness)
        cv2.line(frame, (0, 0), (0, self.corner_size), self.hud_color, self.corner_thickness)
        
        # Top-right corner
        cv2.line(frame, (width, 0), (width - self.corner_size, 0), self.hud_color, self.corner_thickness)
        cv2.line(frame, (width, 0), (width, self.corner_size), self.hud_color, self.corner_thickness)
        
        # Bottom-left corner
        cv2.line(frame, (0, height), (self.corner_size, height), self.hud_color, self.corner_thickness)
        cv2.line(frame, (0, height), (0, height - self.corner_size), self.hud_color, self.corner_thickness)
        
        # Bottom-right corner
        cv2.line(frame, (width, height), (width - self.corner_size, height), self.hud_color, self.corner_thickness)
        cv2.line(frame, (width, height), (width, height - self.corner_size), self.hud_color, self.corner_thickness)
        
        return frame
    
    def draw_sign_language(self, frame):
        if self.current_sign_frame is not None:
            height, width = frame.shape[:2]
            
            # Position in bottom left corner
            x = self.sign_x
            y = height - self.sign_height - self.sign_y
            
            try:
                # Resize the sign frame if needed
                sign_frame = cv2.resize(self.current_sign_frame, (self.sign_width, self.sign_height))
                
                # Get the region of interest in the main frame
                roi = frame[y:y+self.sign_height, x:x+self.sign_width]
                
                # Handle transparency if present (for PNGs with alpha channel)
                if sign_frame.shape[2] == 4:
                    # Extract the alpha channel and create 3-channel alpha
                    alpha = sign_frame[:, :, 3] / 255.0
                    alpha = cv2.merge([alpha, alpha, alpha])
                    
                    # Extract the RGB channels
                    foreground = sign_frame[:, :, :3].astype(float)
                    background = roi.astype(float)
                    
                    # Blend the images
                    blended = cv2.multiply(alpha, foreground) + cv2.multiply(1.0 - alpha, background)
                    roi[:] = blended.astype(np.uint8)
                else:
                    # No transparency - just overlay the image
                    roi[:] = sign_frame
                
                # Draw a border around the sign
                cv2.rectangle(frame, (x, y), (x+self.sign_width, y+self.sign_height), self.hud_color, 2)
                
            except Exception as e:
                print(f"Error overlaying sign: {e}")
                
        return frame
    
    def run(self):
        listen_thread = threading.Thread(target=self.listen_thread)
        process_thread = threading.Thread(target=self.process_words)
        
        listen_thread.daemon = True
        process_thread.daemon = True
        
        listen_thread.start()
        process_thread.start()
        
        while self.is_listening:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = self.draw_ar_corners(frame)
            frame = self.draw_sign_language(frame)
            
            cv2.putText(frame, self.status, (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.putText(frame, f"Words in queue: {len(self.word_buffer)}", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow(self.window_name, frame)
            
            if cv2.waitKey(1) == 27:
                self.is_listening = False
                self.video_playing = False
                break
                
        self.is_listening = False
        self.video_playing = False
        self.cap.release()
        cv2.destroyAllWindows()
        listen_thread.join()
        process_thread.join()
        if self.video_thread:
            self.video_thread.join()

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        frame = self.draw_ar_corners(frame)
        frame = self.draw_sign_language(frame)
        
        cv2.putText(frame, self.status, (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Words in queue: {len(self.word_buffer)}", (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame

# Global AR display instance
ar_display = None

# Load models for sign-to-voice
def load_sign_models():
    model_dict = pickle.load(open('./model.p', 'rb'))
    sign_language_model = model_dict['model']
    gender_model = tf.keras.models.load_model('gender_detection.keras')
    return sign_language_model, gender_model

def apply_settings(self, settings):
        """Apply new settings dynamically"""
        self.sign_width = settings.get('sign_size', 200)
        self.sign_height = settings.get('sign_size', 200)
        
        # Update HUD color based on theme
        if settings.get('high_contrast', False):
            self.hud_color = (255, 255, 0)  # Yellow for high contrast
        else:
            self.hud_color = (0, 255, 100)  # Default green
            
        # Update other settings as needed
        print("Applied new AR display settings")

# Text processing
class UselessWords:
    @staticmethod
    def words():
        return {"is", "to", "the", "of", "and", "a", "an", "it", "in", "on", "for", "by"}

def process_text(text):
    tokenizer = RegexpTokenizer(r'\w+')
    return [w.lower() for w in tokenizer.tokenize(text) if w.lower() not in UselessWords.words()]

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Sign-to-Voice Functions
def sign_to_voice_generator():
    global engine, current_character, is_running_sign
    
    sign_language_model, gender_model = load_sign_models()
    labels_dict = {i: chr(65+i) for i in range(26)}  # A-Z
    
    # Initialize text-to-speech
    engine = pyttsx3.init()
    engine.setProperty('rate', 125)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    
    cap = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
    
    is_running_sign = True
    
    while is_running_sign:
        data_aux = []
        x_ = []
        y_ = []

        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Face and gender detection
        faces, confidence = cv.detect_face(frame)
        detected_gender = None

        for idx, f in enumerate(faces):
            (startX, startY, endX, endY) = f
            face_crop = np.copy(frame[startY:endY, startX:endX])

            if face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
                continue

            face_crop = cv2.resize(face_crop, (96, 96))
            face_crop = face_crop.astype("float") / 255.0
            face_crop = tf.keras.preprocessing.image.img_to_array(face_crop)
            face_crop = np.expand_dims(face_crop, axis=0)

            conf = gender_model.predict(face_crop)[0]
            detected_gender = ['male', 'female'][np.argmax(conf)]

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

            prediction = sign_language_model.predict([np.asarray(data_aux)])
            current_character = labels_dict[int(prediction[0])]

            if detected_gender == 'male':
                engine.setProperty('voice', voices[0].id)
            elif detected_gender == 'female':
                engine.setProperty('voice', voices[1].id)

            engine.say(current_character)
            engine.runAndWait()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()
    engine.stop()

# Text-to-Sign Functions
def preload_assets():
    global word_map
    word_map = {}
    if os.path.exists(ASSETS_FOLDER):
        files = [f for f in os.listdir(ASSETS_FOLDER) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        word_map = {os.path.splitext(f)[0].strip().lower(): os.path.join(ASSETS_FOLDER, f) for f in files}

def find_in_assets(w):
    if w in word_map:
        return word_map[w]
    
    best_score = -1.0
    best_match = None
    for title in word_map.keys():
        score = similar(w, title)
        if score > best_score:
            best_score = score
            best_match = title
    return word_map[best_match] if best_score > SIMILARITY_RATIO else None

def play_videos(video_paths):
    global current_video_path_text, is_playing_text, current_frame_text
    
    for path in video_paths:
        if not path:
            continue
            
        current_video_path_text = path
        cap = cv2.VideoCapture(path)
        
        while cap.isOpened() and is_playing_text:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.resize(frame, (640, 480))
            current_frame_text = frame
            time.sleep(0.03)
            
        cap.release()
        if not is_playing_text:
            break
    
    is_playing_text = False
    current_video_path_text = ""
    current_frame_text = None

# Voice-to-Sign Functions
def play_buffered_signs():
    global word_buffer, current_frame_voice, is_listening
    
    while is_listening or word_buffer:
        if len(word_buffer) >= SIGN_TRIGGER_COUNT:
            # Join the words and process
            text = ' '.join(word_buffer[:SIGN_TRIGGER_COUNT])
            del word_buffer[:SIGN_TRIGGER_COUNT]
            
            print(f"Processing text for signs: {text}")
            words = process_text(text)
            video_paths = []
            
            for word in words:
                match = find_in_assets(word)
                if match:
                    video_paths.append(match)
                else:
                    for char in word:
                        char_match = find_in_assets(char)
                        if char_match:
                            video_paths.append(char_match)
            
            if video_paths:
                for path in video_paths:
                    if not is_listening and not word_buffer:
                        break
                        
                    if not os.path.exists(path):
                        print(f"Video file not found: {path}")
                        continue
                        
                    print(f"Playing video: {path}")
                    cap = cv2.VideoCapture(path)
                    
                    if not cap.isOpened():
                        print(f"Failed to open video: {path}")
                        continue
                        
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    delay = 1/max(fps, 30)
                    
                    while cap.isOpened() and (is_listening or word_buffer):
                        ret, frame = cap.read()
                        if not ret:
                            break
                            
                        frame = cv2.resize(frame, (640, 480))
                        current_frame_voice = frame
                        time.sleep(delay)
                        
                    cap.release()
        else:
            time.sleep(0.1)
    
    current_frame_voice = None
    print("Sign playback finished")

def recognize_speech():
    global is_listening, recognized_text, word_buffer
    
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Start sign playback thread
        threading.Thread(target=play_buffered_signs, daemon=True).start()
        
        while is_listening:
            try:
                print("\nListening... (say 'stop' to end)")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                
                try:
                    # Try offline recognition first
                    text = recognizer.recognize_sphinx(audio).lower()
                    print(f"Offline recognition: {text}")
                except sr.UnknownValueError:
                    try:
                        # Fall back to online recognition
                        text = recognizer.recognize_google(audio).lower()
                        print(f"Online recognition: {text}")
                    except Exception as e:
                        print(f"Recognition failed: {e}")
                        continue
                
                recognized_text = text
                
                if "stop" in text:
                    is_listening = False
                    break
                
                # Add words to buffer
                new_words = text.split()
                word_buffer.extend(new_words)
                print(f"Buffer: {word_buffer} (Count: {len(word_buffer)})")
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Error: {e}")
                break
    
    print("Stopped listening")

# AR Display Functions
def ar_display_generator():
    global ar_display

    if ar_display is None:
        settings = UserSettings.get_settings("current_user")
        ar_display = ARSignLanguageDisplay()
        ar_display.apply_settings(settings)  # Apply initial settings

        # Start the listening and processing threads
        listen_thread = threading.Thread(target=ar_display.listen_thread)
        process_thread = threading.Thread(target=ar_display.process_words)
        listen_thread.daemon = True
        process_thread.daemon = True
        listen_thread.start()
        process_thread.start()

    while True:
        # Refresh settings periodically
        if int(time.time()) % 5 == 0:  # Every 5 seconds
            new_settings = UserSettings.get_settings("current_user", force_refresh=True)
            ar_display.apply_settings(new_settings)

        frame = ar_display.get_frame()
        if frame is None:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        

def settings_watcher():
    while True:
        time.sleep(5)  # Check every 5 seconds
        if ar_display:
            new_settings = UserSettings.get_settings("current_user", force_refresh=True)
            ar_display.apply_settings(new_settings)
        if ar_headset:
            new_settings = UserSettings.get_settings("current_user", force_refresh=True)
            ar_headset.apply_settings(new_settings)





# Routes
@app.route('/settings')
def settings():
    # In a real app, you'd get the user_id from the session
    user_id = "current_user"  # Replace with actual user ID from session
    settings = UserSettings.get_settings(user_id)
    return render_template('settings.html', settings=settings)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    try:
        # Get user ID (in a real app, this would come from session/auth)
        user_id = "current_user"  # Replace with actual user ID from session
        
        # Validate request
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400
            
        updates = request.get_json()
        if not updates:
            return jsonify({'status': 'error', 'message': 'No updates provided'}), 400

        # Validate and process updates
        processed_updates = {}
        
        # AR/VR settings
        if 'ar_vr_mode' in updates:
            processed_updates['ar_vr_mode'] = bool(updates['ar_vr_mode'])
            if processed_updates['ar_vr_mode']:
                # Special handling for AR/VR mode activation
                pass
    
        # Input/Output settings
        if 'input_mode' in updates:
            valid_input_modes = ['voice', 'text', 'gesture']
            if updates['input_mode'] in valid_input_modes:
                processed_updates['input_mode'] = updates['input_mode']
            else:
                return jsonify({'status': 'error', 'message': 'Invalid input mode'}), 400
                
        if 'output_mode' in updates:
            valid_output_modes = ['sign', 'voice', 'text']
            if updates['output_mode'] in valid_output_modes:
                processed_updates['output_mode'] = updates['output_mode']
            else:
                return jsonify({'status': 'error', 'message': 'Invalid output mode'}), 400
    
        # Voice and Sign settings
        if 'voice_speed' in updates:
            try:
                speed = int(updates['voice_speed'])
                if 50 <= speed <= 200:  # Validate range
                    processed_updates['voice_speed'] = speed
                    # Apply to TTS engine if running
                    if engine:
                        engine.setProperty('rate', speed)
                else:
                    return jsonify({'status': 'error', 'message': 'Voice speed out of range'}), 400
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid voice speed'}), 400
                
        if 'sign_size' in updates:
            try:
                size = int(updates['sign_size'])
                if 100 <= size <= 300:  # Validate range
                    processed_updates['sign_size'] = size
                else:
                    return jsonify({'status': 'error', 'message': 'Sign size out of range'}), 400
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid sign size'}), 400
    
        # Accessibility settings
        if 'high_contrast' in updates:
            processed_updates['high_contrast'] = bool(updates['high_contrast'])
            
        if 'text_size' in updates:
            try:
                size = int(updates['text_size'])
                if 12 <= size <= 24:  # Validate range
                    processed_updates['text_size'] = size
                else:
                    return jsonify({'status': 'error', 'message': 'Text size out of range'}), 400
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid text size'}), 400
    
        # Connectivity settings
        if 'bluetooth_enabled' in updates:
            processed_updates['bluetooth_enabled'] = bool(updates['bluetooth_enabled'])
    
        # User preferences
        if 'theme' in updates:
            valid_themes = ['light', 'dark', 'system']
            if updates['theme'] in valid_themes:
                processed_updates['theme'] = updates['theme']
            else:
                return jsonify({'status': 'error', 'message': 'Invalid theme'}), 400

        # Update in database
        UserSettings.update_settings(user_id, processed_updates)
        
        # Immediately apply settings to active components
        current_settings = UserSettings.get_settings(user_id, force_refresh=True)
        
        if ar_display:
            ar_display.apply_settings(current_settings)
        if ar_headset:
            ar_headset.apply_settings(current_settings)
        
        # If TTS engine is running, update its properties
        if engine:
            if 'voice_speed' in processed_updates:
                engine.setProperty('rate', processed_updates['voice_speed'])
            # Add other TTS-related settings here
            
        return jsonify({
            'status': 'success', 
            'message': 'Settings updated and applied',
            'settings': current_settings
        })
        
    except Exception as e:
        app.logger.error(f"Error updating settings: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error': str(e)
        }), 500
    
def update_theme():
    try:
        user_id = "current_user"
        data = request.get_json()
        theme = data.get('theme')
        
        if theme not in ['light', 'dark', 'system']:
            return jsonify({'status': 'error', 'message': 'Invalid theme'}), 400
            
        UserSettings.update_settings(user_id, {'theme': theme})
        
        # Return the new theme setting
        return jsonify({
            'status': 'success',
            'message': 'Theme updated',
            'theme': theme
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

#settings to handle themes
@app.context_processor
def inject_theme():
    user_id = "current_user"  # Replace with actual user ID from session
    settings = UserSettings.get_settings(user_id)
    return {'theme': settings.get('theme', 'light')}



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_to_voice')
def sign_to_voice():
    return render_template('sign_to_voice.html')

@app.route('/text_to_sign')
def text_to_sign():
    return render_template('text_to_sign.html')

@app.route('/voice_to_sign')
def voice_to_sign():
    return render_template('voice_to_sign.html')

@app.route('/ar_display')
def ar_display_route():
    return render_template('ar_signs.html')

# Sign-to-Voice Routes
@app.route('/video_feed_sign')
def video_feed_sign():
    return Response(sign_to_voice_generator(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_character')
def get_character():
    return current_character

@app.route('/stop_sign_to_voice')
def stop_sign_to_voice():
    global is_running_sign
    is_running_sign = False
    return jsonify({'status': 'success'})

# Text-to-Sign Routes
@app.route('/process_text', methods=['POST'])
def process_text_request():
    global is_playing_text
    
    is_playing_text = False
    time.sleep(0.5)
    
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({'status': 'error', 'message': 'No text provided'})
    
    words = process_text(text)
    video_paths = []
    
    for w in words:
        path = find_in_assets(w)
        if path:
            video_paths.append(path)
        else:
            video_paths.extend([find_in_assets(char) for char in w if find_in_assets(char)])
    
    if not video_paths:
        return jsonify({'status': 'error', 'message': 'No matching signs found'})
    
    is_playing_text = True
    threading.Thread(target=play_videos, args=(video_paths,)).start()
    
    return jsonify({'status': 'success'})

@app.route('/video_feed_text')
def video_feed_text():
    def generate():
        global current_frame_text
        
        while True:
            if current_frame_text is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame_text)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                blank_frame = cv2.imencode('.jpg', cv2.imread('static/blank.jpg'))[1].tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + blank_frame + b'\r\n')
            time.sleep(0.03)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_text_to_sign')
def stop_text_to_sign():
    global is_playing_text
    is_playing_text = False
    return jsonify({'status': 'success'})

# Voice-to-Sign Routes
@app.route('/start_listening', methods=['POST'])
def start_listening():
    global is_listening
    
    if is_listening:
        return jsonify({'status': 'error', 'message': 'Already listening'})
    
    is_listening = True
    threading.Thread(target=recognize_speech).start()
    
    return jsonify({'status': 'success'})

@app.route('/stop_listening', methods=['POST'])
def stop_listening():
    global is_listening
    is_listening = False
    return jsonify({'status': 'success'})

@app.route('/get_recognized_texts')
def get_recognized_texts():
    return jsonify({
        'current_text': ' '.join(word_buffer),
        'processed_text': recognized_text,
        'word_count': len(word_buffer)
    })

@app.route('/video_feed_voice')
def video_feed_voice():
    def generate():
        global current_frame_voice
        
        while True:
            if current_frame_voice is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame_voice)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                blank_frame = cv2.imencode('.jpg', cv2.imread('static/blank.jpg'))[1].tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + blank_frame + b'\r\n')
            time.sleep(0.03)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Add these routes with your other routes
@app.route('/ar_headset')
def ar_headset_route():
    return render_template('ar_words.html')

@app.route('/video_feed_headset')
def video_feed_headset():
    def generate():
        global ar_headset
        
        if ar_headset is None:
            ar_headset = ARHeadsetDisplay()
            # Start listening thread
            listen_thread = threading.Thread(target=ar_headset.listen_thread)
            listen_thread.daemon = True
            listen_thread.start()
            # Start processing thread
            process_thread = threading.Thread(target=ar_headset.process_words)
            process_thread.daemon = True
            process_thread.start()
        
        while True:
            frame = ar_headset.get_frame()
            if frame is None:
                break
                
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_headset', methods=['POST'])
def stop_headset():
    global ar_headset
    
    if ar_headset:
        ar_headset.listening = False
        ar_headset.cap.release()
        ar_headset = None
    
    return jsonify({'status': 'success'})

# AR Display Routes
@app.route('/video_feed_ar')
def video_feed_ar():
    return Response(ar_display_generator(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_ar_display', methods=['POST'])
def start_ar_display():
    global ar_display
    
    if ar_display is None:
        try:
            ar_display = ARSignLanguageDisplay()
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'success'})

@app.route('/stop_ar_display', methods=['POST'])
def stop_ar_display():
    global ar_display
    
    if ar_display:
        ar_display.is_listening = False
        ar_display.video_playing = False
        if ar_display.video_thread:
            ar_display.video_thread.join()
        ar_display.cap.release()
        ar_display = None
    
    return jsonify({'status': 'success'})


# Logout Route - Add this before the main block
@app.route('/logout')
def logout():
    """Handle user logout and redirect to React app"""
    try:
        # Clear server session data
        session.clear()
        
        # Create redirect response to React app
        response = redirect('http://localhost:5173/')
        
        # Clear all authentication-related cookies
        response.delete_cookie('session')
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('username')
        response.delete_cookie('remember_me')
        
        # Stop any running processes
        global is_running_sign, is_playing_text, is_listening, ar_display, ar_headset
        
        # Stop sign-to-voice
        is_running_sign = False
        
        # Stop text-to-sign
        is_playing_text = False
        
        # Stop voice-to-sign
        is_listening = False
        
        # Clean up AR displays
        if ar_display:
            ar_display.is_listening = False
            ar_display.video_playing = False
            if hasattr(ar_display, 'cap') and ar_display.cap:
                ar_display.cap.release()
            ar_display = None
            
        if ar_headset:
            ar_headset.listening = False
            if hasattr(ar_headset, 'cap') and ar_headset.cap:
                ar_headset.cap.release()
            ar_headset = None
        
        print("✅ User logged out successfully - redirected to React app")
        return response
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        # Fallback redirect even if there's an error
        return redirect('http://localhost:5173/')


if __name__ == '__main__':
    #threading for settings
    settings_thread = threading.Thread(target=settings_watcher)
    settings_thread.daemon = True
    settings_thread.start()

    # Create necessary directories
    if not os.path.exists(ASSETS_FOLDER):
        os.makedirs(ASSETS_FOLDER)
    
    # Create blank image if it doesn't exist
    if not os.path.exists('static/blank.jpg'):
        blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.imwrite('static/blank.jpg', blank_image)

    
    preload_assets()
    
    # Ensure Flask runs on port 5000 consistently
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print("")
    print("======= SignVision AR Application =======")
    print(f"Flask AR App: http://{host}:{port}")
    print("")
    print("*** WEBSITE SHOULD OPEN AUTOMATICALLY! ***")
    print("Website URL: http://localhost:5173")
    print("")
    print("Flow: Login Website (5173) -> AR Application (5000)")
    print("If browser doesn't open, visit: http://localhost:5173")
    print("=========================================")
    
    app.run(host=host, port=port, debug=True)
