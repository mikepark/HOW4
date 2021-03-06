from __future__ import division

#===============================================================================
def writeGMSH(filename_base, ref, Q, E, V, nLE, NC, nWK, nWB, nr):

    f = open(filename_base + '_ref'+str(ref)+ '_Q'+str(Q)+'.msh', 'w')

    nelem = E.shape[0];
    nnode = V.shape[0];
    nbAirfoil = int((nLE-1)/Q)
    nbInflow = int((nWB-1)/Q)
    nbOutflow = int(2*(nr-1)/Q);

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

    f.write('$Elements\n')
    f.write(str(nelem+nbAirfoil+nbInflow+nbOutflow)+'\n')
    
    for e in xrange(nelem):
        f.write(str(e+1) + ' ' + str(GmshElemType) + ' 2 0 0 ')
        
        #Write nodes
        for k in xrange((Q+1)*(Q+1)):
            f.write(str(E[e,nodemapinv[k]])+' ')
        f.write('\n')

    
    if Q == 1: GmshLineType = 1 #2-node line
    if Q == 2: GmshLineType = 8 #3-node line
    if Q == 3: GmshLineType = 26 #4-node line
    if Q == 4: GmshLineType = 27 #5-node line
    
    #----------------#
    # Boundary faces #
    #----------------#

    # Airfoil
    BC = 1
    for i in xrange(int((nLE-1)/Q)):
        f.write(str(nelem+i+1) + ' ' + str(GmshLineType) + ' 2 ' + str(BC) + ' 0 ')
        #Write end points
        f.write(str(NC[nWK-1+Q*i,0]) + ' ' + str(NC[nWK-1+Q*(i+1),0]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[nWK-1+Q*i+q,0]+1) + ' ')
        f.write('\n')
      
    # Farfield inflow
    BC = 2
    for i in xrange(int((nWB-1)/Q)):
        f.write(str(nelem+nbAirfoil+i+1) + ' ' + str(GmshLineType) + ' 2 ' + str(BC) + ' 0 ')
        #Write end points
        f.write(str(NC[Q*i,nr-1]) + ' ' + str(NC[Q*(i+1),nr-1]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[Q*i+q,nr-1]) + ' ')
        f.write('\n')

    # Farfield Outflow
    BC = 3
    for i in xrange(int((nr-1)/Q)):
        f.write(str(nelem+nbAirfoil+nbInflow+i+1) + ' ' + str(GmshLineType) + ' 2 ' + str(BC) + ' 0 ')
        #Write end points
        f.write(str(NC[0,Q*i]) + ' ' + str(NC[0,Q*(i+1)]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[0,Q*i+q]) + ' ')
        f.write('\n')
        
    for i in xrange(int((nr-1)/Q)):
        f.write(str(nelem+nbAirfoil+nbInflow+int(nbOutflow/2)+i+1) + ' ' + str(GmshLineType) + ' 2 ' + str(BC) + ' 0 ')
        #Write end points
        f.write(str(NC[nWB-1,Q*i]) + ' ' + str(NC[nWB-1,Q*(i+1)]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[nWB-1,Q*i+q]) + ' ')
        f.write('\n')

    f.write('$EndElements\n')
    f.write('$PhysicalNames\n')
    f.write('4\n')
    f.write('2 0 \"MeshInterior\"\n')
    f.write('1 1 \"Wall\"\n')
    f.write('1 2 \"Farfield Inflow\"\n')
    f.write('1 3 \"Farfield Outflow\"\n')
    f.write('$EndPhysicalNames\n')
    
    
    f.close()
    