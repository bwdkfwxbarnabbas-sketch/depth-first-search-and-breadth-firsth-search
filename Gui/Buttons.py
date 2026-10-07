"""Tkinter interface for stepping through the maze search algorithms."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any


_DEFAULT_LAYOUT = (
    "..........",
    "####.###.#",
    "..........",
    ".#######..",
    "..........",
    "########.#",
    "..........",
    ".#######.#",
    "..........",
    "########..",
)


class MazeVisualizer:
    DEFAULT_ROWS = 10
    DEFAULT_COLUMNS = 10
    LAYOUT = _DEFAULT_LAYOUT
    DEFAULT_WALKABLE = {
        (row, column)
        for row, line in enumerate(_DEFAULT_LAYOUT)
        for column, cell in enumerate(line)
        if cell == "."
    }
    DIRECTIONS = (
        (-1, 0),  # up
        (0, 1),   # right
        (1, 0),   # down
        (0, -1),  # left
    )
    CELL_SIZE = 34
    GRID_LEFT = 18
    GRID_TOP = 18
    MIN_SIZE = 2
    MAX_SIZE = 40

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Maze Search Visualizer")
        self.root.minsize(1000, 720)
        self.root.configure(bg="#f8fafc")

        self.rows = self.DEFAULT_ROWS
        self.columns = self.DEFAULT_COLUMNS
        self.START = (0, 0)
        self.GOAL = (self.rows - 1, self.columns - 1)
        self.open_cells = set(self.DEFAULT_WALKABLE)
        self.algorithm = tk.StringVar(value="Depth-first search (DFS)")
        self.status = tk.StringVar()
        self.step_text = tk.StringVar()
        self.rows_input = tk.StringVar(value=str(self.rows))
        self.columns_input = tk.StringVar(value=str(self.columns))
        self.speed = tk.IntVar(value=450)
        self.history: list[dict[str, Any]] = []
        self.history_index = 0
        self.after_id: str | None = None
        self.drag_open: bool | None = None
        self.last_drag_cell: tuple[int, int] | None = None

        self._build_ui()
        self._reset_search()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)

        heading = ttk.Frame(outer)
        heading.pack(fill="x", pady=(0, 14))
        ttk.Label(
            heading, text="Maze Search", font=("Segoe UI", 21, "bold")
        ).pack(anchor="w")
        ttk.Label(
            heading,
            text="Watch depth-first and breadth-first search explore the same maze.",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=(0, 12))
        ttk.Label(controls, text="Rows").pack(side="left", padx=(0, 4))
        ttk.Spinbox(
            controls,
            from_=self.MIN_SIZE,
            to=self.MAX_SIZE,
            textvariable=self.rows_input,
            width=4,
        ).pack(side="left", padx=(0, 8))
        ttk.Label(controls, text="Columns").pack(side="left", padx=(0, 4))
        ttk.Spinbox(
            controls,
            from_=self.MIN_SIZE,
            to=self.MAX_SIZE,
            textvariable=self.columns_input,
            width=4,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(controls, text="Apply size", command=self._apply_size).pack(
            side="left", padx=(0, 12)
        )

        ttk.Label(controls, text="Algorithm").pack(side="left", padx=(0, 7))
        choice = ttk.Combobox(
            controls,
            textvariable=self.algorithm,
            values=("Depth-first search (DFS)", "Breadth-first search (BFS)"),
            state="readonly",
            width=30,
        )
        choice.pack(side="left", padx=(0, 12))
        choice.bind("<<ComboboxSelected>>", lambda _event: self._reset_search())

        self.play_button = ttk.Button(
            controls, text="▶ Play", command=self._toggle_play
        )
        self.play_button.pack(side="left", padx=3)
        ttk.Button(controls, text="Step", command=self._step).pack(
            side="left", padx=3
        )
        ttk.Button(controls, text="Reset", command=self._reset_search).pack(
            side="left", padx=3
        )
        ttk.Button(controls, text="Clear walls", command=self._clear_walls).pack(
            side="left", padx=3
        )

        ttk.Label(controls, text="Speed").pack(side="left", padx=(16, 5))
        ttk.Scale(
            controls,
            from_=1000,
            to=100,
            variable=self.speed,
            orient="horizontal",
            length=115,
        ).pack(side="left")

        content = ttk.Frame(outer)
        content.pack(fill="both", expand=True)

        grid_panel = ttk.Frame(content)
        grid_panel.pack(side="left", fill="both", expand=True)
        grid_panel.rowconfigure(0, weight=1)
        grid_panel.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            grid_panel,
            width=700,
            height=550,
            bg="#e2e8f0",
            highlightthickness=0,
        )
        vertical_scrollbar = ttk.Scrollbar(
            grid_panel, orient="vertical", command=self.canvas.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            grid_panel, orient="horizontal", command=self.canvas.xview
        )
        self.canvas.configure(
            xscrollcommand=horizontal_scrollbar.set,
            yscrollcommand=vertical_scrollbar.set,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.bind("<Button-1>", self._on_grid_click)
        self.canvas.bind("<B1-Motion>", self._on_grid_drag)
        self.canvas.bind("<ButtonRelease-1>", self._finish_grid_drag)

        side = ttk.Frame(content, width=250, padding=(18, 0, 0, 0))
        side.pack(side="right", fill="y")
        side.pack_propagate(False)
        ttk.Label(side, text="Search state", font=("Segoe UI", 12, "bold")).pack(
            anchor="w"
        )
        ttk.Label(side, textvariable=self.status, wraplength=220).pack(
            anchor="w", pady=(6, 10)
        )
        ttk.Label(side, textvariable=self.step_text).pack(anchor="w", pady=(0, 12))

        ttk.Label(side, text="Frontier (waiting)", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )
        self.frontier_list = tk.Listbox(
            side, height=8, font=("Consolas", 10), relief="flat",
            bg="#f1f5f9", activestyle="none",
        )
        self.frontier_list.pack(fill="x", pady=(4, 12))
        ttk.Label(side, text="Explored", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )
        self.explored_list = tk.Listbox(
            side, height=8, font=("Consolas", 10), relief="flat",
            bg="#f1f5f9", activestyle="none",
        )
        self.explored_list.pack(fill="both", expand=True, pady=(4, 10))

        ttk.Label(
            outer,
            text=(
                "Click or drag across tiles to paint/erase walls. "
                "Start and goal are fixed at opposite corners. "
                f"Grid size: {self.MIN_SIZE}–{self.MAX_SIZE} rows/columns."
            ),
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(10, 0))

    def _apply_size(self) -> None:
        try:
            rows = int(self.rows_input.get())
            columns = int(self.columns_input.get())
        except ValueError:
            self.status.set("Enter whole numbers for the row and column counts.")
            return

        if not (
            self.MIN_SIZE <= rows <= self.MAX_SIZE
            and self.MIN_SIZE <= columns <= self.MAX_SIZE
        ):
            self.status.set(
                f"Choose row and column counts from "
                f"{self.MIN_SIZE} to {self.MAX_SIZE}."
            )
            return

        if rows == self.rows and columns == self.columns:
            self._reset_search()
            return

        self._pause()
        self.rows = rows
        self.columns = columns
        self.START = (0, 0)
        self.GOAL = (rows - 1, columns - 1)
        self.open_cells = {
            (row, column)
            for row in range(rows)
            for column in range(columns)
        }
        self._reset_search()

    def _clear_walls(self) -> None:
        self.open_cells = {
            (row, column)
            for row in range(self.rows)
            for column in range(self.columns)
        }
        self._reset_search()

    def _make_history(self) -> list[dict[str, Any]]:
        is_dfs = self.algorithm.get().startswith("Depth-first")
        frontier = [self.START]
        explored: list[tuple[int, int]] = []
        parents: dict[tuple[int, int], tuple[int, int] | None] = {
            self.START: None
        }
        history = [
            {
                "frontier": frontier.copy(),
                "explored": explored.copy(),
                "parents": parents.copy(),
                "current": None,
                "path": [],
                "done": False,
                "message": (
                    f"Ready on a {self.rows}×{self.columns} maze. "
                    "The start is waiting in the frontier."
                ),
            }
        ]

        while frontier:
            current = frontier.pop() if is_dfs else frontier.pop(0)
            explored.append(current)
            found = current == self.GOAL

            if not found:
                for row_delta, column_delta in self.DIRECTIONS:
                    neighbor = (current[0] + row_delta, current[1] + column_delta)
                    if (
                        0 <= neighbor[0] < self.rows
                        and 0 <= neighbor[1] < self.columns
                        and neighbor in self.open_cells
                        and neighbor not in parents
                    ):
                        parents[neighbor] = current
                        frontier.append(neighbor)

            path: list[tuple[int, int]] = []
            if found:
                position: tuple[int, int] | None = self.GOAL
                while position is not None:
                    path.append(position)
                    position = parents[position]
                path.reverse()

            done = found or not frontier
            if found:
                message = "Goal found!"
            elif done:
                message = "No route to the goal."
            else:
                message = f"Explored tile {current}."
            history.append(
                {
                    "frontier": frontier.copy(),
                    "explored": explored.copy(),
                    "parents": parents.copy(),
                    "current": current,
                    "path": path,
                    "done": done,
                    "message": message,
                }
            )
            if done:
                break

        if len(history) == 1:
            history[0]["done"] = True
            history[0]["message"] = "No route to the goal."
        return history

    def _reset_search(self) -> None:
        self._pause()
        if self.START not in self.open_cells or self.GOAL not in self.open_cells:
            self.open_cells.update((self.START, self.GOAL))
        self.history = self._make_history()
        self.history_index = 0
        self._render()

    def _step(self) -> None:
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._render()
        if self.history[self.history_index]["done"]:
            self._pause()

    def _toggle_play(self) -> None:
        if self.after_id is not None:
            self._pause()
        elif not self.history[self.history_index]["done"]:
            self.play_button.configure(text="⏸ Pause")
            self._schedule_step()

    def _schedule_step(self) -> None:
        if self.after_id is None:
            delay = max(50, int(self.speed.get()))
            self.after_id = self.root.after(delay, self._play_step)

    def _play_step(self) -> None:
        self.after_id = None
        self._step()
        if self.after_id is not None:
            return
        if not self.history[self.history_index]["done"]:
            self._schedule_step()

    def _pause(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if hasattr(self, "play_button"):
            self.play_button.configure(text="▶ Play")

    def _on_grid_click(self, event: tk.Event) -> None:
        self.drag_open = None
        self.last_drag_cell = None
        cell = self._cell_at(event)
        if cell is None or cell in (self.START, self.GOAL):
            return
        self.drag_open = cell not in self.open_cells
        self._paint_cell(cell)

    def _on_grid_drag(self, event: tk.Event) -> None:
        if self.drag_open is None:
            return
        cell = self._cell_at(event)
        if cell is not None:
            self._paint_cell(cell)

    def _finish_grid_drag(self, _event: tk.Event) -> None:
        self.drag_open = None
        self.last_drag_cell = None

    def _cell_at(self, event: tk.Event) -> tuple[int, int] | None:
        x = self.canvas.canvasx(event.x) - self.GRID_LEFT
        y = self.canvas.canvasy(event.y) - self.GRID_TOP
        column = int(x // self.CELL_SIZE)
        row = int(y // self.CELL_SIZE)
        if 0 <= row < self.rows and 0 <= column < self.columns:
            return row, column
        return None

    def _paint_cell(self, cell: tuple[int, int]) -> None:
        if cell in (self.START, self.GOAL) or cell == self.last_drag_cell:
            return
        self.last_drag_cell = cell
        if self.drag_open:
            if cell in self.open_cells:
                return
            self.open_cells.add(cell)
        else:
            if cell not in self.open_cells:
                return
            self.open_cells.discard(cell)
        self._reset_search()

    def _render(self) -> None:
        snapshot = self.history[self.history_index]
        self.canvas.delete("all")
        explored = set(snapshot["explored"])
        frontier = set(snapshot["frontier"])
        current = snapshot["current"]
        path = set(snapshot["path"])

        for row in range(self.rows):
            for column in range(self.columns):
                cell = (row, column)
                x1 = self.GRID_LEFT + column * self.CELL_SIZE
                y1 = self.GRID_TOP + row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE - 2
                y2 = y1 + self.CELL_SIZE - 2
                if cell not in self.open_cells:
                    fill = "#1e293b"
                elif cell == current:
                    fill = "#fb923c"
                elif cell in path:
                    fill = "#60a5fa"
                elif cell in explored:
                    fill = "#a7f3d0"
                elif cell in frontier:
                    fill = "#fde68a"
                else:
                    fill = "#ffffff"
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill, outline="#cbd5e1", width=1
                )
                label = "S" if cell == self.START else "G" if cell == self.GOAL else ""
                if label:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=label,
                        fill="#0f172a",
                        font=("Segoe UI", 18, "bold"),
                    )

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                self.GRID_LEFT * 2 + self.columns * self.CELL_SIZE,
                self.GRID_TOP * 2 + self.rows * self.CELL_SIZE,
            )
        )
        self.status.set(snapshot["message"])
        self.step_text.set(
            f"Step {self.history_index} of {len(self.history) - 1}   "
            f"Moves in path: {max(0, len(snapshot['path']) - 1)}"
        )
        self.frontier_list.delete(0, tk.END)
        next_cell = (
            snapshot["frontier"][-1]
            if self.algorithm.get().startswith("Depth-first")
            else snapshot["frontier"][0] if snapshot["frontier"] else None
        )
        for cell in snapshot["frontier"]:
            marker = "  ← next" if cell == next_cell else ""
            self.frontier_list.insert(tk.END, f"{cell}{marker}")

        self.explored_list.delete(0, tk.END)
        for cell in snapshot["explored"]:
            self.explored_list.insert(tk.END, str(cell))
        if snapshot["explored"]:
            self.explored_list.see(tk.END)

        if snapshot["done"]:
            self._pause()
