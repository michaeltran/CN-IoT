# COSC 6377 - Computer Networks (Project)

Name: Hai-Y Michael Tran Nguyen

UH email address: mhtran4@uh.edu

Your ID: 0925358

## Implementation Details:

Server Component implemented using Python 2.7.12.
Android Component implemented using C#/Xamarin.

## System Requirements
	Raspberry Pi 2B
		USB Webcam
		VL53L0X Distance Sensor
		Speaker
	2 Windows Servers
		Main Server
		SQL Server
	Android Phone and/or Emulator

## How to Run:
For detailed instructions on how to setup this application - see report.pdf.

### On Server:
	run ./Server/server.py
	run ./Server/serverHTTP.py

### On Raspberry Pi:
	run ./RaspberryPi/client.py -f <FACE_RECOGNITION_TYPE>
<FACE_RECOGNITION_TYPE> = AWS or OPENCV

### On Android:
	Start "COSC6377 Project" Application

## Limitations:

This script requires you to be connected to the internet (on Server, Raspberry Pi, and Android) to run.

## Required Stuff:

### Server
	AWS
	pyodbc

### Raspberry Pi
	AWS
	VL53L0X
	MPG123
	OpenCV
	wondershaper

## Internet Throttling
	sudo wondershaper wlan0 256 128
	sudo wondershaper clear wlan0