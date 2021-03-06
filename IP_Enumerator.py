import queue
import subprocess
from os import path
from threading import Thread

from netaddr import IPNetwork

file_count = 0
file_name = None
num_threads = 10
q = queue.Queue()


def ping_request(que):
    while True:
        ip = str(que.get())
        command = "ping -n 1 " + str(ip)
        pro = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()[0]
        if "TTL=" in pro.decode('utf-8'):
            print(str(ip) + " is alive\n")
        elif "Ping request could not find host" in pro.decode('utf-8'):
            print("Not able to sent Packet ! Connection down")
        else:
            pass
        que.task_done()


def file_reader(file_path):  # read the network block file line by line
    with open(file_path, 'r') as open_obj:
        for line in open_obj:
            host_finder(line)


def host_finder(net_block):  # find all valid hosts & write it to Separate files
    global file_name, file_count
    file_count = file_count + 1
    file_name = ("output{}.txt".format(str(file_count)))
    print("Finding all valid hosts for the subnet - " + str(net_block))
    for ip in IPNetwork(net_block).iter_hosts():
        with open(file_name, 'a+') as write_obj:
            write_obj.write(str(ip) + "\n")


def create_threads(thread_count):
    for i in range(thread_count):
        worker = Thread(target=ping_request, args=(q,))
        worker.setDaemon(True)
        worker.start()
    q.join()
    print("done")


def push_queue():  # push hosts of each subnet into queue for pinging
    global file_name
    for i in range(1, file_count + 1):
        file_name = ("output{}.txt".format(str(i)))
        with open(file_name, 'r') as queue_obj:
            for host in queue_obj:
                q.put(host)
            create_threads(num_threads)


if __name__ == '__main__':  # Start execution from here
    Path = input("Enter the Path to the network block file\n")
    if path.exists(Path):
        file_reader(Path)
        print("All valid hosts has been found ! ")
        push_queue()
    else:
        print("\nInvalid path ! Program exiting\n")
