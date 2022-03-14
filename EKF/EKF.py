from math import sqrt
from numpy.random import randn
from numpy import eye, array, asarray, diag, arange
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import ExtendedKalmanFilter
import matplotlib.pyplot as plt 
# import kf_book.ekf_internal as ekf_internal

def HJacobianAt(x):
    """Compute Jacobain of H matrix at x"""
    horiz_dist = x[0]
    altitude = x[2]
    denom =sqrt(horiz_dist**2 + altitude**2)
    return array([[horiz_dist / denom, 0, altitude / denom]])

def hx(x):
    """compute measurement for slant range that would correspond
    to state x"""
    return sqrt((x[0]**2 + x[1]**2))


class RadarSim:
    """
    Simulates the radar signalreturns from an object
    flying at a constant altitude and velocity in 1D
    """
    
    def __init__(self, dt, pos, vel, alt):
        self.dt = dt
        self.pos = pos
        self.vel = vel
        self.alt = alt
    
    def getRange(self):
        """
        Returns slant range to the object. Call once
        for each new measurementat dt time from last call
        """

        # add some process noise to the system 
        self.vel += 0.1 * randn()
        self.alt += 0.1 *  randn()
        self.pos += self.vel * self.dt

        err = self.pos * 0.05 *  randn()
        slant_dist = sqrt(self.pos**2 + self.alt**2)

        return slant_dist + err

pos_idx = 0
vel_idx = 1
alt_idx = 2
dt = 0.05
rk = ExtendedKalmanFilter(dim_x = 3, dim_z = 1)
radar = RadarSim(dt, pos = 0., vel = 100., alt = 1000.)

# make an imperfect starting guess
rk.x = array([radar.pos - 100, radar.vel + 100, radar.alt + 1000])
rk.F = eye(3) + array([[0,1,0], 
                       [0,0,0], 
                       [0,0,0]]) * dt
range_std = 5.
rk.R = diag([range_std **2])
rk.Q[0:2, 0:2] = Q_discrete_white_noise(2, dt = dt, var = 0.1)
rk.Q[2,2] = 0.1
rk.P *= 50

xs , track = [], []

for i in range(int(20/dt)):
    z = radar.getRange()
    track.append((radar.pos, radar.vel, radar.alt))

    rk.update(array([z]), HJacobianAt, hx)
    xs.append(rk.x)
    rk.predict()

xs = asarray(xs)
track = asarray(track)
time = arange(0, len(xs) * dt, dt)

# plt.plot(time, xs[:,1])
plt.plot(time, track[:,2], 'r--', time, xs[:,2])
plt.show()
# ekf_internal.plot_radar(xs, track, time)

