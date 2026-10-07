"""Launch the maze visualizer from the project root with ``python main.py``."""

import tkinter as tk

from Gui.Buttons import MazeVisualizer


def main() -> None:
    root = tk.Tk()
    MazeVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()