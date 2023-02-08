'''
Description: Runs and Linear Programming Optimization of 
an operational scenario and then moves the solution slightly to check
that the electrical production does infact decrease

Input: none

Output: Graphic of System optimized and moved off solution

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
import locale

if __name__ == "__main__":
    
    
    print('='*65)
    print('This Program Runs an Operational Scenario for a')
    print('Cogeneration Plant Steam System and Computes the')
    print('Optimal Path for All Steam Flows to Produce Maximum')
    print('Electrical Power While Supplying all Steam Users')
    print('Subject to Equipment Constraints.')
    print('The flows are then moved slightly off the calculated')
    print('solution to see that the MW production does indeed decrease')
    print('='*65)
    print()

    '''Build Model Object'''
    ss = SteamSystem()
    
    
    test_conditions = np.array([1415, 15, 250, 900])
    mv_amt = np.random.rand()*30 + 15


    print('Opeartional Scenario \n[Fpb, FL1, FL2, FL3] :')
    print(test_conditions)
    
    print('\n================ LP Solution ==================')
    res = ss.runScipyLP(test_conditions).to_string(index=False)
    print('Solution:\n',res.translate({ord(i): ' ' for i in '{}$'}))
    opt_mw = np.matmul(ss.X,ss.c)
    print('\nLP Solution MegaWatts: {:0.3f}'.format(opt_mw))
    scipyFig = ss.plotResults(returnFig=True)
    scipyFig.canvas.set_window_title('Optimal LP Solution')
    
    
    print('\n========== Off Optimal LP Solution =============')
    ss.X[1] = ss.X[1] + mv_amt
    ss.X[7] = ss.X[7] - mv_amt
    ss.X[6] = ss.X[6] + mv_amt
    ss.X[8] = ss.X[8] - mv_amt
    ss.X[-1] = ss.X[-1] + mv_amt
    ss.updateSol()
    print('Solution:\n',
          ss.sol.to_string(index=False).translate({ord(i): ' ' for i in '{}$'}))
    sub_mw = np.matmul(ss.X,ss.c)
    print('\nOff Solution MegaWatts: {:0.3f}'.format(sub_mw))
    print('\nConstraints Satisfied: {:s}'.format(str(ss.checkResult())))
    offFig = ss.plotResults(returnFig=True)
    offFig.canvas.set_window_title('Off Optimal LP Solution')
    
    scipyFig.show()
    offFig.show()
    
    # calculate lost revenue based on 15 days down time and 50$ per MW-hr
    locale.setlocale(locale.LC_ALL, '')  # sets to match user default laguange
    lost_rev = (opt_mw - sub_mw)*24*350*50
    lost_rev = locale.currency(lost_rev,grouping=True)
    print('='*50)
    print('Lost Revenue Per Year: {:s}'.format(lost_rev))
    
    input('\n\nPress Enter to Exit....')
    print('\nExecution Complete...')    

