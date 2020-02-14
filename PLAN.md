# BALLS project plan
## Components
* BALLS: these are the objects that will be juggled; they house the transmitters and LEDs. They need to be transparent so as to allow the LED lights to shine through; semi-transparency is probably preferred since a fully transparent ball would be hard to detect with CV. They also must be sturdy enough to protect the components inside.
   * LEDs: each ball will have a multicolored LED capable of switching between different hues based on a digital control signal. 
   * BALL-radio modules: each ball will have a XBee radio module capable of communicating with the controller and updating the LEDs accordingly. The firmware for XBee transmitters is flashed using [XCTU](https://www.digi.com/products/embedded-systems/digi-xbee/digi-xbee-tools/xctu).
   * Accelerometer: we are predicting that if issues arise with the central processor knowing which ball is which at all times via OpenCV(say for example a ball is thrown behind the back or a multiplexing such as [this](http://www.libraryofjuggling.com/Tricks/5balltricks/FiveBallStackedMultiplexCascade.html) is thrown), having an auxiliary data source could be useful for the central controller for knowing which ball is which. An accelerometer sensor will tell us which direction each ball is travelling in space which can be useful for ball matching as well as for statistics gathering.  
* Central controller: The balls will coordinate with some sort of central processor that will handle the OpenCV processing and tell which balls to light up
   * OpenCV: the crux of the project, OpenCV is a computer vision software library that will track the balls and be able to provide data about the BALLS as they are being thrown using blob detection.
   * Coordinator-radio module: the central controller will feature a radio module as well which will gather XBee sensor data and transmit which module should change to which color accordingly.
   * Camera module: the camera module will gather the video data to send to OpenCv.
   * Processing: we separated this from OpenCV since functionally we only expect to get from OpenCV information about the travel paths of different blobs. The Processing submodule will keep track of which ball corresponds to which blob, choose which color to send to each ball by running the OpenCV data on the selected pattern software, and will transmit the color information to the balls.
   * Pattern software: we will have different software APIs for updating the LEDs on the balls based on how we perceive its travel path. We haven’t worked on the exact specifics but we imagine that we will have time series data of where each blob is at any time and by looking at the blobs over short periods of time we can ascertain different properties about each individual ball (traveling left, traveling up, stationary, etc) and using these properties we can design different pattern functions that have the balls become different hues based on their properties.    
   * Statistics gathering: The other angle of that the project could go into based on timing constraints is statistics gathering. Since we are gathering all of these sensor and video images anyways, it could be interesting to do something with it such as track how long the juggler is able to maintain their pattern, how many catches they throw, etc.
   * Buttons: no use case yet but 
## Timeline
### Checkpoint 1
We will have a functional CV setup capable of blob-tracking objects roughly the expected size of the ball.
### Checkpoint 2
We will have a CV setup on the main computer capable of blob-tracking the balls while they are in motion, such as when being juggled. Using the output from OpenCV, the positions of the balls will be mapped to a 2-D plane perpendicular to the juggler’s orientation (that is, horizontal position as the x-axis, and distance from the floor as the y-axis).

We will have the radio module installed to the central computer as well as a simple assembly consisting of a BALL-radio module and LED connected to a battery. Through crafting arbitrary signals on the central controller, we will be capable of sending a signal to a BALL-radio module to make its LED turn a certain color.
# Component interfaces
* XBee: XBee radio modules are programmed using XCTU software via USB, receives data to transmit via UART but also supports both digital and analog direct sampling. Samples are transmitted over the air in the 2.4GHz band using an OQPSK modulation pattern.
* LED: the LEDs on the balls will produce different hues of light based on a sensor input ideally a digital input.
* Accelerometer: The accelerometer will output X,Y, and Z acceleration data from BALLS information via an analog output.
* Camera: the camera will provide a link between the external visual plane and the central controller, allowing the central controller to act on movement in the world around it
* Controller: the central hub that connects the coodinator-radio module, OpenCV, and the data processing software. Information will be received from OpenCV, processed using our BALL-tracking algorithm, and then, based on certain conditions occurring in the movement of the ball, sends signals to the BALL-radio module to change the lighting.
# Security
The recreational nature of this project means that security is not as high a concern as the other components. With that said, AES-128 encryption will be used on all data sent between the XBee radio modules to check that the signals it is receiving are indeed coming from the main computer; otherwise, a nefarious party could send signals to the balls that cause the balls to perform undesirable actions, such as lighting up at the wrong time.

The US Department of Homeland Security provides a document[1] detailing precautions that manufacturers of IoT devices should consider. We will follow the advice of incorporate security at the design phase by choosing secure hardware, using the latest version of Linux (on the main computer) and device firmware (for smaller components like the receiver). We are still not sure of the potential distribution model of BALLS, but their advice of advance security updates and vulnerability management will be followed on the devices that we use for our demonstrations, and updates that patch security vulnerabilities will be automatically installed by nature of running a Linux distribution on the main computer. Since it’s hard to argue a reason not to follow standard security practices, we will follow their advice of build on proven security practices. We will also prioritize security measures according to potential impact by focusing on the security of wireless communications, as that is the main attack vector by which malicious parties could attack a BALLS-driven performance. Since BALLS is a self-contained system that, outside of installing updates, has no need to connect to an external network, promoting transparency across IoT will be a lesser concern. We will be connecting carefully and deliberately by choosing components that are hard to tamper with, as well as avoiding internet connections wherever possible.
# Assignments
##Mike Hegarty
* XBee
* Accelerometer
* Pattern software
* Radio
* LEDs
## Zach Day
* OpenCV (small contribution)
* Processing
* Pattern software
* Statistics gathering
## Greg Kahl
* OpenCV
* Camera
* Pattern software


________________
[1] https://github.com/gwu-iot/collaboration/blob/master/papers/dhs16guidelines.pdf
