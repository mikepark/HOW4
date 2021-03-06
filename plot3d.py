from __future__ import division
import numpy as npy

#-----------------------------------------------------------
# writes a 2D ascii plot3d grid file
def writePlot2D(fname, X, Y):
    f = open(fname, 'w')
    ni, nj = X.shape
    
    npy.set_printoptions( precision=16, threshold = ni )
    
    f.write('1'+'\n')
    f.write(str(ni) + ' ' + str(nj) + ' 1'+'\n')
    for j in xrange(nj):
        f.write(npy.array_str(X[:,j])[1:-1]+'\n')
    for j in xrange(nj):
        f.write(npy.array_str(Y[:,j])[1:-1]+'\n')
    for j in xrange(nj):
        f.write('0 '*ni+'\n')
               
    f.close()


#-----------------------------------------------------------
def Write3DArray(f,X):	
    ni, nj = X.shape
    
    for j in xrange(nj):
        f.write(npy.array_str(X[:,j])[1:-1]+'\n')

#-----------------------------------------------------------
# writes a 3D ascii plot3d grid file
def writePlot3D(fname, X, Y):
    f = open(fname, 'w')
    ni, nj = X.shape; nk = 2
    
    npy.set_printoptions( precision=16, threshold = ni )
    
    f.write('1'+'\n')
    f.write(str(ni) + ' ' + str(nj) + ' ' + str(nk) + '\n')
    Write3DArray(f,X)
    Write3DArray(f,X)
    Write3DArray(f,Y)
    Write3DArray(f,Y)
    Z = npy.zeros(X.shape)
    Write3DArray(f,Z)
    Z = npy.ones(X.shape)
    Write3DArray(f,Z)
               
    f.close()

#-----------------------------------------------------------
# writes a 3D ascii plot3d grid file
def writeOVERFLOW(fname, X, Y):
    f = open(fname, 'w')
   
    # Overflow requires 3 spanwise ndoes

    ni, nj = X.shape; nk = 3
    
    npy.set_printoptions( precision=16, threshold = ni )
    
    f.write('1'+'\n')
    f.write(str(ni) + ' ' + str(nk) + ' ' + str(nj) + '\n')
    Write3DArray(f,X)
    Write3DArray(f,X)
    Write3DArray(f,X)

    Z = npy.ones(X.shape)*0
    Write3DArray(f,Z)
    Z = npy.ones(X.shape)*0.5
    Write3DArray(f,Z)
    Z = npy.ones(X.shape)*1
    Write3DArray(f,Z)

    Write3DArray(f,Y)
    Write3DArray(f,Y)
    Write3DArray(f,Y)
               
    f.close()

#-----------------------------------------------------------
# reads a 2D ascii plot3d grid file assuming an X-Z plane (i.e. OVERFLOW)
def readPlot2D(fname):
    f = open(fname, 'r')
    
    data = f.read()
    f.close()
    data = data.strip()
    data = npy.array(data.split())
    ngrid = int(data[0])
    assert(ngrid == 1)
    ni = int(data[1]); nj = int(data[2]); nk = int(data[3])
    assert(nj == 1)
        
    X = data[4:4+ni*nk].astype(npy.float).reshape( (ni,nk) )
    Y = data[4+ni*nk:4+2*ni*nk].astype(npy.float).reshape( (ni,nk) )
    
    return X, Y