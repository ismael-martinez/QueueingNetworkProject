import simpy
import sys
import getopt
from Network import Network
from Member import Member
from Node import QueueNode

# The service rate in hours
SERVICE_RATE = 290

# TODO CSV Exporting


def main(argv):
    # Arguments
    network_path = ''  # Default
    level_path = ''
    econ_path = ''
    output_queue_wait_path = ''
    output_weekly_queue_path = ''
    asn_policy = ''
    prio_policy = ''
    weeks = 26
    delay = -1
    pr_dist = 'Constant'
    variance = 0
    range_window = 0
    try:
        opts, args = getopt.getopt(argv, "hn:l:e:a:p:w:d:q:o:r:v:i:")
    except getopt.GetoptError:
        print 'Simulation.py -n <network csv> -l <level csv> -e <econ csv> -a <assignment policy> ' \
                  '-p <priority policy> -w <weeks> -d <surge delay> -q <output csv> -o <output weekly queue> -r <probability distribution>' \
                  '-v <variance> -i <range window>'
        sys.exit(2)

    # Initialize simpy environment
    env = simpy.Environment()
    # Build Network
    # This will be done via the CSV later
    for opt, arg in opts:
        if opt == '-h':
            print 'Simulation.py -n <network csv> -l <level csv> -e <econ csv> -a <assignment policy> ' \
                  '-p <priority policy> -w <weeks> -d <surge delay> -q <output csv> -o <output weekly queue> -r <probability distribution>' \
                  '-v <variance> -i <range window>'
            print '-a: Uniform, Deterministic Wait, Deterministic Service\n'
            print '-p: FIFO, Centre, Refugee, Balance'
            print '-r: Constant, Uniform, Normal, Exponential'
            return
        elif opt == '-n':
            network_path = arg
        elif opt == '-l':
            level_path = arg
        elif opt == '-e':
            econ_path = arg
        elif opt == '-a':
            asn_policy = arg
        elif opt == '-p':
            prio_policy = arg
        elif opt == '-q':
            output_queue_wait_path = arg
        elif opt == '-o':
            output_weekly_queue_path = arg
        elif opt == '-w':
            weeks = int(arg)
        elif opt == '-d':
            delay = int(arg)
        elif opt == '-r':
            pr_dist = arg
        elif opt == '-v':
            variance = int(arg)
        elif opt == '-i':
            range_window = int(arg)

        if delay == -1:
            delay = weeks

    # Build network
    network = Network(env, network_path)
    network.set_level_arrival(level_path)
    network.asn_policy = asn_policy

    # Set Class Time distribution
    Member.pr_dist = pr_dist
    Member.variance = variance
    Member.range_window = range_window

    # Set priority policy
    QueueNode.priority_policy = prio_policy

    Network.service_rate = SERVICE_RATE
    QueueNode.service_rate = SERVICE_RATE

    # Set up the Member proportions
    Member.set_priority_class(econ_path)
    # Set Member csvs
    Member.queue_csv = output_queue_wait_path
    Member.begin_csv()

    network.queue_weekly_csv = output_weekly_queue_path
    network.initialize_queue_csv()

    # Run simulation for 104+ weeks -> ~ 2 years
    env.process(network.arrival())
    env.process(network.refugee_surge(delay))
    env.process(network.print_network_queues())
    env.run(until=weeks)

    Member.end_csv()
    network.close_queue_csv()

if __name__ == "__main__":
    main(sys.argv[1:])






