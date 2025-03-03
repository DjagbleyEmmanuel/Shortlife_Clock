import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QGridLayout,
    QMessageBox, QCheckBox, QTextEdit, QProgressBar, QDateEdit, QFileDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QInputDialog, QToolTip
)
from PyQt5.QtCore import QTimer, QDate, Qt, QSettings
from PyQt5.QtGui import QIntValidator, QIcon
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import choice
import csv

# Sample life expectancy data
life_expectancy_data = {
    "World": {"Male": 70, "Female": 75},
    "Africa": {"Male": 64, "Female": 67},
    "Asia": {"Male": 72, "Female": 75},
    "Europe": {"Male": 78, "Female": 83},
    "North America": {"Male": 76, "Female": 81},
    "South America": {"Male": 72, "Female": 79},
    "Australia": {"Male": 81, "Female": 85},
}

# Default health tips and motivational quotes
default_health_tips = [
    "Drink plenty of water every day.",
    "Exercise regularly to maintain a healthy body.",
    "Eat a balanced diet rich in fruits and vegetables.",
    "Get enough sleep to allow your body to recover.",
    "Avoid smoking and excessive alcohol consumption."
]

default_motivational_quotes = [
    "The best time to plant a tree was 20 years ago. The second best time is now.",
    "Your time is limited, don't waste it living someone else's life.",
    "The purpose of life is not to be happy. It is to be useful, to be honorable, to be compassionate, to have it make some difference that you have lived and lived well.",
    "Not how long, but how well you have lived is the main thing."
]

class ManageTipsDialog(QDialog):
    def __init__(self, tips, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.tips = tips
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.tips)
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_tip)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_tip)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_tip(self):
        tip, ok = QInputDialog.getText(self, "Add Tip", "Enter a new tip:")
        if ok and tip:
            self.list_widget.addItem(tip)
            self.tips.append(tip)

    def remove_tip(self):
        selected = self.list_widget.currentRow()
        if selected >= 0:
            self.list_widget.takeItem(selected)
            self.tips.pop(selected)

class ShortlifeClock(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.manual_age = False
        self.settings = QSettings("ShortlifeClock", "Settings")
        self.health_tips = self.settings.value("health_tips", default_health_tips)
        self.motivational_quotes = self.settings.value("motivational_quotes", default_motivational_quotes)
        self.initUI()
        self.load_settings()

    def initUI(self):
        # Create layout
        layout = QGridLayout()

        # Labels and Inputs
        self.age_label = QLabel('Age:')
        self.age_input = QLineEdit()
        self.age_input.setValidator(QIntValidator(0, 150, self))
        self.age_input.setEnabled(False)

        self.birthdate_label = QLabel('Birthdate:')
        self.birthdate_input = QDateEdit()
        self.birthdate_input.setCalendarPopup(True)
        self.birthdate_input.setDate(QDate.currentDate())

        self.age_option_checkbox = QCheckBox('Enter age manually')
        self.age_option_checkbox.stateChanged.connect(self.toggle_age_input)

        self.gender_label = QLabel('Gender:')
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female"])

        self.continent_label = QLabel('Continent:')
        self.continent_input = QComboBox()
        self.continent_input.addItems(["World", "Africa", "Asia", "Europe", "North America", "South America", "Australia"])

        self.health_tips_checkbox = QCheckBox('Show daily health tips')
        self.health_tips_checkbox.stateChanged.connect(self.toggle_health_tips)

        self.show_percentage_checkbox = QCheckBox('Show remaining days as percentage')
        self.show_percentage_checkbox.stateChanged.connect(self.update_remaining_display)

        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.calculate_life_percentage)

        self.dark_mode_button = QPushButton('Toggle Dark/Light Mode')
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.dark_mode_button.setIcon(QIcon("dark_mode_icon.png"))  # Add an icon

        self.manage_health_tips_button = QPushButton('Manage Health Tips')
        self.manage_health_tips_button.clicked.connect(self.manage_health_tips)

        self.manage_quotes_button = QPushButton('Manage Motivational Quotes')
        self.manage_quotes_button.clicked.connect(self.manage_motivational_quotes)

        self.export_button = QPushButton('Export Data')
        self.export_button.clicked.connect(self.export_data)

        self.result_label = QLabel('Life Percentage Used: ')
        self.days_lived_label = QLabel('Days Lived: ')
        self.remaining_days_label = QLabel('Remaining Days: ')
        self.health_tips_label = QLabel('Health Tips:')
        self.health_tips_text = QTextEdit()
        self.health_tips_text.setReadOnly(True)

        self.progress_bar = QProgressBar()

        self.quote_label = QLabel('Motivational Quote:')
        self.quote_text = QTextEdit()
        self.quote_text.setReadOnly(True)

        self.countdown_label = QLabel('Time Remaining:')
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 0

        # Add widgets to layout
        layout.addWidget(self.age_label, 0, 0)
        layout.addWidget(self.age_input, 0, 1)
        layout.addWidget(self.birthdate_label, 1, 0)
        layout.addWidget(self.birthdate_input, 1, 1)
        layout.addWidget(self.age_option_checkbox, 2, 0, 1, 2)
        layout.addWidget(self.gender_label, 3, 0)
        layout.addWidget(self.gender_input, 3, 1)
        layout.addWidget(self.continent_label, 4, 0)
        layout.addWidget(self.continent_input, 4, 1)
        layout.addWidget(self.health_tips_checkbox, 5, 0, 1, 2)
        layout.addWidget(self.show_percentage_checkbox, 6, 0, 1, 2)
        layout.addWidget(self.calculate_button, 7, 0, 1, 2)
        layout.addWidget(self.dark_mode_button, 8, 0, 1, 2)
        layout.addWidget(self.manage_health_tips_button, 9, 0, 1, 2)
        layout.addWidget(self.manage_quotes_button, 10, 0, 1, 2)
        layout.addWidget(self.export_button, 11, 0, 1, 2)
        layout.addWidget(self.result_label, 12, 0, 1, 2)
        layout.addWidget(self.days_lived_label, 13, 0, 1, 2)
        layout.addWidget(self.remaining_days_label, 14, 0, 1, 2)
        layout.addWidget(self.progress_bar, 15, 0, 1, 2)
        layout.addWidget(self.quote_label, 16, 0, 1, 2)
        layout.addWidget(self.quote_text, 17, 0, 1, 2)
        layout.addWidget(self.health_tips_label, 18, 0, 1, 2)
        layout.addWidget(self.health_tips_text, 19, 0, 1, 2)
        layout.addWidget(self.countdown_label, 20, 0, 1, 2)

        self.setLayout(layout)
        self.setWindowTitle('Shortlife Clock')

        # Timer for daily health tips
        self.health_tips_timer = QTimer(self)
        self.health_tips_timer.timeout.connect(self.show_health_tip)

        # Tooltips
        self.age_input.setToolTip("Enter your age manually or use the birthdate field.")
        self.birthdate_input.setToolTip("Select your birthdate to calculate your age.")
        self.dark_mode_button.setToolTip("Toggle between dark and light mode.")

    def toggle_age_input(self, state):
        if state == Qt.Checked:
            self.age_input.setEnabled(True)
            self.birthdate_input.setEnabled(False)
            self.manual_age = True
        else:
            self.age_input.setEnabled(False)
            self.birthdate_input.setEnabled(True)
            self.manual_age = False

    def calculate_life_percentage(self):
        try:
            if self.manual_age:
                age = int(self.age_input.text())
            else:
                birthdate = self.birthdate_input.date().toPyDate()
                today = datetime.today().date()
                if birthdate > today:
                    raise ValueError("Birthdate cannot be in the future.")
                age = relativedelta(today, birthdate).years

            gender = self.gender_input.currentText()
            continent = self.continent_input.currentText()

            if age < 0:
                raise ValueError("Age cannot be negative")

            life_expectancy = life_expectancy_data[continent][gender]
            if age > life_expectancy:
                QMessageBox.warning(self, "Input Error", "Age exceeds life expectancy for the selected region and gender.")
                return

            life_percentage_used = (age / life_expectancy) * 100

            self.result_label.setText(f'Life Percentage Used: {life_percentage_used:.2f}%')

            # Calculate days lived and remaining days
            days_lived = age * 365
            remaining_days = (life_expectancy * 365) - days_lived
            self.days_lived_label.setText(f'Days Lived: {days_lived}')
            self.remaining_days_label.setText(f'Remaining Days: {remaining_days}')

            # Update progress bar
            self.progress_bar.setValue(min(int(life_percentage_used), 100))

            # Show motivational quote
            self.show_motivational_quote()

            # Start countdown
            self.countdown_timer.stop()
            self.remaining_seconds = remaining_days * 24 * 3600  # Convert days to seconds
            self.countdown_timer.start(1000)  # Update every second
            self.update_countdown()

            # Update display for remaining days as percentage if checkbox is checked
            self.update_remaining_display()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def update_remaining_display(self):
        if self.show_percentage_checkbox.isChecked():
            gender = self.gender_input.currentText()
            continent = self.continent_input.currentText()
            life_expectancy = life_expectancy_data[continent][gender]
            remaining_days = (self.remaining_seconds // 3600) // 24
            remaining_percentage = (remaining_days / (life_expectancy * 365)) * 100
            self.remaining_days_label.setText(f'Remaining Life: {remaining_percentage:.2f}%')
        else:
            remaining_days = (self.remaining_seconds // 3600) // 24
            self.remaining_days_label.setText(f'Remaining Days: {remaining_days}')

    def show_health_tip(self):
        tip = choice(self.health_tips)
        self.health_tips_text.setText(tip)

    def toggle_health_tips(self, state):
        if state == Qt.Checked:
            self.show_health_tip()
            self.health_tips_timer.start(86400000)  # Update daily
        else:
            self.health_tips_text.clear()
            self.health_tips_timer.stop()

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet("")
            self.dark_mode = False
        else:
            self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
            self.dark_mode = True
        self.save_settings()

    def show_motivational_quote(self):
        quote = choice(self.motivational_quotes)
        self.quote_text.setText(quote)

    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            days = self.remaining_seconds // (24 * 3600)
            hours = (self.remaining_seconds % (24 * 3600)) // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60
            self.countdown_label.setText(f'Time Remaining: {days}d {hours}h {minutes}m {seconds}s')
        else:
            self.countdown_timer.stop()
            self.countdown_label.setText('Time Remaining: Expired')

    def export_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Life Percentage Used", "Days Lived", "Remaining Days"])
                writer.writerow([
                    self.result_label.text().split(": ")[1],
                    self.days_lived_label.text().split(": ")[1],
                    self.remaining_days_label.text().split(": ")[1]
                ])

    def manage_health_tips(self):
        dialog = ManageTipsDialog(self.health_tips, "Manage Health Tips", self)
        if dialog.exec_() == QDialog.Accepted:
            self.health_tips = dialog.tips
            self.settings.setValue("health_tips", self.health_tips)

    def manage_motivational_quotes(self):
        dialog = ManageTipsDialog(self.motivational_quotes, "Manage Motivational Quotes", self)
        if dialog.exec_() == QDialog.Accepted:
            self.motivational_quotes = dialog.tips
            self.settings.setValue("motivational_quotes", self.motivational_quotes)

    def load_settings(self):
        self.dark_mode = self.settings.value("dark_mode", False, bool)
        if self.dark_mode:
            self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")

    def save_settings(self):
        self.settings.setValue("dark_mode", self.dark_mode)
        self.settings.setValue("health_tips", self.health_tips)
        self.settings.setValue("motivational_quotes", self.motivational_quotes)

def main():
    app = QApplication(sys.argv)
    clock = ShortlifeClock()
    clock.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
