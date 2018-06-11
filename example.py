from MyDoc import document
from sympy.physics.units import meter, second, inch, newton, pascal
with document() as a:
	a.options = '12pt'
	a.chapter('''First Chapter''')
	a.type = 'report'
	a.file = 'docx'
	a.append('''It should be emphasized that for systems in which the inputs are known ahead of time and in which there are no disturbances it is advisable to use open-loop control.  Closed-loop control systems have advantages only when unpredictable disturbanc and/or unpredictable variations in system components are present. Note that the  output power rating partially determines the cost,weight,and size of a control system.  The number of components used in a closed-loop control system is more than that for  a corresponding open-loop control system. Thus, the closed-loop control system is  generally higher in cost and power.To decrease the required power of a system,open-  loop control may be used where applicable.A proper combination of open-loop and  closed-loop controls is usually less expensive and will give satisfactory overall system  performance.''')
	a.section('The section')

	a.append('''$F = ma$ It should be emphasized that for systems in which the inputs are known ahead of time and in which there are no disturbances it is advisable to use open-loop control.  Closed-loop control systems have advantages only when unpredictable disturbanc  and/or unpredictable variations in system components are present. Note that the  output power rating partially determines the cost,weight,and size of a control system.  The number of components used in a closed-loop control system is more than that for  a corresponding open-loop control system. Thus, the closed-loop control system is generally higher in cost and power.To decrease the required power of a system,open-  loop control may be used where applicable.A proper combination of open-loop and  closed-loop controls is usually less expensive and will give satisfactory overall system  performance.''')
	a.subsection('''The section''')

	a.append('''Note that the  output power rating partially determines the cost,weight,and size of a control system.  The number of components used in a closed-loop control system is more than that for  a corresponding open-loop control system. Thus, the closed-loop control system is  generally higher in cost and power.''')
	a.equation('''L_M = \\pi\\times \\frac{\\theta}{56}''', inline=True)

	a.append('''Note that the  output power rating partially determines the cost,weight,and size of a control system.  The number of components used in a closed-loop control system is more than that for  a corresponding open-loop control system. Thus, the closed-loop control system is  generally higher in cost and power.\\\\''')
	a.aserar('beta_ = 3*newton', 'define')
	a.aserar('Theta_ = 98*meter**2', 'define')
	a.aserar('''B = (beta_/Theta_)''', unit = pascal)

	a.append('''Note that the  output power rating partially determines the cost,weight,and size of a control system.  The number of components used in a closed-loop control system is more than that for  a corresponding open-loop control system. Thus, the closed-loop control system is generally higher in cost and power.''')
