import time
import socket
import struct
import threading
from datetime import datetime


class NetworkTimeValidator:
    NTP_SERVERS = [
        'time.google.com',
        'time.cloudflare.com',
        'time.windows.com',
        'pool.ntp.org',
        'time.apple.com',
        'time.nist.gov'
    ]
    
    HTTP_TIME_SERVERS = [
        ('www.google.com', 443),
        ('www.cloudflare.com', 443),
        ('www.amazon.com', 443),
        ('www.microsoft.com', 443),
        ('www.apple.com', 443)
    ]
    
    def __init__(self):
        self.cached_time = None
        self.cache_timestamp = 0
        self.cache_duration = 60
        self.lock = threading.Lock()
    
    def get_ntp_time(self, server):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(2)
            data = b'\x1b' + 47 * b'\0'
            client.sendto(data, (server, 123))
            response, _ = client.recvfrom(1024)
            if len(response) >= 48:
                t = struct.unpack('!12I', response)[10]
                t -= 2208988800
                client.close()
                return t
        except:
            pass
        return None
    
    def get_http_time(self, server, port):
        try:
            import http.client
            if port == 443:
                conn = http.client.HTTPSConnection(server, timeout=3)
            else:
                conn = http.client.HTTPConnection(server, timeout=3)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            date_header = response.getheader('date')
            conn.close()
            
            if date_header:
                from email.utils import parsedate_to_datetime
                network_time = parsedate_to_datetime(date_header)
                return int(network_time.timestamp())
        except:
            pass
        return None
    
    def get_network_time(self):
        with self.lock:
            current = time.time()
            if self.cached_time and (current - self.cache_timestamp) < self.cache_duration:
                age = current - self.cache_timestamp
                return self.cached_time + int(age)
        
        times = []
        
        for server in self.NTP_SERVERS[:3]:
            ntp_time = self.get_ntp_time(server)
            if ntp_time:
                times.append(ntp_time)
                break
        
        for server, port in self.HTTP_TIME_SERVERS[:2]:
            http_time = self.get_http_time(server, port)
            if http_time:
                times.append(http_time)
        
        if times:
            avg_time = int(sum(times) / len(times))
            with self.lock:
                self.cached_time = avg_time
                self.cache_timestamp = time.time()
            return avg_time
        
        return None
    
    def validate_local_time(self, local_time):
        network_time = self.get_network_time()
        if network_time is None:
            return True
        
        diff = abs(local_time - network_time)
        return diff < 300
