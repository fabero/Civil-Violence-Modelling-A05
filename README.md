# Introduction
Implementation of Simulation 1 from Epstein's paper ["Modeling civil violence: an agent-based computational approach"](https://www.semanticscholar.org/paper/Modeling-civil-violence%3A-an-agent-based-approach.-Epstein/012d71badb72df66a59c306dc597b4c96d783083), augmented to further model the spread of propaganda in favour of rebellion amongst citizens. 

Baseline mplementation is based on the given examples of the [mesa framework](https://github.com/projectmesa/mesa/tree/master/examples/epstein_civil_violence), but modified so that the simulation demonstrates the system punctuated equilibria that Epstein describes in his paper. The modifications are based on the [NetLogo implementation](https://ccl.northwestern.edu/netlogo/models/Rebellion).


# Packages Required
- pip install mesa
- or pip install -r requirements.txt

# Run
- python CivilViolenceServer.py

# Baseline: Differences from mesa original implementation

- ``portrayal.py``, this is actually rendundant and it's embedded inside CivilVioleneServer.py and called locally.

- ``CivilViolenceServer.py``, model parameters given as dynamic reconfigurable settings + the line chart for showing the plots.

- ``CivilViolenceAgent.py``, 1) Update arrest probability formula with flooring the ratio, 2) Move a cop to the position of the arrestee instead of choosing a random position, 3) update_neighbours should work for radius=self.vision instead of simply 1, and 4) after a jailed agent comes out of jail, her state is set to quiet instead of her previous state before arrest (active).
        
 - ``CivilViolenceModel.py``, the same, only the parameters as of NetLogo's model are given, and also percentages are scaled to [0,100] instead of [0,1]
  to be able to reconfigure them from webserver

# Alpha Version: Implementing propaganda agents
For our current experimental setup, the 70% of population is divided in 60% citizens - 10% propaganda agents. Propaganda agents spread propaganda to their local vision with a uniformly distributed influence, which affects the desicion of population agents to rebel by introfucing a new factor to their grievance variable, called Propaganda Effect (PE). By properly adjusting the model parameters, we see the effect of propaganda agents in the system's equilibria in the figures below: 
- Baseline Model (Epstein). The system equilibria described in Epstein's paper.
    ![Screenshot](https://github.com/fabero/Civil-Violence-Modelling-A05/blob/master/figures/Baseline.png)
- Alpha Version Model. We see the effect that propaganda agents have in the simulation, namely: a) Increase in rebellion outburst, as well as time in it (the slope of the red curves), b) Increase in rebellion outburst frequency, as witnessed by viewing the spikes in the x-axis, c) Finally converge in a state where most citizens are steadily in jail and so no more rebellions can outburst.
    ![Screenshot](https://github.com/fabero/Civil-Violence-Modelling-A05/blob/giorgos/figures/Selection_004.jpg)

# Beta Version: Changes in propaganda
Changes are in topics of propaganda agent implementation,
refning the model to propaganda effect and cops interaction to propaganda
agents. A summary is:

### 1.1 Propanda Agents
In current implementation, propaganda are normal population agents (citizens)
that follow the normal citizen behaviour (respect the activation rule A to check
whether they go active or not) and essentially count as citizens themselves.
This is translated in the grid initialization by having citizen density=60 and
propaganda density=10 so to make the same total of 70% as in Epstein.

Today we agreed on a different implementation. one that respects the 70% of
population agents and introduces a new percentage of propaganda agents (the
global propaganda density term) that spread propaganda. These "agents" are
not actually citizens (or cops), they do not become active or account as popu-
lation/cop agents for calculations of other agents. All they do is spread propa-
ganda to the grid. The theory behind this change is to leave out of our research
the inter-dynamics of propaganda-population agents (accounting propaganda
agents as citizens themselves) and simply model the effect of propaganda in the
standard population-cop Epstein system.

Propaganda agents are now dened by the following properties:
- agent class = 'propaganda'
- influence = uniform(0,1). The effect of the propaganda they spread
to citizens within local vision. This is uniformly distributed amongst pro-
paganda agents.
- total influence = int. This is an attribute that gets updated in each
new simulation step, counting how many citizens are influenced by this propaganda agent in the course of the simulation.

- jail threshold = XXX. At each time step, the total influence is com-
pared to this threshold. If it exceeds it, then this propaganda agent has
severely influenced citizens and is visible to authorities (cops can see and
jail them).
- visible to cops = False. When the above threshold is exceeded, this flag becomes True so cops can see and arrest them.


### 1.2 Population Agents
The citizen activation rule A is now:
        
        A : G' - NR > T                     (1)
where G' is the new Grievance term, NR is the old Net Risk parameter:
        
        NR = risk_aversion.prob_of_arrest  (2)
        
and T is the active threshold, dynamically set from UI (global parameter). The
new Grievance is now calculated as:
    
        G' = (G + w*PE)/1 + w              (3)
with w being a global UI parameter that decides the importance of the pro-
paganda effect in the model (this is the propaganda_factor parameter in the
current implementation, now set to :001). The propaganda effect is implemented
as:

        PE = s * sum(Influence(PropagandaAgent_i)/N)    (4)
with s denoting the susceptibility of each citizen (as in current implementation
susceptibility = uniform(0,1)) and N the total number (and not percent-
age) of propaganda agents currently in the board.


### 1.3 Cop Agents
Cop agents rule for capturing agents needs to be changes so that rst they
look for propaganda agents with the visible to cops 
ag on. If they do, the catch her (or a random selection of them if they are multiple). Otherwise,
they proceed with their regular search for active agents. The theory behind
this choice is that the central authority has exposed the certain propaganda
agent (because her influence exceeded the desired threshold) and has prioritized
grabbing them. Maybe also the jailing factor should be greater for this type of
jailing (the sentence is bigger).