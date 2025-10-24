#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画をGIFに変換するGUIツール
主に.webm形式の動画をサポート
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
import tempfile
from PIL import Image
import sys
import numpy as np

# Pillow 10.x の互換性パッチ
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# ffmpegを直接使用するため、moviepyのパッチは不要

class GIFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("動画→GIF変換ツール")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 変数の初期化
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.start_time = tk.DoubleVar(value=0.0)
        self.duration = tk.DoubleVar(value=5.0)
        self.fps = tk.IntVar(value=10)
        self.scale = tk.DoubleVar(value=0.5)
        self.is_converting = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 入力ファイル選択
        ttk.Label(main_frame, text="入力動画ファイル:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_input_file).grid(row=0, column=2, padx=5, pady=5)
        
        # 出力ファイル選択
        ttk.Label(main_frame, text="出力GIFファイル:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="参照", command=self.select_output_file).grid(row=1, column=2, padx=5, pady=5)
        
        # 設定パラメータ
        settings_frame = ttk.LabelFrame(main_frame, text="変換設定", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 開始時間
        ttk.Label(settings_frame, text="開始時間 (秒):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=0, to=999, textvariable=self.start_time, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # 継続時間
        ttk.Label(settings_frame, text="継続時間 (秒):").grid(row=0, column=2, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=0.1, to=60, textvariable=self.duration, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # FPS
        ttk.Label(settings_frame, text="FPS:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=1, to=30, textvariable=self.fps, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # スケール
        ttk.Label(settings_frame, text="スケール:").grid(row=1, column=2, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=0.1, to=2.0, textvariable=self.scale, width=10, increment=0.1).grid(row=1, column=3, padx=5, pady=2)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # ステータスラベル
        self.status_label = ttk.Label(main_frame, text="ファイルを選択してください")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.convert_button = ttk.Button(button_frame, text="変換開始", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="終了", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def select_input_file(self):
        """入力ファイルを選択"""
        filetypes = [
            ("動画ファイル", "*.webm *.mp4 *.avi *.mov *.mkv"),
            ("WebM", "*.webm"),
            ("MP4", "*.mp4"),
            ("すべてのファイル", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="動画ファイルを選択",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            # 自動的に出力ファイル名を設定
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_path = os.path.join(os.path.dirname(filename), f"{base_name}.gif")
            self.output_file.set(output_path)
            self.status_label.config(text="ファイルが選択されました")
    
    def select_output_file(self):
        """出力ファイルを選択"""
        filename = filedialog.asksaveasfilename(
            title="GIFファイルの保存先を選択",
            defaultextension=".gif",
            filetypes=[("GIFファイル", "*.gif"), ("すべてのファイル", "*.*")]
        )
        
        if filename:
            self.output_file.set(filename)
    
    def start_conversion(self):
        """変換を開始"""
        if not self.input_file.get():
            messagebox.showerror("エラー", "入力ファイルを選択してください")
            return
            
        if not self.output_file.get():
            messagebox.showerror("エラー", "出力ファイルを選択してください")
            return
        
        if self.is_converting:
            messagebox.showwarning("警告", "既に変換処理が実行中です")
            return
        
        # 別スレッドで変換を実行
        self.is_converting = True
        self.convert_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="変換中...")
        
        thread = threading.Thread(target=self.convert_video)
        thread.daemon = True
        thread.start()
    
    def convert_video(self):
        """動画をGIFに変換（ffmpegを直接使用）"""
        try:
            input_path = self.input_file.get()
            output_path = self.output_file.get()
            start_time = self.start_time.get()
            duration = self.duration.get()
            fps = self.fps.get()
            scale = self.scale.get()
            
            # ffmpegコマンドを構築
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-vf', f'fps={fps},scale=iw*{scale}:ih*{scale}',
                '-y',  # 上書き確認なし
                output_path
            ]
            
            # ffmpegを実行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # UIを更新
            self.root.after(0, self.conversion_completed)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"ffmpegエラー: {e.stderr}"
            self.root.after(0, lambda: self.conversion_error(error_msg))
        except FileNotFoundError:
            error_msg = "ffmpegが見つかりません。ffmpegをインストールしてください。"
            self.root.after(0, lambda: self.conversion_error(error_msg))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.conversion_error(error_msg))
    
    def conversion_completed(self):
        """変換完了時の処理"""
        self.is_converting = False
        self.convert_button.config(state='normal')
        self.progress.stop()
        self.status_label.config(text="変換が完了しました！")
        messagebox.showinfo("完了", f"GIFファイルが作成されました:\n{self.output_file.get()}")
    
    def conversion_error(self, error_message):
        """変換エラー時の処理"""
        self.is_converting = False
        self.convert_button.config(state='normal')
        self.progress.stop()
        self.status_label.config(text="変換に失敗しました")
        messagebox.showerror("エラー", f"変換中にエラーが発生しました:\n{error_message}")

def main():
    """メイン関数"""
    root = tk.Tk()
    app = GIFConverter(root)
    
    # ウィンドウを中央に配置
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
