import simpy
from Member import Member


class QueueNode:

    service_rate = 267.4
    priority_policy = "FIFO"
    balance_window = 0.1    # If a proportions passes p + balance_window, prioritize

    @staticmethod
    def reposition(array, element_index, new_position):
        prio = array[element_index].priority
        for i in reversed(range(new_position+1, element_index+1)):
            array[i].priority = array[i-1].priority
        array[new_position].priority = prio

    @staticmethod
    def reposition(array, element_index, new_position):
        item = array[element_index]
        for i in reversed(range(new_position+1, element_index+1)):
            array[i] = array[i-1]
        array[new_position] = item

    def __init__(self, env, level, capacity=1, frequency=1, centre=1):
        self.env = env
        self.level = level
        self.capacity = capacity    # Max number of seats
        self.seats = simpy.PriorityResource(self.env, capacity=capacity)
        self.frequency = frequency  # Hours per week
        self.centre_id = centre     # Centre ID
        self.queue_array = []      # Array of Members in class and wait list
        self.outgoing_edges = []
        self.incoming_edges = []
        self.last_accepted_member = None
        self.last_accepted_centre = None

    def expected_wait(self, member, int_node):
        q = self.get_queue(member, int_node)
        s = self.seats.users
        if len(s) < self.capacity:
            return 0.
        else:
            rate = self.frequency/float(QueueNode.service_rate)
            return (len(q)+1)/float(self.capacity*rate)

    def expected_service(self, member, int_node):
        q = self.get_queue(member, int_node)
        s = self.seats.users
        if len(s) < self.capacity:
            return float(member.service_rate)/self.frequency
        else:
            rate = self.frequency/float(member.service_rate)
            return ((len(q)+1)/float((self.capacity*rate))) + 1./rate

    def set_capacity(self, capacity):
        self.seats = simpy.Resource(self.env, capacity=capacity)
        self.capacity = capacity

    def add_outgoing_edge(self, edge):
        self.outgoing_edges.append(edge)

    def add_incoming_edge(self, edge):
        self.incoming_edges.append(edge)

    def add_to_queue(self, member):
        self.queue_array.append(member)
        self.rearrange_queue()

    def release_from_queue(self, member):
        self.queue_array.remove(member)


    # TODO Do not physically rearrange the resource, but change the priority levels
    def rearrange_queue(self):
        last_accepted_member = self.last_accepted_member
        if last_accepted_member is None:   # No users yet, do nothing
            return

        if QueueNode.priority_policy == "FIFO": # FIFO means do nothing
            return
        elif QueueNode.priority_policy == "Centre":
            if self.last_accepted_centre is None:
                return
            last_accepted_centre = self.last_accepted_centre
            my_centre = self.centre_id
            queue = self.seats.queue
            queue_length = len(queue)
            if last_accepted_centre == self.centre_id:
                for q in range(0, queue_length):
                    if q % 2 == 0:
                        if self.queue_array[q].centres_visited[-1] == my_centre:
                            old_q = q
                            while q < queue_length and self.queue_array[q].centres_visited[-1] == my_centre:
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
                    else:
                        if self.queue_array[q].centres_visited[-1] != my_centre:
                            old_q = q
                            while q < queue_length and self.queue_array[q].centres_visited[-1] != my_centre:
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
            else:
                for q in range(0, queue_length):
                    if q % 2 == 1:
                        if self.queue_array[q].centres_visited[-1] == my_centre:
                            old_q = q
                            while q < queue_length and self.queue_array[q].centres_visited[-1] == my_centre:
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
                    else:
                        if self.queue_array[q].centres_visited[-1] != my_centre:
                            old_q = q
                            while q < queue_length and self.queue_array[q].centres_visited[-1] != my_centre:
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
            # Re-enumerate so requests are taken in this order!
            for i in range(0, len(queue)):
                queue[i].priority = i - len(queue)
            return
        elif QueueNode.priority_policy == "Refugee":
            last_class = last_accepted_member.priority_class
            queue = self.seats.queue
            queue_length = len(queue)
            if last_class == "Refugee":
                for q in range(0, queue_length):
                    if q % 2 == 0:
                        if self.queue_array[q].priority_class == "Refugee":
                            old_q = q
                            while q < queue_length and self.queue_array[q].priority_class == "Refugee":
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
                    else:
                        if self.queue_array[q].priority_class != "Refugee":
                            old_q = q
                            while q < queue_length and self.queue_array[q].priority_class != "Refugee":
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
            else:
                for q in range(0, queue_length):
                    if q % 2 == 1:
                        if self.queue_array[q].priority_class == "Refugee":
                            old_q = q
                            while q < queue_length and self.queue_array[q].priority_class == "Refugee":
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
                    else:
                        if self.queue_array[q].priority_class != "Refugee":
                            old_q = q
                            while q < queue_length and self.queue_array[q].priority_class != "Refugee":
                                q += 1
                            if q < queue_length:
                                QueueNode.reposition(queue, q, old_q)
                                QueueNode.reposition(self.queue_array, q, old_q)
                            q = old_q + 1
            # Re-enumerate so requests are taken in this order!
            for i in range(0, len(queue)):
                queue[i].priority = i - len(queue)

        elif QueueNode.priority_policy == "Balance":
            ref_index = Member.priority_class.index("Refugee")
            historical_ref_proportion = Member.priority_proportions[ref_index]
            # What's the proportion of refugees in the wait list
            refugees = 0
            queue = self.seats.queue
            if not queue:
                return
            for q in self.queue_array:
                if q.priority_class == "Refugee":
                    refugees += 1
            current_ref_proportion = refugees/float(len(self.queue_array))

            wnd = QueueNode.balance_window
            if current_ref_proportion > historical_ref_proportion + wnd:    # Strictly greater, so 3/10 is okay
                q = 0
                inserted = 0
                while q < len(self.queue_array) and refugees/float(len(self.queue_array)) > historical_ref_proportion + wnd:
                    if self.queue_array[q] == "Refugee":
                        QueueNode.reposition(self.queue_array, q, inserted)
                        QueueNode.reposition(queue, q, inserted)
                        inserted += 1
                        refugees -= 1
                    q += 1
            elif current_ref_proportion < historical_ref_proportion - wnd:    # Strictly greater, so 3/10 is okay
                q = 0
                inserted = 0
                while q < len(self.queue_array) and refugees/float(len(self.queue_array)) < historical_ref_proportion - wnd:
                    if self.queue_array[q] != "Refugee":
                        QueueNode.reposition(self.queue_array, q, inserted)
                        QueueNode.reposition(queue, q, inserted)
                        inserted += 1
                        refugees += 1
                    q += 1

            # Re-enumerate so requests are taken in this order!
            for i in range(0, len(queue)):
                queue[i].priority = i - len(queue)

            else:
                return
        else:   # If none, assume FIFO
            return

    def get_queue(self, member, interested_node):
        last_accepted_member = self.last_accepted_member
        if last_accepted_member is None:
            return self.seats.queue
        if QueueNode.priority_policy == "FIFO": # FIFO means do nothing
            return self.seats.queue
        elif QueueNode.priority_policy == "Centre":
            prev_centre = self.last_accepted_centre
            if prev_centre is None:     # First run, do nothing
                return self.seats.queue

            this_centre = self.centre_id
            considered_centre = interested_node.centre_id
            self.rearrange_queue()
            # Then determine the place of the newest member
            queue = []
            for q in self.seats.queue:    # Make a copy of the array contents
                queue.append(q)
            if not queue:
                return self.seats.queue
            if prev_centre == this_centre:
                if queue[0] == this_centre:  # Assume the rearrangement is correct
                    return self.seats.queue
                else:                       # We begin with a different class
                    for q in range(1, len(queue)):
                        if queue[q-1] == queue[q] and queue[q]:
                            if queue[q] != this_centre and considered_centre == this_centre \
                                    or queue[q] == this_centre and considered_centre != this_centre:
                                return queue[0:q]
            else:
                if queue[0] != this_centre:  # Assume the rearrangement is correct
                    return self.seats.queue
                else:                       # We begin with a different class
                    for q in range(1, len(queue)):
                        if queue[q] != this_centre and considered_centre == this_centre \
                                    or queue[q] == this_centre and considered_centre != this_centre:
                            return queue[0:q]
            return queue

        elif QueueNode.priority_policy == "Refugee":
            prev_class = last_accepted_member.priority_class
            interested_class = member.priority_class
            # First, rearrange the queue
            self.rearrange_queue()
            # Then determine the place of the newest member
            queue = []
            for q in self.seats.queue:    # Make a copy of the array contents
                queue.append(q)
            if not queue:
                return self.seats.queue
            if prev_class == "Refugee":
                if queue[0] == "Refugee":  # Assume the rearrangement is correct
                    return self.seats.queue
                else:                       # We begin with a different class
                    for q in range(1, len(queue)):
                        if queue[q-1] == queue[q] and queue[q]:
                            if queue[q] != "Refugee" and interested_class == "Refugee" \
                                    or queue[q] == "Refugee" and interested_class != "Refugee":
                                return queue[0:q]
            else:
                if queue[0] != "Refugee":  # Assume the rearrangement is correct
                    return self.seats.queue
                else:                       # We begin with a different class
                    for q in range(1, len(queue)):
                        if queue[q] != "Refugee" and interested_class == "Refugee" \
                                    or queue[q] == "Refugee" and interested_class != "Refugee":
                            return queue[0:q]
            return queue
        elif QueueNode.priority_policy == "Balance":
            self.rearrange_queue()  # Reorder
            queue = []
            for q in self.seats.queue:    # Make a copy of the array contents
                queue.append(q)
            if not queue:
                return queue
            ref_index = Member.priority_class.index("Refugee")
            historical_ref_proportion = Member.priority_proportions[ref_index]
            refugee = 0
            wnd = QueueNode.balance_window
            for q in self.queue_array:
                if q.priority_class == "Refugee":
                    refugee += 1

            # How would the new member affect the queue proportions
            if member.priority_class == "Refugee":  # Refugee will either be behind other refugees, or at the back
                if 1/float(len(queue)+1) > historical_ref_proportion + wnd:
                    return queue[0:refugee]
                else:
                    return queue

            else:
                return queue
        else:   # If none, assume FIFO
            return self.seats.queue







class BiasNode:

    def __init__(self, skill_level):
        self.skill_level = skill_level
        self.edges = []
        self.centre_id = 0

    def add_outgoing_edge(self, edge):
        self.edges.append(edge)




