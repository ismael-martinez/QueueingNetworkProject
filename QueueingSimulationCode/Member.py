import csv
from random import expovariate
from scipy.stats import uniform, norm
from CSV import QueueDataCSV


class Member:

    id = 0  # ID of the Member
    priority_class = []
    priority_proportions = []
    priority_service_rates = []
    queue_csv = ""
    queue_csv_writer = None
    pr_dist = 'Constant'
    variance = 0
    range_window = 0

    @staticmethod
    def begin_csv():
        Member.queue_csv_writer = QueueDataCSV(Member.queue_csv)

    @staticmethod
    def end_csv():
        Member.queue_csv_writer.close()

    def __init__(self, priority_class, level):
        self.priority_class = priority_class    # String: "family", "refugee", "worker", "econ", "other"
        self.member_id = Member.id + 1
        self.level = level
        self.service_rate = self.service_rate()
        self.advancement_duration = 0           # Service rate depends on the priority_class, normal distr.
        self.centres_visited = [0]              # Arrival node

        self.pr_dist = Member.pr_dist           # Class Time distribution
        self.variance = Member.variance         # Variance for Normal distribution
        self.range_window = Member.range_window # Range for uniform distribution

        Member.id += 1                          # Increment the Member class count

    def advance(self):
        self.level += 1

    def request(self, choice_node, prev_node, exp_wait, exp_service, env):
        self.advancement_duration = self.set_advancement_duration(choice_node)
        # Add self to the queue system
        choice_node.add_to_queue(self)
        req = choice_node.seats.request(priority=0)
        arrived = env.now
        yield req
        accepted = env.now
        self.centres_visited.append(choice_node.centre_id)
        choice_node.release_from_queue(self)
        # Rearrange the priority queues
        choice_node.last_accepted_member = self
        choice_node.last_accepted_centre = prev_node.centre_id
        choice_node.rearrange_queue()
        waited = accepted - arrived
        #print("Member %d got into the class level %d at time %7.4f and waited %7.4f. Expected Wait was %7.4f" %
        #     (self.member_id, choice_node.level, accepted, waited, exp_wait))
        # Obtained the seat
        yield env.timeout(self.advancement_duration)
        choice_node.seats.release(req)
        left_class = env.now
        total_service = left_class - arrived
        #print("Member %d left class level %d at time %7.3f" % (self.member_id, choice_node.level, left_class))
        Member.queue_csv_writer.write(self.member_id, arrived, exp_wait, exp_service, waited, accepted,
                                      self.advancement_duration, left_class, total_service, choice_node.level, self.priority_class)
        self.advance()

    def set_advancement_duration(self, node):
        frequency = node.frequency
        expected_service = self.service_rate/frequency
        if self.pr_dist == 'Constant':
            return expected_service
        elif self.pr_dist == 'Uniform':
            shift = float(self.range_window)/frequency
            return uniform.rvs(expected_service - shift, 2*shift)
        elif self.pr_dist == 'Exponential':
            return expovariate(1./expected_service)
        elif self.pr_dist == 'Normal':
            duration = -1
            while duration < 0:
                duration = norm.rvs(expected_service, self.variance)
            return duration


    def service_rate(self):
        index = Member.priority_class.index(self.priority_class)
        mean = Member.priority_service_rates[index]
        return mean

    @staticmethod
    def set_priority_class(proportions_path):
        with open(proportions_path, 'rb') as csv_file:
            data_reader = csv.reader(csv_file)
            iterrows = iter(data_reader)    # Skip first line in a csv
            next(iterrows)
            for row in data_reader:
                Member.priority_class.append(row[0])
                Member.priority_proportions.append(0.01*float(row[1]))
                Member.priority_service_rates.append(float(row[2]))
