# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 15:00:02 2024

@author: Caytte Itoh

(c)2024~ All rights reserved.
"""

###Load packages
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
from datetime import datetime
import pytz
import schedule
import nfc
import requests
import binascii
from pygame import mixer
from zoneinfo import ZoneInfo
import json
import os
import subprocess
import sys

def restart_programme():
    print("restarting system...")
    time.sleep(1)
    python = sys.executable
    script = os.path.abspath(__file__)
    os.execv(python, [python, script] + sys.argv[1:])

class PaymentApp:
    ##design section
    def __init__(self, root):
        self.root = root
        self.root.title("丸PAY v3.3")
        self.root.configure(bg="#d1e1e6")
        self.root.attributes('-fullscreen', True)
    
        self.x = None
        self.y = None
    
        self.root.bind('<Escape>', self.toggle_fullscreen)
    
        # 左フレームの幅を小さくし、右フレームの幅を広げる
        self.left_frame = tk.Frame(root, bg="#FFFFFF", width=800, height=1280)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.left_frame.pack_propagate(False)  # サイズを固定
    
        self.right_frame = tk.Frame(root, bg="#346272")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
    
        self.app_script_url = "https://script.google.com/macros/s/AKfycbxgX2OmPEM0XSaJlka3fa3aP7xsWgfJ9jHCyWjSwco8aqhjvDMnm1mZZ9SX6G2QKNlb/exec"
    
        self.setup_logo()
        self.setup_console()
        self.setup_status_box()
    
        self.start_status_checks()
    
        # Initialize NFC and payment processing
        self.clf = None
        self.payment_thread = threading.Thread(target=self.payment_loop, daemon=True)
        self.payment_thread.start()

    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        if not self.root.attributes('-fullscreen'):
            self.root.geometry('860x450')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        if not self.root.attributes('-fullscreen'):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def setup_logo(self):
        # リサイズ後のサイズを定義
        new_size = (1800, 1800)

        # 静的ロゴのリサイズ
        self.static_gif = Image.open("logo_main.gif")
        self.static_frames = self.resize_gif(self.static_gif, new_size)
        
        # 成功ロゴのリサイズ
        self.success_gif = Image.open("logo_success.gif")
        self.success_frames = self.resize_gif(self.success_gif, new_size)
        
        # 失敗ロゴのリサイズ
        self.fail_gif = Image.open("logo_fail.gif")
        self.fail_frames = self.resize_gif(self.fail_gif, new_size)
        
        self.logo_label = tk.Label(self.left_frame, bg="#FFFFFF")
        self.logo_label.pack(pady=(300, 10), padx=0)
        
        # Create frame for the three images below the logo
        self.images_frame = tk.Frame(self.left_frame, bg="#FFFFFF")
        self.images_frame.pack(pady=10)
        
        # Load and display the three images in a row

        # Set a smaller size for the images
        image_size = (160, 160)
        
        # QR image
        self.qr_image = Image.open("pay.png").resize(image_size, Image.LANCZOS)
        self.qr_photo = ImageTk.PhotoImage(self.qr_image)
        self.qr_label = tk.Label(self.images_frame, image=self.qr_photo, bg="#FFFFFF")
        self.qr_label.pack(side=tk.LEFT, padx=15)
        
        # Character image
        self.char_image = Image.open("char.png").resize(image_size, Image.LANCZOS)
        self.char_photo = ImageTk.PhotoImage(self.char_image)
        self.char_label = tk.Label(self.images_frame, image=self.char_photo, bg="#FFFFFF")
        self.char_label.pack(side=tk.LEFT, padx=15)
        
        # Request image
        self.req_image = Image.open("req.png").resize(image_size, Image.LANCZOS)
        self.req_photo = ImageTk.PhotoImage(self.req_image)
        self.req_label = tk.Label(self.images_frame, image=self.req_photo, bg="#FFFFFF")
        self.req_label.pack(side=tk.LEFT, padx=15)
        
        #print("Images loaded successfully")  # 4Debug

        
        self.is_animating = False
        self.show_static_logo()
        
    def resize_gif(self, gif, size):
        frames = []
        for frame in ImageSequence.Iterator(gif):
            resized_frame = frame.copy()
            resized_frame.thumbnail(size, Image.LANCZOS)
            frames.append(ImageTk.PhotoImage(resized_frame))
        return frames

    def show_static_logo(self):
        if not self.is_animating:
            for i in range(len(self.static_frames)):
                frame = self.static_frames[i]
                self.logo_label.configure(image=frame)
                self.root.update()
                time.sleep(0.015)
            self.logo_label.configure(image=self.static_frames[-1])


    def animate_logo(self, status):
        self.is_animating = True
        if status == "SUCCESS":
            frames = self.success_frames
        elif status == "FAILED":
            frames = self.fail_frames
        else: pass
        
        for i in range(len(frames)):
            if not self.is_animating:
                break
            frame = frames[i]
            self.logo_label.configure(image=frame)
            self.root.update()
            time.sleep(0.015)
        
        self.is_animating = False
        self.show_static_logo()

    def setup_console(self):
        self.console_frame = tk.Frame(self.right_frame, bg="#346272")
        self.console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20,10))  # パディングを調整
        
        self.inner_console_frame = tk.Frame(self.console_frame, bg="#ffffff")
        self.inner_console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('T I M E', 'D A T E', 'I D', 'R E S U L T', 'B A L A N C E')
        
        self.style = ttk.Style()
        self.style.configure('Treeview', 
                             background='#ffffff', 
                             foreground='#000000',
                             borderwidth=0,
                             font=('Helvetica', 10),
                             rowheight=30)
        self.style.map('Treeview', background=[('selected', '#ffffff')])
        self.style.configure('Treeview.Heading', 
                             background='#ffffff', 
                             foreground='#000000',
                             relief='flat',
                             borderwidth=0,
                             padding=(5,0,5,0),
                             font=('Helvetica', 10, 'bold'))
        self.style.map('Treeview.Heading',
                       background=[('active', '#edf1f2')])
        
        self.tree = ttk.Treeview(self.inner_console_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)  # カラムの幅を広げる
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=55, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=12)
        
        self.tree.tag_configure('success', foreground='#16A085')
        self.tree.tag_configure('failed', foreground='#E74C3C')
        
        self.tree.tag_configure('success', foreground='#16A085')
        self.tree.tag_configure('failed', foreground='#E74C3C')
        self.tree.tag_configure('paying', foreground='#F39C12')  # オレンジ色で"paying..."を表示

    ##status section
    def setup_status_box(self):
        self.status_frame = tk.Frame(self.right_frame, bg="#346272")
        self.status_frame.pack(fill=tk.X, expand=False, padx=20, pady=(0, 20))  # パディングを調整

        self.status_box = tk.Frame(self.status_frame, bg="#333333", height=60)  # 高さを調整
        self.status_box.pack(fill=tk.X, expand=False)
        self.status_box.pack_propagate(False)

        self.status_labels = {}
        #for status_type in ['Reader status', 'Network status']:
        for status_type in ['Network status']:
            label = tk.Label(self.status_box, text=f"{status_type}: Unknown", bg="#333333", fg="#FFFFFF", font=('Helvetica', 10))
            label.pack(side=tk.LEFT, padx=20, pady=5)
            self.status_labels[status_type] = label

    def start_status_checks(self):
        self.check_status_process1()
        #self.check_status_process2()
        
        def run_schedule():
            while True:
                self.check_status_process1()
                #self.check_status_process2()
                time.sleep(1800)

        self.schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        self.schedule_thread.start()
        
    def check_status_process1(self):
        try:
            url = "https://script.google.com/macros/s/AKfycbxgX2OmPEM0XSaJlka3fa3aP7xsWgfJ9jHCyWjSwco8aqhjvDMnm1mZZ9SX6G2QKNlb/"
            response = requests.get(url, timeout=5)
            status = "ONLINE" if response.status_code == 200 else "OFFLINE"
        except requests.RequestException:
            status = "OFFLINE"
        self.update_status('Network status', status)

    #def check_status_process2(self):
        #try:
        #    tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
        #    status = "ONLINE"
        #except Exception as e:
        #    status = "OFFLINE"
        #self.update_status('Reader status', status)
    

    def update_status(self, process_name, status):
        color = "#16A085" if status == "ONLINE" else "#E74C3C"
        self.root.after(0, lambda: self.status_labels[process_name].config(text=f"{process_name}: {status}", fg=color))
    
    def update_latest_console_entry(self, time_str, date_str, user, status, balance):
        children = self.tree.get_children()
        if children:
            latest_item = children[0]  # 最新のアイテムは常に一番上
            
            # タグを設定
            tag = 'success' if status == "SUCCESS" else 'failed'
            
            # アイテムの値を更新
            self.tree.item(latest_item, values=(time_str, date_str, user, status, balance), tags=(tag,))
            
            # アニメーションを実行（"paying..."の場合は実行しない）
            if status != "paying...":
                threading.Thread(target=self.animate_logo, args=(status,)).start()

    def fetch_spreadsheet_value(self, cell):
        full_url = f"{self.app_script_url}?data1={cell}"
        response = requests.get(full_url)
        
        if response.status_code == 200:
            content = response.text
            #おまじない!!
            start = content.index('CaLeNdAr') + len('CaLeNdAr')
            end = content.rindex('CaLeNdAr')
            value_json = content[start:end]
            value = json.loads(value_json)
            return value
        else:
            return f"Error: {response.status_code}"

    def send_request(self, alpha1, alpha2):
        try:
            url = f"{self.app_script_url}?data1={alpha2}"
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                start = content.index('CaLeNdAr') + len('CaLeNdAr')
                end = content.rindex('CaLeNdAr')
                value_json = content[start:end]
                value = json.loads(value_json)
                return "SUCCESS", value
            else:
                return "FAILED", None
        except:
            return "FAILED", None

    def insert_console_data(self, time_str, date_str, user, status, balance):
        # "paying..."の場合は特別なタグを設定
        if status == "paying...":
            tag = 'paying'
        else:
            tag = 'success' if status == "SUCCESS" else 'failed'
        
        item = self.tree.insert('', 0, values=(time_str, date_str, user, status, balance), tags=(tag,))
        
        if self.tree.get_children().__len__() > 10:
            self.tree.delete(self.tree.get_children()[-1])
        
            # "paying..."の場合はアニメーションを実行しない
        if status != "paying...":
            threading.Thread(target=self.animate_logo, args=(status,)).start()

    def payment_loop(self):
        i = 0
        j = 0 #counter for restart system
        while True:
            self.clf = nfc.ContactlessFrontend("usb")
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            idm = str(binascii.hexlify(tag._nfcid))
            i += 1
            
            # カードがタッチされた時の時刻を取得
            japan_tz = pytz.timezone('Asia/Tokyo')
            current_time = datetime.now(japan_tz)
            time_str = current_time.strftime("%H : %M : %S")
            date_str = current_time.strftime("%d / %m / %Y")
            
            user_data = {
                "b'012e5ce6de843949'": ("ITOH", "B5"),
                "b'012e5d000ccb4b56'": ("MATSUDA", "B19"),
                "b'012e5ce6de884567'": ("Kawai", "B3"),
                "b'012e50f4d8d55825'": ("SHIMA", "B17"),
                "b'012e5ce6de843b21'": ("NAGAO", "B8"),
                "b'0113030008174316'": ("Maru", "B2"),
                "b'012e5d000cca505d'": ("Hu", "B12"),
                "b'012e5ce6de874e61'": ("ZHOU", "B11"),
                "b'012e5ce6de893c43'": ("Kana", "B13"),
                "b'012e5ce6de864940'": ("Noel", "B20"),
                "b'012e5d000cca4a23'": ("Hong", "B21"),
                "b'012e58a80f974a2d'": ("seta", "B6")
            }
            
            if idm in user_data:
                user, code = user_data[idm]
                
                # 最初に "paying..." を表示
                self.root.after(0, self.insert_console_data, time_str, date_str, user, "paying...", "N/A")
                
                # 実際の処理を実行
                status, balance = self.send_request(user, code)
                balance_str = f"{balance:.2f}" if balance is not None else "N/A"
                
                # 処理結果で最新のエントリを更新
                self.root.after(0, self.update_latest_console_entry, time_str, date_str, user, status, balance_str)
                
                if status == "FAILED":
                    subprocess.call("mpg321 new_Fail.mp3", shell=True)
                    time.sleep(5)
                    self.clf.close()
                if status == "SUCCESS":
                    subprocess.call("mpg321 new_success.mp3",shell=True)
                    self.clf.close()
            else:
                # 未知のカードの場合も最初に "paying..." を表示
                user = "UNKNOWN"
                self.root.after(0, self.insert_console_data, time_str, date_str, user, "paying...", "N/A")
                
                # 少し待ってから失敗を表示
                time.sleep(0.5)  # 短い待機時間
                status = "FAILED"
                balance_str = "N/A"
                self.root.after(0, self.update_latest_console_entry, time_str, date_str, user, status, balance_str)
                
                subprocess.call("mpg321 new_Fail.mp3", shell=True)
                time.sleep(5)
                self.clf.close()
            
            j += 1
            if(j>=10):
                status = "Restarting System"
                user ="root"
                balance_str = "N/A"
                japan_tz = pytz.timezone('Asia/Tokyo')
                current_time = datetime.now(japan_tz)
                time_str = current_time.strftime("%H : %M : %S")
                date_str = current_time.strftime("%d / %m / %Y")
                self.root.after(0, self.insert_console_data, time_str, date_str, user, status, balance_str)
                time.sleep(5)
                self.clf.close()
                restart_programme()
                

if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentApp(root)
    root.mainloop()
