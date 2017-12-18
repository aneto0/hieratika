from ahkab import new_ac, run
from ahkab.circuit import Circuit
#from ahkab.plotting import plot_results # calls matplotlib for you
import numpy as np

# Define the circuit
cir = Circuit('Butterworth 1kHz band-pass filter')
cir.add_vsource('V1', 'n1', cir.gnd, dc_value=0., ac_value=1.)
cir.add_resistor('R1', 'n1', 'n2', 50.)
cir.add_inductor('L1', 'n2', 'n3', 0.245894)
cir.add_capacitor('C1', 'n3', 'n4', 1.03013e-07)
cir.add_inductor('L2', 'n4', cir.gnd, 9.83652e-05)
cir.add_capacitor('C2', 'n4', cir.gnd, 0.000257513)
cir.add_inductor('L3', 'n4', 'n5', 0.795775)
cir.add_capacitor('C3', 'n5', 'n6', 3.1831e-08)
cir.add_inductor('L4', 'n6', cir.gnd, 9.83652e-05)
cir.add_capacitor('C4', 'n6', cir.gnd, 0.000257513)
cir.add_capacitor('C5', 'n7', 'n8', 1.03013e-07)
cir.add_inductor('L5', 'n6', 'n7', 0.245894)
cir.add_resistor('R2', 'n8', cir.gnd, 50.)

# Define the analysis
ac1 = new_ac(.97e3, 1.03e3, 1e2, x0=None)

# run it
res = run(cir, ac1)

print res["ac"].keys()
print res["ac"]["f"]
print np.abs(res["ac"]["Vn8"])
print np.angle(res["ac"]["Vn8"])
# plot the results
#plot_results('5th order 1kHz Butterworth filter', [('|Vn8|',"")], res['ac'], outfilename='bpf_transfer_fn.png')
