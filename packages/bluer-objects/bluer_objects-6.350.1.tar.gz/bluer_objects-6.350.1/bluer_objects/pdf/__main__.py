import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_objects import NAME
from bluer_objects.pdf.convert.functions import convert
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="convert",
)
parser.add_argument(
    "--docs_path",
    type=str,
)
parser.add_argument(
    "--module_name",
    type=str,
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--suffixes",
    type=str,
)
parser.add_argument(
    "--combine",
    type=int,
    default=0,
    help="0 | 1",
)
args = parser.parse_args()

success = False
if args.task == "convert":
    success = convert(
        docs_path=args.docs_path,
        module_name=args.module_name,
        list_of_suffixes=args.suffixes.split(","),
        object_name=args.object_name,
        combine=args.combine == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
