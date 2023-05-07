import psutil
from threading import Thread
import time
import matplotlib.pyplot as plt
import matplotlib
import os
from Client.state_manager import StateManager


class Monitor:

    @staticmethod
    def clean(abs_path):
        try:
            os.remove(os.path.join(abs_path, 'cpu_data.txt'))
        except:
            pass
        try:
            os.remove(os.path.join(abs_path, 'mem_data.txt'))
        except:
            pass
        try:
            os.remove(os.path.join(abs_path, 'net_data.txt'))
        except:
            pass
        try:
            os.remove(os.path.join(abs_path, 'cpu_usage.png'))
        except:
            pass
        try:
            os.remove(os.path.join(abs_path, 'mem_usage.png'))
        except:
            pass
        try:
            os.remove(os.path.join(abs_path, 'net_usage.png'))
        except:
            pass


    @staticmethod
    def collect_resources_usage(abs_path):
        with open(os.path.join(abs_path, 'cpu_data.txt'), 'a') as cpu_file, \
                open(os.path.join(abs_path, 'mem_data.txt'), 'a') as mem_file, \
                open(os.path.join(abs_path, 'net_data.txt'), 'a') as net_file:
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

    @staticmethod
    def create_plots(abs_path):
        # print('plots creations ...')

        matplotlib.use("Agg") # set not interactive mode

        with open(os.path.join(abs_path, 'cpu_data.txt'), 'r') as cpu_file, \
                open(os.path.join(abs_path, 'mem_data.txt'), 'r') as mem_file, \
                open(os.path.join(abs_path, 'net_data.txt'), 'r') as net_file:
            cpu_data = cpu_file.readlines()
            mem_data = mem_file.readlines()
            net_data = net_file.readlines()

        cpu_values = [float(value) for value in cpu_data]
        mem_values = [float(value) for value in mem_data]
        net_values = [[float(value) for value in line.split(',')] for line in net_data]

        plt.plot(cpu_values)
        plt.title('CPU usage')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.savefig(os.path.join(abs_path, 'cpu_usage.png'))
        plt.clf()

        plt.plot(mem_values)
        plt.title('Memory usage')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.savefig(os.path.join(abs_path, 'mem_usage.png'))
        plt.clf()

        net_sent_values = [values[0] for values in net_values]
        net_recv_values = [values[1] for values in net_values]
        plt.plot(net_sent_values, label='Sent')
        plt.plot(net_recv_values, label='Received')
        plt.title('Network usage')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (bytes)')
        plt.legend()
        plt.savefig(os.path.join(abs_path, 'net_usage.png'))
        plt.clf()

        print("plots creation completed")


    @staticmethod
    def run():
        abs_path = os.path.dirname(__file__)
        Monitor.clean(abs_path)
        Monitor.collect_resources_usage(abs_path)
        Monitor.create_plots(abs_path)

if __name__ == '__main__':
    t1 = Thread(target=Monitor.run, args=(), daemon=False)
    StateManager.get_instance().set_state('monitor_thread', True)
    t1.start()
    print("monitor started")

    input("press something to stop")
    StateManager.get_instance().set_state('monitor_thread', False)
    exit(0)
