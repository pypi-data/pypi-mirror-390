from mrjob.job import MRJob
from datetime import datetime
import json

class LogAnalysis(MRJob):

    def mapper(self, _, line):
        parts = line.strip().split()
        if len(parts) == 3:
            user, timestamp, action = parts
            yield user, json.dumps((timestamp, action))

    def reducer(self, user, values):
        events = []
        for v in values:
            timestamp, action = json.loads(v)  
            events.append((timestamp, action))

        total = 0
        login_time = None

        for timestamp, action in sorted(events):
            try:
                t = datetime.fromisoformat(timestamp)
            except ValueError:
                continue  

            if action == "login":
                login_time = t
            elif action == "logout" and login_time:
                total += (t - login_time).total_seconds()
                login_time = None

        yield user, round(total / 3600, 2)  

if __name__ == "__main__":
    LogAnalysis.run()