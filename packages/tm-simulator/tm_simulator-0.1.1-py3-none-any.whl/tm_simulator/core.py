import os
import typing
import warnings
from .tm import Tape, Transition, TuringMachine as TM, MultiTapeTuringMachine as MTTM

def run_tm(file_path: str, tm_input: str) -> None:
    turing_machine_input = tm_input.split(',')
    turing_machine = load_tm(file_path)

    turing_machine.input(turing_machine_input)

    turing_machine.run()

def load_tm(file_path: str) -> typing.Union[MTTM, TM]:
    
    if not file_path.endswith(('.TM', '.MTTM')):
        raise ValueError('The provided file is not a .TM or .MTTM file.')
    
    file_lines = read_file(file_path)

    if not file_lines:
        raise ValueError('Could not read file or file is empty.')

    if len(file_lines) < 5:
        raise ValueError('File is not in the correct format, please check your file again.')
    
    file_lines.reverse()

    tapes = 1

    if file_path.endswith('.MTTM'):
        tapes = int(file_lines.pop())

    states = int(file_lines.pop())
    alphabet = list(file_lines.pop())
    tape_alphabet = list(file_lines.pop())

    if not Tape.blank() in tape_alphabet:
        warnings.warn('The tape alpahabet does not contain the blank symbole', UserWarning)

    start_state = file_lines.pop()
    end_state = file_lines.pop()

    if not file_lines:
        raise ValueError('The TM does not have any transtions.')

    try:
        transitions = [Transition.from_input_str(s) for s in file_lines]
    except ValueError as e:
        raise ValueError(f"Error parsing transitions: {e}")

    if tapes > 1:
        turing_machine = MTTM(tapes, states, alphabet, tape_alphabet, start_state, end_state, transitions) 
    else:
        turing_machine = TM(states, alphabet, tape_alphabet, start_state, end_state, transitions)

    return turing_machine


def read_file(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' couldn't be found.")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        return lines
    except Exception as e:
        raise IOError(f'An error occurred by ready the file: {e}') from e