import serial

# ttyUSB0 & ttyUSB1
def read_data(com):
    try:
        arduino = serial.Serial(com, 9600, timeout=1)
        data = int(arduino.readline().decode('utf-8').rstrip())
        return data
    except serial.SerialException:
        return 0

if __name__ == "__main__":
    while True:
        print(read_data('/dev/ttyUSB0'))