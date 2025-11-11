from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QDialog, QTextEdit, QHBoxLayout, QMessageBox
import os, shutil


class AdvancedSettingsWidget(QDialog):
    def __init__(self,settings_file, custom_file, parent=None, title="Copasi"):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        layout = QVBoxLayout(self)
        
        # QTextEdit for displaying file content
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_text)
        

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_text)
       
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.reset_button, 1)
        button_layout.addWidget(self.cancel_button, 4.5)
        button_layout.addWidget(self.save_button, 4.5)
        
        layout.addLayout(button_layout)

        #* setupt initial file_content
        self.settings_file = settings_file
        self.moded_file_path = custom_file
        self.read_file()
        
    def read_file(self):
        if not os.path.exists(self.moded_file_path):
            shutil.copyfile(self.settings_file, self.moded_file_path)
        # path =  self.moded_file_path if os.path.exists(self.moded_file_path) else self.settings_file

        with open(self.moded_file_path, 'r') as settings_f:
            file_content = settings_f.read()
            self.set_text(file_content)
        
    def set_text(self, text):
        self.text_edit.setPlainText(text)
        
    def save_text(self, text=None):
        new_content = text if text else self.text_edit.toPlainText()
    
        # Save the new content to the file
        with open(self.moded_file_path, 'w') as file:
            file.write(new_content)

        self.set_text(new_content)
            
    def reset_text(self):
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to reset the file?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Delete the file if "Yes" is selected
            try:
                os.remove(self.moded_file_path)
                self.read_file()
                # QMessageBox.information(self, "Reset", "File 'test.txt' deleted.")
            except FileNotFoundError:
                QMessageBox.information(self, "Reset", "File 'test.txt' does not exist.")

    def get_settings_string(self):
        path =  self.moded_file_path if os.path.exists(self.moded_file_path) else self.settings_file

        with open(path, 'r') as settings_f:
            file_content = settings_f.read()
            return file_content


if __name__ == "__main__":
    
    def show_advanced_copasi_dialog():
        filename = "test.txt"
        dialog = AdvancedSettingsWidget(settings_file=filename, custom_file="user_text.txt")
        
        dialog.exec()


    app = QApplication([])
    advanced_copasi_b = QPushButton("!")
    advanced_copasi_b.setFixedSize(100, 100)  # Adjust the size as needed
    advanced_copasi_b.clicked.connect(show_advanced_copasi_dialog)
    advanced_copasi_b.show()
    app.exec()
