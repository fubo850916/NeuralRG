import os
import sys
sys.path.append(os.getcwd())

from profilehooks import profile

import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
torch.manual_seed(42)

import numpy as np
from numpy.testing import assert_array_almost_equal,assert_array_equal
from model import Gaussian,MLP,RealNVP,CNN

from subprocess import Popen, PIPE
import pytest

noCuda = 0
try:
    p  = Popen(["nvidia-smi","--query-gpu=index,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode", "--format=csv,noheader,nounits"], stdout=PIPE)
except OSError:
    noCuda = 1

maxGPU = 0
if noCuda == 0:
    try:
        p = os.popen('nvidia-smi --query-gpu=index --format=csv,noheader,nounits')
        i = p.read().split('\n')
        maxGPU = int(i[-2])+1
    except OSError:
        noCuda = 1

skipIfNoCuda = pytest.mark.skipif(noCuda == 1,reason = "No cuda insatllation, found through nvidia-smi")
skipIfOnlyOneGPU = pytest.mark.skipif(maxGPU < 2,reason = "Only one gpu")

def test_invertible():

    print("test realNVP")
    gaussian = Gaussian([2])

    sList = [MLP(1, 10), MLP(1, 10), MLP(1, 10), MLP(1, 10)]
    tList = [MLP(1, 10), MLP(1, 10), MLP(1, 10), MLP(1, 10)]

    realNVP = RealNVP([2], sList, tList, gaussian)

    z = realNVP.prior(10)
    #mask = realNVP.createMask()
    assert realNVP.mask.shape[0] == 2

    print("original")
    #print(x)

    x = realNVP.generate(z)

    print("Forward")
    #print(z)

    zp = realNVP.inference(x)

    print("Backward")
    #print(zp)

    assert_array_almost_equal(z.data.numpy(),zp.data.numpy())

    saveDict = realNVP.saveModel({})
    torch.save(saveDict, './saveNet.testSave')
    # realNVP.loadModel({})
    sListp = [MLP(1, 10), MLP(1, 10), MLP(1, 10), MLP(1, 10)]
    tListp = [MLP(1, 10), MLP(1, 10), MLP(1, 10), MLP(1, 10)]

    realNVPp = RealNVP([2], sListp, tListp, gaussian)
    saveDictp = torch.load('./saveNet.testSave')
    realNVPp.loadModel(saveDictp)

    xx = realNVP.generate(z)
    print("Forward after restore")

    assert_array_almost_equal(xx.data.numpy(),x.data.numpy())

def test_3d():

    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    #mask3d = realNVP3d.createMask()

    assert realNVP3d.mask.shape[0] == 2
    assert realNVP3d.mask.shape[1] == 4
    assert realNVP3d.mask.shape[2] == 4

    print("test high dims")

    print("Testing 3d")
    print("3d original:")
    #print(x3d)

    z3d = realNVP3d.generate(x3d,2)
    print("3d forward:")
    #print(z3d)

    zp3d = realNVP3d.inference(z3d,2)
    print("Backward")
    #print(zp3d)

    print("3d logProbability")
    print(realNVP3d.logProbability(z3d,2))

    saveDict3d = realNVP3d.saveModel({})
    torch.save(saveDict3d, './saveNet3d.testSave')
    # realNVP.loadModel({})
    sListp3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tListp3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVPp3d = RealNVP([2,4,4], sListp3d, tListp3d, gaussian3d)
    saveDictp3d = torch.load('./saveNet3d.testSave')
    realNVPp3d.loadModel(saveDictp3d)

    zz3d = realNVPp3d.generate(x3d,2)
    print("3d Forward after restore")
    #print(zz3d)

    assert_array_almost_equal(x3d.data.numpy(),zp3d.data.numpy())
    assert_array_almost_equal(zz3d.data.numpy(),z3d.data.numpy())

def test_checkerboardMask():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask3d = realNVP3d.createMask("checkerboard")
    print(realNVP3d.mask)

    z3d = realNVP3d.generate(x3d,2)
    print(realNVP3d.mask)
    print("3d forward:")
    #print(z3d)

    zp3d = realNVP3d.inference(z3d,2)
    print("Backward")
    #print(zp3d)

    print("3d logProbability")
    print(realNVP3d.logProbability(z3d,2))

    saveDict3d = realNVP3d.saveModel({})
    torch.save(saveDict3d, './saveNet3d.testSave')
    # realNVP.loadModel({})
    sListp3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tListp3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVPp3d = RealNVP([2,4,4], sListp3d, tListp3d, gaussian3d)
    saveDictp3d = torch.load('./saveNet3d.testSave')
    realNVPp3d.loadModel(saveDictp3d)

    zz3d = realNVPp3d.generate(x3d,2)
    print("3d Forward after restore")
    #print(zz3d)

    assert_array_almost_equal(x3d.data.numpy(),zp3d.data.numpy())
    assert_array_almost_equal(zz3d.data.numpy(),z3d.data.numpy())

@skipIfNoCuda
def test_checkerboard_cuda():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3).cuda()
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d).cuda()
    mask3d = realNVP3d.createMask("checkerboard")

    z3d = realNVP3d.generate(x3d,2)
    zp3d = realNVP3d.inference(z3d,2)

    print(realNVP3d.logProbability(z3d,2))

    assert_array_almost_equal(x3d.cpu().data.numpy(),zp3d.cpu().data.numpy())

def test_sample():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d,"checkerboard")

    z3d = realNVP3d.sample(100,2,True)

    zp3d = realNVP3d.sample(100,2,False)

    print(realNVP3d.logProbability(z3d,2))

@skipIfNoCuda
def test_sample_cuda():
    gaussian3d = Gaussian([2,4,4])
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d,"checkerboard").cuda()

    z3d = realNVP3d.sample(100,2,True)

    zp3d = realNVP3d.sample(100,2,False)

    print(realNVP3d.logProbability(z3d,2))

@skipIfOnlyOneGPU
def test_checkerboard_cuda_cudaNot0():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3).cuda(maxGPU//2)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]
    tList3d = [CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure),CNN([2,4,2],netStructure)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d).cuda(maxGPU//2)
    mask3d = realNVP3d.createMask("checkerboard")

    z3d = realNVP3d.generate(x3d,2)
    zp3d = realNVP3d.inference(z3d,2)

    print(realNVP3d.logProbability(z3d,2))

    assert_array_almost_equal(x3d.cpu().data.numpy(),zp3d.cpu().data.numpy())

@profile
@pytest.mark.skip(reason = "speed test")
def testCopyspeed():
    for _ in range(100):
        t = torch.randn([1000,1000])
        a = Variable(t)

@profile
@pytest.mark.skip(reason = "speed test")
def testCopyspeedCuda():
    for i in range(100):
        t = torch.randn([3000,3000]).cuda()
        t = torch.randn([3000,3000]).pin_memory().cuda()

if __name__ == "__main__":
    #test_checkerboardMask()
    #test_checkerboard_cuda_cudaNot0()
    #copyTest()
    #copyTest_model()
    testCopyspeed()
