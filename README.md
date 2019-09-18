# beans_autodoser_acaia

Software Dependencies:

Python3, touchphat, numpy, pyacaia and https://github.com/edwios/bluepy/tree/master/bluepy.

sudo apt-get install python3-numpy python3-pip 
curl https://get.pimoroni.com/touchphat  | bash
git clone https://github.com/edwios/bluepy/tree/master/bluepy
sudo pip3 install pyacaia
cd bluepy
sudo python setup.py install
cd
git clone git@github.com:lucapinello/beans_autodoser_acaia.git
cd beans_autodoser_acaia
Run with:  python3 beans_autodoser.py 

Hardware list:

Food dispenser with base https://www.amazon.com/dp/B000LFCLJ2

From Adafruit:
- Pimoroni Touch pHAT for Raspberry Pi Zero[ID:3472] 
- Raspberry Pi Zero WH (Zero W with Headers)[ID:3708]
- 16GB SD Card with Stretch Lite[ID:2820] 
- USB power (5v @1A)
- cables

servo motor: https://www.pololu.com/product/2149

Some 3d printed parts from here: https://www.thingiverse.com/thing:2907583 ( you need to cut post print the servo holder to fit properly the dispenser)

Some M2x8 Hex Head Screws

Mason Jar lid (medium) with some plumber tape around to have a snug fit. This goes on the exit an it should almost touch the paddles ( you need to make an hole that allows 1-2 beans at the time).










