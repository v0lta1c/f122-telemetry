import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import time
import sys

from packets import ParticipantData, CarTelemetry, SessionData

class TelemetryApp:
    def __init__(self, root, car_telemetry_data: CarTelemetry, participant_data: ParticipantData, session_data: SessionData):
        self.root = root;
        self.root.title("Car Telemetry Data");

        self.car_telemetry_data = car_telemetry_data;
        self.participant_data = participant_data;
        self.session_data = session_data;

        self.create_widget();
        self.selected_driver = tk.IntVar();
        #Set the first driver as default
        self.selected_driver.set(0);

        self.all_times = [];
        self.all_speeds = {};

        self.previous_time = 0;

        #Handle the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing);

    def create_widget(self):
        
        #Combobox for selecting driver ID
        self.driver_combobox = ttk.Combobox(self.root, values=[]);
        self.driver_combobox.bind("<<ComboboxSelected>>", self.update_plot);
        self.driver_combobox.pack();

        #Create a figure for the plot
        self.figure = Figure(figsize=(6,4), dpi=100);
        self.ax = self.figure.add_subplot(111);
        self.line, = self.ax.plot([], []);

        self.canvas = FigureCanvasTkAgg(self.figure, self.root);
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True);

        #Animation for real-time plotting
        self.anim = animation.FuncAnimation(self.figure, self.animate, interval=1000, cache_frame_data=False);
    
        self.update_driver_combobox();
        self.root.after(100, self.update_driver_combobox_periodically);

    def animate(self, interval):

        sessionDuration = self.session_data.get_session_data_from_key('m_sessionDuration');
        sessionTimeLeft = self.session_data.get_session_data_from_key('m_sessionTimeLeft');
        current_time = 0;
        if sessionDuration is None or sessionTimeLeft is None:
            return  # No session duration available, cannot update plot
        if sessionDuration and sessionTimeLeft:
            current_time = sessionDuration - sessionTimeLeft;
        if current_time == self.previous_time:
            return  # No updates so no plotting
        speed_available = False;

        for driverId in range(len(self.participant_data.data)):
            current_speed = self.car_telemetry_data.get_car_telemetry_data_from_key(driverId)['m_speed'];
            if driverId  not in self.all_speeds:
                self.all_speeds[driverId] = [];
            if current_speed is not None:
                self.all_speeds[driverId].append(current_speed);
                speed_available = True;

        if speed_available:
            self.all_times.append(current_time);
            self.previous_time = current_time;
        
        self.update_plot(None);

    def update_driver_combobox(self):
        driverIds = list(self.participant_data.data.keys());
        driverNames = [self.participant_data.get_participant(i)['m_name'] for i in driverIds];
        self.driver_combobox['values'] = driverNames;
        selected_index = self.driver_combobox.current();
        if selected_index is not None and selected_index >= 0:
            selected_driver_index = self.selected_driver.get();
            selected_driver_id = driverIds[selected_driver_index];
            self.selected_driver.set(selected_driver_id);
    
    def update_driver_combobox_periodically(self):
        self.update_driver_combobox();
        self.root.after(100, self.update_driver_combobox_periodically);

    def update_plot(self, event=None):

        if len(self.all_times) > 0 and self.previous_time > self.all_times[-1]:
            self.ax.clear();
            self.all_speeds.clear();
            self.all_times.clear();
            return

        if not self.car_telemetry_data.data:
            self.ax.clear();
            self.ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=self.ax.transAxes);
            self.canvas.draw();
            return;
    
        selected_driver = self.driver_combobox.current();
        if selected_driver == -1:
            return  #No driver selected
        
        driverId = list(self.participant_data.data.keys())[selected_driver];

        self.ax.clear();
        if self.all_speeds and self.all_times:
            self.ax.plot(self.all_times, self.all_speeds.get(driverId, []));
            self.ax.set_xlabel('Time');
            self.ax.set_ylabel('Speed');
            self.ax.set_title(f'Driver {self.participant_data.get_participant(driverId)['m_name']} Speed');
        else:
            self.ax.text(9.5, 0.5, 'No Data Available', ha='center', va='center');

        self.canvas.draw();

    def on_closing(self):
        self.root.quit();
        self.root.destroy();
        sys.exit();

def run_gui(car_telemetry_data, participant_data, session_data):
    root = tk.Tk();
    app = TelemetryApp(root, car_telemetry_data, participant_data, session_data);
    root.mainloop();

