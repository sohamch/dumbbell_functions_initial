
# coding: utf-8

# import modules

# In[3]:


import numpy as np
import numpy.linalg as la
import onsager.crystal as crystal
from collections import namedtuple


# Single dumbbell state representer class.
# 1. Format - 'i o R c' -> basis index, orientation, lattice vector, active atom indicator
# 2. Should be able to check if two dumbbell states are identical
# 3. Should be able to add a jump to a dumbbell state.
# 4. Should be able to apply a given group operation (crystal specified) to a dumbbell.

# In[5]:


class dumbbell(namedtuple('dumbbell','i o R c')):
    
    def __eq__(self,other):
        true_class = isinstance(other,self.__class__)
        if (self.i==other.i and np.allclose(self.R,other.R,atol=1e-8) and np.allclose(self.o,other.o,atol=1e-8) 
            and self.c==other.c):
            return (True and true_class)
    def __ne__(self,other):
        return not self.__eq__(other) 
    
    def __add__(self,other):
        if not isinstance(other,Jumps):
            raise TypeError("Can only add a jump to a state.")
            
        if not (self.i==other.i and np.allclose(self.o,other.o1,atol=1e-8)
                and np.allclose(self.R,other.R_1,atol=1e-8) and self.c==other.c1): 
            raise ArithmeticError("Initial state of Jump object must match current dumbbell state")
        
        return self.__class__(other.j,other.o2,other.R2,other.c2)
        
    def gop(self,crys,chem,g):
        r1, i1 = crys.g_pos(g,self.R,(chem,self.i))
        o1 = np.dot(g.cartrot,self.o)
        return self.__class__(i1,o1,r1,self.c)


# A Pair object (that represents a dumbbell-solute state) should have the following attributes:
# 1. It should have the locations of the solute and dumbbell.
# 2. A pair object contains information regarding which atom in the dumbbell is going to jump.
# 3. We should be able to apply Group operations to it to generate new pairs.
# 4. We should be able to add a Jump object to a Pair object to create another pair object.
# 5. We should be able to test for equality.

# In[10]:


class pairs(namedtuple('Pairs',"i_s i_d o R_s R_d dx c")):
     
    def __eq__(self, other):
        true_class = isinstance(other,self.__class__)
        true_vectors = np.allclose(self.R_s,other.R_s) and np.allclose(self.R_d,other.R_d) and np.allclose(self.dx,other.dx)
        true_indices = (self.i_s == other.i_s and self.i_d==other.i_d and self.c == other.c)
        return (true_class and true_vectors and true_indices)
    
    def __add__(self,other):
        if not isinstance(other,Jumps):
            raise TypeError("Can only add a jump to a state.")
        if not (self.i_s==other.i and self.c==other.c1 and np.allclose(self.R_d,other.R1) and np.allclose(self.o,other.or1)):
            raise ArithmeticError("Initial state of Jumps object must match current dumbbell state")

        return self.__class__(self.i_s,other.j,other.or2,self.R_s,other.R2,self.dx+other.dx,self.c)
    
    def gop(self,crys,chem,g):#apply group operation
        R_s_new, (c,i_s_new) = crys.g_pos(g,self.R_s,(chem,self.i_s))
        R_d_new, (c,i_d_new) = crys.g_pos(g,self.R_d,(chem,self.i_d))
        or_new = g.cartrot.dot(self.o)
        dx_new = crys.g_direc(g, self.dx)
        return self.__class__(i_s_new,i_d_new,or_new,R_s_new,R_d_new,dx_new,self.c)
        


# Jump objects are rather simple, contain just initial and final orientations, location and pointers towards jumping/active atom (+1 for head of orientation vector, -1 for tail of orientation vector).

# In[12]:


class jumps(namedtuple('jump','i j or1 or2 R1 R2 dx c1 c2')):
    
    def __add__(self,other):
        if not isinstance(other,self.__class__):
            raise TypeError("Can only add two jumps.")
            
        if not (self.j==other.i and np.allclose(self.or2,other.or1),np.allclose(self.R2,other.R1),
                self.c2==other.c1):
            raise ArithmeticError("Starting point of second jump does not match end point of first")
            
        return self.__class__(self.i,other.j,self.or1,other.or2,self.R1,other.R2,
                              self.dx+other.dx,self.c1,other.c2)
    
    def gop(self,crys,chem,g): #Find symmetry equivalent jumps - required when making composite jumps.
        R1new,inew = crys.g_pos(g, R1, (chem, self.i))
        R2new,jnew = crys.g_pos(g, R2, (chem, self.j))
        or1_new = g.cartrot,dot(or1)
        or2_new = g.cartrot,dot(or2)
        dx_new = crys.g_direc(g, self.dx)
        return self.__class__(inew,jnew,or1_new,or2_new,R1new,R2new,dx_new,self.c1,self.c2)
        

