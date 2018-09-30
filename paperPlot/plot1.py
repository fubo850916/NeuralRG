import numpy as np

import matplotlib.pyplot as plt

T = np.array([2.0,2.1,2.2,2.269185314213022,2.3,2.4,2.5])

loss4 = np.array([-660.8114624023438,-632.1803588867188,-606.3014526367188,-589.8558349609375,-582.8676147460938,-561.7283935546875,-542.5540771484375])

loss3 = np.array([-660.7703857421875,-632.1431884765625,-606.2661743164062, -589.8319091796875,-582.8795166015625,-561.7555541992188,-542.6287841796875])

loss2 = np.array([-660.5372314453125,-631.9585571289062,-606.1282958984375,-589.7266845703125,-582.7877197265625,-561.6671142578125,-542.4461059570312])

loss1 = np.array([-657.83349609375,-629.3168334960938,-603.5908203125,-587.3035278320312,-580.3790893554688,-559.396240234375,-540.4917602539062])

exact = np.array([263.29621043402125,252.8952741554581,243.9756979903575,238.64225663513287,236.59802766605696,230.73226236763298,225.81063208450638])

fix = np.array([399.418793393396,381.48763983688104,364.9500280838529,354.2334832224499,349.63580114185936,335.4021735990462,322.1283767570811])

res1 = np.abs(-loss1-exact-fix)/(exact+fix)
res2 = np.abs(-loss2-exact-fix)/(exact+fix)
res3 = np.abs(-loss3-exact-fix)/(exact+fix)
res4 = np.abs(-loss4-exact-fix)/(exact+fix)

plt.plot(T,res1,label="depth = 1")
plt.plot(T,res2,label="depth = 2")
plt.plot(T,res3,label="depth = 3")
plt.plot(T,res4,label="depth = 4")

plt.legend()

plt.xlabel("Temperature")
plt.ylabel("$|loss-exact lnZ|/exact lnZ$")

plt.show()


import pdb
pdb.set_trace()