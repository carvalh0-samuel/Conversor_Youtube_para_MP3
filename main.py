import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import yt_dlp

# Ativa automaticamente o static-ffmpeg se estiver instalado no ambiente
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass


class YDLLogger:
    """Captura avisos e erros reais do yt-dlp/FFmpeg e exibe na interface."""
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def debug(self, msg):
        pass

    def warning(self, msg):
        self.log_callback(f"[AVISO] {msg}")

    def error(self, msg):
        self.log_callback(f"[ERRO] {msg}")


class YouTubeMP3Downloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube para MP3 Player")
        self.root.geometry("650x570")
        self.root.resizable(False, False)

        default_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Musicas_MP3")
        self.output_dir = tk.StringVar(value=default_dir)
        self.auth_mode = tk.StringVar(value="Firefox (Automático)")
        self.cookies_path = tk.StringVar(value="")
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="192")
        self.is_downloading = False
        self.custom_ffmpeg_path = ""

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 15, "pady": 6}

        # 1. Link do YouTube
        frame_url = tk.Frame(self.root)
        frame_url.pack(fill="x", **pad)
        tk.Label(frame_url, text="Link do Vídeo ou Playlist do YouTube:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.entry_url = tk.Entry(frame_url, textvariable=self.url_var, font=("Segoe UI", 10))
        self.entry_url.pack(fill="x", pady=(4, 0), ipady=4)

        # 2. Pasta de Destino
        frame_dir = tk.Frame(self.root)
        frame_dir.pack(fill="x", **pad)
        tk.Label(frame_dir, text="Pasta de Destino (ou unidade do MP3 Player):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        dir_row = tk.Frame(frame_dir)
        dir_row.pack(fill="x", pady=(4, 0))
        tk.Entry(dir_row, textvariable=self.output_dir, font=("Segoe UI", 9), state="readonly").pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(dir_row, text="Escolher Pasta...", command=self._choose_directory, font=("Segoe UI", 9)).pack(side="right", padx=(8, 0), ipady=2)

        # 3. Autenticação (Cookies)
        frame_auth = tk.Frame(self.root)
        frame_auth.pack(fill="x", **pad)
        tk.Label(frame_auth, text="Autenticação (evita erro de bot):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        auth_row = tk.Frame(frame_auth)
        auth_row.pack(fill="x", pady=(4, 0))
        
        self.auth_combo = ttk.Combobox(
            auth_row,
            textvariable=self.auth_mode,
            values=["Firefox (Automático)", "Arquivo cookies.txt", "Nenhuma"],
            width=22,
            state="readonly"
        )
        self.auth_combo.pack(side="left")
        self.auth_combo.bind("<<ComboboxSelected>>", self._on_auth_change)

        self.entry_cookies = tk.Entry(auth_row, textvariable=self.cookies_path, font=("Segoe UI", 9), state="disabled")
        self.entry_cookies.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=4)
        
        self.btn_cookies = tk.Button(auth_row, text="Selecionar...", command=self._choose_cookies, font=("Segoe UI", 9), state="disabled")
        self.btn_cookies.pack(side="right", padx=(6, 0), ipady=2)

        # 4. Qualidade e Botão de Ação
        frame_opts = tk.Frame(self.root)
        frame_opts.pack(fill="x", **pad)
        tk.Label(frame_opts, text="Qualidade MP3:", font=("Segoe UI", 10)).pack(side="left")
        quality_menu = ttk.Combobox(frame_opts, textvariable=self.quality_var, values=["128", "192", "320"], width=6, state="readonly")
        quality_menu.pack(side="left", padx=(6, 2))
        tk.Label(frame_opts, text="kbps", font=("Segoe UI", 10)).pack(side="left")

        self.btn_download = tk.Button(
            frame_opts,
            text="Baixar Músicas",
            command=self._start_download_thread,
            bg="#1e88e5",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=16,
            pady=4
        )
        self.btn_download.pack(side="right")

        # 5. Barra de Progresso
        frame_prog = tk.Frame(self.root)
        frame_prog.pack(fill="x", **pad)
        self.status_label = tk.Label(frame_prog, text="Pronto para iniciar.", font=("Segoe UI", 9), fg="#555")
        self.status_label.pack(anchor="w")
        self.progress = ttk.Progressbar(frame_prog, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(4, 0))

        # 6. Histórico
        frame_log = tk.Frame(self.root)
        frame_log.pack(fill="both", expand=True, **pad)
        tk.Label(frame_log, text="Histórico de Execução:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(frame_log, height=11, font=("Consolas", 9), state="disabled", bg="#f4f4f4")
        self.log_area.pack(fill="both", expand=True, pady=(4, 0))

    def _on_auth_change(self, event=None):
        if self.auth_mode.get() == "Arquivo cookies.txt":
            self.entry_cookies.config(state="readonly")
            self.btn_cookies.config(state="normal")
        else:
            self.entry_cookies.config(state="disabled")
            self.btn_cookies.config(state="disabled")

    def _choose_directory(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)

    def _choose_cookies(self):
        selected = filedialog.askopenfilename(
            title="Selecione o arquivo cookies.txt",
            filetypes=[("Arquivos de Cookies", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if selected:
            self.cookies_path.set(selected)

    def _log(self, message):
        def append():
            self.log_area.config(state="normal")
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state="disabled")
        self.root.after(0, append)

    def _update_status(self, text, percent=None):
        def update():
            self.status_label.config(text=text)
            if percent is not None:
                self.progress["value"] = percent
        self.root.after(0, update)

    def _check_ffmpeg(self):
        if self.custom_ffmpeg_path and os.path.exists(self.custom_ffmpeg_path):
            return self.custom_ffmpeg_path
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin:
            return os.path.dirname(ffmpeg_bin)
        return None

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            filename = os.path.basename(d.get("filename", ""))
            if total:
                percent = (downloaded / total) * 100
                self._update_status(f"Baixando: {filename} ({percent:.1f}%)", percent)
        elif d["status"] == "finished":
            filename = os.path.basename(d.get("filename", ""))
            self._update_status(f"Convertendo para MP3: {filename}...", 100)
            self._log(f"[OK] Baixado, convertendo: {filename}")

    def _postprocessor_hook(self, d):
        if d["status"] == "finished" and d.get("postprocessor") == "ExtractAudio":
            filepath = d.get("info_dict", {}).get("filepath", "")
            if filepath:
                self._log(f"[MP3] Salvo: {os.path.basename(filepath)}")

    def _start_download_thread(self):
        if self.is_downloading:
            return

        ffmpeg_dir = self._check_ffmpeg()
        if not ffmpeg_dir:
            messagebox.showerror(
                "FFmpeg não encontrado",
                "O FFmpeg não foi detectado.\n\nRode no terminal:\npip install static-ffmpeg"
            )
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole um link válido do YouTube.")
            return

        dest = self.output_dir.get()
        os.makedirs(dest, exist_ok=True)

        self.is_downloading = True
        self.btn_download.config(state="disabled", text="Baixando...")
        self.progress["value"] = 0
        self._log("--- Iniciando tarefa ---")

        mode = self.auth_mode.get()
        cookies_file = self.cookies_path.get().strip()

        thread = threading.Thread(
            target=self._download_worker,
            args=(url, dest, ffmpeg_dir, mode, cookies_file),
            daemon=True
        )
        thread.start()

    def _download_worker(self, url, dest, ffmpeg_dir, mode, cookies_file):
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
            "ffmpeg_location": ffmpeg_dir,
            "js_runtimes": {"deno": {}, "node": {}},
            "outtmpl": os.path.join(dest, "%(playlist_index&{:02d} - |)s%(title).100s.%(ext)s"),
            "windowsfilenames": True,
            "ignoreerrors": True,
            "noplaylist": False,
            "writethumbnail": False,
            "sleep_interval": 3,
            "max_sleep_interval": 6,
            "logger": YDLLogger(self._log),
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": self.quality_var.get(),
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
            ],
        }

        if mode == "Firefox (Automático)":
            ydl_opts["cookiesfrombrowser"] = ("firefox",)
            self._log("[INFO] Lendo sessão diretamente do Firefox...")
        elif mode == "Arquivo cookies.txt" and cookies_file and os.path.exists(cookies_file):
            ydl_opts["cookiefile"] = cookies_file
            self._log(f"[INFO] Usando arquivo: {os.path.basename(cookies_file)}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self._update_status("Concluído!", 100)
            self._log("=== Tarefa finalizada! ===\n")
            self.root.after(0, lambda: messagebox.showinfo("Concluído", "Processo finalizado!"))
        except Exception as e:
            self._update_status("Erro crítico.", 0)
            self._log(f"[ERRO CRÍTICO] {str(e)}")
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.btn_download.config(state="normal", text="Baixar Músicas"))


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeMP3Downloader(root)
    root.mainloop()