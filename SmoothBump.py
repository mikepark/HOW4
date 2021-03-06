import numpy as npy
from plot3d import writeOVERFLOW, writePlot3D

#===============================================================================
def writeGMSH(filename_base, ref, Q, E, V, NC, ni, nj):

    f = open(filename_base + '_ref'+str(ref)+ '_Q'+str(Q)+'.msh', 'w')

    nelem = E.shape[0];
    nnode = V.shape[0];
    
    nInflow = int((nj-1)/Q)
    nOutflow = nInflow
    nWall = int((ni-1)/Q)

    floatformat = "{:3.16e}"
    
    #Write out the Gmsh file format
    f.write('$MeshFormat\n')
    f.write('2.2 0 8\n')
    f.write('$EndMeshFormat\n')
    f.write('$Nodes\n')
    f.write(str(nnode)+'\n')
    for i in xrange(nnode):
        f.write("{:2d}".format(i+1) + ' ' + floatformat.format(V[i,0]) + ' ' + floatformat.format(V[i,1]) + ' 0.0\n')
    f.write('$EndNodes\n')

    f.write('$Elements\n')
    f.write(str(4 + nelem+nInflow+nOutflow+2*nWall)+'\n')

    #----------------#
    # Corners        #
    #----------------#

    f.write('1 15 2 0 6 ' + str(NC[ 0, 0]) + '\n')
    f.write('2 15 2 0 6 ' + str(NC[-1, 0]) + '\n')
    f.write('3 15 2 0 6 ' + str(NC[-1,-1]) + '\n')
    f.write('4 15 2 0 6 ' + str(NC[ 0,-1]) + '\n')

    if Q == 1: GmshLineType = 1 #2-node line
    if Q == 2: GmshLineType = 8 #3-node line
    if Q == 3: GmshLineType = 26 #4-node line
    if Q == 4: GmshLineType = 27 #5-node line
    
    #----------------#
    # Boundary faces #
    #----------------#

    # Inflow
    BC = 1
    for j in xrange(nInflow):
        f.write(str(j+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[0,Q*j]) + ' ' + str(NC[0,Q*(j+1)]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[0,Q*j+q]) + ' ')
        f.write('\n')
      
    # Outflow
    BC = 2
    for j in xrange(nOutflow):
        f.write(str(nInflow+j+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[ni-1,Q*j]) + ' ' + str(NC[ni-1,Q*(j+1)]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[ni-1,Q*j+q]) + ' ')
        f.write('\n')

    # Walls
    BC = 3
    for i in xrange(nWall):
        f.write(str(nInflow+nOutflow+i+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[Q*i,0]) + ' ' + str(NC[Q*(i+1),0]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[Q*i+q,0]) + ' ')
        f.write('\n')
        
    BC = 4
    for i in xrange(nWall):
        f.write(str(nInflow+nOutflow+nWall+i+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[Q*i,nj-1]) + ' ' + str(NC[Q*(i+1),nj-1]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[Q*i+q,nj-1]) + ' ')
        f.write('\n')

        
        
    if Q == 1: #4-node quadrangle
        GmshElemType = 3 
        nodemap = (0, 1, 
                   3, 2)
    if Q == 2:  #9-node second order quadrangle
        GmshElemType = 10
        nodemap = (0, 4, 1, 
                   7, 8, 5, 
                   3, 6, 2)
    if Q == 3:  #16-node third order quadrangle
        GmshElemType = 36
        nodemap = ( 0,  4,  5, 1, 
                   11, 12, 13, 6, 
                   10, 14, 15, 7, 
                    3,  9,  8, 2)
    if Q == 4: #25-node fourth order quadrangle
        GmshElemType = 37 
        nodemap = ( 0,  4,  5,  6, 1, 
                   15, 16, 17, 18, 7,
                   14, 19, 20, 21, 8,
                   13, 22, 23, 24, 9,
                    3, 12, 11, 10, 2)

    #Invert the map
    nodemapinv = []
    for k in xrange((Q+1)*(Q+1)):
        j = 0
        while nodemap[j] != k: j += 1
        nodemapinv.append(j)

    
    for e in xrange(nelem):
        f.write(str(nInflow+nOutflow+2*nWall+e+5) + ' ' + str(GmshElemType) + ' 2 0 5 ')
        
        #Write nodes
        for k in xrange((Q+1)*(Q+1)):
            f.write(str(E[e,nodemapinv[k]])+' ')
        f.write('\n')

    f.write('$EndElements\n')
    f.write('$PhysicalNames\n')
    f.write('5\n')
    f.write('2 0 \"MeshInterior\"\n')
    f.write('1 1 \"Inflow\"\n')
    f.write('1 2 \"Outflow\"\n')
    f.write('1 3 \"Lower Wall\"\n')
    f.write('1 4 \"Upper Wall\"\n')
    f.write('$EndPhysicalNames\n')
    
    
    f.close()

#-----------------------------------
def block_elem(N, Q):
    nx, ny = N.shape;
    #if (Q != 1) and ((mod(nx,Q) != 1) or (mod(ny,Q) != 1)): print('ERROR 2'); return;
    mx = int((nx-1)/Q);
    my = int((ny-1)/Q);
    E = npy.zeros( (mx*my,(Q+1)*(Q+1)),int);
    dy = ny;
    i = 0;
    for imy in xrange(my):
      for imx in xrange(mx):
        ix = Q*(imx+1)-(Q-1)-1;
        iy = Q*(imy+1)-(Q-1)-1;
        k = 0;
        for ky in xrange(Q+1):
          for kx in xrange(Q+1):
            E[i,k] = N[ix+kx,iy+ky]
            k = k+1;

        i = i + 1;
      
    return E

#-----------------------------------------------------------
# writes BC information for FUN3D
def writeNMF(fname, ni, nj):

    nk = 2

    f = open(fname, 'w')
    f.write('# ===================================================================================\n')
    f.write('# Block# IDIM JDIM KDIM\n')
    f.write('# -----------------------------------------------------------------------------------\n')
    f.write('1\n')
    f.write(str(ni) + ' ' + str(nj) + ' ' + str(nk) + '\n')
    f.write('# ===================================================================================\n')
    f.write('# Type            B1 F1   S1 E1   S2 E2   B2 F2   S1 E1   S2 E2   Swap\n')
    f.write('# -----------------------------------------------------------------------------------\n')
    f.write("'tangency'        1 1   1 " + str(ni) + "   1 " +str(nj) + "\n")
    f.write("'tangency'        1 2   1 " + str(ni) + "   1 " +str(nj) + "\n")
    f.write("'Subsonic inflow' 1 3   1 " + str(nj) + "   1 " +str(nk) + "\n")
    f.write("'Back pressure'   1 4   1 " + str(nj) + "   1 " +str(nk) + "\n")
    f.write("'tangency'        1 5   1 " + str(nk) + "   1 " +str(ni) + "\n")
    f.write("'tangency'        1 6   1 " + str(nk) + "   1 " +str(ni) + "\n")

#===============================================================================
def SmoothBump(ni, nj, Q, ref):
    
    ni = ni*Q*2**ref+1
    nj = nj*Q*2**ref+1
    
    #Create all the vertexes
    V = npy.zeros((ni,nj,2),float)

    #Upper boundary
    y1 = 0.8
    x0 = npy.linspace(-1.5, 1.5, ni)

    for i in xrange(ni):
        x = x0[i];
        y0 = 0.0625*npy.exp(-25.*x**2)
        y = npy.linspace(y0, y1, nj)
        V[i,:,0] = x
        V[i,:,1] = y

    writeOVERFLOW('grid.in.'+str(ref), V[:,:,0], V[:,:,1])
    writeNMF('SmoothBump_ref'+str(ref)+'.nmf', ni, nj)
    writePlot3D('SmoothBump_ref'+str(ref)+'.p3d', V[:,:,0], V[:,:,1])
    
    V = V.reshape( (ni*nj,2) )
    
    #---------------------------------------------#
    # node number matrices for writing out blocks #
    #---------------------------------------------#

    NC = npy.arange(ni*nj).reshape( (ni, nj) )+1
    
    #---------------#
    # form elements #
    #---------------#
    E = block_elem(NC, Q);

    writeGMSH('SmoothBump', ref, Q, E, V, NC, ni, nj)


Q = 2
ref = 0
ni = 6
nj = 2
SmoothBump(ni, nj, Q, ref)
#file = open("bump.dat", "w")
#file.write(str(ni)+'\n')
#for i in xrange(ni):
#    file.write(str(x[i]) + "  " + str(Bump[i]) + "  0.0\n")
#file.close()
