import threading
import customtkinter

from logger import Log
from PIL import Image, ImageTk

from Options import Options_toplevel
from Pomodoro_frame import Pomodoro_frame

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.logger = Log()
        self.title("Pomodoro Clock")
        self.geometry("600x200")
        self.icon = ImageTk.PhotoImage(Image.open('clock.ico'))
        self.iconphoto(True, self.icon)

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.timer = Pomodoro_frame(root=self, logger=self.logger)
        self.timer.grid(column=0, row=0, columnspan=2)
        self.thread_watcher = {
            "num": 0,
            "obj": [],
            "stop_flags": [],
            "events": []
        }

        self.pomodoro_counter = customtkinter.CTkLabel(self, 
                                                       textvariable=self.timer.pomodoro_string,
                                                       font=('Arial', 16)) 
        self.pomodoro_counter.grid(column=0, rows=1, sticky='NW', padx=(60,0))

        self.switch = customtkinter.CTkSwitch(self,
                                              text="Start / Pause", 
                                              command=self.play_pause, 
                                              font=('Arial', 16),
                                              state='disabled')
        self.switch.grid(row=1, column=1, sticky='NE', padx=(0,60))

        self.option_button = customtkinter.CTkButton(self,
                                                     width=60,
                                                     height=30,
                                                     text="Options",
                                                     font=('Arial', 12),
                                                     command=self.pop_options)
        self.option_button.grid(row=2, column=1, sticky='N', pady=(0,20), padx=(40, 0))

        # Load settings from settings.json
        self.settings = self.timer.deserialize_settings("settings.json")


    def play_pause(self):
        if not self.timer.start:
            self.thread_watcher["events"][-1].set() 
        self.timer.start = not self.timer.start


    def pop_options(self):
        self.Options = Options_toplevel(root=self, settings=self.settings)


    def start_countdown(self):
        # print(f"threads: {threading.active_count()}")
        self.thread_watcher["events"].append(threading.Event())
        self.thread_watcher["stop_flags"].append(False)
        self.thread_watcher["obj"].append(threading.Thread(name='countdown', 
                                             target=self.timer.countdown,
                                             args=(self.thread_watcher["num"], self.thread_watcher["events"], self.thread_watcher["stop_flags"]),
                                             daemon=False))
        self.thread_watcher["obj"][-1].start()
        self.thread_watcher["num"] += 1


    def cleanup(self):
        print(f"threads: {threading.active_count()}")
        for i, val in enumerate(self.thread_watcher["stop_flags"]):
            self.thread_watcher["stop_flags"][i] = True

        for i, val in enumerate(self.thread_watcher["events"]):
            if not self.thread_watcher["events"][i].is_set():
                self.thread_watcher["events"][i].set()


if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.cleanup()
