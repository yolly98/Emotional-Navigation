from flask import Flask, request


class Listener:

    listener = None

    def __init__(self):
        # Flask instance to receive data
        self.app = Flask(__name__)

    @staticmethod
    def get_instance():
        if Listener.listener is None:
            Listener.listener = Listener()
        return Listener.listener

    def listen(self, ip, port):
        # execute the listening server, for each message received, it will be handled by a thread
        self.app.run(host=ip, port=port, debug=False)

    def get_app(self):
        return self.app


app = Listener.get_instance().get_app()


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    print(received_json)
    return received_json, 200