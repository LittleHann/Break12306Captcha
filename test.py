import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--debug', action='store_true', help='debug mode')

args = parser.parse_args()

print args.debug
