import csv
from Node import BiasNode, QueueNode
from Edge import DirectedEdge
from Member import Member
import numpy
from scipy.stats import randint, bernoulli
from random import expovariate
from CSV import QueueWeeklyCSV



class Network:

    arrival_rate = 110 # Number of people per week
    service_rate = 300  # in hours
    probability_of_leaving = 0.1

    def __init__(self, env, network_path):   # Initialize a blank network
        self.env = env
        self.network = []
        self.proportion_arrival = []    # Sets the proportions of levels
        self.proportion_leave = []
        self.highest_class = 0
        self.build_network(network_path)
        self.asn_policy = 'Uniform'
        self.queue_weekly_csv = ""
        self.queue_weekly_csv_writer = None


    # Read the network csv file and populate the queues
    def build_network(self, network_path):
        # Load CSV file in a readable manner
        with open(network_path, 'rb') as csv_file:
            data_reader = csv.reader(csv_file)
            queue_node = []
            iterrows = iter(data_reader)    # Skip first line in a csv
            next(iterrows)
            for row in data_reader:
                r = [int(row[0]), int(row[1]), float(row[2]), int(row[3])]
                queue_node.append(r)
            # Calculate max class
        for q in queue_node:
            if q[0] > self.highest_class:
                self.highest_class = q[0]
        # Initialize a list of length highest_class
        for l in range(0, self.highest_class+1):
            self.network.append([])
        # Add bias nodes
        for l in range(0, self.highest_class):
            self.network[l].append(BiasNode(l))
        # Create queue nodes and fill the network
        for q in queue_node:
            l = q[0]
            # level, capacity, frequency
            self.network[l].append(QueueNode(self.env, q[0], q[1], q[2], q[3]))
        # Connect edges
        for l in range(0, self.highest_class):
            for q in range(0, len(self.network[l])):
                for nq in range(1, len(self.network[l+1])):
                    # Connect these edges
                    DirectedEdge.set_edge(self.network[l][q], self.network[l+1][nq])

    # Defines the arriving members into the system
    def arrival(self):
        arrival_rate = Network.arrival_rate
        while True:     # Run every time unit
            # Arrival will be Poisson Process
            # Also need to determine the arrival for each level

            # Define the arriving priority class
            arrived_class = numpy.random.multinomial(1, Member.priority_proportions, size=1)[0]
            priority_index = numpy.where(arrived_class == 1)[0][0]
            priority_class = Member.priority_class[priority_index]
            # Define the arriving level
            arrived_level = numpy.random.multinomial(1, self.proportion_arrival, size=1)[0]
            skill_level = numpy.where(arrived_level == 1)[0][0]
            new_member = Member(priority_class, skill_level)
            #print("New member id %d entered system at time %7.3f, priority-class %s and skill level %d" %
            #      (new_member.id, self.env.now, priority_class, skill_level))
            self.env.process(self.push(new_member))

            time = expovariate(arrival_rate)    # Exponential arrival time
            yield self.env.timeout(time)

    def refugee_surge(self, delay):
        arrival_rate = 0.4*Network.arrival_rate
        while self.env.now < delay + 26:     # 26 weeks
            yield self.env.timeout(delay)
            priority_class = "Refugee"
            arrived_level = numpy.random.multinomial(1, self.proportion_arrival, size=1)[0]
            skill_level = numpy.where(arrived_level == 1)[0][0]
            new_member = Member(priority_class, skill_level)
            #print("New member id %d entered system at time %7.3f, priority-class %s and skill level %d" %
            #      (new_member.id, self.env.now, priority_class, skill_level))
            self.env.process(self.push(new_member))

            time = expovariate(arrival_rate)    # Exponential arrival time
            yield self.env.timeout(time)

    # Pushes a member into the network
    def push(self, member):
        arriving_level = member.level
        # For now, we choose any node in level N+1
        if member.level == 8:
            #self.exit(member)
            return
        p = 1 - self.proportion_leave[arriving_level]   # Probability they are assessed and leave
        stay = bernoulli.rvs(p)
        if not stay:
            #self.exit(member)
            return
        arrival_node = self.network[arriving_level][0]  # Arriving node
        queue_choice = None
        wait_cost = 0
        service_cost = 0
        min_cost = 0
        if self.asn_policy == 'Deterministic Wait':
            edges = arrival_node.edges
            min_cost = edges[0].get_wait_cost(member) + 1   # At the least, queue 0 has lower cost
            for q in range(0, len(edges)):
                if min_cost > edges[q].get_wait_cost(member):
                    min_cost = edges[q].get_wait_cost(member)
                    wait_cost = min_cost
                    service_cost = edges[q].get_service_cost(member)
                    queue_choice = edges[q].exit
        if self.asn_policy == 'Deterministic Service':
            edges = arrival_node.edges
            min_cost = edges[0].get_service_cost(member) + 1   # At the least, queue 0 has lower cost
            for q in range(0, len(edges)):
                if min_cost > edges[q].get_service_cost(member):
                    min_cost = edges[q].get_service_cost(member)
                    queue_choice = edges[q].exit
                    wait_cost = edges[q].get_wait_cost(member)
                    service_cost = min_cost
        if self.asn_policy == 'Uniform':
            choice_total = len(self.network[arriving_level+1])
            queue_index = randint.rvs(1, choice_total, size=1)[0]
            queue_choice = self.network[arriving_level+1][queue_index]

        yield self.env.process(member.request(queue_choice, arrival_node, wait_cost, service_cost, self.env))
        self.env.process(self.flow(member, queue_choice))

    # For easy readability
    def exit(self, member):
        print("Member %d left the system at time %7.3f with skill level %d" %
              (member.member_id, self.env.now, member.level))

    # Continues to push a node through the network
    def flow(self, member, queue_node):
        prob_staying_general = 1 - Network.probability_of_leaving
        prob_stay_level = (1 - self.proportion_leave[member.level])*prob_staying_general   # Added prob of leaving per level
        stay = bernoulli.rvs(prob_stay_level)
        if member.level == 8:   # There's also probability they will leave
            #self.exit(member)
            return
        elif not stay:
            #self.exit(member)
            return
        else:
            next_level = member.level + 1
            # Determine the next node to visit
            queue_choice = None
            min_cost = 0
            wait_cost = 0
            service_cost = 0
            if self.asn_policy == 'Deterministic Wait':
                edges = queue_node.outgoing_edges
                min_cost = edges[0].get_wait_cost(member) + 1   # At the least, queue 0 has lower cost
                for q in range(0, len(edges)):
                    if min_cost > edges[q].get_wait_cost(member):
                        min_cost = edges[q].get_wait_cost(member)
                        queue_choice = edges[q].exit
                        wait_cost = min_cost
                        service_cost = edges[q].get_service_cost(member)
            if self.asn_policy == 'Deterministic Service':
                edges = queue_node.outgoing_edges
                min_cost = edges[0].get_service_cost(member) + 1   # At the least, queue 0 has lower cost
                for q in range(0, len(edges)):
                    if min_cost > edges[q].get_service_cost(member):
                        min_cost = edges[q].get_service_cost(member)
                        queue_choice = edges[q].exit
                        service_cost = min_cost
                        wait_cost = edges[q].get_wait_cost(member)
            if self.asn_policy == 'Uniform':
                choice_total = len(self.network[next_level])
                queue_index = randint.rvs(1, choice_total, size=1)[0]
                queue_choice = self.network[next_level][queue_index]
            yield self.env.process(member.request(queue_choice, queue_node, wait_cost, service_cost, self.env))
            # if we are still in the network
            self.flow(member, queue_choice)

    # Reads the csv file and sets the proportions for arrival
    def set_level_arrival(self, level_path):
        with open(level_path, 'rb') as csv_file:
            data_reader = csv.reader(csv_file)
            iterrows = iter(data_reader)    # Skip first line in a csv
            next(iterrows)
            self.proportion_arrival = []    # Reset
            for row in data_reader:
                r = 0.01*float(row[1])
                l = float(row[2])
                self.proportion_arrival.append(r)
                self.proportion_leave.append(l)

    def set_policies(self, policy_path):
        with open(policy_path, 'rb') as csv_file:
            data_reader = csv.reader(csv_file)
            iterrows = iter(data_reader)    # Skip first line in a csv
            next(iterrows)
            self.proportion_arrival = []    # Reset
            for row in data_reader:
                print ", ".join(row)

    def print_network_queues(self):
        while True:
            queue = []
            week = self.env.now
            for l in range(1, len(self.network)-1):
                for q in range(1, len(self.network[l])):
                    queue_length = len(self.network[l][q].seats.queue)
                    queue.append(queue_length)
            for q in range(0, len(self.network[8])):
                queue_length = len(self.network[8][q].seats.queue)
                queue.append(queue_length)
            self.queue_weekly_csv_writer.write(queue, week)
            yield self.env.timeout(1)    # print every week

    def initialize_queue_csv(self):
        fieldnames = ["week"]
        for l in range(1, len(self.network)-1):
            for q in range(1, len(self.network[l])):
                queue_name = "L" + str(l) + "Q" + str(q)
                fieldnames.append(queue_name)
        for q in range(0, len(self.network[8])):
            queue_name = "L" + str(8) + "Q" + str(q)
            fieldnames.append(queue_name)
        self.queue_weekly_csv_writer = QueueWeeklyCSV(self.queue_weekly_csv, fieldnames)

    def close_queue_csv(self):
        self.queue_weekly_csv_writer.close()

