import os
import logging

from pathlib import Path
from nano_dev_utils.file_tree_display import FileTreeDisplay
from nano_dev_utils import timer

from win_tree_wrapper import tree_wrapper


logging.basicConfig(
    filename='Benchmark_FTD.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)

ITER = 1
ONE_MB = 1_048_576


root = r'c:/yd'
# root = r"c:/HugeFolder"
# root = r'c:/workspaces'
# root = 'c:/githubws/graph_walk'

target_path = r'YourTargetPath'

timer.update({'precision': 3})


@timer.timeit(iterations=ITER, timeout=5, per_iteration=True)
def ftd_run():

    # filename = 'nano_filetree_.txt'
    filename = 'ftd_ws_.txt'
    filepath = str(Path(target_path, filename))

    ftd = FileTreeDisplay(
        root_dir=root,
        filepath=filepath,
        indent=2,
        files_first=True,  # default for 'Tree /F'
    )

    return ftd.file_tree_display()


@timer.timeit(iterations=ITER, timeout=10, per_iteration=True)
def win_tree_cmd():
    filename = 'wintree_ws.txt'
    filepath = str(Path(target_path, filename))
    tree_wrapper(root_path=root, show_files=True, save2file=True, filepath=filepath)


def run():
    # timer.printout = True
    # print_stats(root_path=Path(root))
    ftd_run()
    # win_tree_cmd()


@timer.timeit()
def print_stats(root_path: Path) -> None:
    """Compute and print directory statistics."""
    file_count = 0
    dir_count = 0
    total_size = 0
    max_depth = 0

    for dirpath, dirs, files in os.walk(root_path):
        dir_count += len(dirs)
        file_count += len(files)
        dpath = Path(dirpath)
        for f in files:
            try:
                total_size += (dpath / f).stat().st_size
            except OSError:
                continue
        rel_depth = len(dpath.relative_to(root_path).parts)
        max_depth = max(max_depth, rel_depth)

    print(f"\nStats for '{root_path}':")
    print(f"  Folders:     {dir_count}")
    print(f"  Files:       {file_count}")
    print(f"  Max Depth:   {max_depth}")
    print(f"  Total Size:  {total_size / ONE_MB:.2f} MB\n\n")


if __name__ == '__main__':
    run()
