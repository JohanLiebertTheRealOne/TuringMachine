import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class TuringMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, blank_symbol,
                 transitions, start_state, accept_states, reject_states):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.blank_symbol = blank_symbol
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.reject_states = set(reject_states)
        self.reset()

    def reset(self, input_string=""):
        self.tape = list(input_string) if input_string else []
        self.head = 0
        self.current_state = self.start_state
        self.history = []  # store (state, tape, head)

    def step(self):
        symbol = self.tape[self.head] if 0 <= self.head < len(self.tape) else self.blank_symbol
        key = (self.current_state, symbol)
        if key not in self.transitions:
            return False
        new_state, write_symbol, direction = self.transitions[key]
        # save history
        self.history.append((self.current_state, ''.join(self.tape), self.head))
        # write
        if 0 <= self.head < len(self.tape):
            self.tape[self.head] = write_symbol
        else:
            if self.head < 0:
                self.tape.insert(0, write_symbol)
                self.head = 0
            else:
                self.tape.append(write_symbol)
        # move
        self.head += 1 if direction == 'R' else -1
        self.current_state = new_state
        return True

    def run(self, max_steps=100000, callback=None, delay=0.1):
        steps = 0
        while steps < max_steps:
            if self.current_state in self.accept_states or self.current_state in self.reject_states:
                break
            cont = self.step()
            if not cont:
                break
            steps += 1
            if callback:
                callback()
                threading.Event().wait(delay)
        return self.current_state in self.accept_states

    def load_from_json(self, path):
        with open(path) as f:
            data = json.load(f)
        self.__init__(**data)

    def save_to_json(self, path):
        data = {
            'states': list(self.states),
            'input_alphabet': list(self.input_alphabet),
            'tape_alphabet': list(self.tape_alphabet),
            'blank_symbol': self.blank_symbol,
            'transitions': {str(k): v for k, v in self.transitions.items()},
            'start_state': self.start_state,
            'accept_states': list(self.accept_states),
            'reject_states': list(self.reject_states)
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

class TMGUIApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Turing Machine Simulator")
        self.geometry("800x600")
        self.create_widgets()
        # default simple incrementer
        self.load_default_tm()

    def create_widgets(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top, text="Input String:").pack(side=tk.LEFT)
        self.input_entry = tk.Entry(top)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(top, text="Reset & Load", command=self.on_reset).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Step", command=self.on_step).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Run", command=self.on_run).pack(side=tk.LEFT, padx=2)
        self.speed_scale = tk.Scale(top, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, label="Delay(s)")
        self.speed_scale.set(0.1)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
        mid = tk.Frame(self)
        mid.pack(fill=tk.BOTH, expand=True)
        self.tape_canvas = tk.Canvas(mid, height=100, bg='white')
        self.tape_canvas.pack(fill=tk.X, pady=10)
        info = tk.Frame(mid)
        info.pack(fill=tk.X)
        self.state_var = tk.StringVar()
        tk.Label(info, textvariable=self.state_var).pack(side=tk.LEFT, padx=5)
        
        bottom = tk.Frame(self)
        bottom.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(bottom, text="Transitions (state,symbol)->state,write,dir (L/R):").pack(anchor=tk.W)
        self.trans_text = scrolledtext.ScrolledText(bottom, height=10)
        self.trans_text.pack(fill=tk.BOTH, expand=True)
        btns = tk.Frame(bottom)
        btns.pack(fill=tk.X)
        tk.Button(btns, text="Load JSON", command=self.on_load_json).pack(side=tk.LEFT)
        tk.Button(btns, text="Save JSON", command=self.on_save_json).pack(side=tk.LEFT, padx=5)

    def load_default_tm(self):
        data = {
            'states': ["q0","q1","q_accept"],
            'input_alphabet': ["0","1"],
            'tape_alphabet': ["0","1","_"],
            'blank_symbol':"_",
            'transitions':{('q0','0'):('q0','0','R'),('q0','1'):('q0','1','R'),('q0','_'):('q1','_','L'),
                         ('q1','0'):('q_accept','1','R'),('q1','1'):('q1','0','L'),('q1','_'):('q_accept','1','R')},
            'start_state':"q0",
            'accept_states': ["q_accept"],
            'reject_states': []
        }
        self.tm = TuringMachine(**data)
        self.update_transitions_text()

    def update_transitions_text(self):
        self.trans_text.delete('1.0', tk.END)
        for (s,sym), (ns,ws,d) in self.tm.transitions.items():
            self.trans_text.insert(tk.END, f"{s},{sym}->{ns},{ws},{d}\n")

    def parse_transitions(self):
        trans = {}
        for line in self.trans_text.get('1.0', tk.END).splitlines():
            if not line.strip(): continue
            lhs, rhs = line.split('->')
            s, sym = lhs.split(',')
            ns, ws, d = rhs.split(',')
            trans[(s.strip(), sym.strip())] = (ns.strip(), ws.strip(), d.strip())
        return trans

    def draw_tape(self):
        self.tape_canvas.delete('all')
        tape = self.tm.tape or [self.tm.blank_symbol]
        start = max(0, self.tm.head - 10)
        end = self.tm.head + 10
        for i, sym in enumerate(tape[start:end+1]):
            x = 30 + (i * 30)
            self.tape_canvas.create_rectangle(x, 20, x+30, 50)
            self.tape_canvas.create_text(x+15, 35, text=sym)
        # head indicator
        hx = 30 + ((self.tm.head - start) * 30)
        self.tape_canvas.create_polygon(hx, 55, hx+15, 70, hx+30, 55)
        self.state_var.set(f"State: {self.tm.current_state}")

    def on_reset(self):
        inp = self.input_entry.get().strip()
        self.tm.transitions = self.parse_transitions()
        self.tm.reset(inp)
        self.draw_tape()

    def on_step(self):
        if not self.tm.step():
            messagebox.showinfo("Halt", "No more transitions or reached halt state.")
        self.draw_tape()

    def on_run(self):
        delay = self.speed_scale.get()
        def runner():
            accepted = self.tm.run(callback=lambda: self.draw_tape(), delay=delay)
            messagebox.showinfo("Result", f"Accepted? {accepted}")
        threading.Thread(target=runner, daemon=True).start()

    def on_load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if path:
            try:
                self.tm.load_from_json(path)
                self.update_transitions_text()
                messagebox.showinfo("Loaded", "Configuration loaded.")
            except Exception as e:
                messagebox.showerror("Error","Failed to load: " + str(e))

    def on_save_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            try:
                # update transitions
                self.tm.transitions = self.parse_transitions()
                self.tm.save_to_json(path)
                messagebox.showinfo("Saved", "Configuration saved.")
            except Exception as e:
                messagebox.showerror("Error","Failed to save: " + str(e))

if __name__ == "__main__":
    app = TMGUIApplication()
    app.mainloop()