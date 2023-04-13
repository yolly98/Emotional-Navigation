from requests import post, get,  exceptions


class CommunicationManager:

    def __init__(self):
        pass

    @staticmethod
    def send(ip, port, type, data, resource):
        connection_string = f'http://{ip}:{port}/{resource}'
        response = None
        try:
            if type == "GET":
                response = get(connection_string, json=data)
            elif type == "POST":
                response = post(connection_string, json=data)
        except exceptions.RequestException:
            print("Endpoint system unreachable")
            return False

        if response.status_code != 200:
            print(f"Communication error [{response.status_code}]")
            return None

        return response.json()


if __name__ == '__main__':
    msg = dict()
    msg["msg"] = "ciao"
    res = CommunicationManager.send("127.0.0.1", "5000", msg)
    print(res)
