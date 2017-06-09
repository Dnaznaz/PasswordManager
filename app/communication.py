import bluetooth
import select
import threading

import crypto_manager as crypto

def _getConnectivityConfig():
    return ('',0)

SERVER_MAC, PORT = _getConnectivityConfig()
publicKey = None
privateKey = None
socket = None
handlingCommand = None

tempClients = {}
clients = {}
clientKeys = {}

def init(event):
    global socket

    socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    socket.bind((SERVER_MAC, PORT))
    socket.listen(1)

    _generate_key()

    start_listen(event)

def start_listen(event):
    while event.is_set():
        clSocket, addr = socket.accept()
        tempClients[addr] = clSocket
        clSocket.setblocking(0)

        threading.Thread(target=authorize, daemon=True, args=(clSocket, addr,)).start()

def authorize(soc, addr):
    soc.send("PUBLIC-KEY:{key}".format(key=publicKey))

    soc.send("GET-PRIVATE-KEY")
    encData = _recv_timeout(soc, 30)

    if encData == "":
        _terminate_connection(soc, addr)
        return

    clientKeys[addr] = crypto.decrypt_asymm(privateKey, encData)

    if crypto.no_owner:
        _send_encrypted(soc, "NO-OWNER", clientKeys[addr])
        isAuth = True
    else:
        _send_encrypted(soc, "AUTHORIZE", clientKeys[addr])
        encData = _recv_timeout(soc, 120)

        if encData == "":
            _terminate_connection(soc, addr)
            return

        isAuth = crypto.authorize(crypto.decrypt_asymm(privateKey, encData))

    tempClients.pop(addr)

    if isAuth is True:
        clients[addr] = soc
        _send_encrypted(soc, "AUTHORIZED", clientKeys[addr])
        _handle(soc, addr)
    else:
        soc.close()

def set_hadling_command(command):
    global handlingCommand
    handlingCommand = command

def responed(addr, msg):
    _send_encrypted(clients[addr], msg, clientKeys[addr])

def _handle(soc, addr):
    while True:
        encReq = privateKey, _recv_timeout(soc, 60)

        if encReq == "" and _send_isalive(soc, addr) is False:
            break

        decReq = crypto.decrypt_asymm(privateKey, encReq)
        handlingCommand(decReq)


def _send_isalive(soc, addr):
    _send_encrypted(soc, "IS-ALIVE", clientKeys[addr])
    encRes = _recv_timeout(soc, 5)

    if encRes == "":
        _terminate_connection(soc, addr)
        return False
    else:
        decRes = crypto.decrypt_asymm(privateKey, encRes)
        if decRes == "ALIVE":
            return True
        else:
            _terminate_connection(soc, addr)
            return False

def _recv_timeout(soc, timeout, buffer=1024):
    ready = select.select([soc], [], [], timeout)
    if ready[0]:
        return soc.recv(buffer)
    else:
        return ''

def _send_encrypted(soc, msg, key):
    soc.send(crypto.encrypt_asymm(key, msg))

def _generate_key():
    global privateKey, publicKey

    privateKey, publicKey = crypto.generate_comm_keys()

def _terminate_connection(soc, addr):
    _send_encrypted(soc, "CLOSING", clientKeys[addr])
    soc.close()
    clientKeys.pop(addr)
    clientKeys.pop(addr)

def shutdown():
    socket.close()
    map(lambda x: x.close(), tempClients.values())
    map(lambda x: x.close(), clients.values())
