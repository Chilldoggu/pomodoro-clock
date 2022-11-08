import threading
import customtkinter
from pygame import mixer
from PIL import Image, ImageTk

from Options import Options_slider_frame, Options_toplevel
from Pomodoro_frame import Pomodoro_frame

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro Clock")
        self.geometry("600x200")
        self.icon = ImageTk.PhotoImage(Image.open('clock.ico'))
        self.iconphoto(True, self.icon)

        mixer.init()
        mixer.music.load("xue-hua-piao-piao.mp3")

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.timer = Pomodoro_frame()
        self.timer.grid(column=0, row=0, columnspan=2)

        self.pomodoro_counter = customtkinter.CTkLabel(self, 
                                                       textvariable=self.timer.pomodoro_string,
                                                       text_font=('Arial', 12)) 
        self.pomodoro_counter.grid(column=0, rows=1, sticky='NW', padx=(60,0))

        self.switch = customtkinter.CTkSwitch(self,
                                              text="Start / Pause", 
                                              command=self.play_pause, 
                                              text_font=('Arial', 12),
                                              state='disabled')
        self.switch.grid(row=1, column=1, sticky='NE', padx=(0,60))

        self.option_button = customtkinter.CTkButton(self,
                                                     width=60,
                                                     height=30,
                                                     text="Options",
                                                     text_font=('Arial', 12),
                                                     command=self.pop_options)
        self.option_button.grid(row=2, column=1, sticky='N', pady=(0,20), padx=(40, 0))

    def play_pause(self):
        if not self.timer.start:
            self.event.set() 
        self.timer.start = not self.timer.start

    def pop_options(self):
        self.Options = Options_toplevel(self)

    def start_countdown(self):
        self.event = threading.Event()
        threading.Thread(name='countdown', 
                         target=self.timer.countdown,
                         args=(self.event,),
                         daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
