# Packages Required
- pip install mesa
- or pip install -r requirements.txt

# Run
- python CivilViolenceServer.py

# Differences from mesa original implementation:

- portrayal.py, this is actually rendundant and it's embedded inside CivilVioleneServer.py and called locally.

- server.py, model parameters given as dynamic reconfigurable settings + the line chart for showing the plots

- agent.py:
        1) Update arrest probability formula with flooring the ratio,
        2) Move a cop to the position of the arrestee instead of choosing a random position,
        3) update_neighbours should work for radius=self.vision instead of simply 1, and
        4) after a jailed agent comes out of jail, her state is set to quiet instead of her previous state before arrest (active)
        
 - model.py, the same, only the parameters as of NetLogo's model are given, and also percentages are scaled to [0,100] instead of [0,1]
  to be able to reconfigure them from webserver.
