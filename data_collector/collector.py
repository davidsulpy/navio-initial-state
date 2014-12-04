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


def get_and_record_baro():
	# barometer
	baro = MS5611()
	baro.initialize()
	
	while True:
		try:
			baro.refreshPressure()
			baro.refreshTemperature()
			time.sleep(0.01)
			baro.readPressure()
			baro.readTemperature()

			baro.calculatePressureAndTemperature()
			reading = {
				'pressure(millibar)': baro.PRES,
				'temp(C)': baro.TEMP
			}

			streamer.log_object(reading, signal_prefix="baro")

			time.sleep(1)
		except KeyboardInterrupt:
			print "KeyboardInterrupt fired"
			break

def get_and_record_200g_accel():
	# ADC addresses
	ADS1015 = 0x00 # 12-bit ADC
	ADS1115 = 0x01 # 16-bit ADC

	# adc settings
	adc_gain = 4096 # +/- 4.096V gain
	adc_sample_rate = 250 # 250 samples per second
	adc = ADS1x15(ic=ADS1115)
	
	while True:
		try:
			# Get the +/- 200g accelerometer readings
			x_volts = adc.readADCSignalEnded(0, adc_gain, adc_sample_rate) / 1000
			y_volts = adc.readADCSignalEnded(1, adc_gain, adc_sample_rate) / 1000
			z_volts = adc.readADCSignalEnded(2, adc_gain, adc_sample_rate) / 1000

			streamer.log("200_x_volts", x_volts)
			streamer.log("200_y_volts", y_volts)
			streamer.log("200_z_volts", z_volts)

			#Do I need to sleep here??
		except KeyboardInterrupt:
			print "KeyboardInterrupt fired"
			break

def get_and_record_accel_gyro_compas():
	imu = MPU9250()
	test_connection = imu.testConnection()
	streamer.log("imu_debug", "connection established: {}".format(test_connection))
	streamer.log("imu_message", "initializing")
	imu.initialize()
	time.sleep(1)

	while True:
		try:
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

			time.sleep(0.1)
		except KeyboardInterrupt:
			print "KeyboardInterrupt fired"
			break

if __name__ == "__main__":
	baro_thread = threading.Thread(target=get_and_record_baro)
	baro_thread.daemon = False
	accel_thread = threading.Thread(target=get_and_record_200g_accel)
	accel_thread.daemon = False
	imu_thread = threading.Thread(target=get_and_record_accel_gyro_compas)
	imu_thread.daemon = False

	baro_thread.start()
	accel_thread.start()
	imu_thread.start()