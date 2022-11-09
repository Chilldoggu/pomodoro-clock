import customtkinter
import tkinter
import threading
import simpleaudio
from time import strftime, sleep

class Pomodoro_frame(customtkinter.CTkFrame):
    start = True
    study = True
    wave_obj = None

    def __init__(self):
        super().__init__()
        self.study_time = self.break_time = None
        self.pomodoros = 0
        self.pomodoro_string = tkinter.StringVar(value="🍅Pomodoros: 0")
        self.string_time = tkinter.StringVar(value="Setup needed")
        self.time_counter = customtkinter.CTkLabel(self,
                                                   textvariable=self.string_time,
                                                   text_font=('Arial', 40, 'bold'))
        self.time_counter.pack(padx=30, pady=15)

    def update_times(self, new_study_time, new_break_time):
        self.study_time = new_study_time
        self.break_time = new_break_time

    def countdown(self, event):
        while True:
            if self.study:
                hours, minutes, seconds = self.study_time[3], self.study_time[4], self.study_time[5]
            else:
                hours, minutes, seconds = self.break_time[3], self.break_time[4], self.break_time[5]

            for h in range(hours, -1, -1):
                for m in range(minutes, -1, -1):
                    for s in range(seconds, -1, -1):
                        if self.study:
                            self.string_time.set("📖"+strftime("%H : %M : %S", (0, 0, 0, h, m, s, 0, 0, 0))+"📖")
                        else:
                            self.string_time.set("🍵"+strftime("%H : %M : %S", (0, 0, 0, h, m, s, 0, 0, 0))+"🍵")
                        for i in range(10):
                            self.after(100, self.update())
                        if not self.start:
                            event.wait()
                            event.clear()
                    if m:
                        seconds = 59
                if h:
                    minutes = 59
            if self.study:
                self.pomodoros += 1
                self.pomodoro_string.set("🍅Pomodoros: " + str(self.pomodoros))
            self.study = not self.study
            # Daj delay na zagranie sygnalu dzwiekowego konca nauki/przerwy
            if self.wave_obj:
                play_obj = self.wave_obj.play()
                play_obj.wait_done()
