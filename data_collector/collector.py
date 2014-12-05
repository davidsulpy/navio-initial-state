#!env python

import time, signal, sys
# IMU imports
from lib.Adafruit_ADS1x15 import ADS1x15
from lib.MS5611 import MS5611
from lib.MPU9250 import MPU9250

# threading to help?
import threading

# Initial State Imports
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket="Data Collection Board", buffer_size=20)


def signal_handler(signal, frame):
	print 'Ctrl+C pressed!'
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def get_and_record_baro(stop_event):
	# barometer
	baro = MS5611()
	baro.initialize()
	
	while (not stop_event.is_set()):
		baro.refreshPressure()
		baro.refreshTemperature()
		time.sleep(0.01) # 10 milliseconds
		baro.readPressure()
		baro.readTemperature()

		baro.calculatePressureAndTemperature()
		reading = {
			'pressure(millibar)': baro.PRES,
			'temp(C)': baro.TEMP
		}

		streamer.log_object(reading, signal_prefix="baro")

		time.sleep(1)
	print "barometer finished!"

def get_and_record_200g_accel(stop_event):
	# ADC addresses
	#ADS1015 = 0x00 # 12-bit ADC maximum sample rate (3300)
	ADS1115 = 0x01 # 16-bit ADC maximum sample rate (860)

	# adc settings
	adc_gain = 4096 # +/- 4.096V gain
	adc_sample_rate = 860 # 860 samples per second
	adc = ADS1x15(ic=ADS1115) ## http://www.ti.com/lit/ds/symlink/ads1115.pdf
	
	while (not stop_event.is_set()):
		# Get the +/- 200g accelerometer readings
		x_volts = adc.readADCSingleEnded(0, adc_gain, adc_sample_rate)
		y_volts = adc.readADCSingleEnded(1, adc_gain, adc_sample_rate)
		z_volts = adc.readADCSingleEnded(2, adc_gain, adc_sample_rate)

		streamer.log("200_x_mVolts", x_volts)
		streamer.log("200_y_mVolts", y_volts)
		streamer.log("200_z_mVolts", z_volts)

	print "200g accel finished!"

def get_and_record_accel_gyro_compas(stop_event):
	imu = MPU9250() # http://www.invensense.com/mems/gyro/documents/PS-MPU-9250A-01.pdf
	test_connection = imu.testConnection()
	streamer.log("imu_debug", "connection established: {}".format(test_connection))
	streamer.log("imu_message", "initializing")
	imu.initialize()
	## Accel scale is +/- 16g
	## Gyro scale is +/- 2000 deg/s
	## Magnetometer is +/- 4800 micro Teslas sensitivity 0.6 microT/LSB
	time.sleep(1)
	streamer.log("imu_message", "initialized")

	while (not stop_event.is_set()):
		m9a, m9g, m9m = imu.getMotion9()

		accel = {
			"x": m9a[0],
			"y": m9a[1],
			"z": m9a[2]
		}
		gyro = {
			"x": m9g[0],
			"y": m9g[1],
			"z": m9g[2]
		}
		mag = {
			"x": m9m[0],
			"y": m9m[1],
			"z": m9m[2]
		}

		streamer.log_object(accel, signal_prefix="accel")
		streamer.log_object(gyro, signal_prefix="gyro")
		streamer.log_object(mag, signal_prefix="mag")

		time.sleep(0.01) # 10 millisecond resolution

	print "imu finished!"

if __name__ == "__main__":
	stop_event = threading.Event()
	baro_thread = threading.Thread(target=get_and_record_baro, kwargs={"stop_event": stop_event})
	baro_thread.daemon = False
	accel_thread = threading.Thread(target=get_and_record_200g_accel, kwargs={"stop_event": stop_event})
	accel_thread.daemon = False
	imu_thread = threading.Thread(target=get_and_record_accel_gyro_compas, kwargs={"stop_event": stop_event})
	imu_thread.daemon = False

	baro_thread.start()
	accel_thread.start()
	imu_thread.start()

	stop = raw_input("Press [ENTER] to end.")

	stop_event.set()