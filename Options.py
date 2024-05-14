import json
import tkinter
import simpleaudio
import customtkinter

from time import sleep
from pathlib import Path
from tkinter import filedialog

class Options_slider_frame(customtkinter.CTkFrame):
    def __init__(self, top_level, default_value, time_string, range=(0, 120)):
        self.new_time = tkinter.IntVar(value=default_value)
        self.new_time_string = tkinter.StringVar()
        self.new_time_string.set(time_string+str(self.new_time.get()))
        self.time_string_default = time_string

        super().__init__(top_level)

        self.label = customtkinter.CTkLabel(self,
                                            textvariable=self.new_time_string,
                                            font=('Arial', 12))
        self.label.pack(side='top', pady=(5,0))

        self.slider = customtkinter.CTkSlider(self, 
                                              height=20,
                                              from_=range[0], 
                                              to=range[1],
                                              variable=self.new_time,
                                              command=self.change_slider,
                                              number_of_steps=24)
        self.slider.pack(side='left', padx=10, pady=10)
        

    def change_slider(self, *args):
        self.new_time_string.set(self.time_string_default+str(self.new_time.get()))


class Options_toplevel():
    def __init__(self, root, settings):
        self.root = root
        top_level = customtkinter.CTkToplevel() 
        top_level.title("Options")

        self.notification_filename = None

        if settings != 1:
            study_time = settings["study_time"][3] * 60 + settings["study_time"][4]
            break_time = settings["break_time"][3] * 60 + settings["break_time"][4]
            long_break_time = settings["long_break_time"][3] * 60 + settings["long_break_time"][4]
            until_long_break = settings["until_long_break_num"]
        else:
            study_time = 50
            break_time = 10
            long_break_time = 20
            until_long_break = 3


        self.study_frame = Options_slider_frame(top_level, default_value=study_time, time_string="Study time: ")
        self.break_frame = Options_slider_frame(top_level, default_value=break_time, time_string="Break time: ")
        self.long_break_frame = Options_slider_frame(top_level, default_value=long_break_time, time_string="Long break time: ")
        self.until_long_break_frame = Options_slider_frame(top_level, default_value=until_long_break, time_string="Sessions until long break: ", range=(1, 10))
        self.study_frame.pack(pady=(30, 0), padx=30)
        self.break_frame.pack(pady=(30, 0), padx=30)
        self.long_break_frame.pack(pady=(30,0), padx=30)
        self.until_long_break_frame.pack(pady=(30,0), padx=30)
        
        self.upload_music = customtkinter.CTkButton(top_level, 
                                                    text="Add music",
                                                    fg_color="#de333e",
                                                    hover_color="#b02c35",
                                                    command=self.add_music)
        self.upload_music.pack(pady=(30,0), padx=30)

        self.submit_button = customtkinter.CTkButton(top_level, text="Submit", command=self.submit)
        self.submit_button.pack(pady=(30,30), padx=30)


    def add_music(self):
        filetypes = (('wav files', '*.wav'),)
        # Get path relative to current working directory (useful when saving to settings.json)
        self.notification_filename = Path(filedialog.askopenfilename(title='Pick your song',
                                                      initialdir='.',
                                                      filetypes=filetypes)).relative_to(Path().cwd())
        if self.notification_filename:
            # print(filename)
            self.root.timer.wave_obj = simpleaudio.WaveObject.from_wave_file(str(self.notification_filename))        


    def submit(self):
        # (0, 0, 0, h, m, s, 0, 0, 0)
        study_minutes = self.study_frame.new_time.get()
        break_minutes = self.break_frame.new_time.get()
        long_break_minutes = self.long_break_frame.new_time.get()
        until_long_break_num = self.until_long_break_frame.new_time.get()
        notification_filename = str(self.notification_filename)

        study_time      = (0, 0, 0, int(study_minutes/60), study_minutes % 60, 0, 0, 0, 0)
        break_time      = (0, 0, 0, int(break_minutes/60), break_minutes % 60, 0, 0, 0, 0)
        long_break_time = (0, 0, 0, int(long_break_minutes/60), long_break_minutes % 60, 0, 0, 0, 0)

        self.root.timer.update_times(study_time, break_time, long_break_time, until_long_break_num)

        json_data = {}
        json_data["study_time"]            = study_time
        json_data["break_time"]            = break_time
        json_data["long_break_time"]       = long_break_time
        json_data["until_long_break_num"]  = until_long_break_num
        json_data["notification_filename"] = notification_filename

        # Save to json
        with open("settings.json", "w") as settings_file:
            settings_file.write(json.dumps(json_data, indent=4))

        self.root.main_thread_maker() 

