#!/usr/bin/env python3
import os
import time
import json
import socket
import smtplib
from email.message import EmailMessage
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

ES_HOST = os.environ.get('ES_HOST', 'http://localhost:9200')
ALERT_SEVERITY = os.environ.get('ALERT_SEVERITY', 'HIGH')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '30'))
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')
ALERT_EMAIL = os.environ.get('ALERT_EMAIL', '')
SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '25'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')

es = Elasticsearch([ES_HOST])

def send_slack_alert(message):
    if not SLACK_WEBHOOK_URL:
        return
    payload = {"text": message}
    try:
        import urllib.request
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(SLACK_WEBHOOK_URL, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print('Slack response:', resp.status)
    except Exception as e:
        print('Slack send failed:', e)


def send_email_alert(message):
    if not ALERT_EMAIL:
        return
    msg = EmailMessage()
    msg['Subject'] = f'SIEM Alert: {ALERT_SEVERITY} event detected'
    msg['From'] = SMTP_USER or f'no-reply@{socket.gethostname()}'
    msg['To'] = ALERT_EMAIL
    msg.set_content(message)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            if SMTP_USER and SMTP_PASS:
                smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
            print('Email alert sent to', ALERT_EMAIL)
    except Exception as e:
        print('Email send failed:', e)


def check_alerts():
    now = datetime.utcnow()
    since = now - timedelta(minutes=5)
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"severity": ALERT_SEVERITY}},
                    {"range": {"@timestamp": {"gte": since.isoformat(), "lte": now.isoformat()}}}
                ]
            }
        }
    }
    try:
        res = es.search(index='siem-*', body=body, size=10)
        hits = res.get('hits', {}).get('hits', [])
        if hits:
            for h in hits:
                src = h.get('_source', {})
                event_desc = f"ALERT: {src.get('event_type')} user={src.get('user')} src={src.get('src_ip')} dst={src.get('dst_ip')} msg={src.get('message')}"
                print(event_desc)
            if SLACK_WEBHOOK_URL:
                send_slack_alert(f"{len(hits)} high severity events detected in the last 5 minutes.")
            if ALERT_EMAIL:
                send_email_alert(f"{len(hits)} high severity events detected in the last 5 minutes.\n\nDetails:\n" + "\n".join([f"{h.get('_source', {}).get('event_type')} - {h.get('_source', {}).get('message')}" for h in hits]))
    except Exception as e:
        print('Error querying ES:', e)


if __name__ == '__main__':
    print('Starting alert checker (press Ctrl+C to stop)')
    try:
        while True:
            check_alerts()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print('Stopped')
