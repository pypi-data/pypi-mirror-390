import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

temperature = ctrl.Antecedent(np.arange(0, 41, 1), 'temperature')
heater = ctrl.Consequent(np.arange(0, 101, 1), 'heater')

temperature['cold'] = fuzz.trimf(temperature.universe, [0, 0, 20])
temperature['warm'] = fuzz.trimf(temperature.universe, [15, 25, 35])
temperature['hot'] = fuzz.trimf(temperature.universe, [30, 40, 40])

heater['low'] = fuzz.trimf(heater.universe, [0, 0, 50])
heater['medium'] = fuzz.trimf(heater.universe, [25, 50, 75])
heater['high'] = fuzz.trimf(heater.universe, [50, 100, 100])

rule1 = ctrl.Rule(temperature['cold'], heater['high'])
rule2 = ctrl.Rule(temperature['warm'], heater['medium'])
rule3 = ctrl.Rule(temperature['hot'], heater['low'])

heater_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
heater_sim = ctrl.ControlSystemSimulation(heater_ctrl)
    
heater_sim.input['temperature'] = 100
heater_sim.compute()

print("Temperature: 100°C")
print("Heater Output:", heater_sim.output['heater'])
