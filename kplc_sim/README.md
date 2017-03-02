KPLC Sim
========

This creates fake consumers with real-looking historical power and billing data.

The `sim.py` file creates and runs the simulation.

The `sim_api.js` provides a RESTful frontend for apps to interact with the simulation.

While the simulation is running, users will continue to "use" power.
Currently, simulated users automatically pay their balance every month. If a month boundary
happens to go by in the real world, they'll probably pay. Otherwise the intent is for the
RESTful api to allow "users" to pay.
