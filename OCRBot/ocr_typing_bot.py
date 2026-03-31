import rumps
import pytesseract
import pyautogui
import pyperclip
from PIL import Image
from pynput import keyboard
import threading
import subprocess
import time
import os

captured_text = ""

def ocr_from_selection():
    global captured_text

    # Use AppleScript to get screenshot selection saved to temp file
    temp_path = "/tmp/ocr_capture.png"
    script = f'screencapture -i {temp_path}'
    subprocess.run(script, shell=True)

    if os.path.exists(temp_path):
        image = Image.open(temp_path)
        text = pytesseract.image_to_string(image)
        captured_text = text.strip()
        pyperclip.copy(captured_text)
        rumps.notification("OCR Bot", "", "Text captured successfully!")

def type_captured_text():
    global captured_text
    clipboard_text = pyperclip.paste().strip()
    text_to_type = clipboard_text if clipboard_text else captured_text

    if text_to_type:
        rumps.notification("OCR Bot", "", "Typing text...")
        pyautogui.write(text_to_type, interval=0.02)
    else:
        rumps.notification("OCR Bot", "", "No text available to type.")

def hotkey_listener():
    COMBO = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('v')}
    pressed_keys = set()

    def on_press(key):
        if key in COMBO:
            pressed_keys.add(key)
        if COMBO.issubset(pressed_keys):
            type_captured_text()

    def on_release(key):
        if key in pressed_keys:
            pressed_keys.remove(key)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

class OCRTypingBot(rumps.App):
    def __init__(self):
        super(OCRTypingBot, self).__init__("OCR Bot")
        self.menu = ["Capture Text", "Type Text"]

    @rumps.clicked("Capture Text")
    def capture_text(self, _):
        threading.Thread(target=ocr_from_selection).start()

    @rumps.clicked("Type Text")
    def type_text(self, _):
        threading.Thread(target=type_captured_text).start()

if __name__ == "__main__":
    print("🚀 Starting OCR Bot...")
    threading.Thread(target=hotkey_listener, daemon=True).start()
    OCRTypingBot().run()
