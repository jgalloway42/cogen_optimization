'''
Description: Runs and Linear Programming Optimization of 
an operational scenario solved with Scipy's LP and CVXOPT's LP
and shows a graphic of the results for comparison.

Input: none

Output: Graphics of System Solutions

Uses: SteamSystem.py, genericHeader.py, constraints.csv, attributes.csv,
    mass_balance_lhs.csv, mass_balance_rhs.csv, steamHeaderTopology.png
    
Python Version 3.7.3, Matplotlib Version 3.0.3, Numpy Version 1.16.2,
Scipy Version 1.5.2, CVXOPT Version 1.2.0

Author: Josh Galloway
Version: 1.0
Date: 06 Dec 2020
'''
from genericHeader import *
from SteamSystem import *

if __name__ == "__main__":
    
    
    print('='*65)
    print('This Program Runs an Operational Scenario for a')
    print('Cogeneration Plant Steam System and Computes the')
    print('Optimal Path for All Steam Flows to Produce Maximum')
    print('Electrical Power While Supplying all Steam Users')
    print('Subject to Equipment Constraints with Scipy\'s LP Optimizer')
    print('and CVXOPT\'s LP Optimizer and Shows Both Solution for Comparison')
    print('='*65)
    print()

    '''Build Model Object'''
    ss = SteamSystem()
    
    
    test_conditions = np.array([1100, 20, 550, 400])


    print('Opeartional Scenario \n[Fpb, FL1, FL2, FL3] :')
    print(test_conditions)
    
    print('\n======== Scipy Solution =============')
    res = ss.runScipyLP(test_conditions).to_string(index=False)
    print('Solution:\n',res.translate({ord(i): ' ' for i in '{}$'}))
    scipyFig = ss.plotResults(returnFig=True)
    scipyFig.canvas.set_window_title('Scipy LP Solution')
    
    print('\n======== CVXOPT Solution =============')
    res = ss.runCvxoptLP(test_conditions).to_string(index=False)
    print('Solution:\n',res.translate({ord(i): ' ' for i in '{}$'}))
    cvxFig = ss.plotResults(returnFig=True)
    cvxFig.canvas.set_window_title('CVXOPT/GNU LP Kit LP Solution')
    
    scipyFig.show()
    cvxFig.show()
    
    input('Press Enter to Exit....')
        
    

    print('\nExecution Complete...')    

