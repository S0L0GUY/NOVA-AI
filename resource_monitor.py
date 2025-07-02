import psutil
import threading
import GPUtil
import customtkinter as ctk
import time
import datetime
from constants import ResourceMonitor

# Setup CustomTkinter
ctk.set_appearance_mode(ResourceMonitor.APPEARANCE_MODE)
ctk.set_default_color_theme(ResourceMonitor.COLOR_THEME)


class SystemMonitor(ctk.CTk):
    def __init__(self) -> None:
        """Initialize the System Monitor GUI."""
        super().__init__()

        self.title(ResourceMonitor.WINDOW_TITLE)
        self.geometry(ResourceMonitor.WINDOW_SIZE)
        self.resizable(False, False)

        # Make the window always stay on top
        self.attributes("-topmost", True)

        # Start time for uptime calculation
        self.start_time = time.time()

        # Frames for each stat
        self.cpu_label = self.create_stat_frame(
            "CPU Usage",
            ResourceMonitor.CPU_COLOR
            )
        self.ram_label = self.create_stat_frame(
            "RAM Usage",
            ResourceMonitor.RAM_COLOR
            )
        self.disk_label = self.create_stat_frame(
            "Disk Usage",
            ResourceMonitor.DISK_COLOR
            )
        self.gpu_label = self.create_stat_frame(
            "GPU Load",
            ResourceMonitor.GPU_COLOR
            )
        self.gpu_mem_label = self.create_stat_frame(
            "GPU Memory",
            ResourceMonitor.GPU_MEM_COLOR
            )
        self.net_label = self.create_stat_frame(
            "Network Usage",
            ResourceMonitor.NETWORK_COLOR
            )
        self.uptime_label = self.create_stat_frame(
            "Program Uptime",
            ResourceMonitor.UPTIME_COLOR
            )

        self.update_stats()

    def create_stat_frame(
            self,
            label_text: str,
            border_color: str
            ) -> "ctk.CTkLabel":
        """
        Creates a styled frame with a title label and a value label.
        Args:
            label_text (str): The text to display in the title label.
            border_color (str): The color of the border for the frame.
        Returns:
            ctk.CTkLabel: The value label widget, initialized with "Loading..."
            text.
        """

        frame = ctk.CTkFrame(
            self, corner_radius=15, border_width=2, border_color=border_color
            )
        frame.pack(pady=10, padx=20, fill="x")

        title_label = ctk.CTkLabel(
            frame, text=label_text, font=("Segoe UI", 18)
            )
        title_label.pack(pady=(10, 5))
        value_label = ctk.CTkLabel(
            frame, text="Loading...", font=("Segoe UI", 24, "bold")
            )
        value_label.pack(pady=(0, 10))

        return value_label

    def get_gpu_usage(self) -> tuple[float, float]:
        """Fetch GPU load and memory usage."""
        gpus = GPUtil.getGPUs()
        if not gpus:
            return 0, 0

        return gpus[0].load * 100, gpus[0].memoryUtil * 100

    def get_uptime(self) -> str:
        """Calculate program uptime in hours, minutes, and seconds."""
        elapsed_time = time.time() - self.start_time
        uptime = str(datetime.timedelta(seconds=int(elapsed_time)))

        return uptime

    def update_stats(self) -> None:
        """Fetch and update all stats every second."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        net_io = psutil.net_io_counters()
        net_usage = (net_io.bytes_sent + net_io.bytes_recv) / 1e6
        gpu_load, gpu_mem = self.get_gpu_usage()
        uptime = self.get_uptime()

        # Update labels
        self.cpu_label.configure(text=f"{cpu:.1f}%")
        self.ram_label.configure(text=f"{ram:.1f}%")
        self.disk_label.configure(text=f"{disk:.1f}%")
        self.gpu_label.configure(text=f"{gpu_load:.1f}%")
        self.gpu_mem_label.configure(text=f"{gpu_mem:.1f}%")
        self.net_label.configure(text=f"{net_usage:.2f} MB")
        self.uptime_label.configure(text=f"{uptime}")

        # Schedule next update
        self.after(ResourceMonitor.UPDATE_INTERVAL, self.update_stats)


def run_monitor() -> None:
    app = SystemMonitor()
    app.mainloop()


if __name__ == "__main__":
    monitor_thread = threading.Thread(target=run_monitor)
    monitor_thread.start()
