from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QWidget, QProgressBar, QRadioButton, QGroupBox, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
import sys
import itertools
import string


class CrackingThread(QThread):
    # Custom signal to update progress
    progress_update = Signal(int, str)
    finished = Signal()

    def __init__(self, method, password):
        super().__init__()
        self.method = method
        self.password = password
        self._running = True

    def run(self):
        if self.method == 'brute_force':
            self.brute_force_attack(self.password)
        elif self.method == 'dictionary':
            self.dictionary_attack(self.password)

    def brute_force_attack(self, password):
        charset = string.ascii_letters + string.digits + string.punctuation
        max_length = 6  # Set maximum length for brute force to avoid excessive time
        total_attempts = sum(len(charset) ** i for i in range(1, max_length + 1))

        attempt = 0
        for length in range(1, max_length + 1):
            for guess in itertools.product(charset, repeat=length):
                if not self._running:
                    self.progress_update.emit(0, "Cancelled")
                    self.finished.emit()
                    return

                guess_password = ''.join(guess)
                attempt += 1
                progress = int((attempt / total_attempts) * 100)
                self.progress_update.emit(progress, guess_password)
                if guess_password == password:
                    self.progress_update.emit(100, f"Password found: {guess_password}")
                    self.finished.emit()
                    return

        self.progress_update.emit(100, "Password not found within limit.")
        self.finished.emit()

    def dictionary_attack(self, password):
        try:
            with open('common_passwords.txt', 'r') as file:
                lines = file.readlines()
                total_lines = len(lines)
                for i, line in enumerate(lines):
                    if not self._running:
                        self.progress_update.emit(0, "Cancelled")
                        self.finished.emit()
                        return

                    guess_password = line.strip()
                    progress = int((i / total_lines) * 100)
                    self.progress_update.emit(progress, guess_password)
                    if guess_password == password:
                        self.progress_update.emit(100, f"Password found: {guess_password}")
                        self.finished.emit()
                        return
            self.progress_update.emit(100, "Password not found in dictionary.")
            self.finished.emit()
        except FileNotFoundError:
            self.progress_update.emit(100, "Dictionary file not found.")
            self.finished.emit()

    def stop(self):
        self._running = False


class PasswordCrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Cracking Tool")
        self.setGeometry(100, 100, 600, 400)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        attack_method_layout = QHBoxLayout()

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter the password to crack")

        self.start_button = QPushButton("Start Cracking")
        self.start_button.clicked.connect(self.start_cracking)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_cracking)
        self.cancel_button.setEnabled(False)

        self.brute_force_radio = QRadioButton("Brute Force")
        self.dictionary_radio = QRadioButton("Dictionary Attack")
        self.brute_force_radio.setChecked(True)

        attack_method_layout.addWidget(self.brute_force_radio)
        attack_method_layout.addWidget(self.dictionary_radio)

        self.result_label = QLabel("Results will be displayed here")
        self.progress_bar = QProgressBar()

        main_layout.addWidget(QLabel("Password Cracking Tool", alignment=Qt.AlignCenter))
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(QGroupBox("Select Attack Method", layout=attack_method_layout))
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_label)

        central_widget.setLayout(main_layout)

    def start_cracking(self):
        password = self.password_input.text()
        if not password:
            self.result_label.setText("Please enter a password to crack.")
            return

        method = 'brute_force' if self.brute_force_radio.isChecked() else 'dictionary'

        # Disable the start button and enable the cancel button
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Create and start the cracking thread
        self.cracking_thread = CrackingThread(method, password)
        self.cracking_thread.progress_update.connect(self.update_progress)
        self.cracking_thread.finished.connect(self.cracking_finished)
        self.cracking_thread.start()

    def cancel_cracking(self):
        if hasattr(self, 'cracking_thread'):
            self.cracking_thread.stop()

    def update_progress(self, progress, current_guess):
        self.progress_bar.setValue(progress)
        self.result_label.setText(f"Trying: {current_guess}")

    def cracking_finished(self):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.information(self, "Finished", "Password cracking process completed.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordCrackerApp()
    window.show()
    sys.exit(app.exec())
