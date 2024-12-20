import ctypes
import time
import sys
import tkinter as tk
from threading import Thread
from tkinter import messagebox
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
        sys.exit(10)
    else:
        print("PCAN initialized successfully.")

# Function to send CAN message
def send_can_message(can_id, data):
    class  xTPCANMsg(ctypes.Structure):
        _fields_ = [("ID", ctypes.c_uint32),
                    ("MSGTYPE", ctypes.c_ubyte),
                    ("LEN", ctypes.c_ubyte),
                    ("DATA", ctypes.c_ubyte * 8)]
    
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
def main():
    
    can_init()
    
    try:
           
        #Sending speed from 1 to 100
        for value in range(1, 101):
            # Prepare the data (only using the first byte)
            data = [1] * 8  
            
            data[1] = value
            # Send the CAN message
            send_can_message(0x607, data)  # Replace 0x607 with your desired CAN ID

            # Wait for 0.2 seconds between each send
            time.sleep(0.2)
            
        #Sending speed data from 100 to 0
        for value in range(1, 102):
            # Prepare the data (only using the first byte)
            data = [1] * 8  # 8 bytes of data; adjust if necessary
            data[1] = 101-value
            # Send the CAN message
            send_can_message(0x607, data)  # Replace 0x607 with your desired CAN ID
            time.sleep(0.2)
            
        # Function to send SOC from 1 to 100
        # def send_soc_messages():
        for soc_value in range(100, 1001,50 ):  # Range from 0 to 1000, representing 0% to 100%
            data = [0] * 8  # 8 bytes of data
        
            data[1] = soc_value & 0xFF  
            data[0] = (soc_value >> 8) & 0xFF  
        
            send_can_message(0x602, data)  # Send message with CAN ID 0x602
            time.sleep(0.5)  # Add delay to mimic real-time data flow
            
        # # Function to send SOC from 100 to 1
        # def send_soc_messages():
        for soc_value in range(1001,100,-50 ):  # Range from 0 to 1000, representing 0% to 100%
            data = [0] * 8  # 8 bytes of data
        
            data[1] = soc_value & 0xFF  
            data[0] = (soc_value >> 8) & 0xFF  
        
            send_can_message(0x602, data)  # Send message with CAN ID 0x602
            time.sleep(0.5)  # Add delay to mimic real-time data flow

        data = [0] * 8  # 8 bytes of data; adjust if necessary
            
        data[0] = 1
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        data[0] = 18
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        data[0] = 20
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        data[0] = 17
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        data[0] = 34
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        data[0] = 66
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        data[0] = 17
            # Send the CAN message
        send_can_message(0x607, data)
        time.sleep(5)
        messagebox.showinfo("Information", "Test Completed. Press START TEST button to restart or EXIT to quit application")
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    finally:
        can_de_init()


# Function to run `main` in a separate thread
def run_main_in_thread():
    thread = Thread(target=main)
    thread.daemon = True  # Ensures thread exits when the GUI is closed
    thread.start()


# Creating the GUI
def create_gui():
    root = tk.Tk()
    root.title("Chimera Test Application | Kayens Technology")
    root.geometry("350x500")

    # Add a button to start the main function
    start_button = tk.Button(root, text="START TEST", command=run_main_in_thread, font=("Arial", 12))
    start_button.pack(pady=20)

    # Add a button to close the application
    exit_button = tk.Button(root, text="EXIT", command=root.quit, font=("Arial", 12))
    exit_button.pack(pady=20)

    # Run the GUI event loop
    root.mainloop()


# Run GUI
if __name__ == "__main__":
    
   create_gui()
