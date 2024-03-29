# BALLS - Checkpoint 2

## System Overview

### Blob Detection
* Since we are no longer using smart balls at the moment we are keeping with our original ball detection strategy of looking for masking for blue objects and using blob detection to find all balls in each frame
### Ball States
* The BALLS have three different states: Caught, Airborne, and "Jumpsquat" (In the process of being thrown)
* We use the Jumpsquat state because as the ball is in the juggler's hand it can dip in and out of frame, this prevents false positive of catches

|Initial State |New State | Transition condition |
| - | - | -|
| Airborne | Caught| A ball is "caught" when it reaches the juggler's hand and it is lost by the blob detection |
| Caught | Jumpsquat| A ball enters jumpsquat when it first re-appears after being caught |
| Jumpsquat | Airborne | A ball is airborne once it crosses past an intial threshhold x or y value from where it first came back into frame|


### Ball Asigning
* Once the blobs have been detected we then need to find which ball object they correspond to. 
* We check if the detected blobs intersect with the area of the balls from the last frame, in which case the blob is identified as belonging to that ball and the ball's location data is updated. 
* When a "new" blob is detected that doesn't intersect with the previous balls, it checks all the non-airborne balls, and assigns the blob to the closest one. This newly assigned ball is put into the Jumpsquat state.

![](res/check2_1.png)
![](res/check2_2.png)
