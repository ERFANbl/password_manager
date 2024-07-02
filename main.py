import tkinter as tk
from tkinter import messagebox, simpledialog
from mysql import connector
import hashlib

# another change
def connect_db():
    return connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="password_manager"
    )

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check if master password exists
def master_password_exists():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    db.close()
    return result[0] > 0

# Verify master password
def verify_master_password(master_password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT master_password FROM users WHERE id = 1")
    result = cursor.fetchone()
    db.close()
    return result[0] == hash_password(master_password)

# Create master password
def create_master_password(master_password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (master_password) VALUES (%s)", (hash_password(master_password),))
    db.commit()
    db.close()

# Main application
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")

        if master_password_exists():
            self.show_login_screen()
        else:
            self.show_registration_screen()

    def show_login_screen(self):
        self.clear_screen()
        self.master_password_label = tk.Label(self.root, text="Enter Master Password:")
        self.master_password_label.pack()
        self.master_password_entry = tk.Entry(self.root, show='*')
        self.master_password_entry.pack()
        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack()
        self.register_link = tk.Button(self.root, text="Don't have an account? Click here to register", command=self.show_registration_screen)
        self.register_link.pack()

    def show_registration_screen(self):
        self.clear_screen()
        self.master_password_label = tk.Label(self.root, text="Create Master Password:")
        self.master_password_label.pack()
        self.master_password_entry = tk.Entry(self.root, show='*')
        self.master_password_entry.pack()
        self.register_button = tk.Button(self.root, text="Register", command=self.register)
        self.register_button.pack()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        master_password = self.master_password_entry.get()
        if verify_master_password(master_password):
            messagebox.showinfo("Success", "Login successful!")
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Invalid master password")

    def register(self):
        master_password = self.master_password_entry.get()
        if master_password:
            create_master_password(master_password)
            messagebox.showinfo("Success", "Master password created successfully!")
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Master password cannot be empty")

    def show_main_screen(self):
        self.clear_screen()
        self.add_button = tk.Button(self.root, text="Add Entry", command=self.add_entry)
        self.add_button.pack()
        self.view_button = tk.Button(self.root, text="View Entries", command=self.view_entries)
        self.view_button.pack()
        self.update_button = tk.Button(self.root, text="Update Entry", command=self.update_entry)
        self.update_button.pack()
        self.delete_button = tk.Button(self.root, text="Delete Entry", command=self.delete_entry)
        self.delete_button.pack()

    def add_entry(self):
        service = simpledialog.askstring("Service", "Enter service name:")
        username = simpledialog.askstring("Username", "Enter username:")
        password = simpledialog.askstring("Password", "Enter password:")

        if service and username and password:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO passwords (service, username, password) VALUES (%s, %s, %s)",
                           (service, username, password))
            db.commit()
            db.close()
            messagebox.showinfo("Success", "Entry added successfully!")

    def view_entries(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT service, username, password FROM passwords")
        entries = cursor.fetchall()
        db.close()

        entries_str = "\n".join([f"Service: {service}, Username: {username}, Password: {password}"
                                 for service, username, password in entries])
        messagebox.showinfo("Entries", entries_str if entries_str else "No entries found.")

    def update_entry(self):
        service = simpledialog.askstring("Service", "Enter service name to update:")
        if service:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT username, password FROM passwords WHERE service = %s", (service,))
            result = cursor.fetchone()

            if result:
                new_username = simpledialog.askstring("Username", "Enter new username:", initialvalue=result[0])
                new_password = simpledialog.askstring("Password", "Enter new password:", initialvalue=result[1])
                
                if new_username and new_password:
                    cursor.execute("UPDATE passwords SET username = %s, password = %s WHERE service = %s",
                                   (new_username, new_password, service))
                    db.commit()
                    db.close()
                    messagebox.showinfo("Success", "Entry updated successfully!")
                else:
                    messagebox.showerror("Error", "Both username and password are required!")
            else:
                db.close()
                messagebox.showerror("Error", "Service not found!")

    def delete_entry(self):
        service = simpledialog.askstring("Service", "Enter service name to delete:")
        if service:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM passwords WHERE service = %s", (service,))
            db.commit()
            db.close()
            messagebox.showinfo("Success", "Entry deleted successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
# git testing