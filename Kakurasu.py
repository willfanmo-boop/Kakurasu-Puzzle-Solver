import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import time
import threading

class KakurasuCSP:
    def __init__(self, size, row_targets, col_targets):
        self.size = size
        self.row_targets = row_targets
        self.col_targets = col_targets
        self.grid = [[-1] * size for _ in range(size)]
        self.nodes_visited = 0
        self.domains = {(r, c): {0, 1} for r in range(size) for c in range(size)}

    # Calculate the sum of the current row
    def row_sum(self, row):
        sum = 0 
        for i in range(self.size):
            if self.grid[row][i] == 1:
                sum += (i + 1)
        return sum

    # Calculate the sum of the current column
    def col_sum(self, col):
        sum = 0
        for i in range(self.size):
            if self.grid[i][col] == 1:
                sum += (i + 1)
        return sum

    # Check if the current grid is valid
    def is_valid(self):
        for row in range(self.size):
            if self.row_sum(row) > self.row_targets[row]:
                return False
        for col in range(self.size):
            if self.col_sum(col) > self.col_targets[col]:
                return False
        return True
    
    # check if the current grid is actually equal to the target
    def sum_check(self):
        for row in range(self.size):
            if self.row_sum(row) != self.row_targets[row]:
                return False
        for col in range(self.size):
            if self.col_sum(col) != self.col_targets[col]:
                return False
        return True

    def backtrack_helper(self, row, col):
        self.nodes_visited += 1
        # calculate the value of the next cell 
        if row == self.size:
            return self.sum_check()
        next_col = col + 1
        next_row = row
        if next_col == self.size:
            next_col = 0
            next_row = row + 1
        # if the current cell is 0, change it to 1
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
            # check whether the current cell is valid
            if self.is_valid():
                # if valid, move to the next possible cell
                if self.backtrack_helper(next_row, next_col):
                    return True
            
            # if invalid, change the state back to 0
            self.grid[row][col] = 0
            if self.backtrack_helper(next_row, next_col):
                return True
        return False


    def get_mrv_variable(self):
        unassigned = [(r, c) for r, c in self.domains if self.grid[r][c] == -1]
        if not unassigned:
            return None
        return min(unassigned, key=lambda x: len(self.domains[x]))

    def _enforce_sum_constraint(self, typ, index):
        changed = False
        target = self.row_targets[index] if typ == "row" else self.col_targets[index]

        current_fixed_sum = 0
        potential_extra_sum = 0
        unassigned_cells = []

        for k in range(self.size):
            r, c = (index, k) if typ == "row" else (k, index)
            weight = k + 1

            if self.grid[r][c] == 1:
                current_fixed_sum += weight
            elif self.grid[r][c] == -1:
                if 1 in self.domains[(r, c)]:
                    potential_extra_sum += weight
                unassigned_cells.append((r, c, weight))

        if current_fixed_sum > target:
            return None
        if current_fixed_sum + potential_extra_sum < target:
            return None

        for r, c, w in unassigned_cells:
            if 1 in self.domains[(r, c)] and (current_fixed_sum + w > target):
                self.domains[(r, c)].remove(1)
                changed = True

            if 0 in self.domains[(r, c)] and (current_fixed_sum + potential_extra_sum - (w if 1 in self.domains[(r,c)] else 0) < target):
                if 0 in self.domains[(r, c)]:
                    self.domains[(r, c)].remove(0)
                    changed = True

            if not self.domains[(r, c)]:
                return None

        return changed

    def apply_ac3_propagation(self):
        changed = True
        while changed:
            changed = False
            for i in range(self.size):
                res = self._enforce_sum_constraint("row", i)
                if res is None:
                    return False
                if res:
                    changed = True

                res = self._enforce_sum_constraint("col", i)
                if res is None:
                    return False
                if res:
                    changed = True

        return True

    def solve_with_ac3(self):
        self.nodes_visited = 0
        self.grid = [[-1] * self.size for _ in range(self.size)]
        self.domains = {(r, c): {0, 1} for r in range(self.size) for c in range(self.size)}
        if not self.apply_ac3_propagation():
            return False
        return self.ac3_backtrack_helper()

    def get_mrv_variable(self):
        unassigned = [(r, c) for (r, c) in self.domains if self.grid[r][c] == -1]
        if not unassigned:
            return None
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def order_values_lcv(self, var):
        r, c = var
        value_scores = []

        for value in self.domains[var]:
            score = 0
            for i in range(self.size):
                if i != c and self.grid[r][i] == -1:
                    if value == 1:
                        score += 1
                if i != r and self.grid[i][c] == -1:
                    if value == 1:
                        score += 1

            value_scores.append((value, score))

        value_scores.sort(key=lambda x: x[1])
        return [v for v, s in value_scores]

    def ac3_backtrack_helper(self):
        self.nodes_visited += 1

        var = self.get_mrv_variable()   # MRV
        if var is None:
            return self.sum_check()

        r, c = var
        original_domains = {k: v.copy() for k, v in self.domains.items()}
        original_value = self.grid[r][c]

        for value in self.order_values_lcv(var):   # LCV
            self.grid[r][c] = value
            self.domains[var] = {value}

            if self.apply_ac3_propagation():
                if self.ac3_backtrack_helper():
                    return True

            # restore state
            self.grid[r][c] = original_value
            self.domains = {k: v.copy() for k, v in original_domains.items()}

        return False

    def solve_with_backtracking(self):
        self.grid = [[0] * self.size for _ in range(self.size)]
        return self.backtrack_helper(0, 0)

class KakurasuGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kakurasu Puzzle")
        self.root.geometry("500x500")
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side="top", fill="x", pady=10)
        # Load button
        self.open_button = tk.Button(self.controls_frame, text="Open", command=self.open_file)
        self.open_button.pack(side="left", padx=10)
        self.combo_box = ttk.Combobox(self.controls_frame, values=["Backtracking", "AC3"])
        self.combo_box.pack(side="left", padx=10)
        # Solve button
        self.solve_button = tk.Button(self.controls_frame, text="Solve", command=self.solve_file)
        self.solve_button.pack(side="left", padx=10)
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(side="top", pady=20, expand=True)
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(side="bottom", fill="x", pady=20)
        
        self.status_label = tk.Label(self.info_frame, text="Status: Ready", font=("Arial", 14))
        self.status_label.pack(side="top", pady=5)
        
        self.stats_label = tk.Label(self.info_frame, text="Runtime: 0.0s | Nodes: 0")
        self.stats_label.pack(side="top")

        self.root.mainloop()
        
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as f:
                size, row_targets, col_targets = f.readlines()
                size = int(size)
                row_targets = [int(x) for x in row_targets.split(",")]
                col_targets = [int(x) for x in col_targets.split(",")] 

                self.solver_instance = KakurasuCSP(size, row_targets, col_targets)
                self.draw_grid(size, row_targets, col_targets)                 
    
    # Puzzle Display
    def draw_grid(self, size, row_targets, col_targets):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        self.buttons = [[None for _ in range(size)] for _ in range(size)]
        
        for i in range(size):
            for j in range(size):
                cell = tk.Label(self.grid_frame, width=4, height=2, bg="white", relief="raised", font=("Arial", 16, "bold"))
                cell.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[i][j] = cell

        for i in range(size):
            lbl = tk.Label(self.grid_frame, text=str(row_targets[i]), font=("Arial", 12, "bold"))
            lbl.grid(row=i, column=size, padx=10)

        for j in range(size):
            lbl = tk.Label(self.grid_frame, text=str(col_targets[j]), font=("Arial", 12, "bold"))
            lbl.grid(row=size, column=j, pady=10)

        self.status_label.config(text="Status: Loaded")
        self.stats_label.config(text="Runtime: 0.0s | Nodes: 0")


    def solve_file(self):
        if not hasattr(self, 'solver_instance'):
            self.status_label.config(text="Status: Please Open a file first!")
            return

        self.status_label.config(text="Status: Solving...")
        threading.Thread(target=self.run_solver, daemon=True).start()

    def run_solver(self):
        start_time = time.time()
        solved = False
        
        self.solver_instance.nodes_visited = 0

        algorithm = self.combo_box.get()
        if algorithm == "Backtracking":
            solved = self.solver_instance.solve_with_backtracking()
        elif algorithm == "AC3":
            solved = self.solver_instance.solve_with_ac3()
        
        end_time = time.time()
        runtime = round(end_time - start_time, 4)
        nodes = self.solver_instance.nodes_visited

        self.root.after(0, lambda: self.update_gui_after_solve(solved, runtime, nodes))

    def update_gui_after_solve(self, solved, runtime, nodes):
        size = self.solver_instance.size
        for i in range(size):
            for j in range(size):
                if self.solver_instance.grid[i][j] == 1:
                    self.buttons[i][j].config(bg="black", text="")
                else:
                    self.buttons[i][j].config(bg="white", text="")

        self.stats_label.config(text=f"Runtime: {runtime}s | Nodes: {nodes}")
        if solved:
            self.status_label.config(text="Status: Solved")
        else:
            self.status_label.config(text="Status: No solution found")

if __name__ == "__main__":
    GUI = KakurasuGUI()


    



    