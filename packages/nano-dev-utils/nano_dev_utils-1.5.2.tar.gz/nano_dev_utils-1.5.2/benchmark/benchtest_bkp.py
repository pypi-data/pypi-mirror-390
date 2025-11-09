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
        # sort_key_name='natural'
        skip_sorting=True,
    )
    # ftd.style_dict['plus2'] = ftd.connector_styler('+--- ', '\\--- ')
    # ftd.style = 'plus2'
    # ftd.printout = True  # ensure it works both with file saving - done
    return ftd.file_tree_display()


@timer.timeit(iterations=ITER, timeout=10, per_iteration=True)
def win_tree_cmd():
    # filename = 'wintree_w_files.txt'
    filename = 'wintree_ws.txt'
    filepath = str(Path(target_path, filename))
    tree_wrapper(root_path=root, show_files=True, save2file=True, filepath=filepath)


def run():
    ftd_run()
    # win_tree_cmd()


if __name__ == '__main__':
    run()
