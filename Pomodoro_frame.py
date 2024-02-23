import customtkinter
import tkinter

from time import strftime
from datetime import date
from PIL import Image, ImageTk

class Pomodoro_frame(customtkinter.CTkFrame):
    start = True
    study = True
    wave_obj = None

    def __init__(self, root, logger = None):
        super().__init__(root)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.root = root
        self.logger = logger
        self.study_time = self.break_time = None
        self.pomodoros = self.get_today_pomodoros()
        self.pomodoro_string = tkinter.StringVar(value=f"Pomodoros: {self.pomodoros}")
        self.string_time = tkinter.StringVar(value="Setup needed")

        self.time_counter = customtkinter.CTkLabel(self,
                                                   textvariable=self.string_time,
                                                   font=('Arial', 40, 'bold'))

        self.study_image = customtkinter.CTkImage(Image.open("book.png"), size=(60, 60))
        self.break_image = customtkinter.CTkImage(Image.open("teacup.png"), size=(60, 60))
        self.study_image_label1 = customtkinter.CTkLabel(self, image=self.study_image, text="")
        self.study_image_label2 = customtkinter.CTkLabel(self, image=self.study_image, text="")
        self.break_image_label1 = customtkinter.CTkLabel(self, image=self.break_image, text="")
        self.break_image_label2 = customtkinter.CTkLabel(self, image=self.break_image, text="")

        self.time_counter.grid(column=1, row=0, padx=0, pady=15)
        

    def update_times(self, new_study_time, new_break_time, new_long_break_time, new_until_long_break):
        self.study_time = new_study_time
        self.break_time = new_break_time
        self.long_break_time = new_long_break_time
        self.until_long_break = new_until_long_break


    def get_today_pomodoros(self):
        pomodoros = 0
        date_today = date.today().isoformat()
        with open("logs.log", "r") as fp_log:
            for line in fp_log:
                line = line.rstrip()
                if date_today in line and "Finished study session." in line:
                    pomodoros += 1
        return pomodoros


    def countdown(self, id, events, stop_flags):
        while True:
            # If it's time for a session
            if self.study:
                self.study_image_label1.grid(column=0, row=0, padx=30, pady=15)
                self.study_image_label2.grid(column=2, row=0, padx=30, pady=15)
                self.logger.logObj.info(f"Starting {self.study_time[3]}H:{self.study_time[4]}M:{self.study_time[5]}S study session.")
                hours, minutes, seconds = self.study_time[3], self.study_time[4], self.study_time[5]
            # If it's time for long break
            elif self.pomodoros % self.until_long_break == 0:
                self.break_image_label1.grid(column=0, row=0, padx=30, pady=15)
                self.break_image_label2.grid(column=2, row=0, padx=30, pady=15)
                self.logger.logObj.info(f"Starting {self.long_break_time[3]}H:{self.long_break_time[4]}M:{self.long_break_time[5]}S long break")
                hours, minutes, seconds = self.long_break_time[3], self.long_break_time[4], self.long_break_time[5]
            # If it's time for normal break
            else:
                self.break_image_label1.grid(column=0, row=0, padx=30, pady=15)
                self.break_image_label2.grid(column=2, row=0, padx=30, pady=15)
                self.logger.logObj.info(f"Starting {self.break_time[3]}H:{self.break_time[4]}M:{self.break_time[5]}S short break")
                hours, minutes, seconds = self.break_time[3], self.break_time[4], self.break_time[5]

            # # If m >= 60, then add time to h
            # if minutes >= 60:
            #     hours = int(minutes/60)
            #     minutes = minutes%60

            # Start the countdown
            for h in range(hours, -1, -1):
                for m in range(minutes, -1, -1):
                    for s in range(seconds, -1, -1):
                        if self.study:
                            self.string_time.set(strftime("%H : %M : %S", (1, 1, 1, h, m, s, 1, 1, 1)))
                        else:
                            self.string_time.set(strftime("%H : %M : %S", (1, 1, 1, h, m, s, 1, 1, 1)))
                        for i in range(10):
                            self.after(100, self.update())
                        # Pause if pause/start switch has been toggled
                        # print(f"Stop flag? {stop_flags[id]}")
                        if stop_flags[id]:
                            # print("Stopped")
                            self.logger.logObj.info(f"Closing thread")
                            return 0
                        if not self.start:
                            # print("Paused inside thread")
                            self.logger.logObj.info(f"Paused")
                            events[id].wait()
                            events[id].clear()
                            self.logger.logObj.info(f"Unpaused")
                        if stop_flags[id]:
                            # print("Stopped")
                            self.logger.logObj.warning(f"Closing thread")
                            return 0
                    if m:
                        seconds = 59
                if h:
                    minutes = 59
                    seconds = 59
            
            # When finished studying add pomodoro else if finished break stop running the clock until client wants
            # to start another session.
            if self.study:
                self.logger.logObj.info(f"Finished study session.")
                self.pomodoros += 1
                self.pomodoro_string.set("🍅Pomodoros: " + str(self.pomodoros))
            elif self.pomodoros % self.until_long_break == 0:
                self.logger.logObj.info(f"Finished long break")
                self.root.switch.toggle()
            else:
                self.logger.logObj.info(f"Finished short break")
                self.root.switch.toggle()

            self.study = not self.study
            # Daj delay na zagranie sygnalu dzwiekowego konca nauki/przerwy
            if self.wave_obj:
                play_obj = self.wave_obj.play()
                play_obj.wait_done()

