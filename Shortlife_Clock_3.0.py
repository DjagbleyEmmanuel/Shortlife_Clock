# FILE: /shortlife-clock/shortlife-clock/src/Shortlife_Clock_3.0.py

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QComboBox, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QMessageBox, QCheckBox, QTextEdit, QProgressBar, QDateEdit)
from PyQt5.QtCore import QTimer, QDate, Qt
from datetime import datetime

# Sample life expectancy data and health tips
life_expectancy_data = {
    "World": {"Male": 70, "Female": 75},
    "Africa": {"Male": 64, "Female": 67},
    "Asia": {"Male": 72, "Female": 75},
    "Europe": {"Male": 78, "Female": 83},
    "North America": {"Male": 76, "Female": 81},
    "South America": {"Male": 72, "Female": 79},
    "Australia": {"Male": 81, "Female": 85},
}

health_tips = [
    "Drink plenty of water every day.",
    "Exercise regularly to maintain a healthy body.",
    "Eat a balanced diet rich in fruits and vegetables.",
    "Get enough sleep to allow your body to recover.",
    "Avoid smoking and excessive alcohol consumption."
]

motivational_quotes = [
    "The best time to plant a tree was 20 years ago. The second best time is now.",
    "Your time is limited, don't waste it living someone else's life.",
    "The purpose of life is not to be happy. It is to be useful, to be honorable, to be compassionate, to have it make some difference that you have lived and lived well.",
    "Not how long, but how well you have lived is the main thing."
]

class ShortlifeClock(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.manual_age = False
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        self.age_label = QLabel('Age:')
        self.age_input = QLineEdit()
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
        layout.addWidget(self.result_label, 9, 0, 1, 2)
        layout.addWidget(self.days_lived_label, 10, 0, 1, 2)
        layout.addWidget(self.remaining_days_label, 11, 0, 1, 2)
        layout.addWidget(self.progress_bar, 12, 0, 1, 2)
        layout.addWidget(self.quote_label, 13, 0, 1, 2)
        layout.addWidget(self.quote_text, 14, 0, 1, 2)
        layout.addWidget(self.health_tips_label, 15, 0, 1, 2)
        layout.addWidget(self.health_tips_text, 16, 0, 1, 2)
        layout.addWidget(self.countdown_label, 17, 0, 1, 2)

        self.setLayout(layout)
        self.setWindowTitle('Shortlife Clock')

        self.health_tips_timer = QTimer(self)
        self.health_tips_timer.timeout.connect(self.show_health_tip)

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
                age = (today - birthdate).days // 365

            gender = self.gender_input.currentText()
            continent = self.continent_input.currentText()

            if age < 0:
                raise ValueError("Age cannot be negative")

            life_expectancy = life_expectancy_data[continent][gender]
            life_percentage_used = (age / life_expectancy) * 100

            self.result_label.setText(f'Life Percentage Used: {life_percentage_used:.2f}%')

            days_lived = age * 365
            remaining_days = (life_expectancy * 365) - days_lived
            self.days_lived_label.setText(f'Days Lived: {days_lived}')
            self.remaining_days_label.setText(f'Remaining Days: {remaining_days}')

            self.progress_bar.setValue(int(life_percentage_used))

            self.show_motivational_quote()

            self.remaining_seconds = remaining_days * 24 * 3600
            self.countdown_timer.start(1000)
            self.update_countdown()

            self.update_remaining_display()

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid age.")

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
        from random import choice
        tip = choice(health_tips)
        self.health_tips_text.setText(tip)

    def toggle_health_tips(self, state):
        if state == Qt.Checked:
            self.show_health_tip()
            self.health_tips_timer.start(86400000)
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

    def show_motivational_quote(self):
        from random import choice
        quote = choice(motivational_quotes)
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

def main():
    app = QApplication(sys.argv)
    clock = ShortlifeClock()
    clock.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()