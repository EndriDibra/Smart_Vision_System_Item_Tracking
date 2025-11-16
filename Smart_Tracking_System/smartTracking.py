# Author: Endri Dibra 
# Project: A smart tracking system for items/products

# Importing required libraries
import os
import cv2
import pyttsx3
import datetime
import threading
import numpy as np
import pytesseract
import pandas as pd
import speech_recognition as sr
from pyzbar.pyzbar import decode
from flask import Flask, render_template, request


# Initializing csv file
CSV_FILE = "Items.csv"

# Creating csv if not existing
if not os.path.exists(CSV_FILE):

    # Creating empty dataframe
    df = pd.DataFrame(columns=["Item_ID", "Type", "Text", "Timestamp", "Location"])

    # Saving empty dataframe
    df.to_csv(CSV_FILE, index=False)


# Defining function for loading data
def loadData():

    # Checking if CSV exists and has content
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:

        # Creating empty dataframe with headers
        df = pd.DataFrame(columns=["Item_ID", "Type", "Text", "Timestamp", "Location"])

        # Saving empty dataframe
        df.to_csv(CSV_FILE, index=False)

        # Returning empty dataframe
        return df

    # Reading csv into dataframe
    return pd.read_csv(CSV_FILE)



# Defining function for saving data
def saveData(df):

    # Writing dataframe to csv
    df.to_csv(CSV_FILE, index=False)


# Defining function for adding item
def addItem(itemID, itemType="barcode", text="", location="Station A"):

    # Loading existing data
    df = loadData()

    # Checking if item already exists
    if not df[df["Item_ID"] == itemID].empty:

        # Printing duplicate message
        print(f"Data Item {itemID} already exists. Skipping save.")

        # Returning without saving
        return

    # Creating timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Creating new row
    newRow = {

        "Item_ID": itemID,
        "Type": itemType,
        "Text": text,
        "Timestamp": timestamp,
        "Location": location
    }

    # Appending new row
    df = pd.concat([df, pd.DataFrame([newRow])], ignore_index=True)

    # Saving updated dataframe
    saveData(df)

    # Printing added item
    print(f"Data Added item: {itemID} ({itemType}) @ {timestamp}")


# Defining function for scanning camera
def scanCamera():

    # Starting video capture
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Printing camera status
    print("Vision Camera started. Press 'q' to quit scanning.")

    # Creating set to track scanned items in session
    scannedItems = set()

    # Looping frames
    while camera.isOpened():

        # Reading frame
        sucess, frame = camera.read()

        # Checking if camera is opened
        if not sucess:

            # Breaking if no frame
            break

        # Decoding codes
        codes = decode(frame)

        # Iterating codes
        for code in codes:

            # Decoding item id
            itemID = code.data.decode("utf-8")

            # Getting code type
            itemType = code.type

            # Checking if item was scanned in session
            if itemID not in scannedItems:

                # Adding item to csv
                addItem(itemID=itemID, itemType=itemType)

                # Adding to session set
                scannedItems.add(itemID)

            # Getting polygon points
            pts = code.polygon

            # Converting points
            pts = [(p.x, p.y) for p in pts]

            # Creating numpy array
            pts = np.array(pts, np.int32)

            # Reshaping points
            pts = pts.reshape((-1, 1, 2))

            # Drawing polygon
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

            # Putting text on frame
            cv2.putText(frame, itemID, (code.rect.left, code.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 200, 50), 2)
        
        # Displaying frame
        cv2.imshow("Smart Vision Track Scanner", frame)

        # Terminating program if q is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):

            # Breaking loop
            break

    # Releasing camera
    camera.release()

    # Destroying all opened windows
    cv2.destroyAllWindows()

    # Printing stop message
    print("Camera scanner stopped.")


# Defining function for extracting text from image
def extractTextFromImage(imgPath):

    # Reading image
    img = cv2.imread(imgPath)

    # Converting to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Extracting text
    text = pytesseract.image_to_string(gray)

    # Stripping text
    cleaned = text.strip()

    # Checking cleaned text
    if cleaned:

        # Adding extracted text
        addItem(itemId=f"text_{len(cleaned)}", itemType="ocr", text=cleaned)

    # Returning text
    return cleaned


# Initializing text-to-speech engine
engine = pyttsx3.init()


# Defining function for speaking text
def speak(text):

    # Printing speaking message
    print(f"TTS {text}")

    # Saying text
    engine.say(text)

    # Running speech engine
    engine.runAndWait()


# Defining function for listening command
# Defining function for listening command with ambient noise adjustment
def listenForCommand():

    # Creating recognizer
    recognizer = sr.Recognizer()

    # Using microphone
    with sr.Microphone() as source:

        # Adjusting for ambient noise to reduce background interference
        print("STT Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        # Listening for command
        print("STT Speak now please...")
        audio = recognizer.listen(source)

    # Trying recognizing
    try:

        # Recognizing audio
        text = recognizer.recognize_google(audio)

        # Printing recognized text
        print("STT You said:", text)

        # Returning lowercased text
        return text.lower()

    # Handling error
    except:

        # Speaking error
        speak("I didn't understand that. Please repeat again.")

        return ""


# Defining function for voice query loop
def voiceQueryLoop():

    # Speaking activation
    speak("Voice assistant activated. Ask me about any item.")

    # Looping for commands
    while True:

        # Listening command
        cmd = listenForCommand()

        # Checking stop command
        if "stop" in cmd or "exit" in cmd:

            # Speaking stop message
            speak("Stopping voice assistant.")

            # Breaking loop
            break

        # Loading data
        df = loadData()

        # Splitting command
        words = cmd.split()

        # Getting candidates
        itemCandidates = [w for w in words if len(w) > 2]

        # Checking candidates
        if not itemCandidates:

            # Speaking error
            speak("I couldn't detect an item ID. Try again.")

            # Continuing loop
            continue

        # Getting item id
        itemID = itemCandidates[-1]

        # Searching item in dataframe
        matches = df[df["Item_ID"].astype(str).str.contains(itemID)]

        # Checking matches
        if matches.empty:

            # Speaking not found
            speak(f"I cannot find item {itemID} in the system.")

        # Handling found match
        else:

            # Getting last entry
            last = matches.iloc[-1]

            # Speaking last location
            speak(f"Item {itemID} was last seen at {last['Location']} on {last['Timestamp']}.")


# Creating Flask app
app = Flask(__name__)


# Defining dashboard route
@app.route("/", methods=["GET", "POST"])

def dashboard():

    # Loading data
    df = loadData()

    # Checking post request
    if request.method == "POST":

        # Getting search input
        search = request.form.get("search", "")

        # Filtering dataframe
        df = df[df["Item_ID"].astype(str).str.contains(search)]

    # Rendering template
    return render_template("dashboard.html", data=df)


# Defining function for running UI
def runUI():

    # Running flask app
    app.run(port=5000, debug=False, use_reloader=False)


# Starting main program
if __name__ == "__main__":

    # Printing menu options
    print("1. Run QR/Barcode Scanner")
    print("2. Run Voice Assistant")
    print("3. Run Web Dashboard")
    print("4. OCR Scan From Image")
    print("5. Exit")

    # Looping for user input
    while True:

        # Getting user choice
        choice = input("Choose option: ")

        # Checking choice 1
        if choice == "1":

            # Running camera scanner
            scanCamera()

        # Checking choice 2
        elif choice == "2":

            # Running voice assistant
            voiceQueryLoop()

        # Checking choice 3
        elif choice == "3":

            # Printing UI status
            print("UI Running at http://127.0.0.1:5000")

            # Running UI in thread
            threading.Thread(target=runUI).start()

        # Checking choice 4
        elif choice == "4":

            # Getting image path
            path = input("Enter image path: ")

            # Extracting text
            text = extractTextFromImage(path)

            # Printing extracted text
            print("Extracted text:", text)

        # Checking choice 5
        elif choice == "5":

            # Printing goodbye
            print("Goodbye!")

            # Breaking loop
            break

        # Handling invalid choice
        else:

            # Printing invalid message
            print("Invalid option.")