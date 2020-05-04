# CHIC sketch book

This document is a presentation (that I keep for myself) to remember what I have done, that shows all the electronic work done for the CHIC project. It is some sort of personal documentation, that I try to let clean to illustrate the progress that i am doing. 

Contains the following sections :

1. Setting up ESP8266 with an arduino
    1. Home made voltage source
    2. Home made USB to TTL cabe (to command the module using arduino's UART from my computer)
    3. Setting up server in R-PI for UDP communication
2. Processing usage within R-PI for image generation

# 1. Wifi module with Arduino and R-PI

At first, we bought two ESP8266 wifi modules, to test if this MC would suits our requirements. As will see, our tests were very successful as we ended up picking this MC as our final one. Also, it allowed us to test the server functionalities of the Raspberry PI, using UDP server protocol. 

The ESP8266 wifi module is a MC that is able to connect to wifi and to be a wifi router. The one that I bought has to be flashed to have some code, and it already has **AT command library**. firmware[a] is a specific class of computer software that provides the low-level control for a device's specific hardware.

We use AT commands to do the most basic operations (setting wifi mode, decide how to )
Wifi module used: ESP-8266-12F

## Problem 1: Current supply of the ESP8266

The second problem is for the current. The wifi module needs that have at maximum 500 mA, and the 5V output pin is good for 400 mA, so I am not sure it will work fine. The 3.3V output is capable of supplying 150 mA. The voltage input of the wifi module has to be maximum 3.6V.

### Solution for current supply: Step-Down Voltage Converter

I have found in my stuff Dc-Dc converter that I can use. By using a USB cable, i was able to create a voltage source with high current tolerance which can go up to 4.4 Volts (that's enough for my wifi module) and that is controllable. I will let it at 3.5 volts for now !

Here is the set-up that i did for the DC-DC 5v to 3.3v converter.

![](pics/dcdc_home_made.jpeg)

Now, I need to start working with the wifi module, which is not going to be easy since I can't flash it... Or I don't know how to do so. Let's try some things.

## Problem 2: Flashing the ESP8266-12F

It turned out that the wifi module I am using is not a single wifi module but is a proper MC itself that needs to be flashed. I do not have a cable to flash it, so it will be very difficult to do anything without it. However I will still try to do without one.

Maybe we don't need flashing, according to those 2 tutorial
https://www.instructables.com/id/Add-WiFi-to-Arduino-UNO/
https://www.instructables.com/id/ESP-12E-ESP8266-With-Arduino-Uno-Getting-Connected/

AT Tutorial to connect to internet: https://arduino.stackexchange.com/questions/32567/get-data-from-website-with-esp8266-using-at-commands
And AT commands tutorial: https://www.esp8266.com/viewtopic.php?f=12&t=13556

### Solution to problem 2: connect to wifi with AT Commands and use Arduino to send the instructions.

So at the end I found proper way to connect to server using the AT example PDF. Properly, I am not flashing the MC but instead I am sending instructions to it.

The setup to use the Arduino board as USB-TTL cable is the following:

![](pics/esp8266_setup_1.jpeg)


## Problem 3: The web server (UDT protocol connection)

My first tentative was to use a HTTP server (like Python.flask or python.Django) but I think it's better to use low-level protocol like TCP or UDP

### TCP or UDP ?

According to this link: http://www.skullbox.net/tcpudp.php, UDP is faster than TCP. The main difference is that TCP is a protocol that waits for a confirmation of received data every time a package is sent, as UDP is a streaming protocol that keeps sending data even if some error occured during the transmission of previously sent data. In our case, we will want to have streaming of sensed data and we don't care if some data was not sent correctly. Therefore, we will want to use TCP.

### Code on the server

Creating an UDP server in python is *extremely simple* and the code to implement it is the following:


```python
#!/usr/bin/env python3

import socket

UDP_IP = "192.168.1.40" # this is the IP of the R-PI
UDP_PORT = 5005 # This port has to be open, with linux command 'sudo ufw enable 5005'

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message:", data.decode())

```

The documentation is accessible at this link: https://wiki.python.org/moin/UdpCommunication

### Commands on the ESP8266

How to send the data (**bytes array**) from the ESP ?

```
AT+CWMODE=3 // Set station mode of the module
AT+CWJPA="name_of_wifi","password" // Connect to the wifi if that wasn't the case
AT+CIFSR // Verify that wifi is connected (this gives the IP address of the ESP8266)

AT+CIPSTART="UDP","192.168.1.40",5005,1112,0 // Connects to the server
AT+SEND=N // Send n bytes
> bytes_to_send
AT+CIPCLOSE=4 // End the connection
```

Those commands works fine, and their are sent via UART from the Arduino. So the next steps are to make sure that it is the arduino itself who is sending those data, and then to try them out from a real sensor to test the actual rate that can be obtained!

# Sensing circuit: actually making the circuit.

The challenge is now to have proper arduino sensing the data and proper esp8266 sending the live stream of data to the host. It is quite different to make every thing automatic rather than using command line tools to make it step by step.

As a matter of fact, I encountered **many** problems while trying to have UART communication purely between the esp8266 and the arduino. It became completely impossible to do, and I don't really have an idea of why that was the case. I came with the following observations
- When grounded to the ground of the power supply (and therefore, the ground of the esp8266), the Arduino serial communication with the computer was broken, but only if the ESP8266 was connected to the power chain
- The esp8266 was doing some hard voltage drops accross the overall power line (for some weird reasons... I think it was taking a lot of current)

So, since I have bought the Huzzah developing board (https://learn.adafruit.com/adafruit-huzzah-esp8266-breakout/overview) I decided I would try with this one instead of being doing all of it manually with the actual module itself.

The good news is that **I have successfully flashed some code over it** using only my **USB to TTL** cable, to that's quite handy for programming over a PCB. There is a 'flashing' mode to be enabled over the MC, which can be done purely with some buttons on the board. Maybe we need to do the same for the atmega328p.

Now I am trying to do the 2 following things with this board
1. UART communication with the arduino
2. Sending stream of data to the host

### Solution 1: UART communication

It was quite simple to set up the UART using the provided board, which makes me wonder why it was impossible without the board. I'll try to find out the problem cause I'm curious

Now, I'm going to try to read some sensor data and to send it to the wifi board, that will in return send it to the host. Let's see what rate we can achieve !

Here is a great link to explain serial communication using Arduino: https://forum.arduino.cc/index.php?topic=396450

### Solution 2: getting rid of the Arduino

A question for myself: "why are we using Arduino ?". Mostly, the answer is "it's because I had nothing to program directly the ESP8266". The Arduino brings nothing to the circuit itself, as the ESP8266 already has a built-in ADC pin, and many GPIO which can perform PWM, as well as digital reading. 

UDP documentation for esp8266: https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/udp-examples.html

#  The PCB design

I attended both workshop held by Octanis about PCB design and PCB layout. It's now time to make it real. Mostly, we already have a fairly good idea of the circuit that we will build, but there are still points that are lacking.

Questions to answer...

- Is the power supply system that we have good enough ? 
- How to use the USB-C cable (that we use to charge the battery) to also send commands to the MC (and eventually as well to the ESP8266, if that's possible !) ?

Also, I need to add a button to reboot the ATMega and the ESP8266, it would be really handy !

Here is a link that shows how to use a ISP header to code the ATMega328: https://maker.pro/custom/tutorial/programming-an-atmega328-microcontroller-on-a-pcb

Here is a link with Schematic of Standalone Arduino With FTDI Programming: https://dzone.com/articles/schematic-of-standalone-arduino-with-ftdi-programm. Note that it say "To program the chip via FTDI module, we have to bootload it first. I used an Arduino Uno as the ISP".

(esp8266 arduino support documentation: https://arduino-esp8266.readthedocs.io/en/2.6.3/reference.html?highlight=digitalRead#digital-io)

# Processing and Arduino

We want to use the data collected by Arduino to generate some videos on processing. Processing is an open-source software (on which Arduino is built on top) for graphics generation. It can be installed on any machine, including for instance our Raspberry pi. 

Command line to turn on processing : `processing-java --sketch=PWD --run`
(X display must be set to 0 with `export DISPLAY=:0`)

I found out that processing has a library (done by someone and found on a server) to make a UDP server directly within processing. This is exactly what we want. There is still a lot of coding to be done, but it is working fine. I can read, using the processing software, the data from the sensors. 

### Receiving the data

The sensors send the following information:

- If a sensor is sensing touch, it sends the number of miliseconds since it was touched, at a frequency of 4 Hz
- When the sensor is getting untouched, it sends an "end" message to let know the server that it stops

This model was used in order to not send bytes of data always, but only when someone is touching one plant. 