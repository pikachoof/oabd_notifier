'''
TODO:
- Fix the timer still working while the timer is "Inactive".
'''

import tkinter as tk
from tkinter import messagebox
import psutil
from datetime import datetime, timedelta
import os
#from playsound import playsound # Import the playsound library

# --- Constants for Notification Window ---
NOTIFICATION_WIDTH = 350
NOTIFICATION_HEIGHT = 100
NOTIFICATION_DURATION_MS = 5000  # 5 seconds
TIMER_CHECK_INTERVAL_MS = 1000  # Check every 1 second
TIMERS_FILE_NAME = "timers.txt"
SOUND_FILE = "notification_sound.wav" # Specify the name of your sound file here

class ProcessMonitorApp(tk.Tk):
    """
    A Tkinter application to monitor processes and send timed notifications.
    This version includes a UI to view active timers and the ability to save/load them,
    as well as activate/deactivate and delete individual timers. The notification
    logic is now based on the total elapsed time of the process and includes sound.
    """
    def __init__(self):
        super().__init__()
        self.title("Process Timer")
        self.geometry("450x600")  # Adjusted window size
        self.minsize(450, 600) # Set the minimum allowed size of the window
        self.config(bg="#f0f0f0")

        self.timers = []
        
        self.setup_ui()
        self.load_timers()
        self.check_timers_loop()

    def setup_ui(self):
        """
        Sets up the main application UI elements, including a listbox for timers
        and buttons for saving, loading, toggling, and deleting.
        """
        # Main frame with padding
        main_frame = tk.Frame(self, padx=20, pady=20, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both")

        # Title
        title_label = tk.Label(main_frame, text="Process Timer Setup", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))

        # --- Input Section ---
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Process Name (e.g., chrome.exe):", bg="#f0f0f0", font=("Helvetica", 10)).pack(anchor="w")
        self.process_name_entry = tk.Entry(input_frame, bd=2, relief="groove")
        self.process_name_entry.pack(pady=5, fill="x")

        tk.Label(input_frame, text="Interval (in minutes):", bg="#f0f0f0", font=("Helvetica", 10)).pack(anchor="w")
        self.interval_entry = tk.Entry(input_frame, bd=2, relief="groove")
        self.interval_entry.pack(pady=5, fill="x")

        tk.Label(input_frame, text="Notification Message:", bg="#f0f0f0", font=("Helvetica", 10)).pack(anchor="w")
        self.message_entry = tk.Entry(input_frame, bd=2, relief="groove")
        self.message_entry.pack(pady=5, fill="x")

        # --- Buttons Section ---
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=20, fill="x")
        
        tk.Button(button_frame, text="Add Timer", command=self.add_timer, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold")).pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(button_frame, text="Save Timers", command=self.save_timers, bg="#2196F3", fg="white", font=("Helvetica", 10, "bold")).pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(button_frame, text="Load Timers", command=self.load_timers, bg="#FFC107", fg="white", font=("Helvetica", 10, "bold")).pack(side="left", padx=5, expand=True, fill="x")

        # --- Timers Display Section ---
        tk.Label(main_frame, text="Active Timers", font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(pady=(20, 5))
        self.timers_listbox = tk.Listbox(main_frame, height=10, bd=2, relief="groove")
        self.timers_listbox.pack(pady=10, fill="both", expand=True)

        # --- Timer Management Buttons ---
        manage_button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        manage_button_frame.pack(fill="x")

        self.toggle_button = tk.Button(manage_button_frame, text="Toggle Status", command=self.toggle_timer_status, state=tk.DISABLED, bg="#9E9E9E", fg="white", font=("Helvetica", 10, "bold"))
        self.toggle_button.pack(side="left", padx=5, expand=True, fill="x")

        self.delete_button = tk.Button(manage_button_frame, text="Delete Selected", command=self.delete_timer, state=tk.DISABLED, bg="#F44336", fg="white", font=("Helvetica", 10, "bold"))
        self.delete_button.pack(side="left", padx=5, expand=True, fill="x")

        # Bind an event to the listbox to enable/disable buttons
        self.timers_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

    def on_listbox_select(self, event):
        """
        Enables or disables the management buttons based on listbox selection.
        """
        selected_index = self.timers_listbox.curselection()
        if selected_index:
            self.toggle_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.toggle_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)

    def toggle_timer_status(self):
        """
        Toggles the 'is_active' status of the selected timer.
        """
        selected_index = self.timers_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            current_status = self.timers[index]["is_active"]
            self.timers[index]["is_active"] = not current_status
            
            # Reset the timer state when deactivating
            if not self.timers[index]["is_active"]:
                self.timers[index]["last_notified"] = datetime.now()
            
            self.update_timers_listbox()

    def delete_timer(self):
        """
        Deletes the selected timer from the list.
        """
        selected_index = self.timers_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            del self.timers[index]
            self.update_timers_listbox()
            self.on_listbox_select(None) # Reset button states

    def add_timer(self):
        """
        Adds a new timer based on user input.
        """
        process_name = self.process_name_entry.get().strip()
        interval_str = self.interval_entry.get().strip()
        message = self.message_entry.get().strip()
        
        if not process_name or not interval_str or not message:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            interval_minutes = int(interval_str)
            if interval_minutes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Interval must be a positive integer.")
            return

        # Create a new timer object with 'is_active' status and last_notified time
        new_timer = {
            "process_name": process_name,
            "interval_minutes": interval_minutes,
            "message": message,
            "is_active": True,
            "last_notified": datetime.now() # Start the timer immediately
        }
        self.timers.append(new_timer)
        self.update_timers_listbox()
        
        # Clear input fields
        self.process_name_entry.delete(0, tk.END)
        self.interval_entry.delete(0, tk.END)
        self.message_entry.delete(0, tk.END)

    def save_timers(self):
        """
        Saves the current list of timers to a text file, including active status.
        """
        try:
            with open(TIMERS_FILE_NAME, "w") as f:
                for timer in self.timers:
                    f.write(f"{timer['process_name']},{timer['interval_minutes']},{timer['message']},{timer['is_active']}\n")
            messagebox.showinfo("Success", f"Timers saved to {TIMERS_FILE_NAME}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save timers: {e}")

    def load_timers(self):
        """
        Loads timers from a text file and adds them to the application.
        """
        self.timers = []  # Clear existing timers before loading
        if not os.path.exists(TIMERS_FILE_NAME):
            messagebox.showinfo("Info", "No saved timers found.")
            self.update_timers_listbox()
            return

        try:
            with open(TIMERS_FILE_NAME, "r") as f:
                for line in f:
                    parts = line.strip().split(',', 3)
                    if len(parts) == 4:
                        process_name, interval_str, message, active_str = parts
                        try:
                            interval_minutes = int(interval_str)
                            is_active = active_str.lower() == "true"
                            if interval_minutes > 0:
                                new_timer = {
                                    "process_name": process_name,
                                    "interval_minutes": interval_minutes,
                                    "message": message,
                                    "is_active": is_active,
                                    "last_notified": datetime.now() # Reset timer on load
                                }
                                self.timers.append(new_timer)
                        except ValueError:
                            continue
            self.update_timers_listbox()
            messagebox.showinfo("Success", f"Timers loaded from {TIMERS_FILE_NAME}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timers: {e}")

    def update_timers_listbox(self):
        """
        Updates the listbox with the current active timers and their status.
        """
        # Get the currently selected items before clearing the listbox
        selected_indices = self.timers_listbox.curselection()

        self.timers_listbox.delete(0, tk.END)
        for i, timer in enumerate(self.timers):
            status = "Inactive"
            time_remaining_str = ""
            
            if timer["is_active"]:
                is_running = self.is_process_running(timer['process_name'])
                if is_running:
                    status = "Active"
                    
                    # Calculate time remaining
                    time_elapsed = datetime.now() - timer["last_notified"]
                    interval_in_seconds = timer["interval_minutes"] * 60
                    
                    time_to_next = timedelta(seconds=interval_in_seconds) - time_elapsed
                    
                    # Ensure time remaining is not negative
                    if time_to_next.total_seconds() < 0:
                        time_to_next = timedelta(seconds=0)

                    time_remaining_str = f" - Next: {str(time_to_next).split('.')[0]}" # Format as HH:MM:SS
                else:
                    status = "Monitoring..."

            self.timers_listbox.insert(tk.END, f"{i+1}. {timer['process_name']} - {timer['message']} - {timer['interval_minutes']} min. ({status}){time_remaining_str}")
        
        # Restore the selection after the listbox has been updated
        for i in selected_indices:
            self.timers_listbox.select_set(i)

    def show_notification(self, message):
        """
        Creates and displays a small pop-up notification window and plays a sound.
        """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = screen_width - NOTIFICATION_WIDTH - 20
        y_pos = screen_height - NOTIFICATION_HEIGHT - 20

        notification_window = tk.Toplevel(self)
        notification_window.overrideredirect(True)
        notification_window.geometry(f"{NOTIFICATION_WIDTH}x{NOTIFICATION_HEIGHT}+{x_pos}+{y_pos}")
        notification_window.attributes("-topmost", True)

        notification_frame = tk.Frame(notification_window, bg="#37df12", relief="solid", bd=2)
        notification_frame.pack(fill="both", expand=True)
        
        message_label = tk.Label(notification_frame, text=message, bg="#37fd12", fg="black", wraplength=NOTIFICATION_WIDTH - 20, font=("Helvetica", 20))
        message_label.pack(pady=20, padx=10)

        # Play the sound when the notification pops up
        '''
        try:
            playsound(SOUND_FILE)
        except Exception as e:
            print(f"Error playing sound: {e}")
        '''

        self.after(NOTIFICATION_DURATION_MS, notification_window.destroy)

    def is_process_running(self, process_name):
        """
        Checks if a process with the given name is currently running.
        """
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def check_timers_loop(self):
        """
        Main loop to check all timers and trigger notifications based on elapsed process time.
        """
        for timer in self.timers:
            if timer["is_active"]:
                is_running = self.is_process_running(timer['process_name'])
                
                if is_running:
                    # Calculate time elapsed since last notification
                    elapsed_seconds = (datetime.now() - timer["last_notified"]).total_seconds()
                    
                    # Check if the interval has passed
                    if elapsed_seconds >= timer["interval_minutes"] * 60:
                        self.show_notification(timer["message"])
                        timer["last_notified"] = datetime.now()
                else:
                    # If process is not running, reset the start time and notification tracker
                    timer["last_notified"] = datetime.now()
        
        self.update_timers_listbox()
        self.after(TIMER_CHECK_INTERVAL_MS, self.check_timers_loop)

if __name__ == "__main__":
    app = ProcessMonitorApp()
    app.mainloop()
