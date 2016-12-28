import tkinter
import time
import numpy as np
#import seaborn as sb

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from magnetometer import GaussMeterGU3001D

class App:
    def __init__(self, master):
        # Create a container
        frame = tkinter.Frame(master)
        self.master = master
        self.meter = GaussMeterGU3001D()
        self.start_time = time.monotonic()
        
        self.button_right = tkinter.Button(frame,text="Increase Slope >",
                                        command=self.increase)
        self.button_right.pack(side="left")

        fig = Figure()
        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel("measurement time [s]")
        self.line, = self.ax.plot(range(0))

        self.canvas = FigureCanvasTkAgg(fig,master=master)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        frame.pack()
        sb.despine()
        self.update()

    def update(self):
        secs, fields = self.line.get_data()
        field = self.meter.measure()
        sec = time.monotonic() - self.start_time

        secs = np.append(secs, sec)
        fields = np.append(fields, field)
        self.ax.set_xlim(xmin=min(secs), xmax=max(secs))
        self.ax.set_ylim(ymin=min(fields), ymax=max(fields))
        print (fields)
        print (secs)
        self.line.set_ydata(fields)
        self.line.set_xdata(secs)
        self.canvas.draw()
        self.master.after(2, self.update)

    def increase(self):
        x, y = self.line.get_data()
        self.line.set_ydata(y + 0.2 * x)
        self.canvas.draw()

root = tkinter.Tk()
app = App(root)
#root.after(2, app.update)
root.mainloop()
