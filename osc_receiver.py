from pythonosc import dispatcher
from pythonosc import osc_server


def print_position(address, *args):
    print(f"OSC message {address}: {args}")


def main():
    disp = dispatcher.Dispatcher()
    disp.map('/tracker/position', print_position)

    server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 8000), disp)
    print('OSC receiver listening on 127.0.0.1:8000')
    print('Waiting for /tracker/position messages...')
    server.serve_forever()


if __name__ == '__main__':
    main()
