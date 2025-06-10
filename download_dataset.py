import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from tkinter.ttk import Progressbar
import boto3
import os
from urllib.parse import urlparse
from dotenv import load_dotenv, set_key

load_dotenv()

def log(message):
    log_box.config(state='normal')
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)
    log_box.config(state='disabled')

def save_credentials_to_env(access_key, secret_key):
    set_key('.env', 'AWS_ACCESS_KEY_ID', access_key)
    set_key('.env', 'AWS_SECRET_ACCESS_KEY', secret_key)

def download_files():
    access_key = access_key_entry.get().strip()
    secret_key = secret_key_entry.get().strip()
    s3_uris = s3_uris_text.get("1.0", tk.END).strip().splitlines()

    if not access_key or not secret_key or not s3_uris:
        messagebox.showerror("Input Error", "Please provide all required fields.")
        return

    output_dir = filedialog.askdirectory(title="Select destination folder")
    if not output_dir:
        return

    save_credentials_to_env(access_key, secret_key)

    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    s3 = session.client("s3")

    total = len(s3_uris)
    progress_bar["value"] = 0
    progress_bar["maximum"] = total

    for i, s3_uri in enumerate(s3_uris):
        try:
            parsed = urlparse(s3_uri)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            filename = os.path.basename(key)
            output_path = os.path.join(output_dir, filename)

            log(f"Downloading: {s3_uri}")
            s3.download_file(bucket, key, output_path)
            log(f"Success: {filename} saved to {output_path}")
        except Exception as e:
            log(f"Error downloading {s3_uri}: {str(e)}")
        finally:
            progress_bar["value"] = i + 1
            root.update_idletasks()

    messagebox.showinfo("Done", "Download process completed.")


# GUI Layout
root = tk.Tk()
root.title("IEEE DataPort S3 Downloader")
root.geometry("650x550")

tk.Label(root, text="AWS Access Key:").pack()
access_key_entry = tk.Entry(root, width=80)
access_key_entry.insert(0, os.getenv('AWS_ACCESS_KEY_ID', ''))
access_key_entry.pack()

tk.Label(root, text="AWS Secret Access Key:").pack()
secret_key_entry = tk.Entry(root, width=80, show="*")
secret_key_entry.insert(0, os.getenv('AWS_SECRET_ACCESS_KEY', ''))
secret_key_entry.pack()

tk.Label(root, text="S3 URIs (one per line):").pack()
s3_uris_text = tk.Text(root, height=8, width=80)
s3_uris_text.pack()

tk.Button(root, text="📥 Start Download", command=download_files).pack(pady=10)

progress_bar = Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress_bar.pack(pady=10)

tk.Label(root, text="Log:").pack()
log_box = scrolledtext.ScrolledText(root, height=12, width=80, state='disabled')
log_box.pack()

root.mainloop()
