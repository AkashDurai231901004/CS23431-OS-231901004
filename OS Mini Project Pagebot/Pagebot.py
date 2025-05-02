import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Simulator")
        self.root.geometry("1000x550")
        self.root.configure(bg="#e8f0fe")

        self.index = 0
        self.reference = []
        self.frames = 0
        self.algorithm = "FIFO"
        self.state = None
        self.auto_mode = False
        self.paused = False

        self.setup_gui()

    def setup_gui(self):
        input_frame = tk.Frame(self.root, bg="#e8f0fe")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Reference String (comma separated):", bg="#e8f0fe").grid(row=0, column=0)
        self.ref_entry = tk.Entry(input_frame, width=50)
        self.ref_entry.grid(row=0, column=1, padx=10)

        tk.Label(input_frame, text="Frames:", bg="#e8f0fe").grid(row=1, column=0)
        self.frames_spin = tk.Spinbox(input_frame, from_=1, to=10, width=5)
        self.frames_spin.grid(row=1, column=1, sticky="w")

        tk.Label(input_frame, text="Algorithm:", bg="#e8f0fe").grid(row=2, column=0)
        self.algo_combo = ttk.Combobox(input_frame, values=["FIFO", "LRU", "Optimal"], state="readonly")
        self.algo_combo.current(0)
        self.algo_combo.grid(row=2, column=1, sticky="w")

        control_frame = tk.Frame(self.root, bg="#e8f0fe")
        control_frame.pack(pady=10)

        tk.Button(control_frame, text="Start Simulation", command=self.start_simulation,
                  bg="#1E88E5", fg="white", width=15).grid(row=0, column=0, padx=10)

        self.manual_btn = tk.Button(control_frame, text="Manual Next", command=self.next_page,
                                    bg="#43A047", fg="white", width=15, state="disabled")
        self.manual_btn.grid(row=0, column=1, padx=10)

        self.auto_btn = tk.Button(control_frame, text="Auto Play", command=self.auto_next,
                                  bg="#fb8c00", fg="white", width=15, state="disabled")
        self.auto_btn.grid(row=0, column=2, padx=10)

        self.pause_btn = tk.Button(control_frame, text="Pause", command=self.toggle_pause,
                                   bg="#6d4c41", fg="white", width=15, state="disabled")
        self.pause_btn.grid(row=0, column=3, padx=10)

        tk.Button(control_frame, text="Reset", command=self.reset,
                  bg="#E53935", fg="white", width=15).grid(row=0, column=4, padx=10)

        self.output_text = tk.Text(self.root, width=80, height=20, font=("Courier New", 10),
                                   bg="#ffffff", relief=tk.SUNKEN, bd=2)
        self.output_text.pack(side=tk.LEFT, padx=10, pady=10)

        self.stack_canvas = tk.Canvas(self.root, width=200, height=400, bg="#f1f8e9", bd=2, relief=tk.SUNKEN)
        self.stack_canvas.pack(side=tk.RIGHT, padx=10)

    def start_simulation(self):
        try:
            self.reference = list(map(int, self.ref_entry.get().strip().split(',')))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid comma-separated reference string.")
            return

        self.frames = int(self.frames_spin.get())
        self.algorithm = self.algo_combo.get()
        self.index = 0
        self.output_text.delete("1.0", tk.END)

        self.state = {
            "frames": [],
            "queue": [],
            "recent": [],
            "faults": 0,
            "hits": 0,
        }

        self.manual_btn.config(state="normal")
        self.auto_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.paused = False

    def auto_next(self):
        self.auto_mode = True
        self.manual_btn.config(state="disabled")
        self.auto_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.auto_step()

    def auto_step(self):
        if self.index >= len(self.reference):
            self.show_best_algorithm()
            return

        if self.paused:
            self.root.after(200, self.auto_step)
            return

        self.next_page()
        self.root.after(1000, self.auto_step)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")

    def next_page(self):
        if self.index >= len(self.reference):
            self.output_text.insert(tk.END, "\n--- Simulation Complete ---\n")
            self.output_text.insert(tk.END, f"Total Page Faults: {self.state['faults']}\n")
            self.output_text.insert(tk.END, f"Total Page Hits:   {self.state['hits']}\n")
            self.show_best_algorithm()
            return

        page = self.reference[self.index]
        frames = self.state["frames"]

        if self.algorithm == "FIFO":
            queue = self.state["queue"]
            if page not in frames:
                if len(frames) < self.frames:
                    frames.append(page)
                else:
                    removed = queue.pop(0)
                    frames.remove(removed)
                    frames.append(page)
                queue.append(page)
                self.state["faults"] += 1
                self.output_text.insert(tk.END, f"Page {page}: {frames}  ❌ Miss\n")
            else:
                self.state["hits"] += 1
                self.output_text.insert(tk.END, f"Page {page}: {frames}  ✅ Hit\n")

        elif self.algorithm == "LRU":
            recent = self.state["recent"]
            if page in frames:
                recent.remove(page)
                self.state["hits"] += 1
                self.output_text.insert(tk.END, f"Page {page}: {frames}  ✅ Hit\n")
            else:
                if len(frames) < self.frames:
                    frames.append(page)
                else:
                    lru = recent.pop(0)
                    frames.remove(lru)
                    frames.append(page)
                self.state["faults"] += 1
                self.output_text.insert(tk.END, f"Page {page}: {frames}  ❌ Miss\n")
            recent.append(page)

        elif self.algorithm == "Optimal":
            future = self.reference[self.index + 1:]
            if page not in frames:
                if len(frames) < self.frames:
                    frames.append(page)
                else:
                    indexes = []
                    for f in frames:
                        if f in future:
                            indexes.append(future.index(f))
                        else:
                            indexes.append(float("inf"))
                    to_replace = frames[indexes.index(max(indexes))]
                    frames.remove(to_replace)
                    frames.append(page)
                self.state["faults"] += 1
                self.output_text.insert(tk.END, f"Page {page}: {frames}  ❌ Miss\n")
            else:
                self.state["hits"] += 1
                self.output_text.insert(tk.END, f"Page {page}: {frames}  ✅ Hit\n")

        self.update_stack_visualization(page)
        self.index += 1

    def update_stack_visualization(self, current_page):
        self.stack_canvas.delete("all")
        pages = self.state["frames"]

        canvas_height = 400
        box_height = 50
        spacing = 10
        bottom = canvas_height - spacing

        for i, page in enumerate(pages):
            y2 = bottom - i * (box_height + spacing)
            y1 = y2 - box_height

            rect = self.stack_canvas.create_rectangle(50, y1, 150, y2, fill="#bbdefb", outline="black", width=2)
            text = self.stack_canvas.create_text(100, (y1 + y2) / 2, text=str(page), font=("Arial", 14))

            # Animate only the latest page
            if page == current_page and i == len(pages) - 1:
                for offset in range(10):
                    self.stack_canvas.move(rect, 0, -1)
                    self.stack_canvas.move(text, 0, -1)
                    self.stack_canvas.update()
                    self.stack_canvas.after(80)

    def reset(self):
        self.ref_entry.delete(0, tk.END)
        self.output_text.delete("1.0", tk.END)
        self.manual_btn.config(state="disabled")
        self.auto_btn.config(state="disabled")
        self.pause_btn.config(state="disabled", text="Pause")
        self.stack_canvas.delete("all")
        self.index = 0
        self.reference = []
        self.state = None
        self.auto_mode = False
        self.paused = False

    def show_best_algorithm(self):
        results = {}
        for algo in ["FIFO", "LRU", "Optimal"]:
            faults = self.simulate_algo(algo)
            results[algo] = faults

        best_algo = min(results, key=results.get)
        values = list(results.values())

        messagebox.showinfo("Best Algorithm", f"The best algorithm is {best_algo} with {results[best_algo]} faults.")

        plt.figure(figsize=(6, 4))
        plt.bar(results.keys(), values, color=["#42a5f5", "#66bb6a", "#ffa726"])
        plt.ylabel("Page Faults")
        plt.title("Page Faults Comparison")
        plt.tight_layout()
        plt.show()

    def simulate_algo(self, algo):
        frames = []
        queue = []
        recent = []
        faults = 0
        for i, page in enumerate(self.reference):
            if algo == "FIFO":
                if page not in frames:
                    if len(frames) < self.frames:
                        frames.append(page)
                    else:
                        removed = queue.pop(0)
                        frames.remove(removed)
                        frames.append(page)
                    queue.append(page)
                    faults += 1
            elif algo == "LRU":
                if page in frames:
                    recent.remove(page)
                else:
                    if len(frames) < self.frames:
                        frames.append(page)
                    else:
                        lru = recent.pop(0)
                        frames.remove(lru)
                        frames.append(page)
                    faults += 1
                recent.append(page)
            elif algo == "Optimal":
                future = self.reference[i + 1:]
                if page not in frames:
                    if len(frames) < self.frames:
                        frames.append(page)
                    else:
                        indexes = []
                        for f in frames:
                            if f in future:
                                indexes.append(future.index(f))
                            else:
                                indexes.append(float("inf"))
                        to_replace = frames[indexes.index(max(indexes))]
                        frames.remove(to_replace)
                        frames.append(page)
                    faults += 1
        return faults

if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()
