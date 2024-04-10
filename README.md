# Reinforcement-Learning-for-Auction-Bidding

### Abstract of report (Final Report.pdf)
This report investigates bidding strategies for an auction scenario with the goal of acquiring a target distribution of paintings from different artists. Simple rule based bots like the Greedy Bot and Fastest Plan are introduced as baselines. Reinforcement learning approaches are then explored, including regression to approximate the Greedy Bot, a genetic algorithm, and a Deep Q-Learning algorithm with separate policy and value networks trained through self-play. While the Deep Q-Learning approach shows promise, the inability to perfectly mirror the testing environment in training stunted its progress. Ultimately, the Greedy Bot with a minor optimisation emerges as the top performer among the strategies evaluated.

### Context
This was a project completed as coursework for a module contributing to my masters degree. The final report describes the goal and the results. Throughout this coursework many different reinforcement learning techniques were employed to attempt to teach a network to play the game set out in the coursework specifications.
