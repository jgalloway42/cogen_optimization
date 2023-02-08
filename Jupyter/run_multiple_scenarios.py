'''
Description: Runs and Linear Programming Optimization of 
several operational scenarios and shows a graphic of the result

Input: none

Output: Graphic of System

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
    print('This Program Runs 5 Operational Scenarios for a')
    print('Cogeneration Plant Steam System and Computes the')
    print('Optimal Path for All Steam Flows to Produce Maximum')
    print('Electrical Power While Supplying all Steam Users')
    print('Subject to Equipment Constraints. Then Graphs the Result')
    print('='*65)


    '''Build Model Object'''
    ss = SteamSystem()
    
    
    test_conditions = np.array([
    [1100, 20, 550, 400],
    [900, 10, 400, 400],
    [1415, 15, 250, 900],
    [1000, 15, 250, 250],
    [800, 100, 350, 300]
    ])


    for row in range(test_conditions.shape[0]):
        print('\nOpeartional Scenario \n[Fpb, FL1, FL2, FL3] :')
        print(test_conditions[row,:])
        res = ss.runScipyLP(test_conditions[row,:]).to_string(index=False)
        print(ss.opt.message)
        print('Solution:\n',res.translate({ord(i): ' ' for i in '{}$'}))
        ss.plotResults()
        print("Close Figure to continue to next scenario...")
        print('='*40)
        plt.show()
        #plt.close()
        
    

    print('\nExecution Complete...')    

