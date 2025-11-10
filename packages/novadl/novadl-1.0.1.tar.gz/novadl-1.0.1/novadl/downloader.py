import yt_dlp
import sys
import re
from pathlib import Path
import platform
import os
import random
import string
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Static, ProgressBar, Label, Switch
from textual.binding import Binding
from textual import work
from rich.text import Text

# --- Utility Functions ---

def is_termux():
    """Check if running on Termux"""
    return os.path.exists("/data/data/com.termux/files/home")

def check_termux_api_app():
    """Check if Termux:API app (APK) is installed"""
    try:
        result = subprocess.run(
            ["cmd", "package", "list", "packages"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "com.termux.api" in result.stdout
    except:
        return False

def check_termux_api_package():
    """Check if termux-api package is installed"""
    try:
        result = subprocess.run(
            ["pkg", "list-installed"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "termux-api" in result.stdout
    except:
        return False

def open_url_termux(url):
    """Open URL using termux-open-url"""
    try:
        subprocess.run(["termux-open-url", url], check=False, timeout=5)
        return True
    except:
        return False

def setup_termux_api():
    """Guide user through Termux API installation"""
    print("\n" + "="*60)
    print("📱 TERMUX API SETUP REQUIRED")
    print("="*60)
    print("\nNova Downloader needs Termux API to work properly.")
    print("This allows downloaded files to appear in your gallery/music app.")
    
    apk_url = "https://f-droid.org/repo/com.termux.api_1002.apk"
    
    # Check what's missing
    has_app = check_termux_api_app()
    has_package = check_termux_api_package()
    
    if not has_app:
        print("\n❌ Termux:API app (APK) is NOT installed")
        print("\n🔧 Step 1: Install Termux:API app")
        print("="*60)
        print(f"Opening download page: {apk_url}")
        
        if open_url_termux(apk_url):
            print("✅ Browser opened successfully!")
        else:
            print(f"⚠️ Could not open browser automatically.")
            print(f"Please manually visit: {apk_url}")
        
        print("\n📥 Download and install the APK from your browser")
        print("="*60)
        
        while True:
            response = input("\n✓ Have you installed the Termux:API app? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                print("\n🔍 Checking for Termux:API app...")
                if check_termux_api_app():
                    print("✅ Termux:API app detected!")
                    has_app = True
                    break
                else:
                    print("❌ Termux:API app not found.")
                    retry = input("Check again? (yes/no): ").strip().lower()
                    if retry not in ['yes', 'y']:
                        print("\n⚠️ Continuing without Termux API...")
                        return False
            
            elif response in ['no', 'n']:
                cont = input("Continue anyway? (files won't auto-appear in gallery) (yes/no): ").strip().lower()
                if cont in ['yes', 'y']:
                    print("⚠️ Continuing without Termux API...\n")
                    return False
                else:
                    print("❌ Installation cancelled. Exiting.")
                    sys.exit(0)
            else:
                print("❌ Please answer 'yes' or 'no'")
    
    if not has_package:
        print("\n❌ termux-api package is NOT installed")
        print("\n🔧 Step 2: Install termux-api package")
        print("="*60)
        print("Run this command in Termux:")
        print("   → pkg install termux-api")
        print("="*60)
        
        while True:
            response = input("\n✓ Have you installed the termux-api package? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                print("\n🔍 Checking for termux-api package...")
                if check_termux_api_package():
                    print("✅ termux-api package detected!")
                    has_package = True
                    break
                else:
                    print("❌ termux-api package not found.")
                    print("Make sure you ran: pkg install termux-api")
                    retry = input("Check again? (yes/no): ").strip().lower()
                    if retry not in ['yes', 'y']:
                        print("\n⚠️ Continuing without Termux API...")
                        return False
            
            elif response in ['no', 'n']:
                cont = input("Continue anyway? (files won't auto-appear in gallery) (yes/no): ").strip().lower()
                if cont in ['yes', 'y']:
                    print("⚠️ Continuing without Termux API...\n")
                    return False
                else:
                    print("❌ Installation cancelled. Exiting.")
                    sys.exit(0)
            else:
                print("❌ Please answer 'yes' or 'no'")
    
    return has_app and has_package

def clean_url(url: str) -> str:
    if "shorts/" in url:
        vid = url.split("shorts/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={vid}"
    if "watch?v=" in url:
        return url.split("&")[0]
    return url

def format_duration(seconds: int) -> str:
    m, s = divmod(seconds or 0, 60)
    return f"{int(m)}:{int(s):02d}"

def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)

def get_silent_logger():
    class SilentLogger:
        def debug(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
    return SilentLogger()

def trigger_media_scan(file_path):
    """Trigger Android media scanner to index the file"""
    if is_termux() and check_termux_api_package():
        try:
            subprocess.run(["termux-media-scan", str(file_path)], check=False, timeout=5)
        except:
            pass

def get_unique_filename(folder: Path, base_name: str, extension: str) -> tuple[Path, bool]:
    """Generate a unique filename by appending random characters if file exists
    Returns: (file_path, was_renamed)"""
    file_path = folder / f"{base_name}.{extension}"
    
    if not file_path.exists():
        return file_path, False
    
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    new_path = folder / f"{base_name}_{suffix}.{extension}"
    while new_path.exists():
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        new_path = folder / f"{base_name}_{suffix}.{extension}"
    return new_path, True

# --- Downloader App ---

class NovaDownloaderApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #url-input {
        margin-bottom: 1;
    }
    
    #options-container {
        height: auto;
        margin-bottom: 1;
        width: 100%;
    }
    
    .option-row {
        height: auto;
        margin-bottom: 1;
        width: 100%;
    }
    
    .option-label {
        width: 1fr;
    }
    
    .option-switch {
        width: auto;
        dock: right;
    }
    
    Switch {
        background: $panel;
    }
    
    Switch:focus {
        background: $panel;
    }
    
    Switch.-on {
        background: $success;
    }
    
    Switch.-on:focus {
        background: $success;
    }
    
    #info-panel {
        border: solid $primary;
        padding: 1 2;
        margin-bottom: 1;
        height: auto;
    }
    
    #progress-container {
        height: auto;
        margin-bottom: 1;
    }
    
    #status-label {
        margin-bottom: 1;
    }
    
    #progress-bar {
        margin-bottom: 1;
    }
    
    #button-container {
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    
    .success {
        color: $success;
    }
    
    .error {
        color: $error;
    }
    
    .info {
        color: $accent;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.video_info = None
        self.base_folder = self.get_download_folder()
        
    def get_download_folder(self):
        if os.path.exists("/data/data/com.termux/files/home/storage"):
            return Path.home() / "storage/downloads/Nova_Downloader"
        elif platform.system().lower() == "windows":
            return Path("D:/Downloads/Nova_Downloader")
        else:
            return Path.home() / "Downloads/Nova_Downloader"
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="main-container"):
            yield Static("🎥 Nova Downloader 🎥", id="title")
            
            yield Input(placeholder="Enter YouTube/Video URL here...", id="url-input")
            
            with Vertical(id="options-container"):
                with Horizontal(classes="option-row"):
                    yield Label("Audio Only", classes="option-label")
                    yield Switch(id="audio-switch", classes="option-switch")
                
                with Horizontal(classes="option-row"):
                    yield Label("Auto Open After Download", classes="option-label")
                    yield Switch(id="open-switch", classes="option-switch")
            
            with Container(id="info-panel"):
                yield Static("Enter a URL and click Download to begin", id="info-display")
            
            with Container(id="progress-container"):
                yield Static("Ready to download", id="status-label")
                yield ProgressBar(total=100, show_eta=False, id="progress-bar")
            
            with Horizontal(id="button-container"):
                yield Button("Download", variant="success", id="download-btn")
                yield Button("Clear", variant="default", id="clear-btn")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-btn":
            self.start_download()
        elif event.button.id == "clear-btn":
            self.clear_all()
    
    def clear_all(self) -> None:
        self.query_one("#url-input", Input).value = ""
        self.query_one("#info-display", Static).update("Enter a URL and click Download to begin")
        self.query_one("#status-label", Static).update("Ready to download")
        self.query_one("#progress-bar", ProgressBar).update(progress=0)
        self.video_info = None
    
    @work(thread=True)
    def start_download(self) -> None:
        url_input = self.query_one("#url-input", Input)
        info_display = self.query_one("#info-display", Static)
        status_label = self.query_one("#status-label", Static)
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        
        url = url_input.value.strip()
        if not url:
            self.call_from_thread(info_display.update, Text("⚠️ Please enter a URL", style="bold red"))
            return
        
        self.call_from_thread(status_label.update, "🔍 Fetching video info...")
        self.call_from_thread(progress_bar.update, progress=0)
        
        url = clean_url(url)
        audio_only = self.query_one("#audio-switch", Switch).value
        open_after = self.query_one("#open-switch", Switch).value
        
        preview_opts = {
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0',
            'http_headers': {'User-Agent': 'Mozilla/5.0'},
            'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4' if not audio_only else None,
        }
        
        try:
            with yt_dlp.YoutubeDL(preview_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            entries = info.get('entries') or [info]
            item = entries[0]
            
            self.video_info = info
            
            platform_name = info.get('extractor_key', 'Unknown').capitalize()
            if audio_only:
                abr = item.get('abr') or item.get('tbr') or 0
                sel_quality = f"{int(abr)} kbps" if abr else 'Audio only'
            else:
                reqs = info.get('requested_formats') or []
                vf = next((f for f in reqs if f.get('vcodec') != 'none'), {})
                height = vf.get('height')
                fps = vf.get('fps')
                sel_quality = f"{height}p {fps}fps" if height else 'Best'
            
            info_text = Text()
            info_text.append("🌐 Platform: ", style="bold cyan")
            info_text.append(f"{platform_name}\n")
            info_text.append("🎵 Title: ", style="bold cyan")
            info_text.append(f"{item.get('title')}\n")
            info_text.append("⏱️ Duration: ", style="bold cyan")
            info_text.append(f"{format_duration(item.get('duration'))}\n")
            info_text.append("📶 Quality: ", style="bold cyan")
            info_text.append(f"{sel_quality}\n")
            info_text.append("🎚️ Mode: ", style="bold cyan")
            info_text.append(f"{'Audio' if audio_only else 'Video'}\n")
            info_text.append("📁 Save to: ", style="bold cyan")
            info_text.append(f"{self.base_folder}")
            
            self.call_from_thread(info_display.update, info_text)
            self.call_from_thread(status_label.update, "✅ Info fetched - Starting download...")
            
        except Exception as e:
            error_text = Text(f"❌ Error: {str(e)}", style="bold red")
            self.call_from_thread(info_display.update, error_text)
            self.call_from_thread(status_label.update, "Error fetching info")
            return
        
        for e in entries:
            title = re.sub(r'[<>:"/\\|?*]', '', e.get('title', 'Untitled'))
            
            self.call_from_thread(status_label.update, f"📥 Downloading: {title}")
            
            self.base_folder.mkdir(parents=True, exist_ok=True)
            
            temp_template = str(self.base_folder / '%(title)s_TEMP_%(id)s.%(ext)s')
            
            def progress_hook(d):
                if d.get('status') == 'downloading':
                    raw_pct = d.get('_percent_str', '0.0%')
                    clean_pct_str = strip_ansi(raw_pct).strip().replace('%','')
                    try:
                        pct = float(clean_pct_str)
                    except ValueError:
                        pct = 0
                    
                    speed = strip_ansi(d.get('_speed_str', '')).strip()
                    eta_seconds = d.get('eta')
                    eta = ''
                    if isinstance(eta_seconds, (int, float)):
                        m, s = divmod(eta_seconds, 60)
                        eta = f"{int(m)}:{int(s):02d}"
                    
                    self.call_from_thread(progress_bar.update, progress=pct)
                    self.call_from_thread(status_label.update, 
                                        f"📥 Downloading: {pct:.1f}% | {speed} | ETA {eta}")
            
            logger = get_silent_logger()
            
            opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': False,
                'nopart': True,
                'user_agent': 'Mozilla/5.0',
                'http_headers': {'User-Agent': 'Mozilla/5.0'},
                'progress_hooks': [progress_hook],
                'logger': logger,
                'outtmpl': temp_template,
                'writethumbnail': True,
            }
            
            if audio_only:
                opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        },
                        {
                            'key': 'FFmpegMetadata',
                            'add_metadata': True,
                        },
                    ],
                })
            else:
                opts.update({
                    'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'postprocessors': [
                        {
                            'key': 'FFmpegMetadata',
                            'add_metadata': True,
                        },
                    ],
                })
            
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([e.get('url') or e.get('webpage_url')])
                
                file_ext = 'mp3' if audio_only else 'mp4'
                temp_files = list(self.base_folder.glob(f"{title}_TEMP_*.{file_ext}"))
                
                if temp_files:
                    temp_file = temp_files[0]
                    final_path, was_renamed = get_unique_filename(self.base_folder, title, file_ext)
                    temp_file.rename(final_path)
                    
                    trigger_media_scan(str(final_path))
                    
                    info_text.append("\n\n💾 Saved as: ", style="bold green")
                    info_text.append(f"{final_path.name}\n")
                    if was_renamed:
                        info_text.append("⚠️ File with same name existed, random suffix added", style="bold yellow")
                    
                    self.call_from_thread(info_display.update, info_text)
                    self.call_from_thread(status_label.update, f"✅ Download complete!")
                    self.call_from_thread(progress_bar.update, progress=100)
                    
                    if open_after:
                        if platform.system().lower() == "windows":
                            os.startfile(final_path)
                        elif platform.system().lower() == "darwin":
                            os.system(f"open '{final_path}'")
                        else:
                            os.system(f"xdg-open '{final_path}'")
                
            except Exception as e:
                error_msg = f"❌ Download failed: {str(e)}"
                self.call_from_thread(status_label.update, error_msg)
                return
        
        self.call_from_thread(status_label.update, "🎉 All downloads complete!")

# --- Main Entry Point ---

def main():
    """Main entry point for the novadl command"""
    if is_termux():
        has_app = check_termux_api_app()
        has_package = check_termux_api_package()
        
        if has_app and has_package:
            print("✅ Termux API fully configured!\n")
        else:
            setup_success = setup_termux_api()
            if not setup_success:
                print("⚠️ Warning: Downloads will work, but files may not appear in gallery immediately.\n")
    
    app = NovaDownloaderApp()
    app.run()

if __name__ == '__main__':
    main()
