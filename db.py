import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  
import sqlite3
from tkinter import font as tkfont

class StudentGradeManager:
    def __init__(self):
        
        self.conn = sqlite3.connect('student_grades.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
       
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                grade REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def add_grade(self, name, subject, grade):
      
        self.cursor.execute('''
            INSERT INTO grades (name, subject, grade)
            VALUES (?, ?, ?)
        ''', (name, subject, grade))
        self.conn.commit()

    def calculate_average(self, name):
       
        self.cursor.execute('''
            SELECT grade FROM grades WHERE name = ?
        ''', (name,))
        grades = self.cursor.fetchall()
        if grades:
            average = sum(grade[0] for grade in grades) / len(grades)
            return average
        return 0

    def get_letter_grade(self, average):
        if average >= 90:
            return 'A'
        elif average >= 80:
            return 'B'
        elif average >= 70:
            return 'C'
        elif average >= 60:
            return 'D'
        else:
            return 'F'

    def get_cgpa(self, average):
        if average >= 90:
            return 4.0
        elif average >= 80:
            return 3.0
        elif average >= 70:
            return 2.0
        elif average >= 60:
            return 1.0
        else:
            return 0.0

    def get_all_grades(self):
        
        self.cursor.execute('''
            SELECT name, subject, grade FROM grades
        ''')
        rows = self.cursor.fetchall()
        result = ""
        student_grades = {}
        for row in rows:
            name, subject, grade = row
            if name not in student_grades:
                student_grades[name] = {}
            student_grades[name][subject] = grade

        for name, grades in student_grades.items():
            average = self.calculate_average(name)
            letter_grade = self.get_letter_grade(average)
            cgpa = self.get_cgpa(average)
            result += f"Student: {name}\n"
            for subject, grade in grades.items():
                result += f"{subject}: {grade}\n"
            result += f"Average: {average:.2f}\n"
            result += f"Letter Grade: {letter_grade}\n"
            result += f"CGPA: {cgpa:.2f}\n"
            result += "------------------------\n"
        return result

    def __del__(self):
      
        self.conn.close()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.manager = StudentGradeManager()
        self.title("Student Grade Tracker")
        self.geometry("600x400")

        self.bg_image = Image.open("krish.jpg")  
        self.bg_image = self.bg_image.resize((600, 400), Image.LANCZOS) 
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.frames = {}
        self.create_frames()
        self.show_frame("HomePage")

    def create_frames(self):
        for F in (HomePage, AddGradePage, DisplayGradesPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self.manager, bg_image=self.bg_photo)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class BackgroundFrame(tk.Frame):
    def __init__(self, parent, controller, bg_image=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.bg_image = bg_image

        if self.bg_image:
            self.bg_label = tk.Label(self, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)

class HomePage(BackgroundFrame):
    def __init__(self, parent, controller, bg_image=None):
        super().__init__(parent, controller, bg_image=bg_image)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        bold_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        title_label = tk.Label(self, text="Student Grade Process", bg='white', font=bold_font)
        title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=20)
        add_grade_button = tk.Button(self, text="Add Grade",
                                     command=lambda: parent.show_frame("AddGradePage"))
        add_grade_button.grid(row=1, column=0, columnspan=2, pady=5, padx=10)
        display_grades_button = tk.Button(self, text="Display Grades",
                                          command=lambda: parent.show_frame("DisplayGradesPage"))
        display_grades_button.grid(row=2, column=0, columnspan=2, pady=5, padx=10)
        quit_button = tk.Button(self, text="Quit", command=parent.quit)
        quit_button.grid(row=3, column=0, columnspan=2, pady=5, padx=10)

class AddGradePage(BackgroundFrame):
    def __init__(self, parent, controller, bg_image=None):
        super().__init__(parent, controller, bg_image=bg_image)

        tk.Label(self, text="Add Grades for a Student", bg='white').grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(self, text="Student Name:", bg='white').grid(row=1, column=0, sticky="e", padx=10)
        self.student_name = tk.Entry(self)
        self.student_name.grid(row=1, column=1, padx=10, pady=5)

        self.subject_labels = ["Major 1:", "Major 2:", "Major 3:"]
        self.subject_entries = [tk.Entry(self) for _ in self.subject_labels]
        self.grade_entries = [tk.Entry(self) for _ in self.subject_labels]

        for i, label in enumerate(self.subject_labels):
            tk.Label(self, text=label, bg='white').grid(row=i+2, column=0, sticky="e", padx=10)
            self.subject_entries[i].grid(row=i+2, column=1, padx=10, pady=5)
            tk.Label(self, text="Marks :", bg='white').grid(row=i+2, column=2, sticky="e", padx=10)
            self.grade_entries[i].grid(row=i+2, column=3, padx=10, pady=5)

        tk.Button(self, text="Add Grades", command=self.add_grades).grid(row=len(self.subject_labels)+2, column=0, columnspan=4, pady=10)
        tk.Button(self, text="Back to Home", command=lambda: parent.show_frame("HomePage")).grid(row=len(self.subject_labels)+3, column=0, columnspan=4, pady=5)

    def add_grades(self):
        name = self.student_name.get()
        subjects = [entry.get() for entry in self.subject_entries]
        grades = []

        for grade_entry in self.grade_entries:
            try:
                grade = float(grade_entry.get())
                grades.append(grade)
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid grades.")
                return

        if name and all(subjects):
            for subject, grade in zip(subjects, grades):
                self.controller.add_grade(name, subject, grade)
            messagebox.showinfo("Success", "Grades added successfully.")
            self.student_name.delete(0, tk.END)
            for entry in self.subject_entries + self.grade_entries:
                entry.delete(0, tk.END)
        else:
            messagebox.showerror("Input Error", "Please fill all fields.")

class DisplayGradesPage(BackgroundFrame):
    def __init__(self, parent, controller, bg_image=None):
        super().__init__(parent, controller, bg_image=bg_image)

        tk.Label(self, text="Display Grades", bg='white').grid(row=0, column=0, pady=10)

        self.text_area = tk.Text(self, wrap=tk.WORD, height=15, width=70)
        self.text_area.grid(row=1, column=0, padx=10, pady=10)

        tk.Button(self, text="Show Grades", command=self.display_grades).grid(row=2, column=0, pady=5)
        tk.Button(self, text="Back to Home",
                  command=lambda: parent.show_frame("HomePage")).grid(row=3, column=0, pady=5)

    def display_grades(self):
        grades_info = self.controller.get_all_grades()
        if grades_info:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, grades_info)
        else:
            messagebox.showinfo("No Grades", "No grades available to display.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
