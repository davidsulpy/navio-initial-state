import getopt, sys, time, csv
from ISStreamer.Streamer import Streamer

def read_args(argv):
	try:
		opts, args = getopt.getopt(argv,"hb:k:",["bucket_name=", "access_key="])
	except getopt.GetoptError:
		print('data_shipper.py -b <bucket_name> -k <access_key> -f <file_location>')

	for opt, arg in opts:
		if opt == '-h':
			print('data_shipper.py -b <bucket_name> -k <access_key>')
		elif opt in ("-b", "--bucket_name"):
			bucket = arg
		elif opt in ("-k", "--access_key"):
			access_key = arg
		elif opt in ("-f", "--file"):
			file_location = arg

	return bucket, access_key, file_location


if __name__ == "__main__":
	bucket, access_key, file_location = read_args(sys.argv[1:])

	streamer = Streamer(bucket_key=bucket, access_key=access_key, buffer_size=20, offline=False)

	with open(file_location, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		counter = 0
		for row in reader:
			streamer.log(row[1], row[2], epoch=row[0])
			counter += 1

			if counter%10==0:
				time.sleep(.01) # rest for 10 ms to not go crazy with resources

	streamer.flush()
