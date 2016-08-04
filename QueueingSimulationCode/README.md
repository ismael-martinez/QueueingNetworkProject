# RefugeeQueueingSimulation
A queueing network simulation written in Python using SimPy, to model refugees arriving into a system, and moving through the language course network.

To run, execute Simulation.py with the appropriate parameters.

Three CSV input files are expected, as well as paths to two output csv files.
-n <network csv> -l <level csv> -e <econ csv> -a <assignment policy> ' \
                  '-p <priority policy> -w <weeks> -d <surge delay> -q <output csv> -o <output weekly queue> -r <probability distribution>' \
                  '-v <variance> -i <range window>'

-n <network csv>:	A csv outlining the layout of the network. The row headers are 
	"Level": The course level 
	"Capacity": The maximum occupancy of the class
	"Frequency": The number of hours per week the class is held
	"Centre": The Centre ID where the course is taught
	
-l <level csv>:		A csv outlining the proportion of students arriving for each course level. The row headers are
	"Level": The course skill level equivalent of the incoming students
	"Proportion": An integer to denote the percentage of students arriving with this skill level. This column should sum to 100
	"Left": The percentage of students who leave the system once attaining this level
	
-e <immigration csv>:		A csv outlining the proportion of students arriving for different immigration classes. The row headers are
	"Immigration Class": The label of the immigration class, such as "Refugee" or "Skilled Worker"
	"Proportion": An integer to denote the percentage of arriving students of that class. This column should sum to 100.
	"Mean Service Rate": The mean number of hours students of this class take to complete a level
	"Variance": The variance in the number of hours students of this class take to complete a level
	
-a <assignment policy>:		The policy used to assign students to the next course. Options are
	"Uniform": Randomly assign a student to the next class
	"Deterministic Wait": Assign a student to the class with the minimum expected wait time
	"Deterministic Service" Assign a student to the class with the minimum expected service time

-p <priority policy>:		The policy used to determine the next student in a queue to enter a course. The options are
	"FIFO": First-In First-Out
	"Centre": Give priority to students already enrolled in that centre. Alternates between current students and new students
	"Refugee": Gives students of the Refugee class priority. Alternates between refugees and non-refugees
	"Balance": Keeps historical proportions in the queue, and gives priority to an group who has a higher proportion than normal
	
-w <weeks>:(Optional)		The number of weeks to run the simulation. The default is 26 weeks.

-d <surge delay>:(Optional) The delay in weeks before a 2xRefugee surge is applied. If ommited, the surge does not take place.

-q <output csv>  			Simulation results are given. Outlines each instance of a student entering a course and completing it, as well as the time frames associated.

-o <output weekly queue>:	Simulation results are given. Outlines each course queue size for each week

-r <probability distribution>: 	Denotes the distribution used to distribute the time students spend in class. Options are
	"Exponential":	Exponentially distributed with the mean in -e file
	"Normal":		Normally distributed with mean in -e file and variance in -v
	"Constant":		Constant time with mean in -e file
	"Uniform":		Uniformly distributed with mean in -e files and range in -immigration
	
-v <variance>:				If "Normal" distribution is selected from -r, enter integer variance
 
-i <range window>: 			If "Uniform" distribution is selected in -r, enter integer range window in hours.	