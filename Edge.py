class DirectedEdge:

    @staticmethod
    def set_edge(entry_node, exit_node):
        edge = DirectedEdge(entry_node, exit_node)
        entry_node.add_outgoing_edge(edge)
        exit_node.add_incoming_edge(edge)

    def __init__(self, entry_node, exit_node):
        self.entry_node = entry_node
        self.exit = exit_node

    def get_wait_cost(self, member):
        return self.exit.expected_wait(member, self.entry_node)

    def get_service_cost(self, member):
        return self.exit.expected_service(member, self.entry_node)

