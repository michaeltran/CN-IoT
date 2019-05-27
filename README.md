# COSC 6377 - Computer Networks (Project)

Name: Hai-Y Michael Tran Nguyen

UH email address: mhtran4@uh.edu

ID: 0925358

## Goal

> The goal of this project is to build a physical authentication system that will stream a series of images (or a video) to an android app and use face recognition to inform an admin of who is currently in the picture. This admin will be able to authenticate, reject, or send a custom message to the raspberry pi and it will output it through speakers. The admin will also be able to program a new user into the face recognition software on command.

## What You Will Learn

> You will learn about all the moving parts (Raspberry Pi, Sensors, Webcams, Main Server, SQL Server, Android, AWS, etc.) that have to work together in unison to provide a simple video stream with authentication functionality to a user. With further usage, you will discover the limitations (of the FPS) of this program due to network and processing times.

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
For detailed instructions on how to setup this application - see [[report.pdf]](https://github.com/michaeltran/CN-IoT/blob/master/report.pdf).

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
	
---
	
## DIY Tutorial

### Setup: Raspberry Pi

First you should connect the USB Webcam and Speaker to the Raspberry Pi. Secondly you should connect the VL53L0X Distance Sensor to the Raspberry Pi (See http://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html on how to connect the sensor to the Pi).

The following Interfaces should be enabled on the Raspberry Pi: Camera, I2C. You should also enable SSH and VNC as it will make life easier.

Install AWS, VL53L0X, MPG123, OpenCV onto the Raspberry Pi. Note: OpenCV installation is a time-consuming process and should be done ASAP.

Now get the folder “./RaspberryPi” from the git repository at https://github.com/cosc6377/project-m1-michaeltran.

Modify the following scripts:

* Client/client.py
	* HOST: The Main Server PUBLIC IP Address
	* PORT: The Port
	* WRITE_LOG (True/False): Turn logging on or off
	* COLLECTION_ID: The AWS COLLECTION_ID

### Setup: Server

You should obtain 2 servers from the AWS EC2 service. One will be for the main server, and one will be the SQL Server that contains the database of names and distances.

On the server for SQL Server, create a database called FACEDB. Run the following script from the git repository on FACEDB: `./Database/DBSchema.sql`.

On the main server, install AWS and pyodbc.

On the main server, get the following folder from the git repository `./Server`.

Modify the following scripts:
* server.py
	* HOST: The Main Server PRIVATE IP Address
	* PORT: The Port for Server/Pi Communication
	* LONG_POLL (True/False): Turn long poll on or off
	* WRITE_LOG (True/False): Turn logging on or off
* httpserver.py
	* HOST: The Main Server PRIVATE IP Address
	* PORT: The port
* customsqlserver.py (connection string)
	* Server: Public IP Address of the SQL Server
	* UID: Username
	* PWD: Password
	
### Setup: Android

On any PC with visual studio and Xamarin, get the following folder from the git repository `./Android`.

Open the project and find all references to CustomHTTPServer and change the first parameter to the main server public IP address and the second parameter to the port.

Build and deploy the application on either your android phone or emulator.

### Setup: AWS

Assuming you have installed and configured AWS on the server (if you haven’t, see http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html), run `./Server/Amazon Api/uploadimage.py` to do an initial setup for the face collection.

### Setup: Final

Now that all 3 parts are setup, we should be able to run the application. Follow these steps:

1. Ensure Main Server and SQL Server are up
2. On the Main Server: run the following scripts on two different command prompts: server.py and httpserver.py
3. On the Raspberry Pi: run client.py -f <option> (option can be either AWS or OPENCV, default is AWS)
4. On the Android: start the application and click on of the options
