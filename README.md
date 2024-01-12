# __IoT-Measurement Platform__


## IoT-Measurement Platform for Collection of Sensor data (Masters Thesis)
Our project adopted the working principle of SensIoT by M.Grossman et al (https://github.com/uniba-ktr/The-SENSIOT-Framework) but
with some modifications in order to achieve our results. 

The amd64/arm base sensor device
which is hosted on a docker container with local sensor devices attached through the i2c
port and gpio ports. The sensor devices collects data, by sensing it’s environment and sends
it to the manager, where this data are processed and analyzed. The processed data is queued
and sent through a message queuing service NSQD1 to amd64 base server which runs other
service for further data manipulation. The user can access and monitor the sensor devices
through a data visualization platform called Grafana.



## How to use
### Test Setup (amd64/arm)
To start the platform, navigate to the home directory of SensIoT, run the docker-compose
command in a detach mode;

```
docker-compose -p sensiot up -d
```

This command will start various containers such as Local manager, NSQ , Promethus and the
rest. Local Manager container will in turn create various sensor containers using docker.sock.
This is the UNIX socket that the process running daemon is listing to, and the main entry
point for Docker API.