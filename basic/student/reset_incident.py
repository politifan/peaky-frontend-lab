"""Restore broken lesson HTML from immutable student fixture, after explicit CLI choice."""
from pathlib import Path
import argparse,shutil
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('task',choices=['05-01-a','05-01-b','05-02-a','05-02-b','05-03-a','05-03-b','05-04-a','05-04-b','05-05-a','05-05-b'])
parser.add_argument('--restore',action='store_true',required=True)
args=parser.parse_args()
target=(ROOT/'tasks'/args.task/'index.html').resolve();source=ROOT/'incidents'/args.task/'broken.html'
assert target.is_relative_to(ROOT/'tasks')
backup=target.with_suffix('.before-reset.html')
shutil.copy2(target,backup);shutil.copy2(source,target)
print({'restored':str(target),'backup':str(backup)})
