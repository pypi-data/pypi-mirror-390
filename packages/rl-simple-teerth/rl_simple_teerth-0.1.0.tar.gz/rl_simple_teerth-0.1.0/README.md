\# RL Simple Package by Teerth



A simple Python package for Reinforcement Learning utilities created by \*\*Teerth\*\* for academic assignment.



\## Installation



pip install rl\_simple\_teerth





\## Features



\- \*\*Epsilon-Greedy Action Selection\*\*: Balance exploration and exploitation

\- \*\*TD Error Calculation\*\*: Compute temporal difference errors



\## Usage



from rl\_simple import epsilon\_greedy\_action, calculate\_td\_error



Epsilon-greedy selection

Q\_values = \[0.1, 0.8, 0.3]

action = epsilon\_greedy\_action(Q\_values, epsilon=0.1)

print(f"Selected action: {action}")



TD error

td\_error = calculate\_td\_error(reward=1.0, gamma=0.9,

current\_value=0.5, next\_value=0.8)

print(f"TD Error: {td\_error}")





\## Author



\*\*Teerth\*\*  

Created for Reinforcement Learning Assignment

