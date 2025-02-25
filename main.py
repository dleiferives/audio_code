import sqlite3
import subprocess
import tempfile
import os
import hashlib
import threading
from playsound import playsound

class EspeakServer:
    """
    A TTS server that uses espeak-ng to generate WAV audio,
    stores responses in an SQLite database (default 'espeak_resp.db'),
    and also caches responses in memory.
    """

    def __init__(self, voice="en-us", rate="150", db_path="espeak_resp.db"):
        """
        Initialize the EspeakServer.

        Args:
            voice (str): The voice (language/accent) to use, e.g., 'en-us'.
            rate (str): Speech rate (words per minute).
            db_path (str): Path to the SQLite database file.
        """
        self.voice = voice
        self.rate = rate
        self.db_path = db_path
        self.cache = {}  # in-memory cache: {hash(text): wav_data (bytes)}
        self.lock = threading.Lock()  # Protect cache and DB operations
        self._init_db()

    def _init_db(self):
        """Creates the SQLite table if it does not already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    key TEXT PRIMARY KEY,
                    wav_data BLOB
                )
            """)
            conn.commit()

    def _retrieve_from_db(self, key):
        """Retrieves WAV data from the database for the given key."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT wav_data FROM responses WHERE key=?", (key,))
            row = cur.fetchone()
            if row:
                return row[0]
            return None

    def _store_in_db(self, key, wav_data):
        """Stores the WAV data in the database using the given key."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO responses (key, wav_data) VALUES (?, ?)",
                (key, wav_data)
            )
            conn.commit()

    def speak(self, text):
        """
        Synthesizes speech from the provided text.
        First checks the in-memory cache, then the database.
        If not cached, generates the speech using espeak-ng,
        caches the result, and returns the WAV data (bytes).
        """
        key = hashlib.md5(text.encode("utf-8")).hexdigest()

        # Check in-memory cache first.
        with self.lock:
            if key in self.cache:
                return self.cache[key]

        # Not found in memory; check the database.
        wav_data = self._retrieve_from_db(key)
        if wav_data is not None:
            with self.lock:
                self.cache[key] = wav_data
            return wav_data

        # Not in cache or DB: generate the WAV data with espeak-ng.
        try:
            # Create a temporary file for espeak-ng output.
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_filename = tmp_file.name

            # Build and run the espeak-ng command.
            command = [
                "espeak-ng",
                "-s", self.rate,
                "-v", self.voice,
                "-w", temp_filename,
                text
            ]
            subprocess.run(command, check=True)

            # Read the generated WAV data.
            with open(temp_filename, "rb") as f:
                wav_data = f.read()
            os.remove(temp_filename)

            # Cache and store the result.
            with self.lock:
                self.cache[key] = wav_data
            self._store_in_db(key, wav_data)

            return wav_data

        except Exception as e:
            print(f"Error generating TTS: {e}")
            return None

def play_wav_data(wav_data):
    """
    Plays WAV data by writing it temporarily to a file and using playsound.

    Args:
        wav_data (bytes): The WAV audio data
    """
    if not wav_data:
        print("No WAV data available to play.")
        return

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(wav_data)
            tmp_file.flush()
            temp_filename = tmp_file.name

        # Play the audio file.
        playsound(temp_filename)

    except Exception as e:
        print(f"Error playing sound: {e}")

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    # You can override the DB file by passing a different path, e.g.,
    # server = EspeakServer(db_path="my_custom_db.db")
    server = EspeakServer()  # Uses the default "espeak_resp.db"

    while True:
        text = input("Enter text to speak (or type 'exit' to quit): ")
        if text.lower() == "exit":
            break

        wav_data = server.speak(text)
        if wav_data:
            print("Playing synthesized speech …")
            play_wav_data(wav_data)
        else:
            print("Failed to generate speech.")
