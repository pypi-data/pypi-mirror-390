import enum

class HeadMovingDirections(enum.Enum):
    N = 'N'
    R = 'R'
    L = 'L'

    @classmethod
    def from_char(cls, input: str):
        try:
             return cls(input.upper())
        except ValueError:
            return None


class MultiTapeTuringMachine:
    def __init__(self, number_of_tapes: int, number_of_states: int, alphabet: list[str], tape_alphabet: list[str], start_state: str, end_state: str, transitions: list['Transition']):
        self.number_of_tapes = number_of_tapes
        self.states: list[str] = [str(i) for i in range(1, number_of_states + 1)]
        self.alphabet = alphabet
        self.tape_alphabet = tape_alphabet
        self.end_state = end_state
        self.transitions = {transition.get_key(): transition for transition in transitions}
        
        self.tapes = [Tape() for _ in range(number_of_tapes)]
        self.start_state = start_state
        self.state = start_state
        self.is_halted = False

    def input(self, inputs: list[str]) -> None:
        if len(inputs) > self.number_of_tapes:
            raise ValueError("More inputs provided than number of tapes.")
        for i, tape_input in enumerate(inputs):
            self.tapes[i].init_tape(tape_input)
    
    def step(self) -> list[HeadMovingDirections] | None:
        if self.state == self.end_state:
            self.is_halted = True
            return None
        tape_symbols = [tape.get_head_value() for tape in self.tapes]
        transition = self.transitions.get(self.state + "".join(tape_symbols))
        if transition is None:
            raise ValueError(f"No transition found for state '{self.state}' and tape symbols '{tape_symbols}'")
        
        if not len(transition.new_tape_symbols) == self.number_of_tapes :
            raise Exception(f"Transition for state '{self.state}' and tape symbols '{tape_symbols}' does not provide the correct number of new tape symbols ({len(transition.new_tape_symbols)} given, expected {self.number_of_tapes}).")


        for tape, new_symbol, direction in zip(self.tapes, transition.new_tape_symbols, transition.directions):
            tape.set_head_value(new_symbol)
            tape.move_head(direction)

        self.state = transition.new_state
        return transition.directions
    
    def run(self) -> None:
        while not self.is_halted:
            print(self.current_tape_str())
            self.step()

    def clear(self, rest_taps: bool = True) -> None:
        self.state = self.start_state
        self.is_halted = False
        if rest_taps:
            for tape in self.tapes:
                tape.clear()

    def current_tape_str(self) -> str:
        return "".join(
            f'Tape {i}: ...B{"".join(left)}[{self.state}]{head}{"".join(right)}B...'
            for i, tape in enumerate(self.tapes)
            for left, head, right in [tape.get_tape_representation()]
        )

"""
Input: M = (Q, Σ, Γ, B, q0, ¯q, δ), 
"""
class TuringMachine(MultiTapeTuringMachine): 
    def __init__(self, number_of_states: int, alphabet: list[str], tape_alphabet: list[str], start_state: str, end_state: str, transitions: list['Transition']):
        super().__init__(
            number_of_tapes=1,
            number_of_states=number_of_states,
            alphabet=alphabet,
            tape_alphabet=tape_alphabet,
            start_state=start_state,
            end_state=end_state,
            transitions=transitions
        )


    def current_tape_str(self) -> str:
        return "".join(
            f'...B{"".join(left)}[{self.state}]{head}{"".join(right)}B...'
            for tape in self.tapes
            for left, head, right in [tape.get_tape_representation()]
        )

"""
δ : (q, a)  → (q′, b, D) 
δ(q₀, (a, □)) = (q₀, (a, a), (R, R))
q, a, q′, b, D
1 0 1 1 R

"""
class Transition:
    def __init__(self, current_state: str, current_tape_symbols: list[str], new_state: str, new_tape_symbols: list[str], directions: list[HeadMovingDirections]) -> None:
        self.current_state = current_state
        self.current_tape_symbols = current_tape_symbols
        self.new_state = new_state
        self.new_tape_symbols = new_tape_symbols
        self.directions = directions
    
    @classmethod
    def from_input_str(cls, input: str) -> 'Transition':
        inputs = input.split()
        directions: list[HeadMovingDirections] = []

        for direction_char in inputs[4].split(','):
            direction = HeadMovingDirections.from_char(direction_char)

            if direction is None:
                 raise ValueError(f"Invalid direction character: '{direction_char}'. Must be one of R, L, N.")
            
            directions.append(direction)

        current_tape_symbols = inputs[1].split(',')
        new_tape_symbols = inputs[3].split(',')

        if not (len(current_tape_symbols) == len(new_tape_symbols) == len(directions)):
            raise ValueError(
                f"Length mismatch: current_tape_symbols ({len(current_tape_symbols)}), "
                f"new_tape_symbols ({len(new_tape_symbols)}), directions ({len(directions)}). "
                "All must have the same length."
            )

        return cls(inputs[0], inputs[1].split(','), inputs[2], inputs[3].split(','), directions)
    
    def get_key(self) -> str:
        return self.current_state + "".join(self.current_tape_symbols)



class Tape:
    def __init__(self) -> None:
        self.tape_to_left: list[str] = []
        self.tape_to_right: list[str] = []

    def clear(self) -> None:
        self.tape_to_left = []
        self.tape_to_right = []

    def init_tape(self, input: str) -> None:
        self.tape_to_right = list(reversed(list(input)))

    def move_head(self, direction: HeadMovingDirections) -> None:
        match direction:
            case HeadMovingDirections.N:
                pass
            case HeadMovingDirections.R:
                self._move_head_right()
            case HeadMovingDirections.L:
                self._move_head_left()

    def get_head_value(self) -> str:
        if self.tape_to_right:
            return self.tape_to_right[-1]
        else:
            return self.blank()
    
    def set_head_value(self, new_head_value: str) -> None:
        if self.tape_to_right:
            self.tape_to_right[-1] = new_head_value
        else:
            self.tape_to_right.append(new_head_value)
    
    def _move_head_right(self) -> None: 
        if self.tape_to_right:
            self.tape_to_left.append(self.tape_to_right.pop())
        else:
            self.tape_to_left.append(self.blank())

    def _move_head_left(self) -> None:
        if self.tape_to_left:
            self.tape_to_right.append(self.tape_to_left.pop())
        else:
            self.tape_to_right.append(self.blank())

    def get_tape_representation(self) -> tuple[list[str], str, list[str]]:
        if not self.tape_to_right:
            head_char = self.blank()
            right_list = []
        else:
            head_char = self.tape_to_right[-1]
            right_list = self.tape_to_right[:-1]
            right_list.reverse()
        return self.tape_to_left, head_char, right_list

    @staticmethod
    def blank() -> str:
        return 'B'

    def __str__(self) -> str:
        left, head, right = self.get_tape_representation()
        return f'...B{"".join(left)}[{head}]{"".join(right)}B...'
    