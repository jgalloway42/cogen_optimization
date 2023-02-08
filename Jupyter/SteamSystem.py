# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 10:27:33 2020
Model of Steam System

@author: Josh.Galloway
"""

import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cvxopt import matrix, solvers


class SteamSystem:
    
    def __init__(self, constraints = 'constraints.csv',
                 attributes = 'attributes.csv',
                 mass_balance_lhs = 'mass_balance_lhs.csv',
                 mass_balance_rhs = 'mass_balance_rhs.csv',
                 steam_graphic = 'steamHeaderTopology.png'):
        
        '''Constructor'''
        # read in csv of constraints and build table
        self.cons_df = pd.read_csv(constraints,index_col='constraint')
        self.cons_df = self.cons_df.astype(float)
        
        # read in csv of attributes and build table
        self.attr_df = pd.read_csv(attributes,index_col='attribute')
        self.attr_df = self.attr_df.astype(float)
        
        # read in csv of mass balance lhs and build table
        self.mb_lhs_df = pd.read_csv(mass_balance_lhs,index_col='equation')
        self.mb_lhs_df = self.mb_lhs_df.astype(float)
        
        # read in csv of constraints and build table
        self.mb_rhs_df = pd.read_csv(mass_balance_rhs,index_col='equation')
        self.mb_rhs_df = self.mb_rhs_df.astype(float)
        
        # read in graphic
        self.img = mpimg.imread(steam_graphic)
        
        # Setup CVX
        solvers.options['show_progress'] = False
        solvers.options['abstol'] = 1e-9
        solvers.options['reltol'] = 1e-9
        return
        

    def buildEqConstraints(self,Op_array):
        '''
        Desc: Build and return Equality Constraint Matrices 
        Inputs: Op_array = numpy array [PB Steam, HP Load,
                                         IP Load, LP Load]
        Outputs: A matrix for lhs, and b matrix for rhs
        '''
        Aeq = self.mb_lhs_df.values                
        beq = np.matmul(self.mb_rhs_df.values,Op_array)
        return Aeq,beq
    
    def buildIneqConstraints(self):
        '''
        Desc: Build and return Inequality Constraint Matrices 
        Inputs: none
        Outputs: A matrix for lhs, b matrix for rhs and bnd bounds list
        '''
        df = self.cons_df
        shape = (df.count().sum(),len(df.columns))
        A_ineq = np.zeros(shape)
        b_ineq = np.zeros(shape[0]) 
        bnd = []
    
        j = 0  # counter for constraints
        for i in range(0,shape[1]):
            # loop for variables
            b_min = df[df.columns[i]].loc['Min']
            b_max = df[df.columns[i]].loc['Max']
    
            # Check Minimum
            if not np.isnan(b_min):
                b_ineq[j] = -b_min
                A_ineq[j,i] = -1
                j = j + 1
    
            # Check Maximum
            if not np.isnan(b_max):
                b_ineq[j] = b_max
                A_ineq[j,i] = 1
                j = j + 1
    
            # add generic non-negative bounds
            bnd.append((0, float("inf")))
            
        return A_ineq,b_ineq,bnd
    
    def build_obj(self):
        '''
        Desc: Build Objective Function 
        Inputs: none
        Outputs: c coefficients for objective function
        '''
        K= 0.000293071 #mBtu/hr -> MW
        H = self.attr_df.loc['BTU/LB'].values
        c = np.array([0, 0, (H[0] -H[1]), 0, (H[1] - H[2]),
                      (H[0] - H[2]), (H[2] - H[1]), 0, (H[2]-H[3]), 0])
        return K*c
    
    def runScipyLP(self,Op_array,method='simplex'):
        '''
        Desc: Build arrays and run LP optimization problem with Scipy
        Inputs: Op_array = numpy array [PB Steam, HP Load,
                                         IP Load, LP Load]
        Outputs: Solution formatted in a Dataframe
        '''
        self.op_array = Op_array # store for later use
        self.A_eq, self.b_eq = self.buildEqConstraints(Op_array)
        self.A_ineq, self.b_ineq, self.bnds = self.buildIneqConstraints()
        self.c = self.build_obj()
        self.opt = linprog(c= - self.c, A_ub=self.A_ineq,
                           b_ub=self.b_ineq, A_eq=self.A_eq,
                           b_eq=self.b_eq, method=method)
        # bounds = self.bnds
        self.X = self.opt.x
        self.sol = pd.DataFrame(self.opt.x.reshape(1,-1),
                           columns = self.cons_df.columns)
        return self.sol
    
    def runCvxoptLP(self,Op_array,method='glpk'):
        '''
        Desc: Build arrays and run LP optimization problem with
        CVX-opt
        Inputs: Op_array = numpy array [PB Steam, HP Load,
                                         IP Load, LP Load]
        Outputs: Solution formatted in a Dataframe
        '''
        self.op_array = Op_array # store for later use
        self.A_eq, self.b_eq = self.buildEqConstraints(Op_array)
        self.A_ineq, self.b_ineq, self.bnds = self.buildIneqConstraints()
        self.c = self.build_obj()
        c = matrix(-self.c)
        G = matrix(self.A_ineq)
        h = matrix(self.b_ineq)
        A = matrix(self.A_eq)
        b = matrix(self.b_eq)
        self.opt = solvers.lp(c,G,h,A,b,solver=method)
        if self.opt['status'] == 'optimal':
            self.X = np.array(self.opt['x']).ravel()
            self.sol = pd.DataFrame(self.X.reshape(1,-1),
                           columns = self.cons_df.columns)
        else:
            self.X = np.zeros(len(self.cons_df.columns))
            self.sol = pd.DataFrame(self.X.reshape(1,-1),
                           columns = self.cons_df.columns)          
                
        return self.sol
        
    def plotResults(self,returnFig=False):        
        '''
        Desc: Display results of Optimization on Graphic
        Inputs: none
        Outputs: plot of steam system with results
        '''
        fig,ax = plt.subplots(figsize=(15, 10))
        plt.imshow(self.img,interpolation='bilinear')
        ax.grid(False)
        ax.axis('off')
        
        txt = []
        # Add Optimized Variables and Ranges
        for col in self.sol.columns:
            s = col + ': {:0.1f}\n'.format(self.sol[col].values[0])
            s = s + '[{:0.1f}, {:0.1f}]'.format(
                self.cons_df.fillna(0)[col].loc['Min'],
                self.cons_df.fillna(0)[col].loc['Max'])
            txt.append(s)
            
        # Add Load and PB Supply
        statics = ['$F_{PB}$','$F_{L1}$','$F_{L2}$','$F_{L3}$']
        for i,pv in enumerate(statics):
            txt.append(pv + ': {:0.1f}'.format(self.op_array[i]))
            
        # Total MW Generation
        txt.append('Total Electrical: {:0.2f} MW'.format(
                np.matmul(self.c,self.X)))
        
        # Locations of text boxes
        locations = np.array([[205,360],
                             [235,150],
                             [560,350],
                             [670,295],
                             [795,295],
                             [560,160],
                             [675,100],
                             [800,100],
                             [940,100],
                             [30,180],
                             [255,450],
                             [430,415],
                             [430,225],
                             [430,85],
                             [760,475]],dtype=float)
        locations[:,0] = locations[:,0]/1000
        locations[:,1] = locations[:,1]/500
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=1)
        
        '''Put results on picture'''
        for i in range(0,len(txt)):
            ax.text(locations[i,0],locations[i,1], txt[i],
                    transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', bbox=props)
            
        font = {'color':  'white', 'weight': 'bold'}
        if self.checkResult():
            props = dict(boxstyle='round', facecolor='green', alpha=1)
            ax.text(0.4,0.975,'Optimization\nSuccessful', transform=ax.transAxes,
                    fontdict = font, fontsize=10,
                    verticalalignment='top', bbox=props)
        else:
            props = dict(boxstyle='round', facecolor='red', alpha=1)
            ax.text(0.4,0.975,'Optimization\nFailed',  transform=ax.transAxes,
                    fontdict = font, fontsize=10,
                    verticalalignment='top', bbox=props)
        if returnFig:
            return fig
        else:
            return

    def checkResult(self):
        '''
        Desc: Checks the results of the optimization
        Inputs: none
        Outputs: True if all constaints are met, False otherwise
        '''
        tol = 1e-8
        good = True # assume solution is good
        
        eq_cnst = np.matmul(self.A_eq,self.X) - self.b_eq
        eq_cnst = np.abs(eq_cnst.sum()) < tol
        good = good and eq_cnst
        
        check_ineq = np.matmul(self.A_ineq,self.X)
        for i in range(0,len(self.b_ineq)):
            good = good and (check_ineq[i] <= self.b_ineq[i])
        
        return good
        
    def updateSol(self):
        '''
        Desc: Updates Solution Dataframe with Current X value
        Inputs: none
        Outputs: none
        '''
        self.sol = pd.DataFrame(self.X.reshape(1,-1),
                                columns = self.cons_df.columns)
        return
