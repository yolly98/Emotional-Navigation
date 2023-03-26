from threading import Thread
from Server.listener import Listener


if __name__ == '__main__':

    # start the listening server that will receive requests
    listener = Thread(target=Listener.get_instance().listen, args=("0.0.0.0", "5000"))
    listener.setDaemon(True)
    listener.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server terminated")
        exit(0)

