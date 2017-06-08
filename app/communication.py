import bluetooth

def _getConnectivityConfig():
    return ('',0)

SERVER_MAC, PORT = _getConnectivityConfig()
socket = None

def init():
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.bind((SERVER_MAC, PORT))
    socket.listen(1)
    try:
        client, clientInfo = socket.accept()
    finally:
        print("closing sockets")
        client.close()
        socket.close()
