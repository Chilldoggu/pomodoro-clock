import customtkinter
import tkinter
from time import strftime

class Pomodoro_frame(customtkinter.CTkFrame):
    start = True
    study = True
    wave_obj = None

    def __init__(self, root, logger = None):
        super().__init__(root)
        self.root = root
        self.logger = logger
        self.study_time = self.break_time = None
        self.pomodoros = 0
        self.pomodoro_string = tkinter.StringVar(value="🍅Pomodoros: 0")
        self.string_time = tkinter.StringVar(value="Setup needed")
        self.time_counter = customtkinter.CTkLabel(self,
                                                   textvariable=self.string_time,
                                                   font=('Arial', 40, 'bold'))
        self.time_counter.pack(padx=30, pady=15)


    def update_times(self, new_study_time, new_break_time, new_long_break_time, new_until_long_break):
        self.study_time = new_study_time
        self.break_time = new_break_time
        self.long_break_time = new_long_break_time
        self.until_long_break = new_until_long_break


    def countdown(self, event):
        while True:
            # If it's time for a session
            if self.study:
                self.logger.logObj.info(f"Starting {self.study_time[3]}H:{self.study_time[4]}M:{self.study_time[5]}S study session.")
                hours, minutes, seconds = self.study_time[3], self.study_time[4], self.study_time[5]
            # If it's time for long break
            elif self.pomodoros % self.until_long_break == 0:
                self.logger.logObj.info(f"Starting {self.long_break_time[3]}H:{self.long_break_time[4]}M:{self.long_break_time[5]}S long break")
                hours, minutes, seconds = self.long_break_time[3], self.long_break_time[4], self.long_break_time[5]
            # If it's time for normal break
            else:
                self.logger.logObj.info(f"Starting {self.break_time[3]}H:{self.break_time[4]}M:{self.break_time[5]}S short break")
                hours, minutes, seconds = self.break_time[3], self.break_time[4], self.break_time[5]

            # If m >= 60, then add time to h
            if minutes >= 60:
                hours = int(minutes/60)
                minutes = minutes%60

            # Start the countdown
            for h in range(hours, -1, -1):
                for m in range(minutes, -1, -1):
                    for s in range(seconds, -1, -1):
                        if self.study:
                            self.string_time.set("📖"+strftime("%H : %M : %S", (1, 1, 1, h, m, s, 1, 1, 1))+"📖")
                        else:
                            self.string_time.set("🍵"+strftime("%H : %M : %S", (1, 1, 1, h, m, s, 1, 1, 1))+"🍵")
                        for i in range(10):
                            self.after(100, self.update())
                        # Pause if pause/start switch has been toggled
                        if not self.start:
                            self.logger.logObj.info(f"Paused")
                            event.wait()
                            event.clear()
                            self.logger.logObj.info(f"Unpaused")
                    if m:
                        seconds = 59
                if h:
                    minutes = 59
            
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

