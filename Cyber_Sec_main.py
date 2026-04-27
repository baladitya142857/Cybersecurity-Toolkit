"""
Security Toolkit - A comprehensive GUI application for security tools
Features: Encryption, Password Management, File Security, and Cyber Forensics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import string
import random
import hashlib
import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
import math

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
    from cryptography.hazmat.primitives import hashes, serialization
except ImportError:
    print("Warning: cryptography module not fully available")

try:
    from PIL import Image, ImageTk
    from PIL.ExifTags import TAGS
except ImportError:
    print("Warning: PIL module not available")




class SecurityToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Security Toolkit - Comprehensive Security Tools")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        self.tabs = {}
        self.password_storage = {}
        self.load_password_storage()
        
        self.create_home_page()
        
    def create_home_page(self):
        """Create the main home page with navigation buttons"""
        home_frame = tk.Frame(self.root, bg='#2c3e50')
        home_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(home_frame, text="Security Toolkit", 
                              font=('Arial', 36, 'bold'), 
                              bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=40)
        
        subtitle_label = tk.Label(home_frame, 
                                 text="Comprehensive Security Tools for Education and Practice",
                                 font=('Arial', 14), bg='#2c3e50', fg='#bdc3c7')
        subtitle_label.pack(pady=10)
        
        button_frame = tk.Frame(home_frame, bg='#2c3e50')
        button_frame.pack(pady=40)
        
        categories = [
            ("🔐 Encryption & Decryption", self.open_encryption_category, '#e74c3c'),
            ("🔑 Password & Authentication", self.open_password_category, '#3498db'),
            ("📁 File & Data Security", self.open_file_security_category, '#2ecc71'),
            ("🔍 Cyber Forensics & Analysis", self.open_forensics_category, '#f39c12')
        ]
        
        for i, (text, command, color) in enumerate(categories):
            btn = tk.Button(button_frame, text=text, command=command,
                          font=('Arial', 14, 'bold'), bg=color, fg='white',
                          width=30, height=2, cursor='hand2',
                          relief=tk.RAISED, bd=3)
            btn.pack(pady=10)
            
        footer_label = tk.Label(home_frame, 
                               text="Educational Security Toolkit - For Learning Purposes Only",
                               font=('Arial', 10, 'italic'), bg='#2c3e50', fg='#95a5a6')
        footer_label.pack(side=tk.BOTTOM, pady=20)
        
    def create_tab_window(self, title, tools_list, color='#34495e'):
        """Create a new tab window with tool list and tab management"""
        if title in self.tabs:
            window, _, _ = self.tabs[title]
            window.lift()
            return
            
        tab_window = tk.Toplevel(self.root)
        tab_window.title(title)
        tab_window.geometry("1200x700")
        tab_window.configure(bg=color)
        
        main_container = tk.Frame(tab_window, bg=color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_container, bg='white', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="Available Tools", 
                font=('Arial', 14, 'bold'), bg='white', fg='#2c3e50').pack(pady=10)
        
        tk.Label(left_panel, text="Click a tool to open it", 
                font=('Arial', 9, 'italic'), bg='white', fg='#7f8c8d').pack(pady=(0, 10))
        
        scrollbar = tk.Scrollbar(left_panel)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tools_listbox = tk.Listbox(left_panel, yscrollcommand=scrollbar.set,
                                   font=('Arial', 11), bg='#ecf0f1', 
                                   selectmode=tk.SINGLE, relief=tk.FLAT,
                                   highlightthickness=0, cursor='hand2')
        tools_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        scrollbar.config(command=tools_listbox.yview)
        
        for tool_name, _ in tools_list:
            tools_listbox.insert(tk.END, tool_name)
        
        right_panel = tk.Frame(main_container, bg=color)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        opened_tools = set()
        
        def open_tool_in_tab(event=None):
            selection = tools_listbox.curselection()
            if not selection:
                return
            
            index = selection[0]
            tool_name, tool_func = tools_list[index]
            
            if tool_name in opened_tools:
                for i, tab_id in enumerate(notebook.tabs()):
                    if notebook.tab(tab_id, 'text') == tool_name:
                        notebook.select(i)
                        return
            
            def on_close():
                opened_tools.discard(tool_name)
            
            tab_frame = self.add_closable_tab(notebook, tool_name, on_close)
            tool_func(tab_frame)
            opened_tools.add(tool_name)
            
            for i, tab_id in enumerate(notebook.tabs()):
                if notebook.tab(tab_id, 'text') == tool_name:
                    notebook.select(i)
                    break
        
        tools_listbox.bind('<<ListboxSelect>>', open_tool_in_tab)
        tools_listbox.bind('<Double-Button-1>', open_tool_in_tab)
        
        self.tabs[title] = (tab_window, notebook, opened_tools)
        
        def on_close():
            if title in self.tabs:
                del self.tabs[title]
            tab_window.destroy()
        
        tab_window.protocol("WM_DELETE_WINDOW", on_close)
        
    def close_category_window(self, title):
        """Close a category window"""
        if title in self.tabs:
            window, _ = self.tabs[title]
            window.destroy()
            del self.tabs[title]
            
    def add_closable_tab(self, notebook, title, on_close_callback=None):
        """Add a tab with a close button"""
        container = tk.Frame(notebook, bg='white')
        notebook.add(container, text=title)
        
        close_button_frame = tk.Frame(container, bg='white')
        close_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        def close_this_tab():
            for i, tab_id in enumerate(notebook.tabs()):
                if notebook.tab(tab_id, 'text') == title:
                    notebook.forget(i)
                    if on_close_callback:
                        on_close_callback()
                    break
        
        close_btn = tk.Button(close_button_frame, text='× Close This Tab', 
                             command=close_this_tab,
                             bg='#e74c3c', fg='white', 
                             font=('Arial', 10, 'bold'),
                             cursor='hand2', relief=tk.FLAT,
                             padx=10, pady=5)
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        content_frame = tk.Frame(container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        return content_frame
        
    def open_encryption_category(self):
        """Open Encryption & Decryption Tools category"""
        tools = [
            ("🔍 Cipher Analysis & Comparison", self.create_cipher_analysis_tool),
            ("SHA-256 Hash", self.create_sha256_tool),
            ("RSA Encryption (Advanced)", self.create_rsa_advanced_tool),
            ("AES-256 Encryption", self.create_aes_tool),
            ("Caesar Cipher", self.create_caesar_cipher_tool),
            ("Vigenère Cipher", self.create_vigenere_cipher_tool),
            ("Multiplicative Cipher", self.create_multiplicative_cipher_tool),
            ("Playfair Cipher", self.create_playfair_cipher_tool),
            ("RSA Encryption", self.create_rsa_tool),
            ("Affine Cipher", self.create_affine_cipher_tool),
            ("Autokey Cipher", self.create_autokey_cipher_tool),
            ("Hill Cipher (2x2)", self.create_hill_cipher_tool),
            ("Columnar Transposition", self.create_columnar_transposition_tool),
            ("Morse Code", self.create_morse_code_tool),
            ("Base64 Encoder/Decoder", self.create_base64_tool),
            ("Transposition Cipher", self.create_transposition_cipher_tool),
            ("Key Transposition Cipher", self.create_key_transposition_cipher_tool)
        ]
        
        self.create_tab_window("Encryption & Decryption Tools", tools, '#c0392b')
            
    def open_password_category(self):
        """Open Password & Authentication Tools category"""
        tools = [
            ("Password Generator", self.create_password_generator_tool),
            ("Password Strength Checker", self.create_password_strength_tool),
            ("Password Manager", self.create_password_manager_tool)
        ]
        
        self.create_tab_window("Password & Authentication Tools", tools, '#2980b9')
            
    def open_file_security_category(self):
        """Open File & Data Security Tools category"""
        tools = [
            ("File Encryption/Decryption", self.create_file_encryption_tool),
            ("Steganography (Text in PNG)", self.create_steganography_tool),
            ("File Hash Checker", self.create_hash_checker_tool),
            ("Secure File Shredder", self.create_file_shredder_tool)
        ]
        
        self.create_tab_window("File & Data Security Tools", tools, '#27ae60')
            
            
    def open_forensics_category(self):
        """Open Cyber Forensics & Analysis Tools category"""
        tools = [
            ("File Metadata Extractor", self.create_metadata_extractor_tool),
            ("Image EXIF Viewer", self.create_exif_viewer_tool),
            ("File Integrity Checker", self.create_integrity_checker_tool),
            ("Log File Analyzer", self.create_log_analyzer_tool),
            ("Email Header Analyzer", self.create_email_header_analyzer_tool)
        ]
        
        self.create_tab_window("Cyber Forensics & Analysis Tools", tools, '#d68910')
    
    # ======================
    # ENCRYPTION TOOLS
    # ======================
    
    def create_cipher_analysis_tool(self, parent):
        """Cipher Analysis & Comparison Tool"""
        tk.Label(parent, text="Cipher Analysis & Comparison", font=('Arial', 18, 'bold'), fg='#2c3e50').pack(pady=15)
        tk.Label(parent, text="Comprehensive comparison of encryption methods by security, speed, and use cases", 
                font=('Arial', 11, 'italic'), fg='#7f8c8d').pack(pady=5)
        
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        comparison_frame = tk.Frame(notebook, bg='white')
        notebook.add(comparison_frame, text="📊 Comparison Table")
        
        canvas = tk.Canvas(comparison_frame, bg='white')
        scrollbar = tk.Scrollbar(comparison_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        cipher_data = [
            {"name": "AES-256", "type": "Symmetric", "time": "O(n)", "security": "⭐⭐⭐⭐⭐", "rating": "10/10", 
             "crack": "Virtually impossible (2^256 combinations)", "use": "Modern encryption standard"},
            {"name": "RSA-2048", "type": "Asymmetric", "time": "O(n³)", "security": "⭐⭐⭐⭐⭐", "rating": "10/10", 
             "crack": "Extremely hard (requires factoring large primes)", "use": "Secure key exchange, digital signatures"},
            {"name": "SHA-256", "type": "Hash", "time": "O(n)", "security": "⭐⭐⭐⭐⭐", "rating": "10/10", 
             "crack": "Impossible (one-way function)", "use": "Data integrity, password hashing"},
            {"name": "Playfair", "type": "Classical", "time": "O(n)", "security": "⭐⭐", "rating": "3/10", 
             "crack": "Moderate (frequency analysis of digraphs)", "use": "Historical, educational"},
            {"name": "Vigenère", "type": "Classical", "time": "O(n)", "security": "⭐⭐", "rating": "2/10", 
             "crack": "Easy (Kasiski examination, frequency analysis)", "use": "Educational purposes"},
            {"name": "Hill Cipher", "type": "Classical", "time": "O(n)", "security": "⭐⭐", "rating": "4/10", 
             "crack": "Moderate (known-plaintext attack)", "use": "Educational, demonstrates linear algebra"},
            {"name": "Affine", "type": "Classical", "time": "O(n)", "security": "⭐", "rating": "2/10", 
             "crack": "Very easy (only 312 possible keys)", "use": "Educational only"},
            {"name": "Multiplicative", "type": "Classical", "time": "O(n)", "security": "⭐", "rating": "2/10", 
             "crack": "Very easy (limited keyspace)", "use": "Educational, demonstrates modular arithmetic"},
            {"name": "Autokey", "type": "Classical", "time": "O(n)", "security": "⭐⭐", "rating": "3/10", 
             "crack": "Moderate (better than Vigenère)", "use": "Historical, educational"},
            {"name": "Caesar", "type": "Classical", "time": "O(n)", "security": "⭐", "rating": "1/10", 
             "crack": "Trivial (only 25 possible shifts)", "use": "Introduction to cryptography"},
            {"name": "Rail Fence", "type": "Transposition", "time": "O(n)", "security": "⭐⭐", "rating": "3/10", 
             "crack": "Moderate (anagramming, pattern analysis)", "use": "Educational, classical cryptography"},
            {"name": "Columnar", "type": "Transposition", "time": "O(n)", "security": "⭐⭐", "rating": "3/10", 
             "crack": "Moderate (anagramming, key recovery)", "use": "Military (historical), educational"},
            {"name": "Key Transposition", "type": "Transposition", "time": "O(n)", "security": "⭐⭐", "rating": "3/10", 
             "crack": "Moderate (pattern analysis)", "use": "Educational, demonstrates transposition"},
            {"name": "Morse Code", "type": "Encoding", "time": "O(n)", "security": "☆", "rating": "0/10", 
             "crack": "Instant (public encoding, not encryption)", "use": "Telegraph, radio, not security"},
            {"name": "Base64", "type": "Encoding", "time": "O(n)", "security": "☆", "rating": "0/10", 
             "crack": "Instant (not encryption, just encoding)", "use": "Data transmission, not security"},
        ]
        
        header_frame = tk.Frame(scrollable_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        headers = ["Cipher", "Type", "Time Complexity", "Security", "Rating", "Difficulty to Crack", "Best Use Case"]
        widths = [15, 12, 15, 10, 8, 35, 30]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            tk.Label(header_frame, text=header, font=('Arial', 10, 'bold'), 
                    bg='#34495e', fg='white', width=width, anchor='w', padx=5).grid(row=0, column=i, sticky='ew', padx=1, pady=5)
        
        for idx, cipher in enumerate(cipher_data):
            row_color = '#ecf0f1' if idx % 2 == 0 else 'white'
            row_frame = tk.Frame(scrollable_frame, bg=row_color, relief=tk.FLAT)
            row_frame.pack(fill=tk.X, pady=1)
            
            values = [cipher["name"], cipher["type"], cipher["time"], cipher["security"], 
                     cipher["rating"], cipher["crack"], cipher["use"]]
            
            for i, (value, width) in enumerate(zip(values, widths)):
                tk.Label(row_frame, text=value, font=('Arial', 9), 
                        bg=row_color, width=width, anchor='w', padx=5).grid(row=0, column=i, sticky='ew', padx=1, pady=8)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        recommendations_frame = tk.Frame(notebook, bg='white')
        notebook.add(recommendations_frame, text="💡 Recommendations")
        
        rec_text = scrolledtext.ScrolledText(recommendations_frame, wrap=tk.WORD, font=('Arial', 11), 
                                             bg='#f8f9fa', fg='#2c3e50', padx=20, pady=20)
        rec_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        recommendations = """
🔐 CIPHER RECOMMENDATIONS BY SECURITY LEVEL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 TIER 1 - PRODUCTION USE (Military-Grade Security)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. AES-256 - BEST FOR: File encryption, VPNs, WiFi security
   ✓ Speed: VERY FAST (hardware acceleration available)
   ✓ Security: Virtually unbreakable (2^256 key combinations)
   ✓ Time to crack: Billions of years with current technology
   ✓ Used by: US Government, financial institutions, secure messaging apps

2. RSA-2048 - BEST FOR: Secure communications, key exchange, digital signatures
   ✓ Speed: SLOWER than AES (good for small data)
   ✓ Security: Extremely high (based on factoring large prime numbers)
   ✓ Time to crack: Thousands of years
   ✓ Used by: HTTPS/SSL, PGP email encryption, SSH, cryptocurrency

3. SHA-256 - BEST FOR: Password storage, data integrity, blockchain
   ✓ Speed: FAST
   ✓ Security: One-way function (cannot be reversed)
   ✓ Collision resistance: Virtually collision-free
   ✓ Used by: Bitcoin, Git, password databases, file verification

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ TIER 2 - HISTORICAL/EDUCATIONAL (Weak Security)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. Playfair Cipher - EDUCATIONAL USE ONLY
   ✓ Speed: Fast
   ✗ Security: Weak (vulnerable to frequency analysis)
   ✗ Time to crack: Minutes to hours with computer analysis
   • Used in: WWI/WWII, now only for teaching cryptography

5. Hill Cipher - EDUCATIONAL USE ONLY
   ✓ Speed: Fast
   ✗ Security: Moderate (vulnerable to known-plaintext attacks)
   ✗ Time to crack: Hours
   • Good for: Teaching linear algebra in cryptography

6. Vigenère Cipher - EDUCATIONAL USE ONLY
   ✓ Speed: Fast
   ✗ Security: Weak (Kasiski examination breaks it easily)
   ✗ Time to crack: Minutes with proper tools
   • Historical significance: "Indecipherable cipher" (broken in 1863)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ TIER 3 - INSECURE (Never Use for Real Security)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. Caesar Cipher - EDUCATIONAL ONLY
   ✗ Security: EXTREMELY WEAK (only 25 possible keys)
   ✗ Time to crack: Seconds
   • Use for: Learning basic cryptography concepts

8. Affine Cipher - EDUCATIONAL ONLY
   ✗ Security: VERY WEAK (only 312 possible keys)
   ✗ Time to crack: Seconds
   • Use for: Understanding modular arithmetic

9. Base64 - NOT ENCRYPTION!
   ✗ Security: NONE (this is encoding, not encryption)
   ✗ Time to "crack": Instant (no key needed)
   • Use for: Data transmission, URLs, email - NOT security

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PERFORMANCE COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Encryption Speed (1 MB of data):
🥇 AES-256:        ~5 milliseconds (FASTEST)
🥈 Classical:      ~10-50 milliseconds
🥉 RSA-2048:       ~200 milliseconds (slowest, but used differently)

Security vs Speed Trade-off:
• AES-256: Perfect balance of speed and security
• RSA: Slower, but needed for key exchange
• Classical ciphers: Fast but INSECURE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PRACTICAL RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For REAL SECURITY:
  ✓ Use AES-256 for encrypting files, messages, or data
  ✓ Use RSA-2048+ for secure key exchange
  ✓ Use SHA-256 for password hashing (with salt!)
  ✓ NEVER use classical ciphers in production

For LEARNING:
  ✓ Start with Caesar to understand basics
  ✓ Progress to Vigenère for polyalphabetic concepts
  ✓ Study Hill cipher for mathematical cryptography
  ✓ Finally learn modern ciphers (AES, RSA)

Why Modern Ciphers Win:
  1. Mathematically proven security
  2. Peer-reviewed by cryptography experts
  3. Resistant to all known attacks
  4. Hardware-accelerated (very fast)
  5. Standard in all secure systems

⚠️ NEVER roll your own crypto - use AES-256 or RSA-2048+ for real security!
"""
        
        rec_text.insert("1.0", recommendations)
        rec_text.config(state='disabled')
        
        complexity_frame = tk.Frame(notebook, bg='white')
        notebook.add(complexity_frame, text="⚡ Time Complexity Details")
        
        comp_text = scrolledtext.ScrolledText(complexity_frame, wrap=tk.WORD, font=('Courier', 10), 
                                              bg='#f8f9fa', fg='#2c3e50', padx=20, pady=20)
        comp_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        complexity_info = """
⚡ TIME COMPLEXITY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 NOTATION EXPLANATION:
  n = length of plaintext
  k = key size in bits
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODERN CIPHERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AES-256:
  Encryption:     O(n)    - Linear time (very fast!)
  Decryption:     O(n)    - Linear time
  Brute Force:    O(2^256) - Effectively impossible
  Note: Hardware-accelerated on modern CPUs (AES-NI instruction set)

RSA-2048:
  Key Generation: O(k³)   - Expensive one-time cost
  Encryption:     O(k²)   - Moderately fast
  Decryption:     O(k³)   - Slower (uses private key)
  Brute Force:    O(2^2048) - Computationally infeasible
  Note: Used for small data (typically to encrypt AES keys)

SHA-256:
  Hashing:        O(n)    - Linear time (very fast)
  Brute Force:    O(2^256) - Impossible to reverse
  Collision:      O(2^128) - Practically collision-free

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLASSICAL CIPHERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Caesar Cipher:
  Encryption:     O(n)    - Very fast
  Brute Force:    O(25)   - Only 25 possible shifts!
  Attack Time:    Seconds

Vigenère Cipher:
  Encryption:     O(n)    - Fast
  Brute Force:    O(26^m) where m = key length
  Smart Attack:   O(n)    - Kasiski examination breaks it quickly
  Attack Time:    Minutes

Playfair Cipher:
  Encryption:     O(n)    - Fast
  Brute Force:    O(26!) = ~4×10^26 combinations
  Smart Attack:   Much faster with frequency analysis
  Attack Time:    Hours

Hill Cipher (2x2):
  Encryption:     O(n)    - Matrix multiplication
  Brute Force:    Large keyspace
  Known-Plaintext: O(n)   - Easy to break with 4 known pairs
  Attack Time:    Hours

Affine Cipher:
  Encryption:     O(n)    - Fast
  Brute Force:    O(312)  - Only 312 possible keys!
  Attack Time:    Seconds

Transposition Ciphers:
  Encryption:     O(n)    - Fast (just rearranging)
  Brute Force:    O(k!)   - Depends on key length
  Pattern Attack: Faster with anagramming
  Attack Time:    Minutes to hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ WHY MODERN CIPHERS ARE BETTER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EXPONENTIAL SECURITY:
   Classical: O(26^m) or O(n!) - Still breakable
   Modern:    O(2^256) - Impossible with current/future technology

2. SPEED WITH SECURITY:
   AES-256: Linear time O(n) + Hardware acceleration = VERY FAST
   Classical: Linear time O(n) but VERY WEAK security

3. MATHEMATICAL FOUNDATION:
   Modern ciphers: Based on hard mathematical problems
   Classical: Based on letter substitution/transposition (pattern-based)

4. RESISTANCE TO ATTACKS:
   Modern: Immune to frequency analysis, pattern matching, etc.
   Classical: Vulnerable to statistical analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 KEY TAKEAWAY:
   "Computational complexity doesn't always equal security!"
   
   Caesar is O(n) fast, but only 25 keys = INSECURE
   AES is O(n) fast, with 2^256 keys = UNBREAKABLE
   
   Modern ciphers achieve BOTH speed AND security! 🏆
"""
        
        comp_text.insert("1.0", complexity_info)
        comp_text.config(state='disabled')
    
    def create_caesar_cipher_tool(self, parent):
        """Caesar Cipher tool"""
        tk.Label(parent, text="Caesar Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Simple substitution cipher - shifts each letter by a fixed number", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Educational purposes, simple text obfuscation (very easy to crack)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Shift (0-25):").pack()
        shift_var = tk.StringVar(value="3")
        tk.Entry(parent, textvariable=shift_var, width=10).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip()
            try:
                shift = int(shift_var.get()) % 26
                result = ""
                for char in text:
                    if char.isalpha():
                        base = ord('A') if char.isupper() else ord('a')
                        result += chr((ord(char) - base + shift) % 26 + base)
                    else:
                        result += char
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid shift value")
        
        def decrypt():
            text = text_input.get("1.0", tk.END).strip()
            try:
                shift = int(shift_var.get()) % 26
                result = ""
                for char in text:
                    if char.isalpha():
                        base = ord('A') if char.isupper() else ord('a')
                        result += chr((ord(char) - base - shift) % 26 + base)
                    else:
                        result += char
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid shift value")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", command=decrypt, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_vigenere_cipher_tool(self, parent):
        """Vigenère Cipher tool"""
        tk.Label(parent, text="Vigenère Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Polyalphabetic cipher using a keyword for multiple Caesar shifts", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Historical encryption, learning cryptography (vulnerable to frequency analysis)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Key:").pack()
        key_var = tk.StringVar(value="KEY")
        tk.Entry(parent, textvariable=key_var, width=30).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def process(encrypt_mode=True):
            text = text_input.get("1.0", tk.END).strip()
            key = key_var.get().upper()
            if not key:
                messagebox.showerror("Error", "Key cannot be empty")
                return
            
            key = ''.join(filter(str.isalpha, key))
            result = ""
            key_index = 0
            
            for char in text:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    key_shift = ord(key[key_index % len(key)]) - ord('A')
                    if not encrypt_mode:
                        key_shift = -key_shift
                    result += chr((ord(char) - base + key_shift) % 26 + base)
                    key_index += 1
                else:
                    result += char
            
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=lambda: process(True), bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", command=lambda: process(False), bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_multiplicative_cipher_tool(self, parent):
        """Multiplicative Cipher tool"""
        tk.Label(parent, text="Multiplicative Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Multiplies each letter position by a key (must be coprime with 26)", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Educational, demonstrates modular arithmetic (weak security)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Key (must be coprime with 26, e.g., 5, 7, 11):").pack()
        key_var = tk.StringVar(value="5")
        tk.Entry(parent, textvariable=key_var, width=10).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def mod_inverse(a, m):
            for i in range(1, m):
                if (a * i) % m == 1:
                    return i
            return None
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip().upper()
            try:
                key = int(key_var.get())
                if math.gcd(key, 26) != 1:
                    messagebox.showerror("Error", "Key must be coprime with 26")
                    return
                
                result = ""
                for char in text:
                    if char.isalpha():
                        result += chr((key * (ord(char) - ord('A'))) % 26 + ord('A'))
                    else:
                        result += char
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid key value")
        
        def decrypt():
            text = text_input.get("1.0", tk.END).strip().upper()
            try:
                key = int(key_var.get())
                inv_key = mod_inverse(key, 26)
                if inv_key is None:
                    messagebox.showerror("Error", "Key must be coprime with 26")
                    return
                
                result = ""
                for char in text:
                    if char.isalpha():
                        result += chr((inv_key * (ord(char) - ord('A'))) % 26 + ord('A'))
                    else:
                        result += char
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid key value")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", command=decrypt, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_playfair_cipher_tool(self, parent):
        """Playfair Cipher tool"""
        tk.Label(parent, text="Playfair Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Digraph substitution cipher using 5x5 matrix from a keyword", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Military communications (WWI/WWII), harder to break than simple ciphers", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Key:").pack()
        key_var = tk.StringVar(value="KEYWORD")
        tk.Entry(parent, textvariable=key_var, width=30).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def create_playfair_matrix(key):
            key = key.upper().replace('J', 'I')
            matrix = []
            used = set()
            
            for char in key:
                if char.isalpha() and char not in used:
                    matrix.append(char)
                    used.add(char)
            
            for char in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
                if char not in used:
                    matrix.append(char)
            
            return [matrix[i:i+5] for i in range(0, 25, 5)]
        
        def find_position(matrix, char):
            for i, row in enumerate(matrix):
                if char in row:
                    return i, row.index(char)
            return None, None
        
        def process_playfair(text, key, encrypt=True):
            matrix = create_playfair_matrix(key)
            text = text.upper().replace('J', 'I')
            text = ''.join(filter(str.isalpha, text))
            
            pairs = []
            i = 0
            while i < len(text):
                a = text[i]
                b = text[i+1] if i+1 < len(text) else 'X'
                if a == b:
                    b = 'X'
                    i += 1
                else:
                    i += 2
                pairs.append((a, b))
            
            result = ""
            for a, b in pairs:
                row1, col1 = find_position(matrix, a)
                row2, col2 = find_position(matrix, b)
                
                if row1 == row2:
                    if encrypt:
                        result += matrix[row1][(col1 + 1) % 5]
                        result += matrix[row2][(col2 + 1) % 5]
                    else:
                        result += matrix[row1][(col1 - 1) % 5]
                        result += matrix[row2][(col2 - 1) % 5]
                elif col1 == col2:
                    if encrypt:
                        result += matrix[(row1 + 1) % 5][col1]
                        result += matrix[(row2 + 1) % 5][col2]
                    else:
                        result += matrix[(row1 - 1) % 5][col1]
                        result += matrix[(row2 - 1) % 5][col2]
                else:
                    result += matrix[row1][col2]
                    result += matrix[row2][col1]
            
            return result
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", 
                 command=lambda: result_text.delete("1.0", tk.END) or 
                 result_text.insert("1.0", process_playfair(text_input.get("1.0", tk.END), key_var.get(), True)),
                 bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", 
                 command=lambda: result_text.delete("1.0", tk.END) or 
                 result_text.insert("1.0", process_playfair(text_input.get("1.0", tk.END), key_var.get(), False)),
                 bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_rsa_tool(self, parent):
        """RSA Encryption tool"""
        tk.Label(parent, text="RSA Encryption (Asymmetric)", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Public-key cryptography - different keys for encryption/decryption", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Secure communications, digital signatures, HTTPS (very secure with large keys)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        keys_frame = tk.Frame(parent)
        keys_frame.pack(pady=10)
        
        self.rsa_private_key = None
        self.rsa_public_key = None
        
        def generate_keys():
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.rsa_public_key = self.rsa_private_key.public_key()
            messagebox.showinfo("Success", "RSA Key Pair Generated!")
        
        tk.Button(keys_frame, text="Generate Key Pair", command=generate_keys, 
                 bg='#3498db', fg='white', width=20).pack()
        
        tk.Label(parent, text="Enter Text to Encrypt:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encrypt():
            if not self.rsa_public_key:
                messagebox.showerror("Error", "Please generate keys first")
                return
            
            text = text_input.get("1.0", tk.END).strip()
            encrypted = self.rsa_public_key.encrypt(
                text.encode(),
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", base64.b64encode(encrypted).decode())
        
        def decrypt():
            if not self.rsa_private_key:
                messagebox.showerror("Error", "Please generate keys first")
                return
            
            try:
                encrypted_data = base64.b64decode(text_input.get("1.0", tk.END).strip())
                decrypted = self.rsa_private_key.decrypt(
                    encrypted_data,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", decrypted.decode())
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", command=decrypt, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_affine_cipher_tool(self, parent):
        """Affine Cipher tool"""
        tk.Label(parent, text="Affine Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Combination of multiplicative and additive ciphers (ax + b mod 26)", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Educational, demonstrates combining cipher techniques (weak security)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        params_frame = tk.Frame(parent)
        params_frame.pack(pady=5)
        
        tk.Label(params_frame, text="a (coprime with 26):").pack(side=tk.LEFT)
        a_var = tk.StringVar(value="5")
        tk.Entry(params_frame, textvariable=a_var, width=5).pack(side=tk.LEFT, padx=5)
        
        tk.Label(params_frame, text="b:").pack(side=tk.LEFT)
        b_var = tk.StringVar(value="8")
        tk.Entry(params_frame, textvariable=b_var, width=5).pack(side=tk.LEFT, padx=5)
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def mod_inverse(a, m):
            for i in range(1, m):
                if (a * i) % m == 1:
                    return i
            return None
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip().upper()
            try:
                a = int(a_var.get())
                b = int(b_var.get())
                if math.gcd(a, 26) != 1:
                    messagebox.showerror("Error", "a must be coprime with 26")
                    return
                
                result = ""
                for char in text:
                    if char.isalpha():
                        result += chr((a * (ord(char) - ord('A')) + b) % 26 + ord('A'))
                    else:
                        result += char
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid parameter values")
        
        def decrypt():
            text = text_input.get("1.0", tk.END).strip().upper()
            try:
                a = int(a_var.get())
                b = int(b_var.get())
                a_inv = mod_inverse(a, 26)
                if a_inv is None:
                    messagebox.showerror("Error", "a must be coprime with 26")
                    return
                
                result = ""
                for char in text:
                    if char.isalpha():
                        result += chr((a_inv * (ord(char) - ord('A') - b)) % 26 + ord('A'))
                    else:
                        result += char
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid parameter values")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", command=decrypt, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_autokey_cipher_tool(self, parent):
        """Autokey Cipher tool"""
        tk.Label(parent, text="Autokey Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Vigenère variant using message itself as part of the key", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Historical encryption, more secure than Vigenère (still vulnerable to analysis)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Key:").pack()
        key_var = tk.StringVar(value="KEY")
        tk.Entry(parent, textvariable=key_var, width=30).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip().upper()
            key = key_var.get().upper()
            text_clean = ''.join(filter(str.isalpha, text))
            key_stream = key + text_clean
            
            result = ""
            key_index = 0
            for char in text:
                if char.isalpha():
                    shift = ord(key_stream[key_index]) - ord('A')
                    result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                    key_index += 1
                else:
                    result += char
            
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
        
        def decrypt():
            text = text_input.get("1.0", tk.END).strip().upper()
            key = key_var.get().upper()
            key_stream = list(key)
            
            result = ""
            key_index = 0
            for char in text:
                if char.isalpha():
                    shift = ord(key_stream[key_index]) - ord('A')
                    decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                    result += decrypted_char
                    key_stream.append(decrypted_char)
                    key_index += 1
                else:
                    result += char
            
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt", command=decrypt, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_hill_cipher_tool(self, parent):
        """Hill Cipher (2x2 Matrix) tool"""
        tk.Label(parent, text="Hill Cipher (2x2 Matrix)", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Matrix-based substitution cipher using linear algebra", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Educational (cryptography/math), resistant to frequency analysis", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text (even length):").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Key Matrix (2x2, format: a,b,c,d):").pack()
        key_var = tk.StringVar(value="3,3,2,5")
        tk.Entry(parent, textvariable=key_var, width=30).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def matrix_mult_mod(matrix, vector):
            result = [0, 0]
            result[0] = (matrix[0][0] * vector[0] + matrix[0][1] * vector[1]) % 26
            result[1] = (matrix[1][0] * vector[0] + matrix[1][1] * vector[1]) % 26
            return result
        
        def mod_inverse(a, m):
            for i in range(1, m):
                if (a * i) % m == 1:
                    return i
            return None
        
        def encrypt():
            text = ''.join(filter(str.isalpha, text_input.get("1.0", tk.END).strip().upper()))
            if len(text) % 2 != 0:
                text += 'X'
            
            try:
                key_values = [int(x.strip()) for x in key_var.get().split(',')]
                if len(key_values) != 4:
                    raise ValueError("Need 4 values for 2x2 matrix")
                matrix = [[key_values[0], key_values[1]], [key_values[2], key_values[3]]]
                
                result = ""
                for i in range(0, len(text), 2):
                    vector = [ord(text[i]) - ord('A'), ord(text[i+1]) - ord('A')]
                    encrypted = matrix_mult_mod(matrix, vector)
                    result += chr(encrypted[0] + ord('A')) + chr(encrypted[1] + ord('A'))
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except Exception as e:
                messagebox.showerror("Error", f"Encryption failed: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Label(btn_frame, text="(Decryption requires inverse matrix)", font=('Arial', 8, 'italic')).pack(side=tk.LEFT, padx=5)
    
    def create_columnar_transposition_tool(self, parent):
        """Columnar Transposition Cipher tool"""
        tk.Label(parent, text="Columnar Transposition Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Rearranges characters in columns based on keyword order", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Military communications, often combined with substitution ciphers", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Key (e.g., ZEBRAS):").pack()
        key_var = tk.StringVar(value="ZEBRAS")
        tk.Entry(parent, textvariable=key_var, width=30).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip().replace(' ', '')
            key = key_var.get()
            
            key_order = sorted(list(enumerate(key)), key=lambda x: x[1])
            num_cols = len(key)
            num_rows = math.ceil(len(text) / num_cols)
            
            grid = ['' for _ in range(num_cols)]
            for i, char in enumerate(text):
                grid[i % num_cols] += char
            
            result = ""
            for idx, _ in key_order:
                result += grid[idx]
            
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack()
    
    def create_morse_code_tool(self, parent):
        """Morse Code Translator tool"""
        tk.Label(parent, text="Morse Code Translator", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Converts text to/from dots and dashes for telegraph communication", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Telegraph, radio, emergency signals (not encryption, just encoding)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': '/'
        }
        
        reverse_morse = {v: k for k, v in morse_dict.items()}
        
        tk.Label(parent, text="Enter Text or Morse Code:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def to_morse():
            text = text_input.get("1.0", tk.END).strip().upper()
            result = ' '.join(morse_dict.get(char, '') for char in text)
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
        
        def from_morse():
            morse = text_input.get("1.0", tk.END).strip()
            result = ''.join(reverse_morse.get(code, '') for code in morse.split())
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Text to Morse", command=to_morse, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Morse to Text", command=from_morse, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_base64_tool(self, parent):
        """Base64 Encoder/Decoder tool"""
        tk.Label(parent, text="Base64 Encoder/Decoder", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Encodes binary data as ASCII text using 64 printable characters", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Email attachments, URLs, data transmission (NOT encryption, easily decoded)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text or Base64:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encode():
            text = text_input.get("1.0", tk.END).strip()
            encoded = base64.b64encode(text.encode()).decode()
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", encoded)
        
        def decode():
            try:
                text = text_input.get("1.0", tk.END).strip()
                decoded = base64.b64decode(text).decode()
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", decoded)
            except Exception as e:
                messagebox.showerror("Error", f"Decoding failed: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encode", command=encode, bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decode", command=decode, bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_transposition_cipher_tool(self, parent):
        """Transposition Cipher tool"""
        tk.Label(parent, text="Transposition Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Rail fence cipher - writes text in zigzag pattern across rails", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Educational, classical cryptography (moderate security)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Number of Rails:").pack()
        rails_var = tk.StringVar(value="3")
        tk.Entry(parent, textvariable=rails_var, width=10).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip()
            try:
                rails = int(rails_var.get())
                fence = [[] for _ in range(rails)]
                rail = 0
                direction = 1
                
                for char in text:
                    fence[rail].append(char)
                    rail += direction
                    if rail == 0 or rail == rails - 1:
                        direction *= -1
                
                result = ''.join([''.join(rail) for rail in fence])
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except ValueError:
                messagebox.showerror("Error", "Invalid number of rails")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt (Rail Fence)", command=encrypt, bg='#27ae60', fg='white', width=20).pack()
    
    def create_key_transposition_cipher_tool(self, parent):
        """Key Transposition Cipher tool"""
        tk.Label(parent, text="Key Transposition Cipher", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Rearranges text in grid using numeric key sequence", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Educational, demonstrates transposition techniques", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=(0,10))
        
        tk.Label(parent, text="Enter Text:").pack()
        text_input = scrolledtext.ScrolledText(parent, height=5, width=60)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Numeric Key (e.g., 3,1,4,2):").pack()
        key_var = tk.StringVar(value="3,1,4,2")
        tk.Entry(parent, textvariable=key_var, width=30).pack()
        
        result_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        result_text.pack(pady=10)
        
        def encrypt():
            text = text_input.get("1.0", tk.END).strip().replace(' ', '')
            try:
                key = [int(x.strip()) for x in key_var.get().split(',')]
                num_cols = len(key)
                num_rows = math.ceil(len(text) / num_cols)
                
                grid = []
                idx = 0
                for _ in range(num_rows):
                    row = []
                    for _ in range(num_cols):
                        if idx < len(text):
                            row.append(text[idx])
                            idx += 1
                        else:
                            row.append('X')
                    grid.append(row)
                
                result = ""
                for k in key:
                    col_idx = k - 1
                    for row in grid:
                        if col_idx < len(row):
                            result += row[col_idx]
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", result)
            except Exception as e:
                messagebox.showerror("Error", f"Encryption failed: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt", command=encrypt, bg='#27ae60', fg='white', width=15).pack()
    
    def create_sha256_tool(self, parent):
        """SHA-256 Hash Tool"""
        tk.Label(parent, text="SHA-256 Hash Tool", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: One-way cryptographic hash function - creates unique fingerprint of data", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Password storage, data integrity verification, blockchain, digital signatures (very secure, cannot be reversed)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=2)
        tk.Label(parent, text="(SHA-256 is a one-way hash function - cannot be decrypted)", 
                font=('Arial', 10, 'italic'), fg='gray').pack()
        
        tk.Label(parent, text="Enter Text to Hash:").pack(pady=(10, 0))
        text_input = scrolledtext.ScrolledText(parent, height=5, width=70)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="SHA-256 Hash Output:").pack(pady=(10, 0))
        hash_output = scrolledtext.ScrolledText(parent, height=3, width=70)
        hash_output.pack(pady=5)
        
        tk.Label(parent, text="Verification Hash (optional - for comparison):").pack(pady=(10, 0))
        verify_input = scrolledtext.ScrolledText(parent, height=2, width=70)
        verify_input.pack(pady=5)
        
        status_label = tk.Label(parent, text="", font=('Arial', 11, 'bold'))
        status_label.pack(pady=5)
        
        def compute_hash():
            text = text_input.get("1.0", tk.END).strip()
            if not text:
                messagebox.showerror("Error", "Please enter text to hash")
                return
            
            hash_value = hashlib.sha256(text.encode()).hexdigest()
            hash_output.delete("1.0", tk.END)
            hash_output.insert("1.0", hash_value)
            status_label.config(text="Hash generated successfully!", fg='green')
        
        def verify_hash():
            text = text_input.get("1.0", tk.END).strip()
            verify_hash_value = verify_input.get("1.0", tk.END).strip()
            
            if not text or not verify_hash_value:
                messagebox.showerror("Error", "Please enter both text and verification hash")
                return
            
            computed_hash = hashlib.sha256(text.encode()).hexdigest()
            
            if computed_hash.lower() == verify_hash_value.lower():
                status_label.config(text="✓ MATCH - Hashes are identical!", fg='green')
                messagebox.showinfo("Verification Success", "The hashes match! The text is verified.")
            else:
                status_label.config(text="✗ NO MATCH - Hashes are different!", fg='red')
                messagebox.showwarning("Verification Failed", "The hashes do NOT match! The text may have been modified.")
        
        def copy_hash():
            hash_value = hash_output.get("1.0", tk.END).strip()
            if hash_value:
                parent.clipboard_clear()
                parent.clipboard_append(hash_value)
                status_label.config(text="Hash copied to clipboard!", fg='blue')
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Generate Hash", command=compute_hash, 
                 bg='#3498db', fg='white', width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Verify Hash", command=verify_hash, 
                 bg='#27ae60', fg='white', width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Copy Hash", command=copy_hash, 
                 bg='#95a5a6', fg='white', width=15, height=2).pack(side=tk.LEFT, padx=5)
    
    def create_rsa_advanced_tool(self, parent):
        """Advanced RSA Encryption/Decryption Tool"""
        tk.Label(parent, text="RSA Encryption (Advanced)", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Asymmetric 2048-bit encryption with public/private key pairs and OAEP padding", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: Secure messaging, digital certificates, key exchange, HTTPS/SSL (industry-standard security)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=2)
        tk.Label(parent, text="Public Key Encryption - Encrypt with public key, decrypt with private key", 
                font=('Arial', 10, 'italic'), fg='gray').pack()
        
        rsa_private_key = [None]
        rsa_public_key = [None]
        
        keys_container = tk.Frame(parent)
        keys_container.pack(pady=10, fill=tk.X, padx=10)
        
        left_keys = tk.Frame(keys_container)
        left_keys.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(left_keys, text="Public Key:", font=('Arial', 11, 'bold')).pack()
        public_key_text = scrolledtext.ScrolledText(left_keys, height=8, width=50, wrap=tk.WORD)
        public_key_text.pack(pady=5)
        
        right_keys = tk.Frame(keys_container)
        right_keys.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(right_keys, text="Private Key:", font=('Arial', 11, 'bold')).pack()
        private_key_text = scrolledtext.ScrolledText(right_keys, height=8, width=50, wrap=tk.WORD)
        private_key_text.pack(pady=5)
        
        def generate_keys():
            rsa_private_key[0] = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            rsa_public_key[0] = rsa_private_key[0].public_key()
            
            public_pem = rsa_public_key[0].public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            
            private_pem = rsa_private_key[0].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            public_key_text.delete("1.0", tk.END)
            public_key_text.insert("1.0", public_pem)
            
            private_key_text.delete("1.0", tk.END)
            private_key_text.insert("1.0", private_pem)
            
            messagebox.showinfo("Success", "RSA Key Pair (2048-bit) Generated Successfully!")
        
        key_btn_frame = tk.Frame(parent)
        key_btn_frame.pack(pady=10)
        tk.Button(key_btn_frame, text="Generate New Key Pair (2048-bit)", command=generate_keys, 
                 bg='#3498db', fg='white', width=30, height=2, font=('Arial', 11, 'bold')).pack()
        
        tk.Label(parent, text="Text to Encrypt/Decrypt:", font=('Arial', 11, 'bold')).pack(pady=(15, 0))
        text_input = scrolledtext.ScrolledText(parent, height=5, width=80)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Result:", font=('Arial', 11, 'bold')).pack(pady=(10, 0))
        result_text = scrolledtext.ScrolledText(parent, height=6, width=80)
        result_text.pack(pady=5)
        
        def encrypt():
            if not rsa_public_key[0]:
                messagebox.showerror("Error", "Please generate keys first!")
                return
            
            text = text_input.get("1.0", tk.END).strip()
            if not text:
                messagebox.showerror("Error", "Please enter text to encrypt")
                return
            
            try:
                encrypted = rsa_public_key[0].encrypt(
                    text.encode(),
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                encrypted_b64 = base64.b64encode(encrypted).decode()
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", encrypted_b64)
                messagebox.showinfo("Success", "Text encrypted successfully with public key!")
            except Exception as e:
                messagebox.showerror("Error", f"Encryption failed: {str(e)}")
        
        def decrypt():
            if not rsa_private_key[0]:
                messagebox.showerror("Error", "Please generate keys first!")
                return
            
            encrypted_text = text_input.get("1.0", tk.END).strip()
            if not encrypted_text:
                messagebox.showerror("Error", "Please enter encrypted text to decrypt")
                return
            
            try:
                encrypted_data = base64.b64decode(encrypted_text)
                decrypted = rsa_private_key[0].decrypt(
                    encrypted_data,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", decrypted.decode())
                messagebox.showinfo("Success", "Text decrypted successfully with private key!")
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {str(e)}")
        
        action_btn_frame = tk.Frame(parent)
        action_btn_frame.pack(pady=15)
        tk.Button(action_btn_frame, text="Encrypt with Public Key", command=encrypt, 
                 bg='#27ae60', fg='white', width=25, height=2, font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=10)
        tk.Button(action_btn_frame, text="Decrypt with Private Key", command=decrypt, 
                 bg='#e74c3c', fg='white', width=25, height=2, font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=10)
    
    def create_aes_tool(self, parent):
        """AES Encryption/Decryption Tool"""
        tk.Label(parent, text="AES-256 Encryption", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="📚 Purpose: Symmetric 256-bit block cipher - fast encryption with shared secret key", 
                font=('Arial', 10, 'italic'), fg='#2c3e50', wraplength=600).pack(pady=2)
        tk.Label(parent, text="🎯 Use Case: File encryption, VPNs, secure storage, WiFi security (WPA2/WPA3), government/military (extremely secure and fast)", 
                font=('Arial', 9), fg='#7f8c8d', wraplength=600).pack(pady=2)
        tk.Label(parent, text="Symmetric Encryption - Same key for encryption and decryption (AES-256-CBC)", 
                font=('Arial', 10, 'italic'), fg='gray').pack()
        
        aes_key = [None]
        aes_iv = [None]
        
        keys_frame = tk.Frame(parent)
        keys_frame.pack(pady=10, fill=tk.X, padx=10)
        
        tk.Label(keys_frame, text="AES Key (256-bit):", font=('Arial', 11, 'bold')).pack()
        key_text = scrolledtext.ScrolledText(keys_frame, height=3, width=80)
        key_text.pack(pady=5)
        
        tk.Label(keys_frame, text="Initialization Vector (IV):", font=('Arial', 11, 'bold')).pack()
        iv_text = scrolledtext.ScrolledText(keys_frame, height=2, width=80)
        iv_text.pack(pady=5)
        
        def generate_key():
            aes_key[0] = os.urandom(32)
            aes_iv[0] = os.urandom(16)
            
            key_b64 = base64.b64encode(aes_key[0]).decode()
            iv_b64 = base64.b64encode(aes_iv[0]).decode()
            
            key_text.delete("1.0", tk.END)
            key_text.insert("1.0", key_b64)
            
            iv_text.delete("1.0", tk.END)
            iv_text.insert("1.0", iv_b64)
            
            messagebox.showinfo("Success", "AES-256 Key and IV Generated!\n\nSave these to decrypt your data later.")
        
        def import_key():
            try:
                key_input = key_text.get("1.0", tk.END).strip()
                iv_input = iv_text.get("1.0", tk.END).strip()
                
                if not key_input or not iv_input:
                    messagebox.showerror("Error", "Please enter both key and IV")
                    return
                
                aes_key[0] = base64.b64decode(key_input)
                aes_iv[0] = base64.b64decode(iv_input)
                
                if len(aes_key[0]) != 32:
                    raise ValueError("Key must be 256 bits (32 bytes)")
                if len(aes_iv[0]) != 16:
                    raise ValueError("IV must be 128 bits (16 bytes)")
                
                messagebox.showinfo("Success", "Key and IV imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import key: {str(e)}")
        
        key_btn_frame = tk.Frame(parent)
        key_btn_frame.pack(pady=10)
        tk.Button(key_btn_frame, text="Generate New Key & IV", command=generate_key, 
                 bg='#3498db', fg='white', width=22, height=2, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(key_btn_frame, text="Import Existing Key & IV", command=import_key, 
                 bg='#95a5a6', fg='white', width=22, height=2, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Label(parent, text="Text to Encrypt/Decrypt:", font=('Arial', 11, 'bold')).pack(pady=(15, 0))
        text_input = scrolledtext.ScrolledText(parent, height=5, width=80)
        text_input.pack(pady=5)
        
        tk.Label(parent, text="Result:", font=('Arial', 11, 'bold')).pack(pady=(10, 0))
        result_text = scrolledtext.ScrolledText(parent, height=6, width=80)
        result_text.pack(pady=5)
        
        def encrypt():
            if not aes_key[0] or not aes_iv[0]:
                messagebox.showerror("Error", "Please generate or import a key first!")
                return
            
            text = text_input.get("1.0", tk.END).strip()
            if not text:
                messagebox.showerror("Error", "Please enter text to encrypt")
                return
            
            try:
                cipher = Cipher(algorithms.AES(aes_key[0]), modes.CBC(aes_iv[0]), backend=default_backend())
                encryptor = cipher.encryptor()
                
                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(text.encode()) + padder.finalize()
                
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                encrypted_b64 = base64.b64encode(encrypted_data).decode()
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", encrypted_b64)
                messagebox.showinfo("Success", "Text encrypted successfully with AES-256!")
            except Exception as e:
                messagebox.showerror("Error", f"Encryption failed: {str(e)}")
        
        def decrypt():
            if not aes_key[0] or not aes_iv[0]:
                messagebox.showerror("Error", "Please generate or import a key first!")
                return
            
            encrypted_text = text_input.get("1.0", tk.END).strip()
            if not encrypted_text:
                messagebox.showerror("Error", "Please enter encrypted text to decrypt")
                return
            
            try:
                encrypted_data = base64.b64decode(encrypted_text)
                
                cipher = Cipher(algorithms.AES(aes_key[0]), modes.CBC(aes_iv[0]), backend=default_backend())
                decryptor = cipher.decryptor()
                
                decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
                
                unpadder = padding.PKCS7(128).unpadder()
                decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", decrypted_data.decode())
                messagebox.showinfo("Success", "Text decrypted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {str(e)}\n\nMake sure you're using the correct key and IV.")
        
        action_btn_frame = tk.Frame(parent)
        action_btn_frame.pack(pady=15)
        tk.Button(action_btn_frame, text="Encrypt", command=encrypt, 
                 bg='#27ae60', fg='white', width=20, height=2, font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=10)
        tk.Button(action_btn_frame, text="Decrypt", command=decrypt, 
                 bg='#e74c3c', fg='white', width=20, height=2, font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=10)
    
    # ======================
    # PASSWORD TOOLS
    # ======================
    
    def create_password_generator_tool(self, parent):
        """Password Generator tool"""
        tk.Label(parent, text="Password Generator", font=('Arial', 16, 'bold')).pack(pady=10)
        
        options_frame = tk.Frame(parent)
        options_frame.pack(pady=10)
        
        tk.Label(options_frame, text="Length:").grid(row=0, column=0, sticky='w', pady=5)
        length_var = tk.StringVar(value="16")
        tk.Entry(options_frame, textvariable=length_var, width=10).grid(row=0, column=1, pady=5)
        
        uppercase_var = tk.BooleanVar(value=True)
        lowercase_var = tk.BooleanVar(value=True)
        digits_var = tk.BooleanVar(value=True)
        symbols_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=uppercase_var).grid(row=1, column=0, sticky='w')
        tk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=lowercase_var).grid(row=1, column=1, sticky='w')
        tk.Checkbutton(options_frame, text="Digits (0-9)", variable=digits_var).grid(row=2, column=0, sticky='w')
        tk.Checkbutton(options_frame, text="Symbols (!@#$...)", variable=symbols_var).grid(row=2, column=1, sticky='w')
        
        result_text = scrolledtext.ScrolledText(parent, height=3, width=60)
        result_text.pack(pady=10)
        
        def generate():
            try:
                length = int(length_var.get())
                if length < 1:
                    raise ValueError("Length must be positive")
                
                chars = ""
                if uppercase_var.get():
                    chars += string.ascii_uppercase
                if lowercase_var.get():
                    chars += string.ascii_lowercase
                if digits_var.get():
                    chars += string.digits
                if symbols_var.get():
                    chars += string.punctuation
                
                if not chars:
                    messagebox.showerror("Error", "Please select at least one character type")
                    return
                
                password = ''.join(random.choice(chars) for _ in range(length))
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", password)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid length: {str(e)}")
        
        tk.Button(parent, text="Generate Password", command=generate, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)
    
    def create_password_strength_tool(self, parent):
        """Password Strength Checker tool"""
        tk.Label(parent, text="Password Strength Checker", font=('Arial', 16, 'bold')).pack(pady=10)
        
        tk.Label(parent, text="Enter Password:").pack()
        password_var = tk.StringVar()
        tk.Entry(parent, textvariable=password_var, width=50, show='*').pack(pady=5)
        
        show_var = tk.BooleanVar()
        def toggle_show():
            entry = parent.children['!entry']
            entry.config(show='' if show_var.get() else '*')
        
        tk.Checkbutton(parent, text="Show Password", variable=show_var, command=toggle_show).pack()
        
        strength_label = tk.Label(parent, text="Strength: ", font=('Arial', 14, 'bold'))
        strength_label.pack(pady=10)
        
        feedback_text = scrolledtext.ScrolledText(parent, height=8, width=60)
        feedback_text.pack(pady=10)
        
        def check_strength():
            password = password_var.get()
            score = 0
            feedback = []
            
            if len(password) >= 8:
                score += 1
                feedback.append("✓ Length is 8 or more characters")
            else:
                feedback.append("✗ Password should be at least 8 characters")
            
            if len(password) >= 12:
                score += 1
                feedback.append("✓ Length is 12 or more characters (good)")
            
            if re.search(r'[A-Z]', password):
                score += 1
                feedback.append("✓ Contains uppercase letters")
            else:
                feedback.append("✗ Should contain uppercase letters")
            
            if re.search(r'[a-z]', password):
                score += 1
                feedback.append("✓ Contains lowercase letters")
            else:
                feedback.append("✗ Should contain lowercase letters")
            
            if re.search(r'\d', password):
                score += 1
                feedback.append("✓ Contains digits")
            else:
                feedback.append("✗ Should contain digits")
            
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                score += 1
                feedback.append("✓ Contains special characters")
            else:
                feedback.append("✗ Should contain special characters")
            
            strength_levels = {
                0: ("Very Weak", "red"),
                1: ("Very Weak", "red"),
                2: ("Weak", "orange"),
                3: ("Moderate", "yellow"),
                4: ("Strong", "lightgreen"),
                5: ("Strong", "green"),
                6: ("Very Strong", "darkgreen")
            }
            
            strength_text, color = strength_levels[score]
            strength_label.config(text=f"Strength: {strength_text} ({score}/6)", fg=color)
            
            feedback_text.delete("1.0", tk.END)
            feedback_text.insert("1.0", "\n".join(feedback))
        
        tk.Button(parent, text="Check Strength", command=check_strength, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)
    
    def create_password_manager_tool(self, parent):
        """Enhanced Password Manager tool with show/hide and copy features"""
        tk.Label(parent, text="Password Manager", font=('Arial', 16, 'bold')).pack(pady=10)
        
        input_frame = tk.Frame(parent, bg='white', relief=tk.GROOVE, bd=2)
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(input_frame, text="Add New Password:", font=('Arial', 12, 'bold'), bg='white').grid(row=0, column=0, columnspan=2, pady=10)
        
        tk.Label(input_frame, text="Service/Website:", bg='white').grid(row=1, column=0, sticky='w', pady=5, padx=10)
        service_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=service_var, width=35).grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="Username:", bg='white').grid(row=2, column=0, sticky='w', pady=5, padx=10)
        username_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=username_var, width=35).grid(row=2, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="Password:", bg='white').grid(row=3, column=0, sticky='w', pady=5, padx=10)
        pwd_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=pwd_var, width=35, show='*').grid(row=3, column=1, pady=5, padx=10)
        
        def add_password():
            service = service_var.get().strip()
            username = username_var.get().strip()
            password = pwd_var.get()
            
            if not service or not password:
                messagebox.showerror("Error", "Service and password are required")
                return
            
            self.password_storage[service] = {
                'username': username,
                'password': password,
                'added': datetime.now().isoformat()
            }
            self.save_password_storage()
            messagebox.showinfo("Success", f"Password for {service} saved!")
            update_password_list()
            service_var.set("")
            username_var.set("")
            pwd_var.set("")
        
        tk.Button(input_frame, text="Save Password", command=add_password, 
                 bg='#27ae60', fg='white', width=20, font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=15)
        
        search_frame = tk.Frame(parent, bg='white')
        search_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(search_frame, text="Search:", font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        def on_search(*args):
            update_password_list(search_var.get())
        
        search_var.trace('w', on_search)
        
        tk.Button(search_frame, text="Clear Search", command=lambda: search_var.set(""), 
                 bg='#95a5a6', fg='white', width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Label(parent, text="Stored Passwords:", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        passwords_container = tk.Frame(parent, bg='white')
        passwords_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(passwords_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(passwords_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def update_password_list(search_term=""):
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            if not self.password_storage:
                tk.Label(scrollable_frame, text="No passwords saved yet.", 
                        font=('Arial', 11, 'italic'), fg='#7f8c8d', bg='white').pack(pady=20)
                return
            
            filtered_passwords = {
                service: data for service, data in self.password_storage.items()
                if search_term.lower() in service.lower() or search_term.lower() in data.get('username', '').lower()
            }
            
            if not filtered_passwords:
                tk.Label(scrollable_frame, text=f"No passwords found matching '{search_term}'", 
                        font=('Arial', 11, 'italic'), fg='#7f8c8d', bg='white').pack(pady=20)
                return
            
            for idx, (service, data) in enumerate(sorted(filtered_passwords.items())):
                password_frame = tk.Frame(scrollable_frame, bg='#ecf0f1', relief=tk.RAISED, bd=1)
                password_frame.pack(fill=tk.X, pady=5, padx=5)
                
                info_frame = tk.Frame(password_frame, bg='#ecf0f1')
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                tk.Label(info_frame, text=f"Service: {service}", font=('Arial', 11, 'bold'), 
                        bg='#ecf0f1', fg='#2c3e50', anchor='w').pack(fill=tk.X)
                
                tk.Label(info_frame, text=f"Username: {data.get('username', 'N/A')}", 
                        font=('Arial', 10), bg='#ecf0f1', fg='#34495e', anchor='w').pack(fill=tk.X)
                
                password_display_frame = tk.Frame(info_frame, bg='#ecf0f1')
                password_display_frame.pack(fill=tk.X, pady=2)
                
                password_label = tk.Label(password_display_frame, text=f"Password: {'*' * 12}", 
                                        font=('Arial', 10), bg='#ecf0f1', fg='#34495e', anchor='w')
                password_label.pack(side=tk.LEFT)
                
                password_visible = [False]
                
                def toggle_password(lbl=password_label, pwd=data['password'], visible=password_visible):
                    if visible[0]:
                        lbl.config(text=f"Password: {'*' * len(pwd)}")
                        visible[0] = False
                    else:
                        lbl.config(text=f"Password: {pwd}")
                        visible[0] = True
                
                tk.Button(password_display_frame, text="Show/Hide", command=toggle_password,
                         bg='#3498db', fg='white', font=('Arial', 8), width=10).pack(side=tk.LEFT, padx=5)
                
                tk.Label(info_frame, text=f"Added: {data.get('added', 'Unknown')[:10]}", 
                        font=('Arial', 9), bg='#ecf0f1', fg='#7f8c8d', anchor='w').pack(fill=tk.X)
                
                buttons_frame = tk.Frame(password_frame, bg='#ecf0f1')
                buttons_frame.pack(side=tk.RIGHT, padx=10, pady=10)
                
                def copy_password(pwd=data['password']):
                    parent.clipboard_clear()
                    parent.clipboard_append(pwd)
                    messagebox.showinfo("Copied", "Password copied to clipboard!")
                
                def copy_username(uname=data.get('username', '')):
                    if uname:
                        parent.clipboard_clear()
                        parent.clipboard_append(uname)
                        messagebox.showinfo("Copied", "Username copied to clipboard!")
                
                def delete_entry(svc=service):
                    result = messagebox.askyesno("Confirm Delete", 
                        f"Are you sure you want to delete the password for '{svc}'?")
                    if result:
                        del self.password_storage[svc]
                        self.save_password_storage()
                        update_password_list(search_term)
                        messagebox.showinfo("Deleted", f"Password for '{svc}' deleted!")
                
                tk.Button(buttons_frame, text="Copy Password", command=copy_password,
                         bg='#27ae60', fg='white', font=('Arial', 9), width=14).pack(pady=2)
                
                tk.Button(buttons_frame, text="Copy Username", command=copy_username,
                         bg='#f39c12', fg='white', font=('Arial', 9), width=14).pack(pady=2)
                
                tk.Button(buttons_frame, text="Delete", command=delete_entry,
                         bg='#e74c3c', fg='white', font=('Arial', 9), width=14).pack(pady=2)
        
        update_password_list()
    
    def load_password_storage(self):
        """Load passwords from file"""
        try:
            if os.path.exists('passwords.json'):
                with open('passwords.json', 'r') as f:
                    self.password_storage = json.load(f)
        except Exception:
            self.password_storage = {}
    
    def save_password_storage(self):
        """Save passwords to file"""
        try:
            with open('passwords.json', 'w') as f:
                json.dump(self.password_storage, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save passwords: {str(e)}")
    
    # ======================
    # FILE SECURITY TOOLS
    # ======================
    
    def create_file_encryption_tool(self, parent):
        """File Encryption/Decryption tool"""
        tk.Label(parent, text="File Encryption/Decryption (AES)", font=('Arial', 16, 'bold')).pack(pady=10)
        
        file_path_var = tk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_file).pack(side=tk.LEFT)
        
        tk.Label(parent, text="Password:").pack()
        password_var = tk.StringVar()
        tk.Entry(parent, textvariable=password_var, width=40, show='*').pack(pady=5)
        
        status_label = tk.Label(parent, text="", font=('Arial', 10))
        status_label.pack(pady=10)
        
        def encrypt_file():
            file_path = file_path_var.get()
            password = password_var.get()
            
            if not file_path or not password:
                messagebox.showerror("Error", "Please select a file and enter a password")
                return
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                key = hashlib.sha256(password.encode()).digest()
                iv = os.urandom(16)
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                encryptor = cipher.encryptor()
                
                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(data) + padder.finalize()
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                
                output_path = file_path + '.encrypted'
                with open(output_path, 'wb') as f:
                    f.write(iv + encrypted_data)
                
                status_label.config(text=f"File encrypted: {output_path}", fg='green')
            except Exception as e:
                messagebox.showerror("Error", f"Encryption failed: {str(e)}")
        
        def decrypt_file():
            file_path = file_path_var.get()
            password = password_var.get()
            
            if not file_path or not password:
                messagebox.showerror("Error", "Please select a file and enter a password")
                return
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                iv = data[:16]
                encrypted_data = data[16:]
                
                key = hashlib.sha256(password.encode()).digest()
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                
                decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
                
                unpadder = padding.PKCS7(128).unpadder()
                decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
                
                output_path = file_path.replace('.encrypted', '.decrypted')
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data)
                
                status_label.config(text=f"File decrypted: {output_path}", fg='green')
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Encrypt File", command=encrypt_file, 
                 bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Decrypt File", command=decrypt_file, 
                 bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_steganography_tool(self, parent):
        """Steganography Tool (Text in PNG)"""
        tk.Label(parent, text="Steganography - Hide Text in PNG", font=('Arial', 16, 'bold')).pack(pady=10)
        
        image_path_var = tk.StringVar()
        
        def select_image():
            filename = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
            if filename:
                image_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="PNG Image:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=image_path_var, width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_image).pack(side=tk.LEFT)
        
        tk.Label(parent, text="Secret Message:").pack()
        message_text = scrolledtext.ScrolledText(parent, height=5, width=60)
        message_text.pack(pady=5)
        
        status_label = tk.Label(parent, text="", font=('Arial', 10))
        status_label.pack(pady=10)
        
        def hide_message():
            image_path = image_path_var.get()
            message = message_text.get("1.0", tk.END).strip()
            
            if not image_path or not message:
                messagebox.showerror("Error", "Please select an image and enter a message")
                return
            
            try:
                img = Image.open(image_path)
                encoded = img.copy()
                width, height = img.size
                
                binary_message = ''.join(format(ord(char), '08b') for char in message)
                binary_message += '1111111111111110'
                
                data_index = 0
                for y in range(height):
                    for x in range(width):
                        if data_index < len(binary_message):
                            pixel = list(img.getpixel((x, y)))
                            pixel[0] = pixel[0] & ~1 | int(binary_message[data_index])
                            encoded.putpixel((x, y), tuple(pixel))
                            data_index += 1
                        else:
                            break
                    if data_index >= len(binary_message):
                        break
                
                output_path = image_path.replace('.png', '_encoded.png')
                encoded.save(output_path)
                status_label.config(text=f"Message hidden in: {output_path}", fg='green')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to hide message: {str(e)}")
        
        def extract_message():
            image_path = image_path_var.get()
            
            if not image_path:
                messagebox.showerror("Error", "Please select an image")
                return
            
            try:
                img = Image.open(image_path)
                width, height = img.size
                
                binary_message = ""
                for y in range(height):
                    for x in range(width):
                        pixel = img.getpixel((x, y))
                        binary_message += str(pixel[0] & 1)
                
                message = ""
                for i in range(0, len(binary_message), 8):
                    byte = binary_message[i:i+8]
                    if byte == '11111110':
                        break
                    message += chr(int(byte, 2))
                
                message_text.delete("1.0", tk.END)
                message_text.insert("1.0", message)
                status_label.config(text="Message extracted successfully!", fg='green')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract message: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Hide Message", command=hide_message, 
                 bg='#27ae60', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Extract Message", command=extract_message, 
                 bg='#e74c3c', fg='white', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_hash_checker_tool(self, parent):
        """File Hash Checker tool"""
        tk.Label(parent, text="File Hash Checker", font=('Arial', 16, 'bold')).pack(pady=10)
        
        file_path_var = tk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_file).pack(side=tk.LEFT)
        
        result_text = scrolledtext.ScrolledText(parent, height=10, width=70)
        result_text.pack(pady=10)
        
        def calculate_hashes():
            file_path = file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select a file")
                return
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                md5_hash = hashlib.md5(data).hexdigest()
                sha1_hash = hashlib.sha1(data).hexdigest()
                sha256_hash = hashlib.sha256(data).hexdigest()
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", f"File: {os.path.basename(file_path)}\n")
                result_text.insert(tk.END, f"Size: {len(data)} bytes\n\n")
                result_text.insert(tk.END, f"MD5:\n{md5_hash}\n\n")
                result_text.insert(tk.END, f"SHA-1:\n{sha1_hash}\n\n")
                result_text.insert(tk.END, f"SHA-256:\n{sha256_hash}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to calculate hashes: {str(e)}")
        
        tk.Button(parent, text="Calculate Hashes", command=calculate_hashes, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)
    
    def create_file_shredder_tool(self, parent):
        """Secure File Shredder tool"""
        tk.Label(parent, text="Secure File Shredder", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="WARNING: This will permanently delete the file!", 
                font=('Arial', 10, 'bold'), fg='red').pack()
        
        file_path_var = tk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_file).pack(side=tk.LEFT)
        
        passes_var = tk.StringVar(value="3")
        tk.Label(parent, text="Number of Overwrite Passes:").pack()
        tk.Entry(parent, textvariable=passes_var, width=10).pack()
        
        status_label = tk.Label(parent, text="", font=('Arial', 10))
        status_label.pack(pady=10)
        
        def shred_file():
            file_path = file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select a file")
                return
            
            result = messagebox.askyesno("Confirm", 
                f"Are you sure you want to permanently delete:\n{file_path}\n\nThis cannot be undone!")
            
            if not result:
                return
            
            try:
                passes = int(passes_var.get())
                file_size = os.path.getsize(file_path)
                
                with open(file_path, 'ba+') as f:
                    for i in range(passes):
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                        status_label.config(text=f"Pass {i+1}/{passes} completed", fg='orange')
                        parent.update()
                
                os.remove(file_path)
                status_label.config(text=f"File securely deleted!", fg='green')
                file_path_var.set("")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to shred file: {str(e)}")
        
        tk.Button(parent, text="Shred File", command=shred_file, 
                 bg='#e74c3c', fg='white', width=20, height=2).pack(pady=10)
    # ======================
    # CYBER FORENSICS TOOLS
    # ======================
    
    def create_metadata_extractor_tool(self, parent):
        """File Metadata Extractor tool"""
        tk.Label(parent, text="File Metadata Extractor", font=('Arial', 16, 'bold')).pack(pady=10)
        
        file_path_var = tk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_file).pack(side=tk.LEFT)
        
        result_text = scrolledtext.ScrolledText(parent, height=15, width=70)
        result_text.pack(pady=10)
        
        def extract_metadata():
            file_path = file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select a file")
                return
            
            try:
                stat_info = os.stat(file_path)
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", f"File: {os.path.basename(file_path)}\n")
                result_text.insert(tk.END, f"Full Path: {file_path}\n\n")
                result_text.insert(tk.END, f"Size: {stat_info.st_size} bytes\n")
                result_text.insert(tk.END, f"Created: {datetime.fromtimestamp(stat_info.st_ctime)}\n")
                result_text.insert(tk.END, f"Modified: {datetime.fromtimestamp(stat_info.st_mtime)}\n")
                result_text.insert(tk.END, f"Accessed: {datetime.fromtimestamp(stat_info.st_atime)}\n\n")
                
                result_text.insert(tk.END, f"Permissions: {oct(stat_info.st_mode)}\n")
                result_text.insert(tk.END, f"Owner UID: {stat_info.st_uid}\n")
                result_text.insert(tk.END, f"Group GID: {stat_info.st_gid}\n")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract metadata: {str(e)}")
        
        tk.Button(parent, text="Extract Metadata", command=extract_metadata, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)
    
    def create_exif_viewer_tool(self, parent):
        """Image EXIF Viewer tool"""
        tk.Label(parent, text="Image EXIF Viewer", font=('Arial', 16, 'bold')).pack(pady=10)
        
        file_path_var = tk.StringVar()
        
        def select_image():
            filename = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.tiff *.bmp")])
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="Image:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_image).pack(side=tk.LEFT)
        
        result_text = scrolledtext.ScrolledText(parent, height=18, width=70)
        result_text.pack(pady=10)
        
        def view_exif():
            file_path = file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select an image")
                return
            
            try:
                image = Image.open(file_path)
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", f"Image: {os.path.basename(file_path)}\n")
                result_text.insert(tk.END, f"Format: {image.format}\n")
                result_text.insert(tk.END, f"Size: {image.size[0]}x{image.size[1]}\n")
                result_text.insert(tk.END, f"Mode: {image.mode}\n\n")
                
                exifdata = image.getexif()
                
                if exifdata:
                    result_text.insert(tk.END, "EXIF Data:\n")
                    result_text.insert(tk.END, "-" * 50 + "\n")
                    for tag_id, value in exifdata.items():
                        tag = TAGS.get(tag_id, tag_id)
                        result_text.insert(tk.END, f"{tag}: {value}\n")
                else:
                    result_text.insert(tk.END, "No EXIF data found in this image.\n")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read EXIF data: {str(e)}")
        
        tk.Button(parent, text="View EXIF Data", command=view_exif, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)
    
    def create_integrity_checker_tool(self, parent):
        """File Integrity Checker tool"""
        tk.Label(parent, text="File Integrity Checker", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(parent, text="Create and verify file checksums", 
                font=('Arial', 10, 'italic')).pack()
        
        file_path_var = tk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename()
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_file).pack(side=tk.LEFT)
        
        stored_hash_var = tk.StringVar()
        tk.Label(parent, text="Stored Hash (for verification):").pack()
        tk.Entry(parent, textvariable=stored_hash_var, width=70).pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(parent, height=10, width=70)
        result_text.pack(pady=10)
        
        def create_checksum():
            file_path = file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select a file")
                return
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                sha256_hash = hashlib.sha256(data).hexdigest()
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", f"File: {os.path.basename(file_path)}\n")
                result_text.insert(tk.END, f"SHA-256 Checksum:\n{sha256_hash}\n\n")
                result_text.insert(tk.END, "Save this checksum to verify file integrity later.")
                
                stored_hash_var.set(sha256_hash)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create checksum: {str(e)}")
        
        def verify_integrity():
            file_path = file_path_var.get()
            stored_hash = stored_hash_var.get()
            
            if not file_path or not stored_hash:
                messagebox.showerror("Error", "Please select a file and enter the stored hash")
                return
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                current_hash = hashlib.sha256(data).hexdigest()
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", f"File: {os.path.basename(file_path)}\n\n")
                result_text.insert(tk.END, f"Current Hash:\n{current_hash}\n\n")
                result_text.insert(tk.END, f"Stored Hash:\n{stored_hash}\n\n")
                
                if current_hash.lower() == stored_hash.lower():
                    result_text.insert(tk.END, "✓ INTEGRITY VERIFIED - File has not been modified\n", 'green')
                else:
                    result_text.insert(tk.END, "✗ INTEGRITY FAILED - File has been modified or corrupted\n", 'red')
                
            except Exception as e:
                messagebox.showerror("Error", f"Verification failed: {str(e)}")
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Create Checksum", command=create_checksum, 
                 bg='#27ae60', fg='white', width=18).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Verify Integrity", command=verify_integrity, 
                 bg='#e74c3c', fg='white', width=18).pack(side=tk.LEFT, padx=5)
    
    def create_log_analyzer_tool(self, parent):
        """Log File Analyzer tool"""
        tk.Label(parent, text="Log File Analyzer", font=('Arial', 16, 'bold')).pack(pady=10)
        
        file_path_var = tk.StringVar()
        
        def select_file():
            filename = filedialog.askopenfilename(filetypes=[("Log files", "*.log"), ("All files", "*.*")])
            if filename:
                file_path_var.set(filename)
        
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="Log File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=file_path_var, width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=select_file).pack(side=tk.LEFT)
        
        result_text = scrolledtext.ScrolledText(parent, height=18, width=70)
        result_text.pack(pady=10)
        
        def analyze_log():
            file_path = file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select a log file")
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                total_lines = len(lines)
                error_count = sum(1 for line in lines if 'error' in line.lower())
                warning_count = sum(1 for line in lines if 'warning' in line.lower())
                critical_count = sum(1 for line in lines if 'critical' in line.lower())
                
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0", f"Log File Analysis: {os.path.basename(file_path)}\n")
                result_text.insert(tk.END, "=" * 60 + "\n\n")
                result_text.insert(tk.END, f"Total Lines: {total_lines}\n")
                result_text.insert(tk.END, f"Errors: {error_count}\n")
                result_text.insert(tk.END, f"Warnings: {warning_count}\n")
                result_text.insert(tk.END, f"Critical: {critical_count}\n\n")
                
                ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                ips = set(re.findall(ip_pattern, ''.join(lines)))
                result_text.insert(tk.END, f"Unique IP Addresses: {len(ips)}\n")
                
                if error_count > 0:
                    result_text.insert(tk.END, "\nRecent Errors:\n")
                    result_text.insert(tk.END, "-" * 60 + "\n")
                    error_lines = [line for line in lines if 'error' in line.lower()]
                    for line in error_lines[:5]:
                        result_text.insert(tk.END, line.strip()[:100] + "\n")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to analyze log: {str(e)}")
        
        tk.Button(parent, text="Analyze Log", command=analyze_log, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)
    
    def create_email_header_analyzer_tool(self, parent):
        """Email Header Analyzer tool"""
        tk.Label(parent, text="Email Header Analyzer", font=('Arial', 16, 'bold')).pack(pady=10)
        
        tk.Label(parent, text="Paste Email Headers:").pack()
        header_text = scrolledtext.ScrolledText(parent, height=10, width=70)
        header_text.pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(parent, height=12, width=70)
        result_text.pack(pady=10)
        
        def analyze_headers():
            headers = header_text.get("1.0", tk.END).strip()
            
            if not headers:
                messagebox.showerror("Error", "Please paste email headers")
                return
            
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", "Email Header Analysis\n")
            result_text.insert(tk.END, "=" * 60 + "\n\n")
            
            from_match = re.search(r'From:(.+)', headers, re.IGNORECASE)
            if from_match:
                result_text.insert(tk.END, f"From: {from_match.group(1).strip()}\n")
            
            to_match = re.search(r'To:(.+)', headers, re.IGNORECASE)
            if to_match:
                result_text.insert(tk.END, f"To: {to_match.group(1).strip()}\n")
            
            subject_match = re.search(r'Subject:(.+)', headers, re.IGNORECASE)
            if subject_match:
                result_text.insert(tk.END, f"Subject: {subject_match.group(1).strip()}\n")
            
            date_match = re.search(r'Date:(.+)', headers, re.IGNORECASE)
            if date_match:
                result_text.insert(tk.END, f"Date: {date_match.group(1).strip()}\n\n")
            
            received_headers = re.findall(r'Received:(.+)', headers, re.IGNORECASE)
            if received_headers:
                result_text.insert(tk.END, f"Email Route (Received Headers): {len(received_headers)} hops\n")
                for i, received in enumerate(received_headers[:3], 1):
                    result_text.insert(tk.END, f"  Hop {i}: {received.strip()[:80]}\n")
            
            ip_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', headers)
            if ip_addresses:
                result_text.insert(tk.END, f"\nIP Addresses Found: {', '.join(set(ip_addresses[:5]))}\n")
            
            spf_match = re.search(r'SPF[:\s](.+)', headers, re.IGNORECASE)
            if spf_match:
                result_text.insert(tk.END, f"\nSPF Result: {spf_match.group(1).strip()}\n")
            
            dkim_match = re.search(r'DKIM[:\s](.+)', headers, re.IGNORECASE)
            if dkim_match:
                result_text.insert(tk.END, f"DKIM Result: {dkim_match.group(1).strip()}\n")
        
        tk.Button(parent, text="Analyze Headers", command=analyze_headers, 
                 bg='#3498db', fg='white', width=20, height=2).pack(pady=10)


def main():
    root = tk.Tk()
    app = SecurityToolkit(root)
    root.mainloop()


if __name__ == "__main__":
    main()
