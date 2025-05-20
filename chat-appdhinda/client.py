import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import cv2  # Tambahkan ini untuk akses kamera

HOST = '192.168.245.63'
PORT = 55555

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""

        self.gui_done = False
        self.running = True

        self.nickname = simpledialog.askstring("Nickname", "Enter your nickname")

        try:
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Gagal terhubung ke server:\n{e}")
            return

        self.sock.send(self.nickname.encode())

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title(f"Chat Client - {self.nickname}")

        self.chat_label = tk.Label(self.win, text="Chat:")
        self.chat_label.pack(padx=10, pady=5)

        self.text_area = scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=10, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tk.Label(self.win, text="Message:")
        self.msg_label.pack(padx=10, pady=5)

        self.input_area = tk.Text(self.win, height=3)
        self.input_area.pack(padx=10, pady=5)

        self.send_button = tk.Button(self.win, text="Send", command=self.write)
        self.send_button.pack(padx=10, pady=5)

        self.camera_button = tk.Button(self.win, text="Open Camera", command=self.open_camera_thread)
        self.camera_button.pack(padx=10, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end').strip()}"
        if message.strip():  # Cek agar tidak kirim pesan kosong
            self.sock.send(message.encode())
            self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode()
                if self.gui_done:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', message + "\n")
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Terjadi error!")
                self.sock.close()
                break

    def show_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Tidak dapat mengakses kamera.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(f"Kamera - {self.nickname}", frame)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def open_camera_thread(self):
        camera_thread = threading.Thread(target=self.show_camera)
        camera_thread.daemon = True
        camera_thread.start()

if __name__ == "__main__":
    Client()
