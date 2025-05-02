#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import asyncio
import websockets
import threading
import sys
import os
from datetime import datetime
import customtkinter as ctk # type: ignore
from PIL import Image, ImageTk # type: ignore
import io
import base64

# Add the parent directory to the path so we can import from app.common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.cipher import encrypt, decrypt

# Import our local cipher implementation as a backup
from cipher_utils import decrypt_message as local_decrypt, visualize_decryption

# Modern color scheme
COLORS = {
    "primary": "#3498db",
    "primary_dark": "#2980b9",
    "secondary": "#2ecc71",
    "secondary_dark": "#27ae60",
    "background": "#f5f5f5",
    "surface": "#ffffff",
    "error": "#e74c3c",
    "warning": "#f39c12",
    "text": "#333333",
    "text_secondary": "#7f8c8d"
}

class ModernSecureChat(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set appearance mode and theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.title("Secure Messaging App")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Variables
        self.username = ctk.StringVar()
        self.message = ctk.StringVar()
        self.encryption_enabled = ctk.BooleanVar(value=True)
        self.rail_count = ctk.IntVar(value=3)
        self.decrypt_rail_count = ctk.IntVar(value=3)
        self.websocket = None
        self.connected = False
        self.server_url = ctk.StringVar(value="ws://localhost:8000/ws/")
        
        # Create frames
        self.create_login_frame()
        self.create_chat_frame()
        
        # Initially show the login frame
        self.show_login_frame()
        
        # Add a protocol handler for window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_login_frame(self):
        self.chat_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
    
    def show_chat_frame(self):
        self.login_frame.pack_forget()
        self.chat_frame.pack(fill="both", expand=True)
    
    def create_login_frame(self):
        """Create the login screen UI components with a modern design"""
        self.login_frame = ctk.CTkFrame(self)
        
        # Logo or Banner
        self.app_logo = ctk.CTkLabel(
            self.login_frame,
            text="Secure Messaging",
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold")
        )
        self.app_logo.pack(pady=(60, 10))
        
        self.app_subtitle = ctk.CTkLabel(
            self.login_frame,
            text="End-to-end encrypted chat with Rail Fence Cipher",
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.app_subtitle.pack(pady=(0, 40))
        
        # Login form container
        login_form = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        login_form.pack(padx=20, pady=20, fill="x", expand=False)
        login_form.columnconfigure(0, weight=1)
        
        # Username
        username_label = ctk.CTkLabel(
            login_form, 
            text="Username",
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        username_label.grid(row=0, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            login_form,
            textvariable=self.username,
            placeholder_text="Enter your username",
            width=400,
            height=40,
            border_width=1,
            corner_radius=8
        )
        self.username_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Server URL
        server_label = ctk.CTkLabel(
            login_form, 
            text="Server URL",
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        server_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.server_entry = ctk.CTkEntry(
            login_form,
            textvariable=self.server_url,
            placeholder_text="Enter WebSocket server URL",
            width=400,
            height=40,
            border_width=1,
            corner_radius=8
        )
        self.server_entry.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 30))
        
        # Connect button
        self.connect_btn = ctk.CTkButton(
            login_form,
            text="Connect",
            command=self.connect_to_server,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold")
        )
        self.connect_btn.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Status message
        self.login_status = ctk.CTkLabel(
            login_form,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=COLORS["error"]
        )
        self.login_status.grid(row=5, column=0, sticky="ew", padx=20, pady=(10, 0))
        
        # Footer
        footer = ctk.CTkLabel(
            self.login_frame,
            text="© 2025 Secure Messaging App",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=COLORS["text_secondary"]
        )
        footer.pack(pady=(50, 20), side="bottom")
    
    def create_chat_frame(self):
        """Create the chat UI components with a modern design"""
        self.chat_frame = ctk.CTkFrame(self)
        
        # Top bar with user info and settings
        top_frame = ctk.CTkFrame(self.chat_frame, height=60, fg_color=COLORS["surface"])
        top_frame.pack(fill="x", side="top")
        top_frame.pack_propagate(False)
        
        # User info
        user_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        user_frame.pack(side="left", padx=20)
        
        user_label = ctk.CTkLabel(
            user_frame,
            text="Logged in as:",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=COLORS["text_secondary"]
        )
        user_label.pack(side="left")
        
        self.user_display = ctk.CTkLabel(
            user_frame,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        )
        self.user_display.pack(side="left", padx=(5, 0))
        
        # Encryption settings
        settings_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        settings_frame.pack(side="right", padx=20)
        
        encrypt_chk = ctk.CTkSwitch(
            settings_frame,
            text="Encrypt Messages",
            variable=self.encryption_enabled,
            onvalue=True,
            offvalue=False
        )
        encrypt_chk.pack(side="right", padx=(20, 0))
        
        rail_label = ctk.CTkLabel(settings_frame, text="Rail count:")
        rail_label.pack(side="left", padx=(0, 5))
        
        rail_spinner = ctk.CTkOptionMenu(
            settings_frame,
            values=["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            command=lambda choice: self.rail_count.set(int(choice))
        )
        rail_spinner.set(str(self.rail_count.get()))
        rail_spinner.pack(side="right")
        
        # Split view for messages and users
        content_frame = ctk.CTkFrame(self.chat_frame, fg_color=COLORS["background"])
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chat display
        chat_display_frame = ctk.CTkFrame(content_frame, fg_color=COLORS["surface"])
        chat_display_frame.pack(fill="both", expand=True, padx=(0, 5), pady=0, side="left")
        
        # Messages area title
        messages_title = ctk.CTkLabel(
            chat_display_frame,
            text="Messages",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            anchor="w"
        )
        messages_title.pack(fill="x", padx=15, pady=10)
        
        # Chat display with styled tags
        self.chat_display = scrolledtext.ScrolledText(
            chat_display_frame,
            wrap=tk.WORD,
            font=("Helvetica", 10),
            bg=COLORS["surface"],
            fg=COLORS["text"],
            bd=0,
            highlightthickness=0
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.chat_display.config(state="disabled")
        
        # Configure tags for message styling
        self.chat_display.tag_configure("system", foreground="#7f8c8d", justify="center", font=("Helvetica", 9, "italic"))
        self.chat_display.tag_configure("username", foreground=COLORS["primary"], font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("timestamp", foreground="#95a5a6", font=("Helvetica", 8))
        self.chat_display.tag_configure("encrypted", foreground="#e67e22")
        
        # Message input and controls
        control_frame = ctk.CTkFrame(self.chat_frame, height=120, fg_color=COLORS["surface"])
        control_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # Message composition area
        compose_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        compose_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.message_entry = ctk.CTkEntry(
            compose_frame,
            textvariable=self.message,
            placeholder_text="Type your message here...",
            height=40,
            corner_radius=20
        )
        self.message_entry.pack(fill="x", side="left", expand=True, padx=(0, 10))
        
        # Bind Enter key to send message
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_btn = ctk.CTkButton(
            compose_frame,
            text="Send",
            width=100,
            height=40,
            corner_radius=20,
            command=self.send_message
        )
        self.send_btn.pack(side="right")
        
        # Decryption controls
        decrypt_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        decrypt_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        decrypt_label = ctk.CTkLabel(decrypt_frame, text="Decrypt a message with custom rail count:")
        decrypt_label.pack(side="left", padx=(0, 10))
        
        decrypt_rail_spinner = ctk.CTkOptionMenu(
            decrypt_frame,
            values=["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            width=60,
            command=lambda choice: self.decrypt_rail_count.set(int(choice))
        )
        decrypt_rail_spinner.set(str(self.decrypt_rail_count.get()))
        decrypt_rail_spinner.pack(side="left", padx=(0, 10))
        
        decrypt_msg_entry = ctk.CTkEntry(
            decrypt_frame,
            placeholder_text="Paste encrypted message here to decrypt",
            height=30,
            width=300
        )
        decrypt_msg_entry.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        decrypt_btn = ctk.CTkButton(
            decrypt_frame,
            text="Decrypt",
            width=100,
            command=lambda: self.decrypt_message(decrypt_msg_entry.get(), self.decrypt_rail_count.get())
        )
        decrypt_btn.pack(side="right")
    
    def connect_to_server(self):
        """Connect to the WebSocket server"""
        if not self.username.get().strip():
            self.login_status.configure(text="Username is required")
            return
        
        if not self.server_url.get().strip():
            self.login_status.configure(text="Server URL is required")
            return
        
        # Show connecting status
        self.login_status.configure(text="Connecting to server...")
        self.connect_btn.configure(text="Connecting...", state="disabled")
        self.update()
        
        # Start connection in a separate thread to keep UI responsive
        threading.Thread(target=self._connect_async, daemon=True).start()
    
    def _connect_async(self):
        """Async connection to WebSocket server"""
        try:
            # Create and start a new asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Connect to server
            websocket_url = f"{self.server_url.get()}{self.username.get()}"
            
            # Create a websocket connection
            websocket = loop.run_until_complete(websockets.connect(websocket_url))
            self.websocket = websocket
            self.connected = True
            
            # Signal connection success to UI thread
            self.after(0, self._on_connected)
            
            # Start listening for messages in a loop
            while self.connected:
                try:
                    # Receive message with a timeout
                    message = loop.run_until_complete(asyncio.wait_for(
                        websocket.recv(), timeout=0.1
                    ))
                    data = json.loads(message)
                    self.after(0, lambda d=data: self.display_message(d))
                except asyncio.TimeoutError:
                    # Just a timeout, continue the loop
                    continue
                except websockets.exceptions.ConnectionClosed:
                    # Connection closed
                    self.connected = False
                    self.websocket = None
                    self.after(0, self._on_disconnected)
                    break
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    continue
                    
        except Exception as e:
            # Update UI with error
            print(f"Connection error: {e}")
            self.after(0, lambda: self._on_connection_error(str(e)))
    
    def send_message(self, event=None):
        """Send a message to the server"""
        if not self.connected or not self.websocket:
            messagebox.showerror("Error", "Not connected to the server")
            return
        
        message_text = self.message.get().strip()
        if not message_text:
            return
        
        # Prepare message data
        message_data = {
            "content": message_text,
            "is_encrypted": self.encryption_enabled.get(),
            "rails": self.rail_count.get()
        }
        
        # Send in a separate thread to keep UI responsive
        threading.Thread(target=self._send_async, args=(message_data,), daemon=True).start()
        
        # Clear input field
        self.message.set("")
    
    def _send_async(self, message_data):
        """Send message asynchronously"""
        try:
            # Create and start a new asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Send message
            if self.websocket:
                # Convert to JSON
                json_data = json.dumps(message_data)
                # Send the message
                loop.run_until_complete(self.websocket.send(json_data))
                print(f"Message sent: {json_data}")
            else:
                print("No active websocket connection")
                self.after(0, lambda: messagebox.showerror("Error", "Connection lost. Please reconnect."))
                self.after(0, self._on_disconnected)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to send message: {str(e)}"))
            # If we have a connection error, force disconnect
            if "connection" in str(e).lower():
                self.after(0, self._on_disconnected)
    
    async def _websocket_send(self, message_data):
        """Send message through websocket"""
        if self.websocket:
            await self.websocket.send(json.dumps(message_data))
    
    def display_message(self, message_data):
        """Display a received message in the chat"""
        sender = message_data.get("sender", "Unknown")
        content = message_data.get("content", "")
        is_encrypted = message_data.get("is_encrypted", False)
        rails = message_data.get("rails", 3)
        timestamp_str = message_data.get("timestamp", "")
        
        # Format timestamp
        timestamp = ""
        if timestamp_str:
            try:
                dt = datetime.fromisoformat(timestamp_str)
                timestamp = dt.strftime("%H:%M:%S")
            except:
                timestamp = timestamp_str
        
        # Enable text widget for editing
        self.chat_display.config(state="normal")
        
        # Store message position for right-click menu
        start_pos = self.chat_display.index(tk.END)
        
        # Insert message with appropriate styling
        if sender == "System":
            # System message
            self.chat_display.insert(tk.END, f"• {content} •\n", "system")
        else:
            # User message
            self.chat_display.insert(tk.END, f"{sender}", "username")
            self.chat_display.insert(tk.END, f" [{timestamp}]: ", "timestamp")
            
            # Get position where the content starts
            content_start = self.chat_display.index(tk.END)
            
            if is_encrypted:
                self.chat_display.insert(tk.END, f"{content} 🔒\n", "encrypted")
                
                # Store the encrypted message info for easy decryption
                end_pos = self.chat_display.index(tk.END)
                tag_name = f"encrypted_msg_{sender}_{timestamp}"
                self.chat_display.tag_add(tag_name, content_start, end_pos)
                
                # Add right-click binding for decryption
                self.chat_display.tag_bind(
                    tag_name, 
                    "<Button-3>", 
                    lambda event, msg=content, r=rails: self._show_decrypt_menu(event, msg, r)
                )
            else:
                self.chat_display.insert(tk.END, f"{content}\n")
        
        # Scroll to the bottom
        self.chat_display.see(tk.END)
        
        # Disable editing
        self.chat_display.config(state="disabled")
    
    def _show_decrypt_menu(self, event, encrypted_msg, rails):
        """Show right-click menu for decryption"""
        decrypt_menu = tk.Menu(self.chat_display, tearoff=0)
        decrypt_menu.add_command(
            label=f"Decrypt (Rail {rails})", 
            command=lambda: self.decrypt_message(encrypted_msg, rails)
        )
        
        # Add other common rail options
        for r in [2, 3, 4, 5]:
            if r != rails:
                decrypt_menu.add_command(
                    label=f"Try Rail {r}", 
                    command=lambda rail=r: self.decrypt_message(encrypted_msg, rail)
                )
        
        # Show context menu
        decrypt_menu.tk_popup(event.x_root, event.y_root)
    
    def _visualize_rail_fence(self, text, rails):
        """Helper method to visualize the rail fence cipher for debugging"""
        # Create a rails x len(text) matrix with null characters
        fence = [[' ' for _ in range(len(text))] for _ in range(rails)]
        
        # Populate fence with markers to show the rail pattern
        rail, direction = 0, 1
        for i in range(len(text)):
            fence[rail][i] = 'x'
            rail += direction
            if rail == 0 or rail == rails-1:
                direction = -direction
        
        # Populate the fence with the text characters
        index = 0
        for r in range(rails):
            for c in range(len(text)):
                if fence[r][c] == 'x' and index < len(text):
                    fence[r][c] = text[index]
                    index += 1
        
        # Generate a visual representation
        visualization = []
        for r in range(rails):
            row = ''.join(fence[r])
            visualization.append(row)
        
        return '\n'.join(visualization)
        
    def decrypt_message(self, encrypted_text, rails):
        """Decrypt a message and show the result"""
        if not encrypted_text:
            return
        
        try:
            print(f"Attempting to decrypt: '{encrypted_text}' with {rails} rails")
            
            # Try to visualize the pattern
            visualization = visualize_decryption(encrypted_text, rails)
            print(f"Visualization of rail fence pattern:\n{visualization}")
            
            # Try both implementations
            try:
                # First try the original implementation
                decrypted = decrypt(encrypted_text, rails)
                print(f"Original implementation result: '{decrypted}'")
            except Exception as e:
                print(f"Original implementation failed: {e}")
                decrypted = None
                
            if not decrypted or decrypted == encrypted_text:
                # Try our local implementation as backup
                decrypted = local_decrypt(encrypted_text, rails)
                print(f"Local implementation result: '{decrypted}'")
            
            # Show the decrypted message in a more readable dialog
            decryption_result = ctk.CTkToplevel(self)
            decryption_result.title("Decrypted Message")
            decryption_result.geometry("500x200")
            decryption_result.resizable(True, True)
            decryption_result.grab_set()  # Make the window modal
            
            # Add some padding
            decryption_result.grid_columnconfigure(0, weight=1)
            decryption_result.grid_rowconfigure(0, weight=0)
            decryption_result.grid_rowconfigure(1, weight=1)
            
            # Header
            header = ctk.CTkLabel(
                decryption_result, 
                text="Decrypted Message", 
                font=ctk.CTkFont(family="Helvetica", size=16, weight="bold")
            )
            header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
            
            # Message display with scroll if needed
            message_frame = ctk.CTkFrame(decryption_result)
            message_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
            
            message_display = ctk.CTkTextbox(message_frame)
            message_display.pack(fill="both", expand=True, padx=10, pady=10)
            message_display.insert("1.0", decrypted)
            message_display.configure(state="disabled")
            
        except Exception as e:
            print(f"Decryption error: {e}")
            messagebox.showerror("Decryption Error", f"Failed to decrypt: {str(e)}")
    
    def _on_connected(self):
        """Handle successful connection"""
        print("Connection successful! Transitioning to chat interface...")
        self.login_status.configure(text="")
        self.connect_btn.configure(text="Connect", state="normal")
        self.user_display.configure(text=self.username.get())
        self.show_chat_frame()
    
    def _on_connection_error(self, error_message):
        """Handle connection error"""
        self.login_status.configure(text=f"Connection error: {error_message}")
        self.connect_btn.configure(text="Connect", state="normal")
    
    def _on_disconnected(self):
        """Handle disconnection"""
        print("Disconnected from server")
        self.connected = False
        self.websocket = None
        messagebox.showinfo("Disconnected", "You have been disconnected from the server.")
        self.show_login_frame()
        self.connect_btn.configure(text="Connect", state="normal")
        self.login_status.configure(text="")
    
    def on_closing(self):
        """Handle window close"""
        if self.connected:
            print("Closing application and disconnecting...")
            threading.Thread(target=self._disconnect_async, daemon=True).start()
            # Give time to disconnect properly, but not too long
            self.after(300, self.destroy)
        else:
            self.destroy()
    
    def _disconnect_async(self):
        """Disconnect from server asynchronously"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if self.websocket:
                loop.run_until_complete(self.websocket.close())
                self.connected = False
                self.websocket = None
                print("Successfully closed WebSocket connection")
        except Exception as e:
            print(f"Error during disconnect: {e}")
    
    async def _websocket_close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            self.websocket = None

if __name__ == "__main__":
    app = ModernSecureChat()
    app.mainloop() 