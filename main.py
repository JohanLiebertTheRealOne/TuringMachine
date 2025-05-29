class TuringMachine:
    """
    A simple theoretical Turing Machine implementation.
    \n    Attributes:
        states: A set of states.
        input_alphabet: Symbols allowed in the input.
        tape_alphabet: Symbols allowed on the tape (includes blank symbol).
        blank_symbol: Symbol representing a blank cell on the tape.
        transitions: A dict mapping (state, symbol) -> (new_state, write_symbol, direction).
        start_state: The initial state.
        accept_states: A set of accepting states.
        reject_states: A set of rejecting states.
    """
    
    def __init__(self, states, input_alphabet, tape_alphabet, blank_symbol,
                 transitions, start_state, accept_states, reject_states):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.blank_symbol = blank_symbol
        self.transitions = transitions  # {(state, symbol): (new_state, write_symbol, direction)}
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.reject_states = set(reject_states)

        # Initialize tape and head
        self.reset()

    def reset(self, input_string=""):
        # Initialize tape from input string
        self.tape = list(input_string) if input_string else []
        self.head = 0
        self.current_state = self.start_state

    def step(self):
        symbol = self.tape[self.head] if 0 <= self.head < len(self.tape) else self.blank_symbol
        key = (self.current_state, symbol)
        if key not in self.transitions:
            # No transition: halt
            return False
        new_state, write_symbol, direction = self.transitions[key]

        # Write symbol
        if 0 <= self.head < len(self.tape):
            self.tape[self.head] = write_symbol
        else:
            # Extend tape if head out of bounds
            if self.head < 0:
                self.tape.insert(0, write_symbol)
                self.head = 0
            else:
                self.tape.append(write_symbol)

        # Move head
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        else:
            raise ValueError(f"Invalid direction: {direction}")

        # Update state
        self.current_state = new_state
        return True

    def run(self, input_string, max_steps=10000):
        """
        Runs the machine on the given input string.
        Returns True if accepted, False if rejected or no transition.
        """
        self.reset(input_string)
        steps = 0
        while steps < max_steps:
            if self.current_state in self.accept_states:
                return True
            if self.current_state in self.reject_states:
                return False
            if not self.step():
                # Halt without accept or reject
                return False
            steps += 1
        raise RuntimeError("Exceeded maximum number of steps")

    def get_tape(self):
        return ''.join(self.tape).strip(self.blank_symbol)

    def __str__(self):
        tape_str = ''.join(self.tape)
        return f"State: {self.current_state}, Head: {self.head}, Tape: {tape_str}"  

# Example usage:
if __name__ == "__main__":
    # Define a simple binary incrementer TM
    states = {"q0", "q1", "q_accept"}
    input_alphabet = {"0", "1"}
    tape_alphabet = {"0", "1", "_"}
    blank = "_"
    transitions = {
        ("q0", "0"): ("q0", "0", 'R'),
        ("q0", "1"): ("q0", "1", 'R'),
        ("q0", "_"): ("q1", "_", 'L'),
        ("q1", "0"): ("q_accept", "1", 'R'),
        ("q1", "1"): ("q1", "0", 'L'),
        ("q1", "_"): ("q_accept", "1", 'R')
    }
    start = "q0"
    accept = {"q_accept"}
    reject = set()

    tm = TuringMachine(states, input_alphabet, tape_alphabet, blank,
                       transitions, start, accept, reject)
    input_str = "1011"  # 11 in binary
    result = tm.run(input_str)
    print(f"Accepted: {result}")
    print(f"Resulting tape: {tm.get_tape()}")
    