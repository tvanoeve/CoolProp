from __future__ import print_function, division
import os.path
import CoolProp
import CoolProp.CoolProp
import subprocess
import sys

import numpy as np

import matplotlib
matplotlib.use('Agg') #Force mpl to use a non-GUI backend
import matplotlib.pyplot as plt

web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
plots_path = os.path.join(web_dir,'fluid_properties','incompressibles_consistency')

N = 50
p = 100e5
Pr = np.empty(N)
la = np.empty(N)
mu = np.empty(N)
cp = np.empty(N)

fig = plt.figure(tight_layout=True)
Pr_axis = fig.add_subplot(221)
la_axis = fig.add_subplot(222)
mu_axis = fig.add_subplot(223)
cp_axis = fig.add_subplot(224)

#Pr_axis = plt.subplot2grid((3,2), (0,0), rowspan=3)
#la_axis = plt.subplot2grid((3,2), (0,1))
#mu_axis = plt.subplot2grid((3,2), (1,1))
#cp_axis = plt.subplot2grid((3,2), (2,1))

Pr_axis.set_xlabel("Temperature $T$ / deg C")
Pr_axis.set_ylabel("Prandtl Number $Pr$")
#Pr_axis.set_yscale("log")
la_axis.set_xlabel("Temperature $T$ / deg C")
la_axis.set_ylabel("Thermal Conductivity $\lambda$ / W/m/K")
mu_axis.set_xlabel("Temperature $T$ / deg C")
mu_axis.set_ylabel("Dynamic Viscosity $\mu$ / Pa s")
#mu_axis.set_yscale("log")
cp_axis.set_xlabel("Temperature $T$ / deg C")
cp_axis.set_ylabel("Isobaric Heat Capacity $c_p$ / J/kg/K")

for fluid in CoolProp.__incompressibles_pure__:
    if "example" in fluid.lower(): continue
    state = CoolProp.AbstractState("INCOMP",fluid)
    T = np.linspace(state.Tmin(), state.Tmax(), N)
    for i, Ti in enumerate(T):
        state.update(CoolProp.PT_INPUTS, p, Ti)
        Pr[i] = state.Prandtl()
        la[i] = state.conductivity()
        mu[i] = state.viscosity()
        cp[i] = state.cpmass()
    #print(np.min(Pr), np.max(Pr))
    Pr_axis.plot(T-273.15,Pr)
    la_axis.plot(T-273.15,la)
    mu_axis.plot(T-273.15,mu)
    cp_axis.plot(T-273.15,cp)
    
    if np.max(Pr)>10000:
        print("Very high Prandtl number for "+fluid)
    
for fluid in CoolProp.__fluids__:
    continue
    state = CoolProp.AbstractState("HEOS",fluid)
    T = np.linspace(state.Tmin(), state.Tmax(), N)
    for i, Ti in enumerate(T):
        try:
            state.update(CoolProp.QT_INPUTS, 0, Ti)
            p = state.p() + 1e5
        except:
            p = 100e5
        Pr[i] = np.nan
        la[i] = np.nan
        mu[i] = np.nan
        cp[i] = np.nan 
        try:
            state.update(CoolProp.PT_INPUTS, p, Ti)
            try: Pr[i] = state.Prandtl()
            except: pass
            try: la[i] = state.conductivity()
            except: pass
            try: mu[i] = state.viscosity()
            except: pass
            try: cp[i] = state.cpmass()
            except: pass
        except:
            pass    
    #print(np.min(Pr), np.max(Pr))
    if np.sum(np.isnan(Pr)) == 0: 
        Pr_axis.plot(T-273.15,Pr,alpha=0.5,ls=":")
    else: 
        #print("Error: Prandtl undefined for "+fluid)
        pass
    if np.sum(np.isnan(la)) == 0: 
        la_axis.plot(T-273.15,la,alpha=0.5,ls=":")
    else: 
        #print("Error: Conductivuty undefined for "+fluid)
        pass
    if np.sum(np.isnan(mu)) == 0: 
        mu_axis.plot(T-273.15,mu,alpha=0.5,ls=":")
    else: 
        #print("Error: Viscosity undefined for "+fluid)
        pass
    if np.sum(np.isnan(cp)) == 0: 
        cp_axis.plot(T-273.15,cp,alpha=0.5,ls=":")
    else: 
        #print("Error: Heat capacity undefined for "+fluid)
        pass
    
    
fig.tight_layout()
fig.savefig(plots_path+'.pdf')
sys.exit(0)

template = """from __future__ import division, print_function
import matplotlib
matplotlib.use('Agg') #Force mpl to use a non-GUI backend

import matplotlib.pyplot as plt
from CoolProp.Plots.ConsistencyPlots import ConsistencyFigure

ff = ConsistencyFigure('{fluid:s}')
ff.savefig('{fluid:s}.png', dpi = 30)
ff.savefig('{fluid:s}.pdf')
plt.close()
del ff
"""
if not os.path.exists(plots_path):
    os.makedirs(plots_path)
    
for fluid in CoolProp.__fluids__:
    print('fluid:', fluid)
    file_string = template.format(fluid = fluid)
    file_path = os.path.join(plots_path, fluid + '.py')
    print('Writing to', file_path)
    with open(file_path, 'w') as fp:
        fp.write(file_string)
    print('calling:', 'python "' + fluid + '.py"', 'in',plots_path)
    subprocess.check_call('python "' + fluid + '.py"', cwd = plots_path, stdout = sys.stdout, stderr = sys.stderr, shell = True)