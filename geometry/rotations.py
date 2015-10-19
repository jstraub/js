import numpy as np
from scipy.linalg import det
import mayavi.mlab as mlab

# original file in python_modules/js/geometry/rotations.py
def plotCosy(fig,R,t,scale,name='',col=None):
  pts = np.zeros((3,6)) 
  for i in range(0,3):
    pts[:,i*2]  = np.zeros(3)
    pts[:,i*2+1] = R[:,i]
  pts *= scale
  pts+= t[:,np.newaxis]
  if col is None:
    mlab.plot3d(pts[0,0:2],pts[1,0:2],pts[2,0:2],figure=fig,color=(1.0,0.0,0.0),tube_radius=0.05*scale)
    mlab.plot3d(pts[0,2:4],pts[1,2:4],pts[2,2:4],figure=fig,color=(0.0,1.0,0.0),tube_radius=0.05*scale)
    mlab.plot3d(pts[0,4:6],pts[1,4:6],pts[2,4:6],figure=fig,color=(0.0,0.0,1.0),tube_radius=0.05*scale)  
  else:
    mlab.plot3d(pts[0,0:2],pts[1,0:2],pts[2,0:2],figure=fig,color=col)            
    mlab.plot3d(pts[0,2:4],pts[1,2:4],pts[2,2:4],figure=fig,color=col)            
    mlab.plot3d(pts[0,4:6],pts[1,4:6],pts[2,4:6],figure=fig,color=col) 
  if name!='':
    mlab.text3d(pts[0,1],pts[1,1],pts[2,1],name,
      scale=.1*scale,color=(0,0,0),line_width=1.0,figure=fig)
    mlab.text3d(pts[0,3],pts[1,3],pts[2,3],name,
      scale=.1*scale,color=(0,0,0),line_width=1.0,figure=fig)
    mlab.text3d(pts[0,5],pts[1,5],pts[2,5],name,
      scale=.1*scale,color=(0,0,0),line_width=1.0,figure=fig)

def norm(v):
  return np.sqrt((v**2).sum())
def normed(v):
  return v/norm(v)

def vee(W):
  A = 0.5*(W - W.T)
  w = np.array([A[2,1],A[0,2],A[1,0]])
  return w

def invVee(w): # also called skew sometimes
  W = np.zeros((3,3))
  W[2,1] = w[0]
  W[0,2] = w[1]
  W[1,0] = w[2]
  W -= W.T # fill other  half of matrix
  return W

class Rot3:
  def __init__(self,R):
    if not (R.shape[0]==3 and R.shape[1]==3):
      raise notImplementedError
    self.R = R
  def toRPY(self):
    yaw   = np.arctan2(self.R[2,1],self.R[2,2])
    pitch = np.arctan2(-self.R[2,0],
        np.sqrt(self.R[2,1]**2+self.R[2,2]**2))
    roll  = np.arctan2(self.R[1,0],self.R[0,0])
    return np.array([roll,pitch,yaw])
  def toQuat(self):
    q = Quaternion()
    q.fromRot3(self.R)
    return q
  def logMap(self):
    theta = np.arccos((np.trace(self.R) -1)/2.0)
    W = theta/(2.*np.sin(theta))*(self.R - self.R.T)
    #print theta/(2.*np.sin(theta))
    #print (self.R - self.R.T)
    return vee(W)
  def expMap(self,ww):
    if ww.shape[0] == 3 and ww.shape[1] == 3:
      W = ww
      w = vee(W)
    elif ww.size == 3:
      w = ww
      W = invVee(w)
    else:
      raise ValueError
    theta = np.sqrt((w**2).sum())
    if theta < 1e-12:
      self.R = np.eye(3)
    else:
      self.R = np.eye(3) + np.sin(theta)/theta * W + (1.0 - np.cos(theta))/theta**2 * W.dot(W)
    return self.R
  def dot(self,Rb):
    return Rot3(self.R.dot(Rb.R))
  def __repr__(self):
    return "{}".format(self.R)

class Quaternion:
  def __init__(self,w=1.0,x=0.0,y=0.0,z=0.0,vec=None):
    self.q =np.array([w,x,y,z])
    if not vec is None and vec.size == 3:
      self.q =np.array([w,vec[0],vec[1],vec[2]])
    if not vec is None and vec.size == 4:
      self.q = vec.copy()
  def setToRandom(self):
    self.q = normed(np.random.randn(4))
  def fromRot3(self,R_):
    # https://www.cs.cmu.edu/afs/cs/academic/class/16741-s07/www/lecture7.pdf
    if isinstance(R_,Rot3):
      R = R_.R
    else:
      R = R_
    qs = np.zeros(4)
    qs[0] = 1.0+R[0,0]+R[1,1]+R[2,2]
    qs[1] = 1.0+R[0,0]-R[1,1]-R[2,2]
    qs[2] = 1.0-R[0,0]+R[1,1]-R[2,2]
    qs[3] = 1.0-R[0,0]-R[1,1]+R[2,2]
    iMax = np.argmax(qs)
    self.q[iMax] = 0.5*np.sqrt(qs[iMax])
    if iMax ==0:
      self.q[1] = 0.25*(R[2,1]-R[1,2])/self.q[0]
      self.q[2] = 0.25*(R[0,2]-R[2,0])/self.q[0]
      self.q[3] = 0.25*(R[1,0]-R[0,1])/self.q[0]
    elif iMax==1:
      self.q[0] = 0.25*(R[2,1]-R[1,2])/self.q[1]
      self.q[2] = 0.25*(R[0,1]+R[1,0])/self.q[1]
      self.q[3] = 0.25*(R[2,0]+R[0,2])/self.q[1]
    elif iMax==2:
      self.q[0] = 0.25*(R[0,2]-R[2,0])/self.q[2]
      self.q[1] = 0.25*(R[0,1]+R[1,0])/self.q[2]
      self.q[3] = 0.25*(R[2,1]+R[1,2])/self.q[2]
    elif iMax==3:
      self.q[0] = 0.25*(R[1,0]-R[0,1])/self.q[3]
      self.q[1] = 0.25*(R[0,2]+R[2,0])/self.q[3]
      self.q[2] = 0.25*(R[2,1]+R[1,2])/self.q[3]
  def inverse(self):
    q = self.normalized().q
    return Quaternion(w=q[0],vec=-q[1:])
  def dot(self,p_):
    # horns paper
    r = self.q
    q = p_.q
    return Quaternion(
        w = r[0]*q[0]-r[1]*q[1]-r[2]*q[2]-r[3]*q[3],
        x = r[0]*q[1]+r[1]*q[0]+r[2]*q[3]-r[3]*q[2],
        y = r[0]*q[2]-r[1]*q[3]+r[2]*q[0]+r[3]*q[1],
        z = r[0]*q[3]+r[1]*q[2]-r[2]*q[1]+r[3]*q[0])
#        w = q[0]*p[0]-q[1]*p[1]-q[2]*p[2]-q[3]*p[3],
#        x = q[0]*p[1]+q[1]*p[0]+q[3]*p[2]-q[2]*p[3],
#        y = q[0]*p[2]-q[3]*p[1]+q[2]*p[0]+q[1]*p[3],
#        z = q[0]*p[3]+q[2]*p[1]-q[1]*p[2]+q[3]*p[0])
  def angleTo(self,q2):
    theta,_ = (self.dot(q2.inverse()).normalized()).toAxisAngle()
    return theta
  def toAxisAngle(self):
    self.normalize()
    theta = 2.0*np.arccos(self.q[0])
    sinThetaHalf = np.sqrt(1.-self.q[0]**2)
    if theta < 1e-5:
      axis = np.array([0,0,1])
    else:
      axis = self.q[1::]/sinThetaHalf
    return theta,axis
  def toRPY(self):
    w,x,y,z = self.q[0],self.q[1],self.q[2],self.q[3]
    roll = np.arctan2(2*y*w-2*x*z,1.-2*y*y - 2*z*z)
    pitch = np.arctan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)
    yaw = np.arcsin(2*x*y + 2*z*w)
    return np.array([roll,pitch,yaw])
  def fromAxisAngle(self,theta,axis):
    self.q[0] = np.cos(theta*0.5)
    self.q[1::] = axis*np.sin(theta*0.5)
  def normalize(self):
    self.q /= np.sqrt((self.q**2).sum())
  def normalized(self):
    norm = np.sqrt((self.q**2).sum())
    return Quaternion(self.q[0]/norm,self.q[1]/norm,self.q[2]/norm,self.q[3]/norm)
  def toAngularRate(self,dt):
    ax,theta = self.toAxisAngle()
    return ax*theta/dt
  def slerp(self,q2,t):
    # http://www.arcsynthesis.org/gltut/Positioning/Tut08%20Interpolation.html
    # http://number-none.com/product/Understanding%20Slerp,%20Then%20Not%20Using%20It/
    a = Quaternion()
    dot = self.q.dot(q2.q)
    if dot > 0.9995:
      #If the inputs are too close for comfort, 
      # linearly interpolate and normalize the result.
      a.q = self.q + t*(q2.q - self.q);
      a.normalize()
      return a;
    dot = min(max(dot,-1.),1.)
    theta_0 = np.arccos(dot);  # theta_0 = angle between input vectors
    theta = theta_0*t;  # theta = angle between v0 and result 
    a.q = q2.q - self.q*dot
    a.normalize()
    a.q = self.q*np.cos(theta) + a.q*np.sin(theta)
    return a
  def toRot(self): # LHCS??
    # this is from wikipedia
    a,b,c,d = self.q[0],self.q[1],self.q[2],self.q[3]
    R = np.array([[a**2+b**2-c**2-d**2, 2*b*c-2*a*d, 2*b*d+2*a*c],
                  [2*b*c+2*a*d, a**2-b**2+c**2-d**2, 2*c*d-2*a*b],
                  [2*b*d-2*a*c, 2*c*d+2*a*b, a**2-b**2-c**2+d**2]])
    return Rot3(R)
  def toRotOther(self): # RHCS  ??
    # http://osdir.com/ml/games.devel.algorithms/2002-11/msg00318.html
    a,b,c,d = self.q[0],self.q[1],self.q[2],self.q[3]
#    R = np.array([[a**2+b**2-c**2-d**2, 2*b*c+2*a*d, 2*b*d+2*a*c],
#                  [2*b*c-2*a*d, a**2-b**2+c**2-d**2, 2*c*d+2*a*b],
#                  [2*b*d+2*a*c, 2*c*d-2*a*b, a**2-b**2-c**2+d**2]])
    R = np.array([[1. -2.*c**2-2.*d**2, 2*b*c+2*a*d, 2*b*d-2*a*c],
                  [2*b*c-2*a*d, 1. -2.*b**2-2.*d**2, 2*c*d+2*a*b],
                  [2*b*d+2*a*c, 2*c*d-2*a*b, 1.-2.*b**2-2.*c**2]])
    return Rot3(R)
  def plot(self, figm, t=None, scale=1., name=''):
    if t is None:
      t = np.zeros(3)
    plotCosy(figm,self.toRot().R,t,scale,name)
  def rotate(self,v):
#    vn = normed(v)
#    vq = Quaternion(w=0.,vec=v)
#    vq = self.dot(vq.dot(self.inverse()))
#    return vq.q[1:] #*norm(v)
    # from Eigen
    # http://eigen.tuxfamily.org/dox/Quaternion_8h_source.html
    uv = np.cross(self.q[1::],v)
    uv += uv
    return v + self.q[0] * uv + np.cross(self.q[1::], uv)

  def __repr__(self):
#    return "{}".format(self.q)
    return "w|x|y|z: {}\t{}\t{}\t{}".format(self.q[0],self.q[1],self.q[2],self.q[3])

def ToRightQuaternionProductMatrix(x):
  return np.array([
    [0., -x[0], -x[1], -x[2]],
    [x[0], 0., x[2], -x[1]],
    [x[1], -x[2], 0., x[0]],
    [x[2], x[1], -x[0], 0.]])

def ToLeftQuaternionProductMatrix(x):
  return np.array([
    [0., -x[0], -x[1], -x[2]],
    [x[0], 0., -x[2], x[1]],
    [x[1], x[2], 0., -x[0]],
    [x[2], -x[1], x[0], 0.]])

if __name__ == "__main__":
  q = Quaternion(1.,0.,0.,0.)
  print q.inverse()
  print q.toAxisAngle()
  q2 = Quaternion(1.,.01,0.,0.)
  q2.normalize()
  print q2
  print q2.inverse()
  print q2.inverse().dot(q2)
  print q2.dot(q2.inverse())
  print q.dot(q2)
  print q.angleTo(q2)
  raw_input()

  q2 = Quaternion(1.,1.,0.,0.)
  q2.fromAxisAngle(np.pi/2.0,np.array([0.,1.,1.]))

  q3 = q.slerp(q2,0.5)
  print q
  print q3
  print q2  
  for t in np.linspace(0.,1.,100):
    qi=q.slerp(q2,t)
    print "--------------------------------------------------------"
    print qi
    print np.sqrt((qi.q**2).sum())
    print 'det: {}'.format( det(qi.toRot().R))
    print "--------------------------------------------------------"
    #print qi.toRot().R


  dq = Quaternion()                                                                                                               
  q0 = Quaternion()                                                                                                               
  qe = Quaternion()                                                                                                               
  qe.fromAxisAngle(180,np.array([0.,0.,1.]))                                                                                      
  for t in np.linspace(0.0,1.0,10):                                                                                              
    # show pc colored according to their MF assignment                                                                            
    dq = q0.slerp(qe,t)
    print '-----------'
    print dq
    print np.sqrt((qi.q**2).sum())
    print 'det: {}'.format( det(dq.toRot().R))
    print dq.toRot().R

    print dq.toRot().logMap()


