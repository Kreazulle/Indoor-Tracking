import argparse
import sys
import time
import cv2
from pythonosc import udp_client


def parse_args():
    parser = argparse.ArgumentParser(
        description='Prototip rapid de detecție IR pentru localizare indoor using OpenCV.'
    )
    parser.add_argument('--device', type=int, default=0, help='Index camera device')
    parser.add_argument('--threshold', type=int, default=240, help='Threshold value for bright IR blob')
    parser.add_argument('--fps', type=int, default=60, help='Requested camera FPS')
    parser.add_argument('--width', type=int, default=640, help='Requested camera width')
    parser.add_argument('--height', type=int, default=480, help='Requested camera height')
    parser.add_argument('--no-osc', action='store_true', help='Disable OSC output')
    parser.add_argument('--osc-host', type=str, default='127.0.0.1', help='OSC host')
    parser.add_argument('--osc-port', type=int, default=8000, help='OSC port')
    parser.add_argument('--osc-path', type=str, default='/tracker/position', help='OSC address path for position')
    parser.add_argument('--osc-status-path', type=str, default='/tracker/status', help='OSC status address path for status')
    parser.add_argument('--show', action='store_true', help='Show live OpenCV windows')
    parser.add_argument('--window-title', type=str, default='IR Tracking', help='Window title for live view')
    return parser.parse_args()


def create_camera(device_index, width, height, fps):
    cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
    return cap


def create_osc_client(host, port):
    return udp_client.SimpleUDPClient(host, port)


def main():
    args = parse_args()
    cap = create_camera(args.device, args.width, args.height, args.fps)

    if not cap.isOpened():
        print('Eroare: nu pot accesa camera. Verifică indexul de dispozitiv sau dacă este ocupată.')
        sys.exit(1)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'Camera inițializată: device={args.device}, rezoluție={actual_width}x{actual_height}, fps={actual_fps:.1f}')

    osc_client = None
    if not args.no_osc:
        osc_client = create_osc_client(args.osc_host, args.osc_port)
        print(f'OSC activat: {args.osc_host}:{args.osc_port} -> {args.osc_path} / {args.osc_status_path}')
    else:
        print('OSC dezactivat. Rulează cu --osc-host/--osc-port pentru a trimite mesaje OSC.')

    print("Pornit: apasă 'q' pentru a ieși.")

    last_led_state = None
    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Frame invalid, ies...')
            break

        frame_count += 1
        if frame_count % 60 == 0:
            elapsed = time.time() - start_time
            measured_fps = frame_count / elapsed if elapsed > 0 else 0.0
            print(f'FPS măsurat: {measured_fps:.1f} (cadre={frame_count}, timp={elapsed:.2f}s)')

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, args.threshold, 255, cv2.THRESH_BINARY)
        M = cv2.moments(thresh)
        led_found = M['m00'] != 0

        if led_found:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])
            status = 'LED_FOUND'
            print(f'LED detectat -> X: {cX}, Y: {cY}')

            if osc_client is not None:
                osc_client.send_message(args.osc_path, [cX, cY])
                if last_led_state != status:
                    osc_client.send_message(args.osc_status_path, [status])
                last_led_state = status
        else:
            status = 'LED_NOT_FOUND'
            print('LED nu a fost găsit în acest cadru.')
            if osc_client is not None and last_led_state != status:
                osc_client.send_message(args.osc_status_path, [status])
                last_led_state = status

        if args.show:
            output = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            if led_found:
                cv2.circle(output, (cX, cY), 8, (0, 0, 255), -1)
            cv2.imshow(args.window_title, output)
            cv2.imshow(f'{args.window_title} - Threshold', thresh)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if args.show:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
