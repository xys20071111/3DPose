from socketserver import TCPServer, BaseRequestHandler
import multiprocessing

MESSAGE_QUEUE = multiprocessing.Queue(10)


class CaptureServerHandler(BaseRequestHandler):
    def setup(self) -> None:
        while not MESSAGE_QUEUE.empty():
            MESSAGE_QUEUE.get()

    def handle(self):
        print('Connected.')
        while True:
            cmd = self.request.recv(4)
            if not cmd:
                print("Disconnected.")
                return
            if cmd == b'next':
                data = MESSAGE_QUEUE.get()
                if data is bytes or data is bytearray:
                    self.request.send(len(data).to_bytes(4, 'little'))
                    self.request.send(data)
                else:
                    data_bytes = data.encode('utf8')
                    self.request.send(len(data_bytes).to_bytes(4, 'little'))
                    self.request.send(data_bytes)


class CaptureServer(multiprocessing.Process):

    def run(self):
        TCPServer(('127.0.0.1', 6354), CaptureServerHandler).serve_forever()
