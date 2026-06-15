#!/usr/bin/env python3
import os
import socket
import json
import time
import random
import datetime

HOST = os.environ.get('LOGSTASH_HOST', 'localhost')
PORT = int(os.environ.get('LOGSTASH_PORT', '5000'))
EVENT_RATE = float(os.environ.get('EVENT_RATE', '1.0'))

event_types = ['auth_failed', 'login_success', 'file_access', 'port_scan', 'malware_alert']
users = ['alice', 'bob', 'carol', 'dave', 'eve']


def gen_event():
    t = datetime.datetime.utcnow().isoformat() + 'Z'
    return {
        'timestamp': t,
        'event_type': random.choice(event_types),
        'user': random.choice(users),
        'src_ip': f'192.168.1.{random.randint(2, 254)}',
        'dst_ip': f'10.0.0.{random.randint(2, 254)}',
        'message': 'Synthetic event for SIEM demo',
        'severity': random.choice(['INFO', 'MEDIUM', 'HIGH']),
    }


def send_event(sock, event):
    data = json.dumps(event).encode('utf-8') + b'\n'
    sock.sendall(data)


def main():
    print(f"Connecting to {HOST}:{PORT} @ {EVENT_RATE} events/sec")
    with socket.create_connection((HOST, PORT)) as sock:
        try:
            while True:
                e = gen_event()
                send_event(sock, e)
                print('sent', e)
                time.sleep(1.0 / EVENT_RATE)
        except KeyboardInterrupt:
            print('Stopped')


if __name__ == '__main__':
    main()
