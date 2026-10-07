"""Launch the maze search visualizer with ``python -m Gui``."""

import tkinter as tk

from .Buttons import MazeVisualizer


def main() -> None:
    root = tk.Tk()
    MazeVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
