import csv


class QueueDataCSV:

    def __init__(self, path):
        self.path = path
        self.csv_file = None
        self.fieldnames = \
            ["MemberID", "ArrivedInQueue", "ExpectedWait", "ExpectedService", "WaitInQueue", "ArrivedInClass",
             "TimeInClass", "LeftClass", "TotalService", "Level", "ImmigrantClass"]
        self.writer = None
        self.start()

    def start(self):
        self.csv_file = open(self.path, 'wb')
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write(self, member_id, arrived_queue, exp_wait, exp_service, waited, arrived_class, class_time, left_class, service_total, level, imm_class):
        self.writer.writerow({"MemberID": member_id, "ArrivedInQueue": arrived_queue, "ExpectedWait": exp_wait, "ExpectedService": exp_service, "WaitInQueue": waited,
                              "ArrivedInClass":arrived_class, "TimeInClass": class_time, "LeftClass": left_class,
                              "TotalService": service_total, "Level": level, "ImmigrantClass": imm_class})

    def close(self):
        self.csv_file.close()


class QueueWeeklyCSV:
    def __init__(self, path, fieldnames):
        self.path = path
        self.csv_file = None
        self.fieldnames = []
        self.writer = None
        self.start(fieldnames)

    def start(self, fieldnames):
        self.fieldnames = fieldnames
        self.csv_file = open(self.path, 'wb')
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write(self, queue, week):  # Pass in queue array
        queue_dict = {"week": week}
        for f in self.fieldnames:
            if f != "week":
                index = self.fieldnames.index(f) - 1
                queue_dict[f] = queue[index]
        self.writer.writerow(queue_dict)

    def close(self):
        self.csv_file.close()
