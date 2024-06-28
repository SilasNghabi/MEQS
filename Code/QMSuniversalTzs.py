import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import socket
import pygame
import threading
import cv2  
import requests

# Create the main window
root = tk.Tk()
root.title("Queue Management System")

# Initialize Pygame for audio
pygame.init()

# Set window to full-screen mode
root.attributes('-fullscreen', True)

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Define frame styles
frame_style = {"bd": 2, "relief": "raised"}

# Set up the TCP server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 33455))  
server_socket.listen(8)  # Allow up to 4 connections

# Customer message frame
customer_message_width = int(screen_width * 0.98)  # 98% of window width
customer_message_padding = int(screen_width * 0.01)  # 1% padding from both sides
customer_message = tk.Frame(root, width=customer_message_width, height=int(screen_height * 0.1), **frame_style)
customer_message.place(x=customer_message_padding, y=int(screen_height * 0.85))

# Add label inside the customer message frame
message_label = tk.Label(customer_message, text="DEAR CUSTOMER, WE ARE PLEASED TO SERVE YOU. KINDLY SIT AND WAIT WHILE WE ARE SERVING OTHER CUSTOMERS",
                         font=("Poppins", int(screen_height * 0.02), "bold"), bg="lightgreen", justify="center")
message_label.pack(fill=tk.BOTH, expand=True)

# Counter frames
num_counters = 4
counter_frame_width = int(screen_width * 0.1)  # 10% of window width
counter_frame_height = int(screen_height * 0.1)  # 10% of window height
counter_spacing = int(screen_width * 0.01)  # Horizontal spacing between counters
counter_x_start = screen_width - counter_frame_width  # Starting X coordinate for the first counter frame
counter_y = 0  # Y coordinate for all counter frames

# List to store references to token number labels
token_number_labels = []

for i in range(num_counters):
    # Add frame to display counters
    counter_frame = tk.Frame(root, width=counter_frame_width, height=counter_frame_height, **frame_style)
    counter_frame.place(x=counter_x_start - i * (counter_frame_width + counter_spacing), y=counter_y)

    # Add label to display counter ID
    counter_label = tk.Label(counter_frame, text=f"Counter\n{num_counters - i}", font=("calibri", int(screen_height * 0.03), "bold"), fg="white", bg="green")
    counter_label.pack(fill=tk.BOTH, expand=True)
    # Center the label vertically and horizontally
    counter_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Add "NOW SERVING" frames below counters
    now_serving_frame = tk.Frame(root, width=counter_frame_width, height=int(counter_frame_height / 2), bg="white")
    now_serving_frame.place(x=counter_x_start - i * (counter_frame_width + counter_spacing), y=counter_y + counter_frame_height)

    # Add label with "NOW SERVING" text
    now_serving_label = tk.Label(now_serving_frame, text="NOW SERVING", fg="green", font=("Arial", int(screen_height * 0.02), "bold"), bg="white")
    now_serving_label.pack(fill=tk.BOTH, expand=True)

    # Add frames for displaying token numbers
    token_frame = tk.Frame(root, width=counter_frame_width, height=int(counter_frame_height * 1.5), **frame_style)
    token_frame.place(x=counter_x_start - i * (counter_frame_width + counter_spacing), y=counter_y + counter_frame_height * 1.5)
    
    # Create a label to display the token number received
    token_number_label = tk.Label(token_frame, text="", font=("calibri", int(screen_height * 0.07), "bold"), fg="black")
    token_number_label.pack(fill=tk.BOTH, expand=True)
    token_number_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Append the label to the list
    token_number_labels.append(token_number_label)


API_KEY = 'fca_live_mYsEF4trK4HJtYz6voDrrO5663krEJewkSMnRYMY'

def update_prices():
    headers = {'apikey': API_KEY}
    api_endpoint = 'https://api.freecurrencyapi.com/v1/latest'
    params = {'apikey': API_KEY, 'currencies': ','.join(currencies)}
    response = requests.get(api_endpoint, headers=headers, params=params)
    data = response.json()
    
    print("API Response:", data)
    
    if 'data' in data:
        currency_data = data['data']
        
        usd_to_tzs = 2600  # 1 USD to TZS conversion rate
        spread_percentage = 2.0 / 100.0
        
        for i, currency in enumerate(currencies):
            if currency in currency_data:
                exchange_rate_to_usd = currency_data[currency]
                
                # print(f"Exchange Rate for {currency}: {exchange_rate_to_usd}")
                
                # Convert the exchange rate to TZS
                if currency == 'USD':
                    base_price_tzs = usd_to_tzs
                else:
                    base_price_tzs = usd_to_tzs / exchange_rate_to_usd
                
                buy_price_tzs = base_price_tzs * (1 - spread_percentage)
                sell_price_tzs = base_price_tzs * (1 + spread_percentage)
                
                print(f"Currency: {currency}")
                print(f"Base Price (TZS): {base_price_tzs}")
                print(f"Buy Price (TZS): {buy_price_tzs}")
                print(f"Sell Price (TZS): {sell_price_tzs}")
                
                buy_labels[i].config(text=f"{buy_price_tzs:.2f} TZS")
                sell_labels[i].config(text=f"{sell_price_tzs:.2f} TZS")
            else:
                print(f"No exchange rate data found for currency {currency}")
    else:
        print("Invalid API response format")
    
    root.after(300000, update_prices)

# Define currencies
currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'CNY', 'CHF', 'AUD']
base_currency = 'USD'

# Frame for currency operations
currency_frame_width = int(screen_width * 0.55)
currency_frame_height = int(screen_height * 0.25)
currency_frame = tk.Frame(root, width=currency_frame_width, height=currency_frame_height, bg="lightgray")
currency_frame.place(x=0, y=int(screen_height * 0.55))  # Place below token frames

# Define column widths for currency operations
column_width = currency_frame_width // 3

# Labels for headings
currency_label = tk.Label(currency_frame, text="CURRENCY", bg="green", font=("Arial", int(screen_height * 0.02), "bold"), fg="white")
currency_label.place(x=0, y=0, width=column_width)

buy_label = tk.Label(currency_frame, text="BUY", bg="green", font=("Arial", int(screen_height * 0.02), "bold"), fg="white")
buy_label.place(x=column_width, y=0, width=column_width)

sell_label = tk.Label(currency_frame, text="SELL", bg="green", font=("Arial", int(screen_height * 0.02), "bold"), fg="white")
sell_label.place(x=2 * column_width, y=0, width=column_width)

# Labels for currency names
currency_labels = []
for i, currency in enumerate(currencies):
    label = tk.Label(currency_frame, text=currency, bg="lightgreen", font=("Arial", int(screen_height * 0.015), "bold"))
    label.place(x=0, y=int(screen_height * 0.025) * (i+1), width=column_width)
    currency_labels.append(label)

# Labels for buy prices
buy_labels = []
for i in range(len(currencies)):
    label = tk.Label(currency_frame, text="", bg="lightgreen", font=("Arial", int(screen_height * 0.015), "bold"))
    label.place(x=column_width, y=int(screen_height * 0.025) * (i+1), width=column_width)
    buy_labels.append(label)

# Labels for sell prices
sell_labels = []
for i in range(len(currencies)):
    label = tk.Label(currency_frame, text="", bg="lightgreen", font=("Arial", int(screen_height * 0.015), "bold"))
    label.place(x=2 * column_width, y=int(screen_height * 0.025) * (i+1), width=column_width)
    sell_labels.append(label)

# Update prices initially
#update_prices()

# Set the path to the directory containing advertisement videos
video_directory = '/home/silas/Desktop/MEQS/Videos'

# Set the path to the directory containing audio files
audio_directory = '/home/silas/Desktop/MEQS/audios'

# Define a dictionary to keep track of tokens served by each counter ID
served_tokens = {}

# Function to update tokens on frames
def update_token_frame(counter, token):
    # Get the token frame corresponding to the counter
    token_frame = root.nametowidget(f"token_frame_{counter}")

    # Clear previous token label (if any)
    for widget in token_frame.winfo_children():
        widget.destroy()

    # Add new token label
    token_label = tk.Label(token_frame, text=f"Token: {token}", font=("Arial", 12), bg="white")
    token_label.pack(fill=tk.BOTH, expand=True)

# Function to play advertisement videos within the GUI window
def play_video():
    # Create a Tkinter frame for video playback
    video_frame = tk.Frame(root, width=int(screen_width * 0.55), height=int(screen_height * 0.5), **frame_style)
    video_frame.place(x=0, y=0)

    # Create a Tkinter canvas to display the video frames
    video_canvas = tk.Canvas(video_frame, width=int(screen_width * 0.55), height=int(screen_height * 0.5))
    video_canvas.pack(fill="both", expand=True)

    # List all video files in the directory
    video_files = [f for f in os.listdir(video_directory) if os.path.isfile(os.path.join(video_directory, f))]

    # Function to play a video file
    def play_video_file(video_path):
        video_capture = cv2.VideoCapture(video_path)

        # Check if the video capture is successful
        if not video_capture.isOpened():
            print(f"Error: Unable to open video file {video_path}")
            return

        # Function to update the canvas with new video frames
        def update_canvas():
            nonlocal video_capture
            ret, frame = video_capture.read()
            if ret:
                # Resize the frame to fit the canvas size
                frame = cv2.resize(frame, (int(screen_width * 0.55), int(screen_height * 0.5)))

                # Convert the OpenCV frame to PIL format
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                # Convert the PIL image to Tkinter format
                photo = ImageTk.PhotoImage(image=image)
                # Update the canvas with the new photo
                video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                video_canvas.photo = photo  # Store reference to prevent garbage collection
                video_frame.after(30, update_canvas)
            else:
                # Restart the video when it reaches the end
                video_capture.release()
                play_video_file(video_path)

        # Start updating the canvas with video frames
        update_canvas()

    # Loop through video files and play each one
    for video_file in video_files:
        video_path = os.path.join(video_directory, video_file)
        play_video_file(video_path)

# Function to play audio sequence corresponding to the received token and counter numbers
def play_audio_sequence(token, counter, language):
    language_folder = os.path.join(audio_directory, language)
    tens = token // 10 * 10
    units = token % 10

    if 10 < token < 20 and language == 'English':
        audio_sequence = [
            "bell.mp3",
            "MtejaNamba.mp3",
            f"nam{token}.mp3",
            "TafadhaliElekeaDirishaNamba.mp3",
            f"nam{counter}.mp3"
        ]
    else:
        audio_sequence = [
            "bell.mp3",
            "MtejaNamba.mp3",
            f"nam{tens}.mp3" if tens else "",
            "Na.mp3" if units and tens and language == "Swahili" else "",
            f"nam{units}.mp3" if units else "",
            "TafadhaliElekeaDirishaNamba.mp3",
            f"nam{counter}.mp3"
        ]

    for audio_file in audio_sequence:
        if audio_file:
            file_path = os.path.join(language_folder, audio_file)
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue

def receive_data():
    while True:
        try:
            print("Waiting for connection...")
            client_socket, client_address = server_socket.accept()  
            print(f"Connection established with {client_address}")

            data = client_socket.recv(1024).decode()
            print("Received data:", data)

            # Extract token and counter numbers from received data
            counter, token = data.strip().split(',')
            counter = int(counter)
            token = int(token)

            # Check if the token has already been served by another counter
            if token not in served_tokens.values():
                served_tokens[counter] = token

                # Update the respective token number label
                token_number_labels[num_counters - counter].config(text=token)

                play_audio_sequence(token, counter, 'Swahili')
                play_audio_sequence(token, counter, 'English')
            else:
                print(f"Token {token} has already been served by another counter.")

        except KeyboardInterrupt:
            print('Program interrupted')
            break
        finally:
            client_socket.close()


if __name__ == "__main__":
    # Start the thread to receive data
    data_thread = threading.Thread(target=receive_data)
    data_thread.start()

    # Start video playback
    play_video()

    # Start the main event loop
    root.mainloop()

    # Close the server socket
    server_socket.close()
    pygame.quit()
