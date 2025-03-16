
global_time = 0


def get_global_time():
    """
    Returns an incremented global time used to stamp sends and receives.
    """
    global global_time
    global_time += 1
    return global_time


class Message:
    def __init__(self, sender_id, vector_clock, event_number,
                 send_time, receipt_time=None):
        """
        :param sender_id: ID of the sending process.
        :param vector_clock: Snapshot of the sender's vector clock at send time.
        :param event_number: The local event number = vector_clock[sender_id] - 1.
        :param send_time: A "physical/logical" time at which the message was sent.
        :param receipt_time: A "physical/logical" time at which the message was received.
        """
        self.sender_id = sender_id
        self.vector_clock = vector_clock.copy()
        self.event_number = event_number
        self.send_time = send_time
        self.receipt_time = receipt_time

    def __repr__(self):
        return (f"Message(from P{self.sender_id}, "
                f"VC={self.vector_clock}, "
                f"event={self.event_number}, "
                f"send_time={self.send_time}, "
                f"receipt_time={self.receipt_time})")


class Process:
    def __init__(self, process_id, total_processes):
        self.id = process_id
        self.total_processes = total_processes
        # Initialize the vector clock for each process to 0.
        self.vector_clock = [0] * total_processes
        # Queue for delayed (undeliverable) messages.
        self.delayed_messages = []

    def increment_event(self):
        """
        Process Pi generates an event:
          1. Increment its own component of the vector clock.
          2. Create a message (where event_number = VT_pi[i] - 1).
          3. Stamp the message with a send_time and broadcast it.
        """
        self.vector_clock[self.id] += 1
        event_number = self.vector_clock[self.id] - 1
        # Mark the time at which we are sending this message.
        send_time = get_global_time()

        message = Message(self.id, self.vector_clock, event_number, send_time)
        print(f"\nProcess {self.id} generated {message}")
        self.broadcast_message(message)

    def broadcast_message(self, message):
        """
        Broadcast the message to all other processes.
        Each receiving process gets a copy of the message with a receipt_time.
        """
        for proc in all_processes:
            if proc.id != self.id:
                # Mark the time at which the message arrives at the receiver.
                receipt_time = get_global_time()
                # Copy the original message, but update the receipt_time.
                msg_copy = Message(message.sender_id,
                                   message.vector_clock,
                                   message.event_number,
                                   message.send_time,
                                   receipt_time)
                proc.receive_message(msg_copy)

    def receive_message(self, message):
        """
        When a message is received:
          1. Check if it is immediately deliverable based on BSS conditions.
          2. If not deliverable, buffer it.
          3. Keep the buffer sorted by (send_time, receipt_time), so that
             messages sent earlier come first, even if they arrive later.
        """
        print(f"Process {self.id} received {message}")

        if self.can_deliver(message):
            self.deliver_message(message)
            # Re-check the delayed queue: delivering one message may enable others.
            self.check_delayed_queue()
        else:
            print(f"Process {self.id} cannot deliver {message} yet. Buffering it.")
            self.delayed_messages.append(message)
            # Sort by (send_time, receipt_time) to respect the earliest-sent message first.
            self.delayed_messages.sort(key=lambda m: (m.send_time, m.receipt_time))

    def can_deliver(self, message):
        """
        A message from Pi is deliverable at Pj if:
          a) VTpj[i] == VTm[i] - 1
          b) For all k != i, VTpj[k] >= VTm[k]
        This is the BSS condition.
        """
        sender = message.sender_id
        # Condition (a)
        if self.vector_clock[sender] != message.vector_clock[sender] - 1:
            return False
        # Condition (b)
        for k in range(self.total_processes):
            if k != sender and self.vector_clock[k] < message.vector_clock[k]:
                return False
        return True

    def deliver_message(self, message):
        """
        Deliver a message:
          - Update the receiver's vector clock to the element-wise max
            of its current clock and the message's clock.
        """
        print(f"Process {self.id} delivering {message}")
        for k in range(self.total_processes):
            self.vector_clock[k] = max(self.vector_clock[k], message.vector_clock[k])
        print(f"Process {self.id} updated vector clock: {self.vector_clock}")

    def check_delayed_queue(self):
        """
        Re-check buffered messages to see if any have become deliverable
        after delivering a prior message.
        """
        delivered_any = True
        while delivered_any:
            delivered_any = False
            # Iterate over a copy, so we can remove from the original.
            for msg in self.delayed_messages[:]:
                if self.can_deliver(msg):
                    self.delayed_messages.remove(msg)
                    self.deliver_message(msg)
                    delivered_any = True
                    # After delivering one message, start over to catch new deliverable ones.
                    break
                else:
                    # Print a separator to visualize re-check attempts if you like
                    print("-------------------------------------------------")


# --- Simulation Setup ---

def simulate_bss():
    global all_processes, global_time
    global_time = 0  # Reset the global time counter.
    no_of_processes = 3
    # Create a list of process objects.
    global all_processes
    all_processes = [Process(i, no_of_processes) for i in range(no_of_processes)]

    # Example scenario:
    print("\n--- Process 1 generates an event ---")
    all_processes[1].increment_event()  # Suppose this is e11 in your figure.

    print("\n--- Process 0 generates an event ---")
    all_processes[0].increment_event()  # e01

    print("\n--- Process 1 generates another event ---")
    all_processes[1].increment_event()  # e12

    print("\n--- Process 2 generates an event ---")
    all_processes[2].increment_event()  # e21


if __name__ == "__main__":
    simulate_bss()
