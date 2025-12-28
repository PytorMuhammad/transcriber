from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.theme import Theme
import datetime

# Elite Theme
theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "brand": "bold magenta"
})

console = Console(theme=theme)

def welcome_banner():
    """Displays a premium welcome banner."""
    banner = """
  _____                               _ _               
 |_   _| __ __ _ _ __  ___  ___ _ __(_) |__   ___ _ __ 
   | || '__/ _` | '_ \/ __|/ __| '__| | '_ \ / _ \ '__|
   | || | | (_| | | | \__ \ (__| |  | | |_) |  __/ |   
   |_||_|  \__,_|_| |_|___/\___|_|  |_|_.__/ \___|_|   
                                                        
    """
    console.print(Panel(banner, border_style="brand", title="[bold white]V1.0.0[/bold white]"))
    console.print(f"[brand]Elite Transcriber Tool - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/brand]\n")

def log_info(message: str):
    console.print(f"[info]ℹ[/info] {message}")

def log_success(message: str):
    console.print(f"[success]✔[/success] {message}")

def log_warning(message: str):
    console.print(f"[warning]⚠[/warning] {message}")

def log_error(message: str):
    console.print(f"[error]✖[/error] {message}")

def get_progress():
    """Returns a rich progress bar instance."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        console=console
    )
