import sys
import os
import csv
import random
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QSystemTrayIcon, QMenu, QStyle, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QInputDialog, QMessageBox, QHeaderView
)
from PyQt6.QtCore import QTimer, Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QMouseEvent, QCloseEvent, QShowEvent

# --- File Definitions ---
REMINDERS_FILE = 'reminders.csv'

# --- The "Always-on-Top" Settings Window (CSV-Aware) ---
class SettingsWindow(QWidget):
    # --- New Signal ---
    # This signal will tell the main app that the CSV has changed
    reminders_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remy Settings (Editing reminders.csv)")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.setGeometry(100, 100, 500, 350) # Made it wider
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # --- Use QTableWidget for CSV data ---
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Time", "Reminder"])
        # Stretch the "Reminder" column to fill space
        header = self.table_widget.horizontalHeader()
        if header: # Pylance Fix: Check if header exists
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        main_layout.addWidget(self.table_widget)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_reminder)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_reminder)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_reminder)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def load_reminders(self):
        self.table_widget.setRowCount(0) # Clear the table
        try:
            with open(REMINDERS_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader) # Skip header row
                for row in reader:
                    if not row: continue # Skip empty rows
                    row_position = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_position)
                    self.table_widget.setItem(row_position, 0, QTableWidgetItem(row[0]))
                    self.table_widget.setItem(row_position, 1, QTableWidgetItem(row[1]))
        except Exception as e:
            print(f"Error loading reminders: {e}")

    def save_reminders(self):
        try:
            with open(REMINDERS_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Time", "Reminder"])
                # Write data rows
                for row in range(self.table_widget.rowCount()):
                    time_item = self.table_widget.item(row, 0)
                    reminder_item = self.table_widget.item(row, 1)
                    
                    # Pylance Fix: Check if items exist before reading .text()
                    time_text = time_item.text() if time_item else ""
                    reminder_text = reminder_item.text() if reminder_item else ""
                    writer.writerow([time_text, reminder_text])
            
            # --- Emit the signal ---
            self.reminders_saved.emit() 
            
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def add_reminder(self):
        time_text, ok1 = QInputDialog.getText(self, "Add Reminder", "Enter Time (e.g., 20:00):")
        if not (ok1 and time_text):
            return # User cancelled
            
        reminder_text, ok2 = QInputDialog.getText(self, "Add Reminder", "Enter new reminder:")
        if ok2 and reminder_text:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(time_text))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(reminder_text))
            self.save_reminders()

    def edit_reminder(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "No reminder selected.")
            return
        
        # Get existing values
        old_time_item = self.table_widget.item(current_row, 0)
        old_reminder_item = self.table_widget.item(current_row, 1)

        # Pylance Fix: Check if items exist
        old_time = old_time_item.text() if old_time_item else ""
        old_reminder = old_reminder_item.text() if old_reminder_item else ""
            
        time_text, ok1 = QInputDialog.getText(self, "Edit Time", "Edit time:", text=old_time)
        if not ok1: return
        
        reminder_text, ok2 = QInputDialog.getText(self, "Edit Reminder", "Edit reminder:", text=old_reminder)
        if ok2:
            # Pylance Fix: Check if items exist before setting text
            if old_time_item:
                old_time_item.setText(time_text)
            if old_reminder_item:
                old_reminder_item.setText(reminder_text)
            self.save_reminders()

    def delete_reminder(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "No reminder selected.")
            return
            
        reply = QMessageBox.question(self, "Delete Reminder", "Are you sure you want to delete this reminder?", 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # Pylance Fix: .question() is a standard method, .confirm is not.
        
        if reply == QMessageBox.StandardButton.Yes: # Pylance Fix: Compare against the enum
            self.table_widget.removeRow(current_row)
            self.save_reminders()

    def showEvent(self, a0: QShowEvent | None): # Pylance Fix: Rename 'event' to 'a0' and add type
        # Refresh the list every time the window is shown
        self.load_reminders()
        if a0:
            a0.accept()

    def closeEvent(self, a0: QCloseEvent | None): # Pylance Fix: Rename 'event' to 'a0' and add type
        # Don't close, just hide
        self.hide()
        if a0:
            a0.ignore()

# --- The Main Pop-up Window ---
class ReminderPopup(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- Window Styling ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setStyleSheet("""
            QWidget {
                background-color: #2D3748; /* Dark blue-gray */
                color: white;
                border-radius: 10px;
                border: 2px solid #4A5568;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                border: none;
                padding: 20px;
                qproperty-alignment: 'AlignCenter | AlignVCenter';
                qproperty-wordWrap: true;
            }
            QPushButton {
                background-color: #4A5568;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #718096;
            }
            #done_button {
                background-color: #38A169; /* Green */
            }
            #done_button:hover {
                background-color: #48BB78;
            }
            #doing_button {
                background-color: #DD6B20; /* Orange */
            }
            #doing_button:hover {
                background-color: #ED8936;
            }
        """)
        
        self.initUI()
        
        self._drag_pos: QPoint | None = None # Pylance Fix: Initialize drag_pos to None

    def initUI(self):
        self._layout = QVBoxLayout()
        
        self.label = QLabel("Hey Nymo! Time to build Remy!", self)
        
        self.doing_button = QPushButton("Doing (Snooze)", self)
        self.doing_button.setObjectName("doing_button")
        self.doing_button.clicked.connect(self.snooze)
        
        self.done_button = QPushButton("Done (For now...)", self)
        self.done_button.setObjectName("done_button")
        self.done_button.clicked.connect(self.hide)
        
        self._layout.addWidget(self.label)
        self._layout.addWidget(self.doing_button)
        self._layout.addWidget(self.done_button)
        self.setLayout(self._layout)
        
        self.setFixedSize(350, 220) # Made it a bit taller for wrapped text

    def snooze(self):
        print("Snoozing... (Hiding window)")
        self.hide()

    def center(self):
        screen = self.screen()
        if screen:
            screen_geo = screen.geometry()
            self.move(
                (screen_geo.width() - self.width()) // 2,
                (screen_geo.height() - self.height()) // 2
            )
        else:
            pass 

    def mousePressEvent(self, a0: QMouseEvent | None):
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = a0.globalPosition().toPoint() - self.frameGeometry().topLeft()
            a0.accept()

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if a0 and a0.buttons() == Qt.MouseButton.LeftButton:
            # Pylance Fix: Check if _drag_pos is not None
            if self._drag_pos is not None:
                self.move(a0.globalPosition().toPoint() - self._drag_pos)
                a0.accept()

# --- Main Application Logic ---
class RemyReminder:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False) 
        
        self.check_or_create_csv()

        self.popup = ReminderPopup()
        self.settings_window = SettingsWindow() # Create the settings window
        # --- Connect the new signal ---
        self.settings_window.reminders_saved.connect(self.load_and_schedule_reminders)

        self.tray_icon = QSystemTrayIcon()
        
        style = self.app.style()
        info_icon = QIcon()
        if style:
            info_icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        
        self.tray_icon.setIcon(info_icon)
        self.tray_icon.setToolTip("Remy Reminder\nClick to show")
        
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show Reminder Now")
        if show_action:
            # Pass a default (non-scheduled) call
            show_action.triggered.connect(lambda: self.show_popup(self.get_random_reminder(), is_scheduled=False)) 
            
        # --- New Settings Action ---
        settings_action = tray_menu.addAction("Settings")
        if settings_action:
            # We just show the window. It loads its own data.
            settings_action.triggered.connect(self.settings_window.show) 
        
        tray_menu.addSeparator()
        
        exit_action = tray_menu.addAction("Exit")
        if exit_action:
            exit_action.triggered.connect(self.exit_app)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.timer = QTimer(self.app) # Give timer a parent
        self.scheduled_reminders = [] # To store CSV data
        
        # --- New scheduler logic ---
        self.load_and_schedule_reminders()

    def check_or_create_csv(self):
        # Create a default CSV if one doesn't exist
        if not os.path.exists(REMINDERS_FILE):
            print("No 'reminders.csv' found. Creating one with default data.")
            default_data = [
                ["Time", "Reminder"],
                ["10:00", "Hey Nymo! Time to build Remy!"],
                ["12:00", "Stop scrolling and start coding."],
                ["14:00", "Is that Android Studio open yet?"],
                ["16:00", "6 months won't wait for you. Build Remyble!"],
                ["18:00", "Check the project plan. What's next?"]
            ]
            try:
                with open(REMINDERS_FILE, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(default_data)
            except Exception as e:
                print(f"Error creating default CSV: {e}")

    # --- New method to get a random reminder ---
    def get_random_reminder(self) -> str:
        """Reads the CSV and returns a single random reminder string."""
        reminders = []
        try:
            with open(REMINDERS_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader) # Skip header
                reminders = list(reader) # Read all rows into a list
        except Exception as e:
            print(f"Error loading reminders for random choice: {e}")
            return "Error loading reminders."

        if reminders:
            # random.choice picks a random row, [1] gets the 2nd column (Reminder text)
            return random.choice(reminders)[1]
        
        return "No reminders found!\nAdd some in Settings."

    # --- New method to load CSV and start the schedule ---
    def load_and_schedule_reminders(self):
        """Loads reminders from CSV and schedules the next one."""
        print("Loading reminders and calculating next schedule...")
        self.scheduled_reminders = [] # Clear old schedule
        try:
            with open(REMINDERS_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader) # Skip header
                self.scheduled_reminders = list(reader) # Read all rows into a list
        except Exception as e:
            print(f"Error loading reminders for scheduling: {e}")

        self.schedule_next_reminder()

    # --- New core scheduling logic ---
    def schedule_next_reminder(self):
        """Calculates and sets a singleShot timer for the next upcoming reminder."""
        self.timer.stop() # Stop any existing timer
        
        if not self.scheduled_reminders:
            print("No reminders to schedule.")
            return

        now = datetime.datetime.now()
        upcoming_times = []

        for time_str, reminder_str in self.scheduled_reminders:
            try:
                # Parse time string like "10:00"
                parsed_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                
                # Create a datetime object for today at that time
                target_time = now.replace(
                    hour=parsed_time.hour, 
                    minute=parsed_time.minute, 
                    second=0, 
                    microsecond=0
                )
                
                # If that time has already passed today...
                if target_time <= now:
                    # ...schedule it for tomorrow
                    target_time += datetime.timedelta(days=1)
                
                upcoming_times.append((target_time, reminder_str))
                
            except ValueError:
                print(f"Skipping malformed time: {time_str}")

        if not upcoming_times:
            # --- FALLBACK LOGIC ---
            # This is the fix for the "bubble not showing"
            print("No valid upcoming reminders found. Reverting to 2-hour random timer.")
            self.timer.setSingleShot(False) # Make it repeating
            
            # Disconnect any old lambda functions
            try: self.timer.timeout.disconnect() 
            except TypeError: pass # No connection to disconnect
            
            self.timer.timeout.connect(lambda: self.show_popup(self.get_random_reminder(), is_scheduled=False)) 
            self.timer.start(2 * 60 * 60 * 1000) # 2 hours
            return
            # --- END FALLBACK ---

        # Sort to find the soonest
        upcoming_times.sort()
        
        next_time, next_reminder = upcoming_times[0]
        
        # Calculate milliseconds until the next event
        ms_until = (next_time - now).total_seconds() * 1000
        
        if ms_until < 0: ms_until = 0 # Failsafe

        print(f"Next reminder set for: {next_time} ({next_reminder[:20]}...)")
        
        # Set the timer
        self.timer.setSingleShot(True)
        # Disconnect any old lambda functions to avoid duplicates
        try: self.timer.timeout.disconnect() 
        except TypeError: pass # No connection to disconnect
        
        self.timer.timeout.connect(lambda: self.show_popup(next_reminder, is_scheduled=True))
        self.timer.start(int(ms_until))

    # --- Updated show_popup ---
    def show_popup(self, reminder_text: str, is_scheduled: bool = False):
        print(f"Timer fired! Showing pop-up. (Scheduled: {is_scheduled})")
        
        if not reminder_text:
            reminder_text = "No reminders found!\nAdd some in Settings."
        
        self.popup.label.setText(reminder_text)
        
        self.popup.center()
        self.popup.show()
        self.popup.activateWindow()

        # --- CRITICAL: Re-schedule after a scheduled event ---
        if is_scheduled:
            # This sets the timer for the *next* day's event
            self.schedule_next_reminder()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger: # Left-click
            # Show a random reminder, not a scheduled one
            self.show_popup(self.get_random_reminder(), is_scheduled=False)

    def exit_app(self):
        print("Exiting Remy Reminder...")
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())

# --- Run the App ---
if __name__ == "__main__":
    reminder = RemyReminder()
    reminder.run()