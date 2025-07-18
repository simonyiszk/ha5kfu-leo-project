import socket
import time
import tqdm
import struct
import subprocess


rot_addr = '10.73.19.30'
rot_port = 4533

rtl_addr = "10.73.19.31"
rtl_port = 7373


def get_pos(sock):
    sock.sendall(b'p\n')
    rec = sock.recv(1024).decode()
    #print(f"get_pos got '{repr(rec)}'")
    az, el = rec.strip().split("\n")
    az,el = float(az), float(el)
    #print(f"{az=}, {el=}")
    return az, el

def moveto(sock, az_target, el_target):
    sock.sendall(f"P {az_target} {el_target}\n".encode())
    #print(f"P {az_target} {el_target}\n".encode())
    #print(sock.recv(100)) # wait for OK
    sock.recv(100)
    while True:
        time.sleep(0.5)
        az, el = get_pos(sock)
        if abs(az-az_target) < 5 and abs(el-el_target)<5:
            return


def rtl_send_command(sock, cmd, arg):
    data = struct.pack("!cI", bytes([cmd]), int(arg))
    sock.sendall(data)

def setup_rtl(addr, port):
        sock_rtl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_rtl.connect((addr, port))
        # set freq with offset tuning
        #rtl_send_command(sock_rtl, 1, 498_000_000 - 200_000)
        rtl_send_command(sock_rtl, 1, 435_360_000 - 200_000)
        # set sample rate
        rtl_send_command(sock_rtl, 2, 1_000_000)
        # set gain (in 0.1 db steps)
        rtl_send_command(sock_rtl, 4, 2*10)
        return sock_rtl


def open_meter(rtl_sock):
    return subprocess.Popen(["./pwrmtr"],stdin=rtl_sock.fileno(),stdout=subprocess.PIPE)

def get_power(process):
    # process.stdout.seek(0,2)
    while True:
        o = process.stdout.readline()
        meas_time, power = o.decode().strip().split(",")
        meas_time, power = int(meas_time), float(power)
        #print(meas_time, time.time())
        if abs(meas_time - time.time()) < 0.75:
            return power

def measure_power_and_pos(rot_sock, proc):
    pos = get_pos(rot_sock)
    power = get_power(proc)
    return [pos, power]

def measure_at_pos(rot_sock, az_target, el_target, proc):
    moveto(rot_sock, az_target, el_target)
    collected_data = []
    for _ in tqdm.trange(60, leave=False, desc=f"Position {az_target}"):
        # setup_rtl(rtl_addr, rtl_port)
        collected_data.append(measure_power_and_pos(rot_sock, proc))
        time.sleep(0.1)
    return collected_data

def measure_around(rot_sock, proc):
    all_data = []
    for az_target in tqdm.trange(0,360,5, desc="Positions"):
        all_data += measure_at_pos(rot_sock, az_target, 0, proc)
    return all_data

sock_rtl = setup_rtl(rtl_addr, rtl_port)
proc = open_meter(sock_rtl)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rot_sock:
    rot_sock.connect((rot_addr, rot_port))
    all_data = measure_around(rot_sock, proc)

    with open("data.csv", "w") as f:
        for pos, power in all_data:
            f.write(f"{pos[0]},{pos[1]},{power}\n")
            print(f"{pos[0]},{pos[1]},{power}")
