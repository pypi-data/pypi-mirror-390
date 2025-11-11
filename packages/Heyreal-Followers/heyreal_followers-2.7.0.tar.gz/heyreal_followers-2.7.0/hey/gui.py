import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import json
import threading
import time
import os
from PIL import Image, ImageDraw
import pystray
import sys

class HeyRealFollowerBot:
    def __init__(self, root):
        self.root = root
        self.root.title("HeyReal Follower Bot v2.7.0")
        self.root.geometry("360x520")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        self.tokens = []
        self.success_count = 0
        self.fail_count = 0
        self.start_time = 0
        self.is_running = False
        self.threads = []
        self.tray_icon = None
        self.is_minimized_to_tray = False
        self.current_theme = "Default"
        self.ensure_token_directory()
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        self.setup_ui()
        self.setup_tray_icon()
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.root.bind('<Unmap>', self.on_minimize)
        
        self.load_tokens()
    
    def ensure_token_directory(self):
        """Membuat direktori Token jika belum ada"""
        if not os.path.exists('Token'):
            os.makedirs('Token')
    
    def setup_ui(self):
        style = ttk.Style()
        self.apply_theme("Default")
        
        main_frame = ttk.Frame(self.root, padding="6")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header Frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 6))
        
        title_label = ttk.Label(header_frame, text="HeyReal Follower Bot v2.7.0", 
                               style='Header.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="by: Dwi Bakti N Dev")
        subtitle_label.pack()
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        
        # Theme Selection Frame
        theme_frame = ttk.LabelFrame(main_frame, text="Theme Settings", padding="4", style='Custom.TLabelframe')
        theme_frame.pack(fill=tk.X, pady=3)
        
        theme_inner_frame = ttk.Frame(theme_frame)
        theme_inner_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(theme_inner_frame, text="Select Theme:").pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value="Default")
        theme_combo = ttk.Combobox(theme_inner_frame, textvariable=self.theme_var, 
                                  values=["Default", "Dark", "Blue", "Green", "Purple"], 
                                  state="readonly", width=12)
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind('<<ComboboxSelected>>', self.change_theme)
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="6", style='Custom.TLabelframe')
        config_frame.pack(fill=tk.X, pady=3)
        
        # Threads setting
        threads_frame = ttk.Frame(config_frame)
        threads_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(threads_frame, text="Threads:").pack(side=tk.LEFT)
        self.threads_var = tk.StringVar(value="1")
        threads_spinbox = ttk.Spinbox(threads_frame, from_=1, to=10, textvariable=self.threads_var, width=6)
        threads_spinbox.pack(side=tk.LEFT, padx=3)
        
        # UID setting
        uid_frame = ttk.Frame(config_frame)
        uid_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(uid_frame, text="Target UID:").pack(side=tk.LEFT)
        self.uid_var = tk.StringVar()
        uid_entry = ttk.Entry(uid_frame, textvariable=self.uid_var, width=20)
        uid_entry.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        # Token management
        tokens_frame = ttk.Frame(config_frame)
        tokens_frame.pack(fill=tk.X, pady=2)
        
        self.tokens_label = ttk.Label(tokens_frame, text="Tokens loaded: 0")
        self.tokens_label.pack(side=tk.LEFT)
        
        # Upload token button
        upload_btn = ttk.Button(tokens_frame, text="Upload Token File", command=self.upload_token_file, width=15)
        upload_btn.pack(side=tk.RIGHT, padx=2)
        
        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=6)
        
        self.start_btn = ttk.Button(button_frame, text="Start Bot", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="Refresh Tokens", command=self.load_tokens).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Hide to Tray", command=self.minimize_to_tray).pack(side=tk.RIGHT, padx=2)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="6", style='Custom.TLabelframe')
        stats_frame.pack(fill=tk.X, pady=3)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        self.success_label = ttk.Label(stats_grid, text="Success: 0", style='Stats.TLabel', foreground='green')
        self.success_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=1)
        
        self.fail_label = ttk.Label(stats_grid, text="Failed: 0", style='Stats.TLabel', foreground='red')
        self.fail_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=1)
        
        self.time_label = ttk.Label(stats_grid, text="Time: 0s", style='Stats.TLabel')
        self.time_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=1)
        
        self.rate_label = ttk.Label(stats_grid, text="Rate: 0/s", style='Stats.TLabel')
        self.rate_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=1)
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="6", style='Custom.TLabelframe')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=50, bg='#f5f5f5', fg='black', 
                                                 font=('Consolas', 7), wrap=tk.WORD, relief='solid', borderwidth=1)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready - Load tokens and configure settings")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, style='TLabel')
        status_bar.pack(fill=tk.X, pady=(3, 0))
    
    def apply_theme(self, theme_name):
        """Apply selected theme"""
        style = ttk.Style()
        
        if theme_name == "Default":
            style.theme_use('clam')
            bg_color = 'white'
            fg_color = 'black'
            accent_color = '#0066cc'
            log_bg = '#f5f5f5'
        elif theme_name == "Dark":
            style.theme_use('alt')
            bg_color = '#2b2b2b'
            fg_color = 'white'
            accent_color = '#4CAF50'
            log_bg = '#1e1e1e'
        elif theme_name == "Blue":
            style.theme_use('clam')
            bg_color = '#e6f2ff'
            fg_color = '#003366'
            accent_color = '#0066cc'
            log_bg = '#f0f8ff'
        elif theme_name == "Green":
            style.theme_use('clam')
            bg_color = '#f0fff0'
            fg_color = '#006400'
            accent_color = '#228B22'
            log_bg = '#f8fff8'
        elif theme_name == "Purple":
            style.theme_use('clam')
            bg_color = '#f8f0ff'
            fg_color = '#4b0082'
            accent_color = '#8A2BE2'
            log_bg = '#faf5ff'
        
        # Configure styles
        style.configure('.', background=bg_color, foreground=fg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Arial', 8))
        style.configure('TButton', font=('Arial', 8), padding=3)
        style.configure('TEntry', font=('Arial', 8))
        style.configure('TSpinbox', font=('Arial', 8))
        style.configure('TCombobox', font=('Arial', 8))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'), foreground=accent_color)
        style.configure('Stats.TLabel', font=('Arial', 8, 'bold'))
        style.configure('Custom.TLabelframe', background=bg_color, foreground=fg_color)
        style.configure('Custom.TLabelframe.Label', background=bg_color, foreground=fg_color)
        style.configure('TScrollbar', background='#e0e0e0')
        
        # Update log background
        if hasattr(self, 'log_text'):
            self.log_text.configure(bg=log_bg, fg=fg_color)
        
        self.current_theme = theme_name
        self.root.configure(bg=bg_color)
    
    def change_theme(self, event=None):
        """Change theme based on selection"""
        theme = self.theme_var.get()
        self.apply_theme(theme)
        self.log_message(f"Theme changed to: {theme}")
    
    def create_tray_image(self):
        """Create system tray icon"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)
        
        dc.rectangle([width//4, height//4, 3*width//4, 3*height//4], fill='#0066cc')
        dc.rectangle([width//3, height//3, 2*width//3, 2*height//3], fill='white')
        
        if self.is_running:
            dc.ellipse([width-20, 5, width-5, 20], fill='green')
        else:
            dc.ellipse([width-20, 5, width-5, 20], fill='red')
            
        return image
    
    def setup_tray_icon(self):
        """Setup system tray icon with menu"""
        image = self.create_tray_image()
        
        menu_items = [
            pystray.MenuItem("Show/Hide", self.toggle_window),
            pystray.MenuItem("Start Bot", self.start_bot_from_tray),
            pystray.MenuItem("Stop Bot", self.stop_bot_from_tray),
            pystray.MenuItem("---", None),
            pystray.MenuItem("Exit", self.quit_application)
        ]
        
        menu = pystray.Menu(*menu_items)
        self.tray_icon = pystray.Icon("heyreal_bot", image, "HeyReal Bot - Stopped", menu)
    
    def update_tray_tooltip(self):
        """Update tray icon tooltip based on bot status"""
        status = "Running" if self.is_running else "Stopped"
        self.tray_icon.title = f"HeyReal Bot - {status} | S:{self.success_count} F:{self.fail_count}"
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.icon = self.create_tray_image()
    
    def toggle_window(self, icon=None, item=None):
        """Toggle show/hide window"""
        if self.root.state() == 'withdrawn' or self.is_minimized_to_tray:
            self.show_window()
        else:
            self.minimize_to_tray()
    
    def show_window(self):
        """Show the main window"""
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.lift)
        self.root.after(0, self.root.focus_force)
        self.is_minimized_to_tray = False
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.visible = False
    
    def minimize_to_tray(self, event=None):
        """Minimize window to system tray"""
        self.root.withdraw()
        self.is_minimized_to_tray = True
        
        def run_tray():
            self.tray_icon.run()
        
        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()
        
        self.log_message("[TRAY] Application minimized to system tray")
    
    def on_minimize(self, event):
        """Handle window minimize event"""
        if self.root.state() == 'iconic':
            self.minimize_to_tray()
    
    def start_bot_from_tray(self, icon=None, item=None):
        """Start bot from tray menu"""
        if not self.is_running:
            self.root.after(0, self.start_bot)
    
    def stop_bot_from_tray(self, icon=None, item=None):
        """Stop bot from tray menu"""
        if self.is_running:
            self.root.after(0, self.stop_bot)
    
    def quit_application(self, icon=None, item=None):
        """Quit the application completely"""
        if self.is_running:
            self.stop_bot()
            time.sleep(1) 
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        
        self.root.quit()
        self.root.destroy()
        os._exit(0)
    
    def upload_token_file(self):
        """Upload token file from external location"""
        file_path = filedialog.askopenfilename(
            title="Select Token File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Baca konten dari file yang dipilih
                with open(file_path, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()
                
                # Pastikan direktori Token ada
                self.ensure_token_directory()
                
                file_path = 'Token/Api.txt'

                with open(file_path, 'w', encoding='utf-8') as target_file:
                    target_file.write(content)
                
                # Langsung memuat token setelah upload
                self.load_tokens()
                
                self.log_message(f"Token file uploaded successfully from: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Token file uploaded successfully!\nTokens automatically loaded.")
                
            except Exception as e:
                self.log_message(f"Error uploading token file: {str(e)}")
                messagebox.showerror("Error", f"Failed to upload token file: {str(e)}")
    
    def log_message(self, message):
        """Log message dengan format yang rapi"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, log_entry + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        self.update_tray_tooltip()
    
    def load_tokens(self):
        """Load tokens from Api.txt file and update UI"""
        token_file_path = os.path.join('Token', 'Api.txt')
        
        try:
            if os.path.exists(token_file_path):
                with open(token_file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    self.tokens = [token.strip() for token in lines if token.strip() and not token.startswith('#')]
                
                # Update UI dengan jumlah token yang dimuat
                token_count = len(self.tokens)
                self.tokens_label.config(text=f"Tokens loaded: {token_count}")
                self.log_message(f"Loaded {token_count} tokens from Api.txt")
                self.status_var.set(f"Loaded {token_count} tokens - Ready to start")
                
            else:
                # File tidak ada, set token kosong
                self.tokens = []
                self.tokens_label.config(text="Tokens loaded: 0")
                self.log_message("Token/Api.txt file not found! Please upload token file first.")
                self.status_var.set("No token file - Please upload token file")
            
            # Update tray tooltip
            self.update_tray_tooltip()
            
        except Exception as e:
            self.log_message(f"Error loading tokens: {str(e)}")
            self.status_var.set("Error loading tokens")
            self.tokens_label.config(text="Tokens loaded: 0")
    
    def update_stats(self):
        elapsed_time = time.time() - self.start_time
        self.success_label.config(text=f"Success: {self.success_count}")
        self.fail_label.config(text=f"Failed: {self.fail_count}")
        self.time_label.config(text=f"Time: {elapsed_time:.1f}s")
        
        if elapsed_time > 0:
            rate = (self.success_count + self.fail_count) / elapsed_time
            self.rate_label.config(text=f"Rate: {rate:.2f}/s")
        self.update_tray_tooltip()
        
        if self.is_running:
            self.root.after(1000, self.update_stats)
    
    def send_follow(self, token, follower_number):
        url = "https://api.heyreal.ai/api/followUpdate"
        
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "nl,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "basic-params": '{"buildVersion":"1","deviceId":"Mozilla50WindowsNT100Win64x64AppleWebKit53736KHTMLlikeGeckoChrome130000Safari53736Edg130000","lang":"nl","deviceName":"Netscape","os":"Windows","osVersion":"","platform":"web"}',
            "content-length": "30",
            "content-type": "application/json",
            "origin": "https://heyreal.ai",
            "priority": "u=1, i",
            "referer": "https://heyreal.ai/",
            "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "traceid": "4QhUJipSkh8IePSanejixoxVT630Hz4i",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "access-token": token.strip()
        }
        
        payload = {
            "uid": self.uid_var.get(),
            "status": 1
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                self.success_count += 1
                self.log_message(f"SUCCESS #{follower_number:03d} | {token[:10]}...")
            else:
                self.fail_count += 1
                self.log_message(f"FAILED #{follower_number:03d} | Code: {response.status_code}")
        except Exception as e:
            self.fail_count += 1
            self.log_message(f"ERROR #{follower_number:03d} | {str(e)[:30]}...")
    
    def bot_worker(self, thread_id):
        """Worker thread untuk menjalankan bot"""
        follower_number = thread_id * 1000
        self.log_message(f"Thread {thread_id} started")
        
        while self.is_running and self.tokens:
            for token in self.tokens:
                if not self.is_running:
                    break
                self.send_follow(token, follower_number)
                follower_number += 1
                time.sleep(0.3)
    
    def start_bot(self):
        if not self.tokens:
            messagebox.showerror("Error", "No tokens loaded! Please upload token file first.")
            return
        
        if not self.uid_var.get().strip():
            messagebox.showerror("Error", "Please enter a target User ID!")
            return
        
        try:
            num_threads = int(self.threads_var.get())
            if num_threads <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter valid number of threads!")
            return
        
        self.is_running = True
        self.success_count = 0
        self.fail_count = 0
        self.start_time = time.time()
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.log_message(f"Starting with {num_threads} threads")
        self.log_message(f"Target UID: {self.uid_var.get()}")
        self.log_message(f"Using {len(self.tokens)} tokens")
        self.status_var.set("Bot running...")
        self.update_tray_tooltip()
    
        self.threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=self.bot_worker, args=(i+1,), daemon=True)
            thread.start()
            self.threads.append(thread)
        self.update_stats()
    
    def stop_bot(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.log_message("Bot stopped by user")
        self.status_var.set("Bot stopped")
        
        elapsed_time = time.time() - self.start_time
        self.log_message(f"Final: {self.success_count} success, {self.fail_count} failed in {elapsed_time:.1f}s")
        self.update_tray_tooltip()

def run_gui():
    root = tk.Tk()
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Warning: DPI awareness setting failed: {e}")

    app = HeyRealFollowerBot(root)

    def show_context_menu(event):
        try:
            context_menu = tk.Menu(root, tearoff=0)
            context_menu.add_command(label="Quit Application", command=app.quit_application)
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    root.bind("<Button-3>", show_context_menu)  
    root.mainloop()

if __name__ == "__main__":
    run_gui()