import os
import speech_recognition as sr
import threading
import queue
import time
from datetime import datetime
import openai
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError

q = queue.Queue()
running = True
openai.api_key = ""

def transcript(file):
    try:
        transcript = openai.Audio.transcribe("whisper-1", file)
        transcript_utf8 = json.dumps(transcript.text, ensure_ascii=False).encode('utf8').decode()
        print(transcript_utf8.replace('"',''))
        return
    except Exception as e:
        pass

def record_audio(q):
    with sr.Microphone() as source:
        while running:
            audio = r.record(source, duration=4)
            q.put(audio)

def process_audio(q):
    
    while running:
        temp_filename = str(time.time()) + ".wav" 
        try:
            audio = q.get(timeout=1)  
            if audio:
                
                with open(temp_filename, "wb") as f:
                    f.write(audio.get_wav_data())
                
                with open(temp_filename, "rb") as file_obj:

                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(transcript(file_obj))
                        try:
                            future.result(timeout=3)  
                        except Exception as e:
                            pass

                os.remove(temp_filename)
                
                    
                
        except queue.Empty:
            pass
        except Exception as e:
            print(e)

r = sr.Recognizer()

# start threads
t1 = threading.Thread(target=record_audio, args=(q,))
t2 = threading.Thread(target=process_audio, args=(q,))

t1.daemon = True
t2.daemon = True

t1.start()
t2.start()

try:
    while running:
        time.sleep(1)
except KeyboardInterrupt:
    print("quiting...")
    running = False
    t1.join()
    t2.join()
