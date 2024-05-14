import json
import threading
import simpleaudio
import customtkinter

from logger import Log
from pathlib import Path
from PIL import Image, ImageTk

from Options import Options_toplevel
from Pomodoro_frame import Pomodoro_frame

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.logger = Log()
        self.title("Pomodoro Clock")
        self.geometry("570x200")
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

        self.pomodoro_counter_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.pomodoro_counter_frame.columnconfigure(0, weight=1)
        self.pomodoro_counter_frame.columnconfigure(1, weight=1)

        self.pomodoro_counter_image = customtkinter.CTkImage(Image.open("tomato.png"), size=(20, 20))
        self.pomodoro_counter_image_label = customtkinter.CTkLabel(self.pomodoro_counter_frame, image=self.pomodoro_counter_image, text="")

        self.pomodoro_counter_text = customtkinter.CTkLabel(self.pomodoro_counter_frame, 
                                                            textvariable=self.timer.pomodoro_string,
                                                            font=('Arial', 16)) 

        self.pomodoro_counter_image_label.grid(column=0, row=0, padx=(5,10))
        self.pomodoro_counter_text.grid(column=1, row=0)
        self.pomodoro_counter_frame.grid(column=0, rows=1, sticky='NW', padx=(60,0))

        self.switch = customtkinter.CTkSwitch(self,
                                              text="Start / Pause", 
                                              command=self.play_pause, 
                                              font=('Arial', 16),
                                              state='disabled')
        self.switch.grid(row=1, column=1, sticky='NE', padx=(0,65))

        self.option_button = customtkinter.CTkButton(self,
                                                     width=60,
                                                     height=30,
                                                     text="Options",
                                                     font=('Arial', 12),
                                                     command=self.pop_options)
        self.option_button.grid(row=2, column=1, sticky='N', pady=(0,20), padx=(35, 0))
        self.skip_break_button = customtkinter.CTkButton(self,
                                                         width=60,
                                                         height=30,
                                                         text="Skip Break",
                                                         fg_color="#de333e",
                                                         hover_color="#b02c35",
                                                         font=('Arial', 12),
                                                         command=self.skip_break,
                                                         state='disabled')
        self.skip_break_button.grid(row=2, column=0, sticky='N', pady=(0,20), padx=(0, 35))

        # Load settings from settings.json and start timer countdown thread
        self.settings = self.deserialize_settings("settings.json")
        # if 1 then error happend when deserializing
        if self.settings != 1:
            self.main_thread_maker()

    def deserialize_settings(self, settings_file):
        json_data = None

        if (not Path().cwd().joinpath(settings_file).exists()):
            self.logger.logObj.error(f"Settings file {settings_file} does not exist.")
            return 1
        
        with open(settings_file, "r") as fp_settings:
            json_data = json.load(fp_settings)

        if not False in [i in json_data.keys() for i in ["study_time", "break_time", "long_break_time", "until_long_break_num", "notification_filename"]]:
            self.timer.update_times(tuple(json_data["study_time"]), tuple(json_data["break_time"]),
                                    tuple(json_data["long_break_time"]), json_data["until_long_break_num"])

            if json_data["notification_filename"] != "None":
                self.timer.wave_obj = simpleaudio.WaveObject.from_wave_file(json_data["notification_filename"])
        else:
            self.logger.logObj.error(f"{settings_file} file is not configured correctly")
            return 1


        return json_data
    
    def serialize_settings(self, settings_file):
        if self.settings == 1 or not Path().cwd().joinpath(settings_file).exists() or \
           False in [i in self.settings.keys() for i in ["study_time", "break_time", "long_break_time", "until_long_break_num", "notification_filename"]]:
            self.logger.logObj.error(f"Can't serialize data into {settings_file}")
            return 1
        
        with open(settings_file, "w") as fp_settings:
            fp_settings.wirte(json.dumps(self.settings, indent=4))


    def play_pause(self):
        if not self.timer.start:
            self.thread_watcher["events"][-1].set() 
        self.timer.start = not self.timer.start


    def skip_break(self):
        self.timer.skip_break = True


    def pop_options(self):
        self.Options = Options_toplevel(root=self, settings=self.settings)


    def main_thread_maker(self):
        if threading.active_count() > 1:
            # If we are paused then unpause with switch
            if not self.timer.start:
                self.switch.toggle()
            # Kill the thread
            self.thread_watcher["stop_flags"][-1] = True

        self.start_countdown()
        self.switch.configure(state='normal')
        self.switch.toggle()


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
        # print(f"threads: {threading.active_count()}")
        for i, val in enumerate(self.thread_watcher["stop_flags"]):
            self.thread_watcher["stop_flags"][i] = True

        for i, val in enumerate(self.thread_watcher["events"]):
            if not self.thread_watcher["events"][i].is_set():
                self.thread_watcher["events"][i].set()


if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.cleanup()
