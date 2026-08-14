import subprocess
import threading
from pathlib import Path
from tkinter import filedialog
from urllib.parse import urlparse

import customtkinter as ctk
import yt_dlp
from yt_dlp.utils import DownloadError

from config import APP_ROOT, COLORS, DEFAULT_DOWNLOAD_PATH, GALLERY_DL_PATH, SUPPORTED_DOMAINS
from database import add_download_record, clear_all_history, delete_download_record, get_recent_downloads


class MediaFetcherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # --- instance state (replaces the old module-level globals) ---
        self.download_path = DEFAULT_DOWNLOAD_PATH
        self.outtmpl_path = str(self.download_path / "%(title)s.%(ext)s")
        self.input_url = ""

        self.title("MediaFetcher - Open Media Downloader")

        icon_path = APP_ROOT / "favicon.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        self.geometry("750x650")
        self.resizable(False, False)
        self.configure(fg_color=(COLORS["light"]["bg"], COLORS["dark"]["bg"]))

        self._build_ui()

    # --------------------------------------------------------------------
    # UI CONSTRUCTION
    # --------------------------------------------------------------------
    def _build_ui(self):
        self.logo = ctk.CTkLabel(
            self,
            text="𝓶",
            font=("Arial", 150),
            text_color=(COLORS["light"]["text"], COLORS["dark"]["text"])
        )
        self.logo.pack(pady=(30, 0))

        self.label = ctk.CTkLabel(
            self,
            text="MediaFetcher",
            font=("Inter", 22, "bold"),
            text_color=(COLORS["light"]["text"], COLORS["dark"]["text"])
        )
        self.label.pack(pady=(5, 10))

        self.design_card = ctk.CTkFrame(
            self,
            width=650,
            height=550,
            fg_color=(COLORS["light"]["bg"], COLORS["dark"]["bg"]),
            border_color=(COLORS["light"]["entry_border"], COLORS["dark"]["entry_border"]),
            border_width=1,
            corner_radius=16
        )
        self.design_card.pack(pady=(20, 0))

        self.responsible_use_label = ctk.CTkLabel(
            self,
            text="Only download media you own, have permission to download, or are otherwise legally entitled to save.",
            font=("Inter", 14),
            text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"]),
            wraplength=480,
        )
        self.responsible_use_label.pack(pady=(40, 0))

        self.design_card.grid_columnconfigure(0, weight=1)
        self.design_card.grid_rowconfigure(0, weight=1)
        self.design_card.grid_rowconfigure(1, weight=1)
        self.design_card.grid_rowconfigure(2, weight=1)

        self.urlentry = ctk.CTkEntry(
            self.design_card,
            placeholder_text="Enter Open-Access / CC Media URL",
            placeholder_text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"]),
            font=("Inter", 16, "bold"),
            width=540,
            height=46,
            border_width=1,
            border_color=(COLORS["light"]["entry_border"], COLORS["dark"]["entry_border"]),
            fg_color=("#F5F8FA", "#16181C"),
            text_color=(COLORS["light"]["text"], COLORS["dark"]["text"]),
            justify="center",
            corner_radius=10
        )
        self.urlentry.grid(row=0, column=0, sticky="s", pady=(30, 10), padx=(20,))

        self.download_button = ctk.CTkButton(
            self.design_card,
            text="Download Media",
            fg_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            text_color=(COLORS["light"]["download_button_idle_text"], COLORS["dark"]["download_button_idle_text"]),
            font=("Inter", 16, "bold"),
            command=self.start_download,
            corner_radius=10,
            width=200,
            height=44,
            hover_color=(COLORS["light"]["download_button_hover"], COLORS["dark"]["download_button_hover"]),
        )
        self.download_button.grid(row=1, column=0, pady=(10, 5))

        self.accessHistory_button = ctk.CTkButton(
            self.design_card,
            text="Previous Downloads",
            fg_color="transparent",
            border_width=1,
            border_color=(COLORS["light"]["entry_border"], COLORS["dark"]["entry_border"]),
            text_color=(COLORS["light"]["text"], COLORS["dark"]["text"]),
            font=("Inter", 14, "bold"),
            command=self.download_history_window,
            corner_radius=8,
            width=200,
            height=36,
            hover_color=(COLORS["light"]["card_border"], COLORS["dark"]["card_border"]),
        )
        self.accessHistory_button.grid(row=2, column=0, pady=(0, 20))

        self.error_label = ctk.CTkLabel(
            self.design_card,
            font=("Inter", 14, "bold"),
            text_color=(COLORS["light"]["error_message"], COLORS["dark"]["error_message"])
        )

        self.download_progress_bar = ctk.CTkProgressBar(
            self,
            width=300,
            height=20,
            mode="determinate",
            progress_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            fg_color=(COLORS["light"]["entry_border"], COLORS["dark"]["entry_border"]),
        )
        self.download_progress_bar.set(0)
        self.download_progress_bar.pack_forget()

        self.appearence_button = ctk.CTkOptionMenu(
            self,
            values=["System", "Light", "Dark"],
            fg_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            button_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            text_color=(COLORS["light"]["download_button_idle_text"], COLORS["dark"]["download_button_idle_text"]),
            font=("Inter", 16, "bold"),
            anchor="center",
            command=self.change_appearance_mode_event,
            button_hover_color="#D7DBDC",
            dropdown_fg_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            dropdown_text_color=(COLORS["light"]["download_button_idle_text"], COLORS["dark"]["download_button_idle_text"]),
            dropdown_hover_color=(COLORS["light"]["download_button_hover"], COLORS["dark"]["download_button_hover"]),
            dropdown_font=("Inter", 12, "bold"),
            corner_radius=12,
            width=40,
            height=28,
        )
        self.appearence_button.set("☼ | ☾")
        self.appearence_button.pack()
        self.appearence_button.place(relx=0.03, rely=0.03, anchor="nw")

    # --------------------------------------------------------------------
    # HELPERS (pure logic, no widget access)
    # --------------------------------------------------------------------
    def is_supported_url(self, url):
        parseable_url = url if "://" in url else "https://" + url
        try:
            hostname = urlparse(parseable_url).hostname
        except ValueError:
            return False
        if not hostname:
            return False
        hostname = hostname.lower()
        return any(
            hostname == domain or hostname.endswith("." + domain)
            for domain in SUPPORTED_DOMAINS
        )

    def friendly_error_message(self, raw_error):
        error_text = str(raw_error).strip()
        lowered = error_text.lower()

        if "429" in error_text or "too many requests" in lowered:
            return "Error: Too many requests — the server is rate-limiting you. Wait a bit and try again."
        if "403" in error_text or "forbidden" in lowered:
            return "Error: Access forbidden (403) — the content may be private or blocked."
        if "404" in error_text or "not found" in lowered:
            return "Error: Content not found (404) — the link may be broken or removed."

        if len(error_text) > 160:
            error_text = error_text[:157] + "..."
        return f"Error: {error_text}" if error_text else "Error: Download failed for an unknown reason."

    # --------------------------------------------------------------------
    # DOWNLOAD FLOW
    # --------------------------------------------------------------------
    def handle_download_failure(self, message):
        self.failed_download_label(message)
        self.download_progress_bar.stop()
        self.download_progress_bar.set(0)
        self.download_progress_bar.pack_forget()
        self.urlentry.configure(state = "disabled", fg_color=("#91979C", "#37383A"))
        self.download_button.configure(
            text="Retry Download",
            state="normal",
            fg_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            hover_color=(COLORS["light"]["download_button_hover"], COLORS["dark"]["download_button_hover"]),
            text_color=(COLORS["light"]["download_button_idle_text"], COLORS["dark"]["download_button_idle_text"]),
            command=self.reset_ui
        )

    def success_download_message(self):
        self.download_progress_bar.set(1.0)
        self.download_button.configure(
            text="Download Complete! Click to reset",
            state="normal",
            fg_color=COLORS["success_dwnldbutton"]["download_button_idle"],
            hover_color=COLORS["success_dwnldbutton"]["download_button_hover"],
            command=self.reset_ui,
            width=200
        )

    def failed_download_label(self, error_message):
        self.error_label.configure(text=str(error_message))
        self.error_label.grid(row=3, column=0, sticky="n", pady=(5, 5))

    def yt_dlp_progress_hook(self, d, input_url):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)

            if total > 0:
                percentage = min(downloaded / total, 1.0)
                self.after(0, lambda p=percentage: self.download_progress_bar.set(p))

        elif d['status'] == 'finished':
            title = d.get('info_dict', {}).get('title') or 'Downloaded Media'
            file_name = Path(title).name

            self.after(0, lambda: add_download_record(
                url=input_url,
                file_name=file_name,
                media_type="Video",
                location=str(self.download_path)
            ))
            self.after(0, lambda: self.download_progress_bar.set(1.0))

    def start_download(self):
        self.input_url = self.urlentry.get().strip()

        if not self.input_url:
            self.handle_download_failure("Error: Entry box cannot be empty!")
            return

        if not self.is_supported_url(self.input_url):
            self.handle_download_failure("Error: URL must be from a supported public domain/open platform!")
            return

        self.error_label.grid_forget()

        chosen_folder = filedialog.askdirectory(title="Select Download Folder")
        if not chosen_folder:
            self.failed_download_label("Download cancelled: no folder selected.")
            return

        self.download_path = Path(chosen_folder)
        self.outtmpl_path = str(self.download_path / "%(title)s.%(ext)s")

        self.download_button.configure(text="Downloading...", state="disabled", fg_color="#536471")

        self.download_progress_bar.set(0)
        self.download_progress_bar.pack(pady=(10, 10))

        threading.Thread(target=self.background_Download, args=(self.input_url,), daemon=True).start()

    def background_Download(self, url):
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': self.outtmpl_path,
                'progress_hooks': [lambda d: self.yt_dlp_progress_hook(d, url)]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as mediaDownloader:
                try:
                    video_info = mediaDownloader.extract_info(url, download=False)
                except DownloadError as e:
                    error_msg = str(e).lower()
                    if any(phrase in error_msg for phrase in ["no video", "unsupported url", "no video formats"]):
                        self.run_gallery_dl_fallback(url)
                        return
                    else:
                        msg = self.friendly_error_message(e)
                        self.after(0, lambda m=msg: self.handle_download_failure(m))
                        return

                if video_info and video_info.get('formats'):
                    try:
                        mediaDownloader.process_info(video_info)
                        self.after(0, self.success_download_message)
                    except DownloadError as e:
                        msg = self.friendly_error_message(e)
                        self.after(0, lambda m=msg: self.handle_download_failure(m))
                    except Exception as e:
                        msg = self.friendly_error_message(e)
                        self.after(0, lambda m=msg: self.handle_download_failure(m))
                else:
                    self.run_gallery_dl_fallback(url)

        except Exception as e:
            msg = self.friendly_error_message(e)
            self.after(0, lambda m=msg: self.handle_download_failure(m))

    def run_gallery_dl_fallback(self, link):
        try:
            result = subprocess.run(
                [GALLERY_DL_PATH, "--range", "1", "--directory", str(self.download_path), link],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                self.after(0, lambda: add_download_record(
                    url=link,
                    file_name="Photo Post / Gallery",
                    media_type="Image",
                    location=str(self.download_path)
                ))
                self.after(0, self.success_download_message)
            else:
                stderr_text = (result.stderr or "").strip()
                msg = self.friendly_error_message(stderr_text) if stderr_text else "Error: gallery-dl failed to download this post."
                self.after(0, lambda m=msg: self.handle_download_failure(m))
        except FileNotFoundError:
            self.after(0, lambda: self.handle_download_failure(
                "Error: gallery-dl tool is missing from system PATH."
            ))
        except subprocess.TimeoutExpired:
            self.after(0, lambda: self.handle_download_failure(
                "Error: gallery-dl timed out. The site may be slow or unresponsive."
            ))
        except Exception as e:
            msg = self.friendly_error_message(e)
            self.after(0, lambda m=msg: self.handle_download_failure(m))

    def reset_ui(self):
        self.urlentry.configure(state="normal", fg_color=("#F5F8FA", "#16181C"))
        self.urlentry.delete(0, "end")
        self.error_label.grid_forget()
        self.download_progress_bar.pack_forget()
        self.download_progress_bar.set(0)
        self.appearence_button.pack()
        self.appearence_button.place(relx=0.03, rely=0.03, anchor="nw")
        self.download_button.configure(
            text="Download Media",
            state="normal",
            fg_color=(COLORS["light"]["download_button_idle"], COLORS["dark"]["download_button_idle"]),
            hover_color=(COLORS["light"]["download_button_hover"], COLORS["dark"]["download_button_hover"]),
            text_color=(COLORS["light"]["download_button_idle_text"], COLORS["dark"]["download_button_idle_text"]),
            command=self.start_download
        )

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    # --------------------------------------------------------------------
    # HISTORY WINDOW
    # --------------------------------------------------------------------
    def download_history_window(self):
        history_GUI = ctk.CTkToplevel(self)

        icon_path = APP_ROOT / "favicon.ico"
        if icon_path.exists():
            history_GUI.iconbitmap(str(icon_path))

        history_GUI.title("Download History")
        history_GUI.geometry("820x540")
        history_GUI.resizable(False, False)
        history_GUI.configure(fg_color=(COLORS["light"]["bg"], COLORS["dark"]["bg"]))

        top_bar = ctk.CTkFrame(history_GUI, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text="Download History",
            font=("Inter", 20, "bold"),
            text_color=(COLORS["light"]["text"], COLORS["dark"]["text"])
        )
        title_lbl.pack(side="left")

        def handle_clear_all():
            clear_all_history()
            history_GUI.destroy()
            self.download_history_window()

        clear_all_btn = ctk.CTkButton(
            top_bar,
            text="Clear History",
            font=("Inter", 11, "bold"),
            fg_color="#E53935",
            hover_color="#C62828",
            text_color="#FFFFFF",
            height=28,
            width=100,
            corner_radius=6,
            command=handle_clear_all
        )
        clear_all_btn.pack(side="right")

        header_frame = ctk.CTkFrame(
            history_GUI,
            fg_color=(COLORS["light"]["card_border"], COLORS["dark"]["card_border"]),
            corner_radius=8,
            height=38
        )
        header_frame.pack(fill="x", padx=20, pady=(0, 5))

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=4)
        header_frame.grid_columnconfigure(2, weight=2)
        header_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(header_frame, text="TYPE", font=("Inter", 11, "bold"), text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"])).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        ctk.CTkLabel(header_frame, text="FILE NAME", font=("Inter", 11, "bold"), text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"])).grid(row=0, column=1, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(header_frame, text="DATE & TIME", font=("Inter", 11, "bold"), text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"])).grid(row=0, column=2, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(header_frame, text="ACTION", font=("Inter", 11, "bold"), text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"])).grid(row=0, column=3, padx=10, pady=8, sticky="e")

        scrollable_bar = ctk.CTkScrollableFrame(
            history_GUI,
            width=780,
            height=400,
            fg_color="transparent"
        )
        scrollable_bar.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        history_records = get_recent_downloads(limit=25)

        if not history_records:
            empty_label = ctk.CTkLabel(
                scrollable_bar,
                text="No download history found.",
                font=("Inter", 14),
                text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"])
            )
            empty_label.pack(pady=50)
            return

        for record in history_records:
            record_id = record[0]
            file_name = record[2]
            media_type = record[3]
            date_str = record[4]

            row_frame = ctk.CTkFrame(
                scrollable_bar,
                corner_radius=8,
                border_width=1,
                border_color=(COLORS["light"]["card_border"], COLORS["dark"]["card_border"])
            )
            row_frame.pack(fill="x", pady=4, padx=5)

            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=4)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=1)

            type_badge = ctk.CTkLabel(
                row_frame,
                text=f" {media_type.upper()} ",
                font=("Inter", 10, "bold"),
                fg_color="#1D9BF0" if media_type == "Video" else "#00BA7C",
                text_color="#FFFFFF",
                corner_radius=6
            )
            type_badge.grid(row=0, column=0, padx=10, pady=10, sticky="w")

            display_name = file_name if len(file_name) < 32 else file_name[:29] + "..."
            name_lbl = ctk.CTkLabel(row_frame, text=display_name, font=("Inter", 13), anchor="w")
            name_lbl.grid(row=0, column=1, padx=10, pady=10, sticky="w")

            date_lbl = ctk.CTkLabel(
                row_frame,
                text=date_str,
                font=("Inter", 11),
                text_color=(COLORS["light"]["placeholder"], COLORS["dark"]["placeholder"]),
                anchor="w"
            )
            date_lbl.grid(row=0, column=2, padx=10, pady=10, sticky="w")

            def handle_delete_row(rec_id=record_id):
                delete_download_record(rec_id)
                history_GUI.destroy()
                self.download_history_window()

            delete_btn = ctk.CTkButton(
                row_frame,
                text="✕",
                font=("Inter", 12, "bold"),
                width=28,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color=("#FFEBEE", "#3C1E1E"),
                text_color=("#E53935", "#FF6B6B"),
                command=handle_delete_row
            )
            delete_btn.grid(row=0, column=3, padx=10, pady=8, sticky="e")