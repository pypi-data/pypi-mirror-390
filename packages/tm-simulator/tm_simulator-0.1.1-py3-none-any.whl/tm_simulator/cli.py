import sys
import logging
from .core import run_tm

def main() -> int:

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


    args = sys.argv
    args_len = len(args)
    if args_len != 3:
        logging.error('Usage: python %s <path_to_file.TM|MTTM> <TM_input>', args[0])
        logging.error('Please provide exactly one file path as an argument')
        return 1
    
    run_tm(args[1], args[2])

    return 0