import ctypes
import time
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from threading import Thread

fade_animation_running = True

# Load the PCANBasic DLL
pcan = ctypes.windll.LoadLibrary("PCANBasic.dll")

# Constants for PCAN
PCAN_USBBUS1 = 0x51  # This is the device handle; change if necessary
PCAN_BAUD_250K = 0x011C  # Baud rate for 250k; adjust if necessary

# Function to initialize PCAN
def can_init():
    result = pcan.CAN_Initialize(PCAN_USBBUS1, PCAN_BAUD_250K)
    if result != 0:
        print(f"Initialization failed with error code: {result}")
        messagebox.showerror("Error", f"Initialization failed with error code: {result}")
        sys.exit(10)

# Function to send CAN message
def send_can_message(can_id, data):
    class xTPCANMsg(ctypes.Structure):
        _fields_ = [
            ("ID", ctypes.c_uint32),
            ("MSGTYPE", ctypes.c_ubyte),
            ("LEN", ctypes.c_ubyte),
            ("DATA", ctypes.c_ubyte * 8),
        ]

    # Create a message object
    msg = xTPCANMsg()
    msg.ID = can_id
    msg.MSGTYPE = 0  # Standard message
    msg.LEN = len(data)

    for i in range(len(data)):
        msg.DATA[i] = data[i]

    # Send the CAN message
    result = pcan.CAN_Write(PCAN_USBBUS1, ctypes.byref(msg))
    if result != 0:
        print(f"Send failed with error code: {result}")
    else:
        print(f"Sent data: {data[1]} on CAN ID: 0x{can_id:X}")

# Function to uninitialize PCAN
def can_de_init():
    pcan.CAN_Uninitialize(PCAN_USBBUS1)
    print("PCAN uninitialized.")

# Main function
def main(progress_bar, progress_label, indicator_label):
    can_init()
    total_steps = 244
    current_step = 0

    try:
        fade_in_out(indicator_label)

        # Sending speed from 1 to 100
        for value in range(1, 101):
            data = [1] * 8
            data[1] = value
            send_can_message(0x607, data)
            time.sleep(0.2)

            current_step += 1
            update_progress(progress_bar, progress_label, current_step, total_steps)

        # Sending speed from 100 to 0
        for value in range(1, 102):
            data = [1] * 8
            data[1] = 101 - value
            send_can_message(0x607, data)
            time.sleep(0.2)

            current_step += 1
            update_progress(progress_bar, progress_label, current_step, total_steps)

        # Sending SOC from 1 to 100
        for soc_value in range(100, 1001, 50):
            data = [0] * 8
            data[1] = soc_value & 0xFF
            data[0] = (soc_value >> 8) & 0xFF
            send_can_message(0x602, data)
            time.sleep(0.5)

            current_step += 1
            update_progress(progress_bar, progress_label, current_step, total_steps)

        # Sending SOC from 100 to 1
        for soc_value in range(1001, 100, -50):
            data = [0] * 8
            data[1] = soc_value & 0xFF
            data[0] = (soc_value >> 8) & 0xFF
            send_can_message(0x602, data)
            time.sleep(0.5)

            current_step += 1
            update_progress(progress_bar, progress_label, current_step, total_steps)

        # Final test sequence
        for value in [1, 18, 20, 17, 34, 66, 17]:
            data = [0] * 8
            data[0] = value
            send_can_message(0x607, data)
            time.sleep(5)

            current_step += 1
            update_progress(progress_bar, progress_label, current_step, total_steps)

        messagebox.showinfo("Information", "Test Completed. Press START TEST button to restart or EXIT to quit application")
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    finally:
        can_de_init()

# Function to update the progress bar and label
def update_progress(progress_bar, progress_label, current, total):
    global fade_animation_running
    progress = int((current / total) * 100)
    progress_bar['value'] = progress
    progress_label.config(text=f"Completed: {progress}%")
    progress_bar.update()

    if progress >= 100:
        fade_animation_running = False

# Animation
def fade_in_out(indicator_label, alpha=0):
    if fade_animation_running:
        alpha = (alpha + 0.1) % 1.0
        indicator_label.config(fg=f'#{int(alpha * 255):02x}{int(alpha * 255):02x}{int(alpha * 255):02x}')
        indicator_label.after(100, fade_in_out, indicator_label, alpha)

# Function to run `main` in a separate thread
def run_main_in_thread(progress_bar, progress_label, indicator_label):
    global fade_animation_running
    fade_animation_running = True
    thread = Thread(target=main, args=(progress_bar, progress_label, indicator_label))
    thread.daemon = True
    thread.start()

# Creating the GUI
def create_gui():
    root = tk.Tk()
    root.title("Chimera Test Application | Kayens Technology")
    root.geometry("400x300")

    # Start button
    start_button = tk.Button(root, text="START TEST", command=lambda: run_main_in_thread(progress_bar, progress_label, indicator_label), font=("Arial", 12, "bold"), bg="green", fg="white")
    start_button.pack(pady=20)

     # Progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate")
    progress_bar.pack(pady=20)

    # Progress label
    progress_label = tk.Label(root, text="Completed: 0%", font=("Arial", 10, "bold"))
    progress_label.pack(pady=10)

    # Indicator label
    indicator_label = tk.Label(root, text="●", font=("Arial", 30, "bold"), fg="green")
    indicator_label.place(x=345, y=10)

    # Exit button
    exit_button = tk.Button(root, text="EXIT", command=root.quit, font=("Arial", 12, "bold"), bg="red", fg="white")
    exit_button.pack(pady=20)

    root.mainloop()

# Run GUI
if __name__ == "__main__":
    create_gui()
