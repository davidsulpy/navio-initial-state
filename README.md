NAVIO + Initial State
===================

Python script to collect Navio IMU board data and stream it into a file using ISStreamer. Then, a helper script `data_shipper.py` to get the IMU board data from the csv output of the `data_collector/collector.py` and ship it to Initial State.

>*Note*: you can change the `data_collector/isstreamer.ini` file to disable offline mode and then supply an `access_key` to stream the data to Initial State real-time. However, if you do this, you need to reduce the rate of data sampling in the `data_collector/collector.py` by increasing sleep times between samples (e.g. line 110 and line 61).