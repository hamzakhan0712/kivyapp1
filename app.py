import os
import cv2
import face_recognition
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.camera import Camera

class AttendanceApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Welcome to the Attendance App", font_size='24sp')
        self.login_button = Button(text="Login", font_size='24sp')
        self.login_button.bind(on_press=self.show_login_popup)
        self.student_button = Button(text="Add Student", font_size='24sp')
        self.student_button.bind(on_press=lambda instance: self.show_student_popup())

        self.start_attendance_button = Button(text="Start Attendance", font_size='24sp')
        self.start_attendance_button.bind(on_press=self.take_attendance)  # Bind to the take_attendance method

        self.admin_username = "admin"  # Set the admin username
        self.admin_password = "password"  # Set the admin password

        self.faculty_credentials = {}

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.login_button)
        self.layout.add_widget(self.student_button)
        self.layout.add_widget(self.start_attendance_button)  # Add the Start Attendance button

        
        # Initialize the SQLite database
        self.conn = sqlite3.connect("attendance.db")
        self.cursor = self.conn.cursor()
        self.create_students_table()

        return self.layout
    

    def create_students_table(self):
        # Create a table to store student data if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                year TEXT,
                division TEXT,
                photo_path TEXT,
                present BOOLEAN DEFAULT 0
            )
        ''')
        self.conn.commit()


    def show_login_popup(self, instance):
        login_popup = Popup(title='Login', size_hint=(None, None), size=(300, 200))
        layout = BoxLayout(orientation='vertical')
        
        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.password_input = TextInput(hint_text='Password', multiline=False, password=True)
        login_button = Button(text='Login')
        login_button.bind(on_press=self.check_login)
        
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        
        login_popup.content = layout
        login_popup.open()
    
    def check_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username == self.admin_username and password == self.admin_password:
            self.layout.clear_widgets()
            self.layout.add_widget(Label(text="Logged in as admin."))
        elif username in self.faculty_credentials and self.faculty_credentials[username] == password:
            self.layout.clear_widgets()
            self.layout.add_widget(Label(f"Logged in as {username}."))
            self.show_student_popup()  # Allow faculty to add students
        else:
            self.show_error_popup()

    def show_error_popup(self):
        error_popup = Popup(title='Login Error', content=Label(text='Invalid credentials'), size_hint=(None, None), size=(300, 150))
        error_popup.open()

    def show_student_popup(self):
        self.student_popup = Popup(title='Add Student', size_hint=(None, None), size=(400, 300))
        layout = BoxLayout(orientation='vertical')
        
        self.name_input = TextInput(hint_text='Name', multiline=False)
        self.id_input = TextInput(hint_text='ID', multiline=False)
        self.year_input = TextInput(hint_text='Year', multiline=False)
        self.division_input = TextInput(hint_text='Division', multiline=False)
        self.camera = Camera(resolution=(640, 480), play=True)
        capture_button = Button(text='Capture')
        capture_button.bind(on_press=self.capture_student_photo)
        add_button = Button(text='Add Student')
        add_button.bind(on_press=self.add_student)
        
        layout.add_widget(self.name_input)
        layout.add_widget(self.id_input)
        layout.add_widget(self.year_input)
        layout.add_widget(self.division_input)
        layout.add_widget(self.camera)
        layout.add_widget(capture_button)
        layout.add_widget(add_button)
        
        self.student_popup.content = layout
        self.student_popup.open()

    def capture_student_photo(self, instance):
        # Check if the student ID input is not empty
        if not self.id_input.text:
            self.show_error_popup("Student ID is required")
            return

        # Increase the resolution for capturing images
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, 1280)  # Set width
        video_capture.set(4, 720)   # Set height

        # Capture a photo and save it to a file
        if self.camera.texture:
            photo_path = 'student_photos'  # Change to your desired folder
            os.makedirs(photo_path, exist_ok=True)
            photo_file = os.path.join(photo_path, f"{self.id_input.text}.jpg")

            # Export the camera frame to a photo file
            try:
                ret, frame = video_capture.read()
                cv2.imwrite(photo_file, frame)
                self.show_info_popup("Photo Captured", f"Photo saved as: {photo_file}")
            except Exception as e:
                self.show_error_popup("Error capturing photo", str(e))

            video_capture.release()  # Release the camera
            self.camera.texture = None  # Reset the camera feed

            # Clear the input fields after capturing
            self.id_input.text = ""
        else:
            self.show_error_popup("Camera feed not available")




    def show_info_popup(self, title, message):
        info_popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        info_popup.open()

    def show_error_popup(self, title, message):
        error_popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        error_popup.open()


    def add_student(self, instance):
        name = self.name_input.text
        student_id = self.id_input.text
        year = self.year_input.text
        division = self.division_input.text

        # Capture a photo and save it to a file
        if self.camera.texture:
            photo_path = 'student_photos'  # Change to your desired folder
            os.makedirs(photo_path, exist_ok=True)
            photo_file = os.path.join(photo_path, f"{student_id}.jpg")

            # Export the camera frame to a photo file
            try:
                video_capture = cv2.VideoCapture(0)
                video_capture.set(3, 1280)  # Set width
                video_capture.set(4, 720)   # Set height
                ret, frame = video_capture.read()
                cv2.imwrite(photo_file, frame)
                video_capture.release()  # Release the camera

                self.show_info_popup("Photo Captured", f"Photo saved as: {photo_file}")
            except Exception as e:
                self.show_error_popup("Error capturing photo", str(e))

        else:
            self.show_error_popup("Camera feed not available")
            return

        # Insert student data into the database
        self.cursor.execute("INSERT INTO students (name, student_id, year, division, photo_path, present) VALUES (?, ?, ?, ?, ?, ?)",
                            (name, student_id, year, division, photo_file, False))
        self.conn.commit()

        self.name_input.text = ''
        self.id_input.text = ''
        self.year_input.text = ''
        self.division_input.text = ''




    def take_attendance(self, instance):
        dataset_path = "student_photos"  # Change to your student photos folder
        attendance_file = "attendance.txt"

        known_face_encodings = []
        known_face_names = []

        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    name = os.path.splitext(file)[0]
                    image_path = os.path.join(root, file)
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)

                    if encodings:
                        encoding = encodings[0]
                        known_face_encodings.append(encoding)
                        known_face_names.append(name)

        # Increase the resolution for capturing images
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, 1280)  # Set width
        video_capture.set(4, 720)   # Set height

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color_green = (0, 255, 0)
        font_color_red = (0, 0, 255)
        line_type = 2

        while True:
            ret, frame = video_capture.read()

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(
                small_frame, face_locations)

            present_students = set()

            for i, face_encoding in enumerate(face_encodings):
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding)
                
                name = "Unknown"
                color = font_color_red
                
                for known_name, match in zip(known_face_names, matches):
                    if match:
                        name = known_name
                        color = font_color_green
                        present_students.add(name)

                top, right, bottom, left = face_locations[i]
                # Adjust coordinates for the larger resolution
                cv2.rectangle(frame, (left * 4, top * 4), (right * 4, bottom * 4), color, 2)
                text = f"{name}"
                # Adjust coordinates for the larger resolution
                cv2.putText(frame, text, (left * 4, bottom * 4), font, font_scale, color, line_type)

            for student_id, name in self.get_students():
                if name in present_students:
                    self.mark_student_present(student_id)
                else:
                    self.mark_student_absent(student_id)

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()



    def get_students(self):
            self.cursor.execute("SELECT student_id, name FROM students")
            return self.cursor.fetchall()

    def mark_student_present(self, student_id):
        self.cursor.execute("UPDATE students SET present = 1 WHERE student_id = ?", (student_id,))
        self.conn.commit()

    def mark_student_absent(self, student_id):
        self.cursor.execute("UPDATE students SET present = 0 WHERE student_id = ?", (student_id,))
        self.conn.commit()


if __name__ == '__main__':
    AttendanceApp().run()
