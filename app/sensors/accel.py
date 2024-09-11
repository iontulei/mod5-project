import smbus					#import SMBus module of I2C
from time import sleep          #import

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

bus = None

def MPU_Init():
	global bus
	bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards

	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
	high = bus.read_byte_data(Device_Address, addr)
	low = bus.read_byte_data(Device_Address, addr+1)
    
	#concatenate higher and lower value
	value = ((high << 8) | low)
	
	#to get signed value from mpu6050
	if(value > 32768):
		value = value - 65536
	return value


Device_Address = 0x68   # MPU6050 device address

# MPU_Init() # moved this into read_raw_acceleration()


SHARP_MOVEMENT_THRESHOLD = 5000

def read_raw_acceleration():
       MPU_Init()
       return read_raw_data(ACCEL_XOUT_H), read_raw_data(ACCEL_YOUT_H), read_raw_data(ACCEL_ZOUT_H)


if __name__ == "__main__":
	prev_acc_x = 0  # Initialize previous acceleration values
	prev_acc_y = 0
	prev_acc_z = 0
	
	while True:
		
		#Read Accelerometer raw value
		# acc_x = read_raw_data(ACCEL_XOUT_H)
		# acc_y = read_raw_data(ACCEL_YOUT_H)
		# acc_z = read_raw_data(ACCEL_ZOUT_H)
		acc_x, acc_y, acc_z = read_raw_acceleration()

		#Calculate changes in acceleration
		delta_x = abs(acc_x - prev_acc_x)
		delta_y = abs(acc_y - prev_acc_y)
		delta_z = abs(acc_z - prev_acc_z)

		prev_acc_x = acc_x
		prev_acc_y = acc_y
		prev_acc_z = acc_z

		print("delta_x: ", delta_x, " delta_y: ", delta_y, " delta_z: ", delta_z)

		# Check for sharp movement
		if delta_x > SHARP_MOVEMENT_THRESHOLD or delta_y > SHARP_MOVEMENT_THRESHOLD or delta_z > SHARP_MOVEMENT_THRESHOLD:
			print("Sharp movement detected")

		#Read Gyroscope raw value
		gyro_x = read_raw_data(GYRO_XOUT_H)
		gyro_y = read_raw_data(GYRO_YOUT_H)
		gyro_z = read_raw_data(GYRO_ZOUT_H)

		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		Ax = acc_x/16384.0
		Ay = acc_y/16384.0
		Az = acc_z/16384.0

		Gx = gyro_x/131.0
		Gy = gyro_y/131.0
		Gz = gyro_z/131.0

		# print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az) 	
		sleep(0.1)