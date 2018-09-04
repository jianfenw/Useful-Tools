import matplotlib.pyplot as plt
import numpy as np


def lineplot_2(x1_data, y1_data, x2_data, y2_data, x_label="", y_label="", title=""):
	# Create the plot object 
	_, ax = plt.subplots()
	# Plot the best fit line, set the linewidth (lw), color and transparency (alpha) of the line 
	ax.plot(x1_data, y1_data, lw = 1.5, color = 'b', alpha = 1)
	ax.plot(x2_data, y2_data, lw = 1.5, color = 'r', alpha = 1)
	# Label the axes and provide a title 
	ax.set_title(title) 
	ax.set_xlabel(x_label)
	ax.set_ylabel(y_label)
	plt.grid(True) 


def lineplot(x_data, y_data, x_label="", y_label="", title=""):
	# Create the plot object 
	_, ax = plt.subplots()
	# Plot the best fit line, set the linewidth (lw), color and transparency (alpha) of the line 
	ax.plot(x_data, y_data, lw = 1.5, color = 'b', alpha = 1)
	# Label the axes and provide a title 
	ax.set_title(title) 
	ax.set_xlabel(x_label) 
	ax.set_ylabel(y_label)
	plt.grid(True) 


def scatterplot(x_data, y_data, x_label="", y_label="", title="", color = "b", yscale_log=False):
	# Create the plot object 
	_, ax = plt.subplots()
	# Plot the data, set the size (s), color and transparency (alpha)
	ax.scatter(x_data, y_data, s = 10, marker='x', color = color, alpha = 0.75)
	if yscale_log == True:
		ax.set_yscale('log')
	ax.set_title(title) 
	ax.set_xlabel(x_label) 
	ax.set_ylabel(y_label)
	plt.grid(True) 

x=[(10+20*i) for i in range(13)] + [350, 450, 650, 850, 1000]
bess_y=[25754.6, 25952.7, 20909.3, 21213.9, 19326.4, 15798.2, 15737.9, 14733.4, 13810.8, 12943.1, 12232.3, 11469.0, 10335.8, 8665.6, 7174.9, 5343.8, 4170.2, 3620.6]
p4_y = [99965.5, 99954.7, 99954.2, 99956.9, 99963.1, 99963.4, 99958.4, 99955.6, 99963.1, 99959.7, 99957.9, 99961.4, 99963.8, 99960.3, 99964.1, 99958.0, 99964.9, 99963.1]
x1_label = '# of table entries'
y1_label = 'Throughput (Mbps)'
fig1_title = 'BESS Throughput Decreases As Number of Table Entries Increases'
lineplot_2(x,bess_y, x,p4_y, x1_label, y1_label, title=fig1_title)
plt.figure(1)



x1=[1,2,3,4,5,6,7]
y1=[12511.4, 7483.9, 5353.7, 4157.5, 3339.1, 2825.8, 2480.8]
x2=[1,2,3,4,5]
y2=[99959.5, 99960.0, 99958.6, 99956.6, 99956.4]
x2_label = '# of ACL modules'
y2_label = 'End-to-end Throughput (Mbps)'
fig2_title = 'Throughput: P4 NF Chain v.s. BESS NF Chain\n(200 Table Entries)'
lineplot_2(x1,y1,x2,y2, x2_label, y2_label, fig2_title)
plt.figure(2)

plt.show()
