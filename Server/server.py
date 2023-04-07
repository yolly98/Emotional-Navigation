from Server.listener import Listener

if __name__ == '__main__':

    # start the listening server that will receive requests
    Listener.get_instance().listen("0.0.0.0", "5000")
