global_time = 0


def get_global_time():
    global global_time
    global_time += 1
    return global_time


class Message:
    def __init__(self, sender_id, receiver_id, vector_clock, event_number, send_time, receipt_time=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.vector_clock = vector_clock.copy()
        self.event_number = event_number
        self.send_time = send_time
        self.receipt_time = receipt_time

    def __repr__(self):
        return (f"Message(from P{self.sender_id} to P{self.receiver_id}, "
                f"VC={self.vector_clock}, event={self.event_number}, "
                f"send_time={self.send_time}, receipt_time={self.receipt_time})")


class Process:
    def __init__(self, process_id, total_processes):
        self.id = process_id
        self.total_processes = total_processes
        self.vector_clock = [0] * total_processes

    def increment_event(self):
        self.vector_clock[self.id] += 1
        event_number = self.vector_clock[self.id] - 1
        send_time = get_global_time()
        print(f"\nProcess {self.id} generated event {event_number}, VC: {self.vector_clock}")

    def send_message(self, receiver):
        send_time = get_global_time()
        event_number = self.vector_clock[self.id] - 1

        message = Message(self.id, receiver.id, self.vector_clock, event_number, send_time)
        print(f"Process {self.id} sending {message}")
        receiver.receive_message(message)

    def receive_message(self, message):
        self.vector_clock[self.id] += 1  # Clock increment on receiving
        self.vector_clock = [max(self.vector_clock[i], message.vector_clock[i]) for i in range(self.total_processes)]
        print(f"Process {self.id} received {message} and updated VC: {self.vector_clock}")


# --- Simulation Setup ---
def simulate_ses():
    global global_time
    global_time = 0
    no_of_processes = 3
    all_processes = [Process(i, no_of_processes) for i in range(no_of_processes)]

    print("\n--- P1 generates an event ---")
    all_processes[1].increment_event()

    print("\n--- P0 generates an event ---")
    all_processes[0].increment_event()

    print("\n--- P1 sends a message to P2 ---")
    all_processes[1].send_message(all_processes[2])

    print("\n--- P2 generates an event ---")
    all_processes[2].increment_event()

    print("\n--- P2 sends a message to P0 ---")
    all_processes[2].send_message(all_processes[0])


if __name__ == "__main__":
    simulate_ses()
