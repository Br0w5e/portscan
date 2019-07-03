import sys
import time
import threading, socket, sys, cmd, os, queue
import re
import requests
lock = threading.Lock()

#用法
def Usage():
    print("Usage python3 portscan.py <target ip or ips> <port or ports> <threads_number>")
    print("eg: python36 portscan.py 127.0.0.1 80 20")
    print("eg: python36 portscan.py 127.0.0.1-255 80, 81 50")
    print("eg: python36 portscan.py 127.0.0.1-255 80-100 50")
    exit(0)

#IP处理 return iplist
def ip_split(ip): 
    ips = len(ip.split('-'))
    iplist= []
    
    #单个IP
    if ips == 1:
        iplist.append(ip)
        return iplist
    
    #ip段
    else:
        ipfinal = ip.split('-')[0][:-len(ip.split('-')[0].split('.')[-1])]
        start = int(ip.split('-')[0].split('.')[-1])
        end = int(ip.split('-')[1]) + 1
        for i in range(start, end):
            if len(ip.split(".")) == 4:
                iplist.append(ipfinal + str(i))
            elif len(ip.split(".")) == 3:
                for j in range(1,255):
                    iplist.append(ipfinal + str(i) + "." + str(j))
        return iplist

#port处理 return ports
def port_split(port):
    portlist = []
    #列举80， 81
    if "," in port:
        portlist =[int(s) for s in port.split(",")] 
    #单个90
    elif len(port.split("-")) == 1:
        portlist.append(int(port))
    #段80-92
    else:
        start, end = int(port.split("-")[0]), int(port.split("-")[1])
        for i in range(start, end+1):
            portlist.append(i)
    return portlist

#混合 
def get_target_queue(ips, ports):
    ipQue = queue.Queue()
    for ip in ips:
        for port in ports:
            ipQue.put((ip, port))
    return ipQue

#运行
def run(ip_lists, port_lists, thread):
    threadList = []
    IpQue = get_target_queue(ip_lists, port_lists)
    #print(IpQue)
    resultQue = queue.Queue()

    for i in range(thread):
        t = Scaner(IpQue)
        t.start()
        threadList.append(t)
    for t in threadList:
        t.join(0.4)

class Scaner(threading.Thread):
    def __init__(self, InQueure):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.InQueure = InQueure
        self.web_title = ''
        self.web_server = ''
        self.web_status = ''

    def scan_target(self, host, port):
        global lock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        address = (host, port)
        socks_banners = ''
        #print(address)
        try:          
            sock.connect(address)
        except:
            sock.close()
            return False
        try:
            sock.send('HELLO\r\n')
            socks_banners = sock.recv(1024).split('\r\n')[0].strip('\r\n')
        except:
            pass
        sock.close()
        self.get_info(host, port)
        if lock.acquire():
            print("[*] %10s : open port %5s  %20s ||  %20s  %5s  %s" %(host, port, socks_banners, self.web_server, self.web_status, self.web_title ))
            lock.release()
        return True
    
    def get_info(self, host, port):
        url = "http://%s:%d" % (host, port)
        #print(url)
        try:
            s = requests.Session()
            s.keep_live = False
            infos = s.get(url=url, timeout=0.2)
            self.web_status = int(infos.status_code)
            try:
                self.web_server = infos.headers['server']
            except:
                pass
            try:
                self.web_title = re.findall(r'<title>(.*)</title>', infos.text)[0]
            except:
                pass
        except:
           pass
    def run(self):
        while not self.InQueure.empty():
            host, port = self.InQueure.get()
            self.scan_target(host, port)

def main():
    try:
        if len(sys.argv) != 4:
            Usage()
        else:
            ip_lists = ip_split(sys.argv[1])
            port_lists = port_split(sys.argv[2])
            thread = int(sys.argv[3])
            print("Scaning…………")
            print("Ctrl + C to Stop!")
            run(ip_lists, port_lists, thread)
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
