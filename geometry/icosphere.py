import numpy as np
import mayavi.mlab as mlab
from itertools import combinations

class IcoSphere(object):
    def __init__(self, depth):
        self.depth = depth
        self.vertices = np.zeros((12, 3))
        self.tri = np.zeros((20, 3), dtype = np.int)
        self.InitGrid()
        for lvl in range(depth):
          self.SubdivideOnce()
        self.figm = None

    def InitGrid(self):
        ''' 
        Initialize a Icosahedron
        '''
        a = (1. + np.sqrt(5.0)) * 0.5

        self.vertices[0, :] = [-1, a, 0]
        self.vertices[1, :] = [1, a, 0]
        self.vertices[2, :] = [-1, -a, 0]
        self.vertices[3, :] = [1, -a, 0]

        self.vertices[4, :] = [0, -1, a]
        self.vertices[5, :] = [0, 1, a]
        self.vertices[6, :] = [0, -1, -a]
        self.vertices[7, :] = [0, 1, -a]

        self.vertices[8, :] = [a, 0, -1]
        self.vertices[9, :] = [a, 0, 1]
        self.vertices[10, :] = [-a, 0, -1]
        self.vertices[11, :] = [-a, 0, 1]

        self.tri[0, :] = [0, 11, 5]
        self.tri[1, :] = [0, 5, 1]
        self.tri[2, :] = [0, 1, 7]
        self.tri[3, :] = [0, 7, 10]
        self.tri[4, :] = [0, 10, 11]

        self.tri[5, :] = [1, 5, 9]
        self.tri[6, :] = [5, 11, 4]
        self.tri[7, :] = [11, 10, 2]
        self.tri[8, :] = [10, 7, 6]
        self.tri[9, :] = [7, 1, 8]

        self.tri[10, :] = [3, 9, 4]
        self.tri[11, :] = [3, 4, 2]
        self.tri[12, :] = [3, 2, 6]
        self.tri[13, :] = [3, 6, 8]
        self.tri[14, :] = [3, 8, 9]

        self.tri[15, :] = [4, 9, 5]
        self.tri[16, :] = [2, 4, 11]
        self.tri[17, :] = [6, 2, 10]
        self.tri[18, :] = [8, 6, 7]
        self.tri[19, :] = [9, 8, 1]
        self.tri_levels = [0, 20]
        self.vertices /= np.sqrt((self.vertices**2).sum(axis=1))[:, np.newaxis]

    def SubdivideOnce(self):
        '''
        Subdivide each of the existing triangles of the current
        IcoSphere into 4 triangles and pop out the inner corners of
        the new triangles to the sphere.
        '''
        n_vertices = self.vertices.shape[0]
        n_tri = self.tri.shape[0]
#        print n_tri, n_vertices
        self.vertices.resize((n_vertices + n_tri * 3, 3), refcheck=False)
        self.tri.resize((n_tri * 5, 3))
        self.tri_levels.append(n_tri * 5)
        for i in range(n_tri):
            i0 = self.tri[i, 0]
            i1 = self.tri[i, 1]
            i2 = self.tri[i, 2]
            i01 = n_vertices + i*3 
            i12 = n_vertices + i*3 + 1
            i20 = n_vertices + i*3 + 2
            self.vertices[i01, :] = 0.5 * (self.vertices[i0, :] + self.vertices[i1, :]) 
            self.vertices[i12, :] = 0.5 * (self.vertices[i1, :] + self.vertices[i2, :]) 
            self.vertices[i20, :] = 0.5 * (self.vertices[i2, :] + self.vertices[i0, :]) 
            self.tri[n_tri + i*4, :] = [i0, i01, i20]
            self.tri[n_tri + i*4 + 1, :] = [i01, i1, i12]
            self.tri[n_tri + i*4 + 2, :] = [i12, i2, i20]
            self.tri[n_tri + i*4 + 3, :] = [i01, i12, i20]
        self.vertices[n_vertices::, :] /= np.sqrt((self.vertices[n_vertices::,:]**2).sum(axis=1))[:, np.newaxis]
        return 

    def GetTrianglID(self, direction):
      direction /= np.sqrt((direction**2).sum())
      j = -1 
      id = []
      for i in range(20):
        i0 = self.tri[i, 0]
        i1 = self.tri[i, 1]
        i2 = self.tri[i, 2]
        if self.Intersects(self.vertices[i0, :], self.vertices[i1, :],
            self.vertices[i2, :], direction):
          j = i 
#          print "level0 triangle", j
          #mlab.show(stop=True)
          break
      if j >= 0:
        id.append(j)
        for lvl, n_lvl in enumerate(self.tri_levels[1:-1]):
          found_triangle = False
          for i in range(4):
            i_tri = n_lvl + j*4 + i
            i0 = self.tri[i_tri, 0]
            i1 = self.tri[i_tri, 1]
            i2 = self.tri[i_tri, 2]
#            print '---', n_lvl, j*4, i
            if self.Intersects(self.vertices[i0, :], self.vertices[i1, :],
                self.vertices[i2, :], direction):
              id.append(i)
              j = n_lvl + (j*4 + i) 
              found_triangle = True
              #mlab.show(stop=True)
              break
          if not found_triangle:
            print "not good ... Did not find a intersection at level {}".format(lvl)
            break
#          else:
#            print "intersecting triangle {} at lvl {}".format(i, lvl)
      else:
        print "No intersection with the base triangles found.", direction
        for i in range(20):
          i0 = self.tri[i, 0]
          i1 = self.tri[i, 1]
          i2 = self.tri[i, 2]
          print "i:", i
          if self.Intersects(self.vertices[i0, :], self.vertices[i1, :],
              self.vertices[i2, :], direction,debug=True):
            break

#      print "returning triangle ID: ", j, self.tri_levels[-1], self.tri_levels[-2], j - self.tri_levels[-2] , id
      return id, j - self.tri_levels[-2]

    def Intersects(self, p0, p1, p2, direction, debug=False):
      '''
      http://geomalgorithms.com/a06-_intersect-2.html
      '''
      if debug:
        # display trinangles intersections for debugging
        if self.figm is None:
          self.figm = mlab.figure()
        mlab.triangular_mesh(np.array([p0[0], p1[0], p2[0]]),
            np.array([p0[1], p1[1], p2[1]]), np.array([p0[2], p1[2],
              p2[2]]), np.array([0, 1, 2])[np.newaxis,:])
        mlab.plot3d([0,direction[0]], [0,direction[1]], [0,direction[2]])
        mlab.points3d([0], [0], [0], scale_factor=0.1)
        #yymlab.show(stop=True)
        #mlab.close(figm)

      n = np.cross(p1 - p0, p2 - p0)
      denom = n.dot(direction)
      if np.abs(denom) < 1e-6:
        # the direction is parallel to the plane of the triangle
        if debug:
          print "Direction and triangle are parallel. {}".format(denom)
        return False
      r = n.dot(p0) / denom
      if r < 0.:
        # We are intersecting on the other side
        if debug:
          print "Intersection is in the opposite direction. {}".format(r)
        return False
      intersection = r * direction
      v = p2 - p0
      u = p1 - p0
      w = intersection - p0
      uv = u.dot(v)
      uu = u.dot(u)
      vv = v.dot(v)
      wv = w.dot(v)
      wu = w.dot(u)
      denom = uv**2 - uu * vv
      s = ((uv * wv) - (vv * wu)) / denom
      t = ((uv * wu) - (uu * wv)) / denom
      if s >= 0 and t >= 0 and s+t <= 1.:
        return True
      else:
        if debug:
          print "Intersection is outside the triangle {}, {}".format(s,t)
        return False

    def GetNumTrianglesAtLevel(self, level):
      if level < len(self.tri_levels) - 1:
        return self.tri_levels[level+1]-self.tri_levels[level]
      else:
        print "Do not have that many levels ({}).".format(level)
        return -1

    def GetTriangleCentersAtLevel(self, level):
      tri = self.tri[self.tri_levels[level]:self.tri_levels[level+1], :]
      cs = np.zeros((tri.shape[0],3))
      for i_tri in range(tri.shape[0]):
        i0 = tri[i_tri, 0]
        i1 = tri[i_tri, 1]
        i2 = tri[i_tri, 2]
        c = (self.vertices[i0,:]+self.vertices[i1,:]+self.vertices[i2,:])/3.
        c /= np.sqrt((c**2).sum())
        cs[i_tri,:] = c
      return cs
    def GetTriangleAreasAtLevel(self, level):
      tri = self.tri[self.tri_levels[level]:self.tri_levels[level+1], :]
      areas = np.zeros(tri.shape[0])
      for i_tri in range(tri.shape[0]):
        i0 = tri[i_tri, 0]
        i1 = tri[i_tri, 1]
        i2 = tri[i_tri, 2]
        a = -self.vertices[i0,:]+self.vertices[i1,:]
        b = -self.vertices[i0,:]+self.vertices[i2,:]
        areas[i_tri] = np.sqrt((np.cross(a,b)**2).sum())*0.5
      return areas

    def GetNumLevels(self):
      return len(self.tri_levels) - 1

    def Plot(self, level, figm, color=None):
        if level + 1 >= len(self.tri_levels):
            print "Cannot plot this level in the IcoSphere"
            return 
        mlab.triangular_mesh(self.vertices[:, 0], self.vertices[:, 1],
            self.vertices[:, 2],
            self.tri[self.tri_levels[level]:self.tri_levels[level+1],
              :], color=(0.6,0.6,0.6))
        if color is None:
          color = (level/float(self.depth), 1-level/float(self.depth), 1.)
        tri = self.tri[self.tri_levels[level]:self.tri_levels[level+1], :]
        for i in range(tri.shape[0]):
          for comb in combinations(range(3), 2):
            a = self.vertices[tri[i, comb[0]],:]
            b = self.vertices[tri[i, comb[1]],:]
            mlab.plot3d([a[0],b[0]], [a[1],b[1]], [a[2],b[2]], tube_radius=0.02,
                color=color)
        return

class IcoSphereTessellation(IcoSphere):
  def PlotTessellation(self, level, figm, color=None):
    tri = self.tri[self.tri_levels[level]:self.tri_levels[level+1], :]
    t = np.linspace(0,1.,10)[:, np.newaxis]
    if color is None:
      color = (level/float(self.depth), 1-level/float(self.depth), 1.)
    for i in range(tri.shape[0]):
      for comb in combinations(range(3), 2):
        a = self.vertices[tri[i, comb[0]],:]
        b = self.vertices[tri[i, comb[1]],:]
        c = a + t*(b-a)
        c = (c.T / np.sqrt((c**2).sum(axis=1))).T
        mlab.plot3d(c[:,0], c[:,1], c[:,2], tube_radius=0.02,
            color=color)

class SphereHistogram:
  def __init__(self, sphereGrid=None, level = None):
    if sphereGrid is None:
      self.sphereGrid = IcoSphere(level)
    else:
      self.sphereGrid = sphereGrid
    if level is None:
      self.level = sphereGrid.GetNumLevels()
    else:
      self.level = level
    self.hist = np.zeros(self.sphereGrid.GetNumTrianglesAtLevel(level))
  def GetTriangleCenters(self):
    return self.sphereGrid.GetTriangleCentersAtLevel(self.level)
  def GetNumTriangles(self):
    return self.sphereGrid.GetNumTrianglesAtLevel(self.level)

  def Compute(self, pts):
    for pt in pts:
      self.hist[self.sphereGrid.GetTrianglID(pt)[1]] += 1.
    self.hist /= self.hist.sum()
    self.pdf = np.zeros_like(self.hist)
    self.areas = self.sphereGrid.GetTriangleAreasAtLevel(self.level)
    for i in range(self.hist.shape[0]):
      self.pdf[i] = self.hist[i]/self.areas[i]

  def PlotGrid(self, level, figm):
    self.sphereGrid.Plot(self.level, figm)

  def PlotHist(self, scale, figm=None):
    if figm is None:
      figm = mlab.figure(bgcolor=(1,1,1))
    cs = self.sphereGrid.GetTriangleCentersAtLevel(self.level)
    for i in range(cs.shape[0]):
      l = cs[i,:]*(self.hist[i]*scale+1.01)
      mlab.plot3d([cs[i,0],l[0]],[cs[i,1],l[1]],[cs[i,2],l[2]],
          color=(0.2,0.2,0.2),tube_radius=None)
  def Entropy(self, pts):
    H = 0.
#    self.areas = self.sphereGrid.GetTriangleAreasAtLevel(self.level)
#    W = 0.
    for pt in pts:
      i = self.sphereGrid.GetTrianglID(pt)[1]
      H -= np.log(self.pdf[i])
#      W += self.areas[i]
    H /=pts.shape[0]
#    H /= W
    return H
  def CrossEntropy(self, pts, q):
    H = 0.
#    self.areas = self.sphereGrid.GetTriangleAreasAtLevel(self.level)
#    W = 0.
    for pt in pts:
      i = self.sphereGrid.GetTrianglID(pt)[1]
      H -= np.log(q[i])
#      W += self.areas[i]
#    H /= W
    H /=pts.shape[0]
    return H

if __name__=="__main__":
  from scipy.linalg import sqrtm
  theta = 0.*np.pi/180.
  R = np.array([[1., 0., 0.], 
                [0., np.cos(theta), -np.sin(theta)],
                [0., np.sin(theta), np.cos(theta)]])
  L = np.eye(3)
  L[0,0] = 100.
  L[1,1] = 1.
  L[2,2] = 1.
  S = R.T.dot(L).dot(R)
  Nr = 20000
  x = sqrtm(S).dot(np.random.randn(3,Nr))
  print np.cov(x)

  sHist = SphereHistogram(level=2)
  sHist.Compute(x.T)

  sHist.PlotHist(10.)
  mlab.show(stop=True)

