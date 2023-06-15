import psutil
from threading import Thread
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib
import os
from Client.state_manager import StateManager


class Monitor:

    monitor = None

    def __init__(self):
        self.is_active = False
        self.start_time = time.time()
        self.abs_path = os.path.dirname(__file__)

    @staticmethod
    def get_instance():
        if Monitor.monitor is None:
            Monitor.monitor = Monitor()
        return Monitor.monitor

    def init(self):
        folder_path = os.path.join(self.abs_path, '..', 'Resources', 'MonitorData')
        for file in os.scandir(folder_path):
            if not file.name == '.gitkeep':
                os.remove(file)

        folder_path = os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal')
        for file in os.scandir(folder_path):
            if not file.name == '.gitkeep':
                os.remove(file)



    def collect_resources_usage(self):
        with open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'cpu_data.txt'), 'a') as cpu_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'mem_data.txt'), 'a') as mem_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'net_data.txt'), 'a') as net_file:
            while True:
                if not StateManager.get_instance().get_state('monitor_thread'):
                    return
                cpu_percent = psutil.Process().cpu_percent(interval=1)
                mem_percent = psutil.Process().memory_percent()
                bytes_sent = psutil.net_io_counters().bytes_sent
                bytes_recv = psutil.net_io_counters().bytes_recv

                # print(f'wirting cpu: {cpu_percent}, mem: {mem_percent}, byte sent: {bytes_sent}, byte recv: {bytes_recv}')
                cpu_file.write(str(cpu_percent) + '\n')
                mem_file.write(str(mem_percent) + '\n')
                net_file.write(str(bytes_sent) + ',' + str(bytes_recv) + '\n')

                cpu_file.flush()
                mem_file.flush()
                net_file.flush()

                time.sleep(1)

    def create_plots(self):
        # print('plots creations ...')

        matplotlib.use("Agg") # set not interactive mode

        with open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'cpu_data.txt'), 'a+') as cpu_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'mem_data.txt'), 'a+') as mem_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'net_data.txt'), 'a+') as net_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'dashboard_data.txt'), 'a+') as dashboard_file,\
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'history_collector_data.txt'), 'a+') as history_collector_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'gps_manager_data.txt'), 'a+') as gps_manager_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'vocal_in_data.txt'), 'a+') as vocal_in_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'vocal_out_data.txt'), 'a+') as vocal_out_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'gps_coords_data.txt'), 'a+') as gps_coords_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'emotions_data.txt'), 'a+') as emotions_file, \
                open(os.path.join(self.abs_path, '..', 'Resources', 'MonitorData', 'path_recalculations_data.txt'), 'a+') as path_recalculations_file:

            cpu_file.seek(0)
            mem_file.seek(0)
            net_file.seek(0)
            dashboard_file.seek(0)
            history_collector_file.seek(0)
            gps_manager_file.seek(0)
            vocal_in_file.seek(0)
            vocal_out_file.seek(0)
            gps_coords_file.seek(0)
            emotions_file.seek(0)
            path_recalculations_file.seek(0)

            cpu_data = cpu_file.readlines()
            mem_data = mem_file.readlines()
            net_data = net_file.readlines()
            dashboard_data = dashboard_file.readlines()
            history_collector_data = history_collector_file.readlines()
            gps_manager_data = gps_manager_file.readlines()
            vocal_in_data = vocal_in_file.readlines()
            vocal_out_data = vocal_out_file.readlines()
            gps_coords_data = gps_coords_file.readlines()
            emotions_data = emotions_file.readlines()
            path_recalculations_data = path_recalculations_file.readlines()

        cpu_values = [float(value) for value in cpu_data]
        mem_values = [float(value) for value in mem_data]
        net_values = [[float(value) for value in line.split(',')] for line in net_data]

        dashboard_y_values = [float(line.split(',')[0]) for line in dashboard_data]
        history_collector_y_values = [float(line.split(',')[0]) for line in history_collector_data]
        gps_manager_y_values = [float(line.split(',')[0]) for line in gps_manager_data]
        vocal_in_y_values = [float(line.split(',')[0]) for line in vocal_in_data]
        vocal_out_y_values = [float(line.split(',')[0]) for line in vocal_out_data]
        gps_coords_y_values = [float(line.split(',')[1]) for line in gps_coords_data]

        dashboard_x_values = [float(line.split(',')[1]) for line in dashboard_data]
        history_collector_x_values = [float(line.split(',')[1]) for line in history_collector_data]
        gps_manager_x_values = [float(line.split(',')[1]) for line in gps_manager_data]
        vocal_in_x_values = [float(line.split(',')[1]) for line in vocal_in_data]
        vocal_out_x_values = [float(line.split(',')[1]) for line in vocal_out_data]
        gps_coords_x_values = [float(line.split(',')[0]) for line in gps_coords_data]

        emotions_values = [[value for value in line.split(',')] for line in emotions_data]
        path_recalculations_values = [[float(value) for value in line.split(',')] for line in path_recalculations_data]

        plt.plot(cpu_values)
        plt.title('CPU usage')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'cpu_usage.png'))
        plt.clf()

        plt.plot(mem_values)
        plt.title('Memory usage')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'mem_usage.png'))
        plt.clf()

        net_sent_values = [values[0] for values in net_values]
        net_recv_values = [values[1] for values in net_values]
        plt.plot(net_sent_values, label='Sent')
        plt.plot(net_recv_values, label='Received')
        plt.title('Network usage')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (bytes)')
        plt.legend()
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'net_usage.png'))
        plt.clf()

        plt.plot(dashboard_x_values, dashboard_y_values)
        plt.title('Dashboard Cycle Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Cycle Time (s)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'dashboard_cycle_time.png'))
        plt.clf()

        plt.plot(history_collector_x_values, history_collector_y_values)
        plt.title('History Collector Cycle Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Cycle Time (s)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'history_collector_cycle_time.png'))
        plt.clf()

        plt.plot(gps_manager_x_values, gps_manager_y_values)
        plt.title('GPS Manager Cycle Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Cycle Time (s)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'gps_manager_cycle_time.png'))
        plt.clf()

        plt.plot(vocal_in_x_values, vocal_in_y_values)
        plt.title('Vocal In Cycle Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Cycle Time (s)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'vocal_in_cycle_time.png'))
        plt.clf()

        plt.plot(vocal_out_x_values, vocal_out_y_values)
        plt.title('Vocal Out Cycle Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Cycle Time (s)')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'vocal_out_cycle_time.png'))
        plt.clf()

        fig, ax = plt.subplots()
        ax.plot(gps_coords_x_values, gps_coords_y_values, c='white', linewidth=1)
        ax.scatter(gps_coords_x_values[len(gps_coords_x_values) - 1], gps_coords_y_values[len(gps_manager_y_values) - 1], marker='*', s=100, c='white')
        for sample in emotions_values:
            emotion = sample[0]
            lat = float(sample[1])
            lon = float(sample[2])
            color = None
            if emotion == 'happy' or emotion == 'surprise':
                color = "green"
            elif emotion == 'neutral':
                color = "yellow"
            else:
                color = "red"
            ax.scatter(lat, lon, marker='o', s=100, c=color)

        for sample in path_recalculations_values:
            lat = sample[0]
            lon = sample[1]
            ax.scatter(lat, lon, marker='v', s=100, c='violet')
        ax.axis('off')
        fig.set_facecolor('black')
        plt.savefig(os.path.join(self.abs_path, '..', 'Resources', 'MonitorSignal', 'path_result.png'))
        plt.clf()

        print("plots creation completed")

    def collect_measure(self, target, measure):
        if not self.is_active:
            return
        if target == 'dashboard' or \
                target == 'history_collector' or \
                target == 'gps_manager' or \
                target == 'vocal_in' or \
                target == 'vocal_out' or \
                target == 'gps_coords' or \
                target == 'emotions' or \
                target == 'path_recalculations':

            abs_path = os.path.dirname(__file__)
            with open(os.path.join(abs_path, '..', 'Resources', 'MonitorData', f'{target}_data.txt'), 'a') as file:

                file.write(str(measure) + ', ' + str(time.time() - self.start_time) + '\n')
                file.flush()
                file.close()
        else:
            print("Unknown target")

    def run(self):
        self.is_active = True
        self.init()
        self.collect_resources_usage()
        self.create_plots()


if __name__ == '__main__':

    Monitor.get_instance().create_plots()
    exit(0)
    t1 = Thread(target=Monitor.get_instance().run, args=(), daemon=False)
    StateManager.get_instance().set_state('monitor_thread', True)
    t1.start()
    print("monitor started")

    input("press something to stop")
    StateManager.get_instance().set_state('monitor_thread', False)
    exit(0)
