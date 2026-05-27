import argparse
import cv2
from pythonosc import udp_client

# Ultra-fast IR LED tracker (monocular)
# Usage example:
#   python tracking_2d.py --osc-host 127.0.0.1 --osc-port 8000


def parse_args():
    parser = argparse.ArgumentParser(description='Monocular IR LED tracker with OSC output.')
    parser.add_argument('--device', type=int, default=0, help='Camera device index')
    parser.add_argument('--threshold', type=int, default=240, help='Binary threshold for bright IR blob')
    parser.add_argument('--osc-host', type=str, default='127.0.0.1', help='OSC target host')
    parser.add_argument('--osc-port', type=int, default=8000, help='OSC target port')
    parser.add_argument('--osc-path', type=str, default='/tracker/position', help='OSC address path')
    parser.add_argument('--osc-status-path', type=str, default='/tracker/status', help='OSC status address path')
    parser.add_argument('--no-osc', action='store_true', help='Disable OSC output')
    return parser.parse_args()


def create_camera(device_index):
    return cv2.VideoCapture(device_index, cv2.CAP_DSHOW)


def create_osc_client(host, port):
    return udp_client.SimpleUDPClient(host, port)


def main():
    args = parse_args()
    cap = create_camera(args.device)

    if not cap.isOpened():
        print('Eroare: nu pot accesa camera.')
        return

    osc_client = None
    if not args.no_osc:
        osc_client = create_osc_client(args.osc_host, args.osc_port)
        print(f'OSC activat: {args.osc_host}:{args.osc_port} -> {args.osc_path} / {args.osc_status_path}')
    else:
        print('OSC dezactivat. Rulează cu --osc-host/--osc-port pentru a trimite mesaje OSC.')

    print("Pornit: apasă 'q' pentru a ieși.")

    last_led_state = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Frame invalid, ies...')
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, args.threshold, 255, cv2.THRESH_BINARY)

        M = cv2.moments(thresh)
        led_found = M['m00'] != 0

        if led_found:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])
            cv2.circle(frame, (cX, cY), 8, (0, 0, 255), -1)
            print(f'LED detectat -> X: {cX}, Y: {cY}')

            if osc_client is not None:
                osc_client.send_message(args.osc_path, [cX, cY])
                if last_led_state != 'found':
                    osc_client.send_message(args.osc_status_path, ['LED_FOUND'])
                last_led_state = 'found'
        else:
            print('LED nu a fost găsit în acest cadru.')
            if osc_client is not None:
                if last_led_state != 'missing':
                    osc_client.send_message(args.osc_status_path, ['LED_NOT_FOUND'])
                last_led_state = 'missing'

        cv2.imshow('Tracking Live', frame)
        cv2.imshow('Threshold', thresh)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
