import ast
import csv
import math
import tkinter as tk
from tkinter import filedialog, ttk, messagebox


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command,
        width=78,
        height=48,
        color="#414141",
        active_color="#555555",
        foreground="#f2f2f2",
        font=("Segoe UI", 11, "bold"),
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
        )
        self.command = command
        self.color = color
        self.active_color = active_color
        self.foreground = foreground
        radius = min(10, (height - 4) / 2, (width - 4) / 2)
        self.shape = self.create_polygon(
            2 + radius, 2,
            width - 2 - radius, 2,
            width - 2, 2,
            width - 2, 2 + radius,
            width - 2, height - 2 - radius,
            width - 2, height - 2,
            width - 2 - radius, height - 2,
            2 + radius, height - 2,
            2, height - 2,
            2, height - 2 - radius,
            2, 2 + radius,
            2, 2,
            fill=color,
            outline=color,
            smooth=True,
            splinesteps=12,
        )
        self.label = self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=foreground,
            font=font,
        )
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._leave)

    def set_text(self, text):
        self.itemconfigure(self.label, text=text)

    def _click(self, _event):
        self.command()

    def _hover(self, _event):
        self.itemconfigure(self.shape, fill=self.active_color, outline=self.active_color)

    def _leave(self, _event):
        self.itemconfigure(self.shape, fill=self.color, outline=self.color)


class SmartCalculator:
    BG = "#292929"
    PANEL = "#333333"
    BUTTON = "#454545"
    BUTTON_HOVER = "#5b5b5b"
    ACCENT = "#f28b62"
    TEXT = "#f5f5f5"
    MUTED = "#b8b8b8"
    ENTRY_BG = "#3b3b3b"

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Calculator")
        self.root.geometry("400x700")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.active_tab = "Basic"
        self.angle_mode = "DEG"
        self.pages = {}
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground=self.ENTRY_BG,
            background=self.BUTTON,
            foreground=self.TEXT,
            arrowcolor=self.TEXT,
            bordercolor=self.ENTRY_BG,
            lightcolor=self.ENTRY_BG,
            darkcolor=self.ENTRY_BG,
            padding=6,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", self.ENTRY_BG)],
            foreground=[("readonly", self.TEXT)],
            selectbackground=[("readonly", self.ENTRY_BG)],
            selectforeground=[("readonly", self.TEXT)],
        )

    def _label(self, parent, text, size=10, color=None, bold=False, **kwargs):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color or self.TEXT,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            **kwargs,
        )

    def _round_button(self, parent, text, command, **kwargs):
        kwargs.setdefault("color", self.BUTTON)
        kwargs.setdefault("active_color", self.BUTTON_HOVER)
        return RoundedButton(parent, text, command, **kwargs)

    def _build(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=16, pady=(10, 4))
        self._label(header, "Smart Calculator", 17, bold=True).pack(anchor="w")
        self._label(
            header, "EVERYDAY MATH, MADE EASY", 8, self.MUTED
        ).pack(anchor="w", pady=(1, 0))

        nav = tk.Frame(self.root, bg=self.BG)
        nav.pack(fill="x", padx=10, pady=(4, 6))
        names = ("Basic", "Scientific", "Convert", "Graph", "BMI", "GST")
        for index, name in enumerate(names):
            button = self._round_button(
                nav,
                name,
                lambda tab=name: self._show_tab(tab),
                width=119,
                height=30,
                font=("Segoe UI", 9, "bold"),
            )
            button.grid(row=index // 3, column=index % 3, padx=4, pady=3)
            nav.grid_columnconfigure(index % 3, weight=1)

        self.content = tk.Frame(self.root, bg=self.BG)
        self.content.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.pages = {
            "Basic": tk.Frame(self.content, bg=self.BG),
            "Scientific": tk.Frame(self.content, bg=self.BG),
            "Convert": tk.Frame(self.content, bg=self.BG),
            "Graph": tk.Frame(self.content, bg=self.BG),
            "BMI": tk.Frame(self.content, bg=self.BG),
            "GST": tk.Frame(self.content, bg=self.BG),
        }
        self.angle_button = None
        self.angle_caption = None
        self._build_calculator(self.pages["Basic"], scientific=False)
        self._build_calculator(self.pages["Scientific"], scientific=True)
        self._build_converter(self.pages["Convert"])
        self._build_graph(self.pages["Graph"])
        self._build_bmi(self.pages["BMI"])
        self._build_gst(self.pages["GST"])
        self._show_tab("Basic")

    def _show_tab(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.active_tab = name
        self.pages[name].pack(fill="both", expand=True)

    def _build_calculator(self, parent, scientific):
        display = tk.Frame(
            parent, bg=self.PANEL, padx=12, pady=9, highlightthickness=1,
            highlightbackground="#484848",
        )
        display.pack(fill="x", pady=(1, 8))
        mode = "Scientific" if scientific else "Basic"
        self._label(display, mode, 9, self.MUTED).pack(anchor="w")
        tk.Entry(
            display,
            textvariable=self.expression,
            justify="right",
            bg=self.PANEL,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            font=("Segoe UI", 20),
        ).pack(fill="x", ipady=3)
        tk.Label(
            display,
            textvariable=self.result,
            anchor="e",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 11),
        ).pack(fill="x")

        if scientific:
            keys = [
                ["sin", "cos", "tan", "log", "ln"],
                ["sqrt", "x²", "1/x", "pi", "e"],
                ["(", ")", "^", "%", "÷"],
                ["7", "8", "9", "×", "−"],
                ["4", "5", "6", "+", "="],
                ["1", "2", "3", "AC", "⌫"],
                ["±", "0", ".", "!", "DEG"],
            ]
            columns = 5
            button_height = 48
            button_width = 48
        else:
            keys = [
                ["AC", "⌫", "%", "÷"],
                ["7", "8", "9", "×"],
                ["4", "5", "6", "−"],
                ["1", "2", "3", "+"],
                ["±", "0", ".", "="],
            ]
            columns = 4
            button_height = 60
            button_width = 60

        pad = tk.Frame(parent, bg=self.BG)
        pad.pack(fill="x", expand=True)
        for column in range(columns):
            pad.grid_columnconfigure(column, weight=1)
        for row, values in enumerate(keys):
            for column, key in enumerate(values):
                button_color = self.ACCENT if key == "=" else self.BUTTON
                hover_color = "#f5a17f" if key == "=" else self.BUTTON_HOVER
                button = self._round_button(
                    pad,
                    key,
                    lambda value=key: self._press(value),
                    width=button_width,
                    height=button_height,
                    color=button_color,
                    active_color=hover_color,
                    foreground="#282828" if key == "=" else self.TEXT,
                    font=("Segoe UI", 10, "bold"),
                )
                button.grid(row=row, column=column, padx=2, pady=2)
                if scientific and key == "DEG":
                    self.angle_button = button
        if scientific:
            self.angle_caption = self._label(
                parent, "DEG mode  •  trig functions use degrees", 8, self.MUTED
            )
            self.angle_caption.pack(anchor="w", pady=(4, 0))

    def _press(self, key):
        current = self.expression.get()
        if key == "AC":
            self.expression.set("")
            self.result.set("0")
        elif key == "⌫":
            self.expression.set(current[:-1])
        elif key == "=":
            self._evaluate()
        elif key == "DEG":
            self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
            self.angle_button.set_text(self.angle_mode)
            self.angle_caption.configure(
                text=f"{self.angle_mode} mode  •  trig functions use {self.angle_mode.lower()}"
            )
        elif key == "±":
            if current:
                self.expression.set(f"-({current})")
            else:
                self.expression.set("-")
        elif key in ("sin", "cos", "tan", "log", "ln", "sqrt"):
            self.expression.set(f"{key}({current})" if current else f"{key}(")
        elif key == "x²":
            self.expression.set(f"({current})**2" if current else "")
        elif key == "1/x":
            self.expression.set(f"1/({current})" if current else "1/(")
        elif key == "pi":
            self.expression.set(current + "pi")
        elif key == "!":
            self.expression.set(f"factorial({current})" if current else "factorial(")
        elif key in ("e", "(", ")", ".", "%"):
            self.expression.set(current + {"%": "/100"}.get(key, key))
        elif key == "^":
            self.expression.set(current + "**")
        elif key in ("÷", "×", "−"):
            self.expression.set(current + {"÷": "/", "×": "*", "−": "-"}.get(key))
        else:
            self.expression.set(current + key)

    def _evaluate(self):
        source = self.expression.get().strip()
        if not source:
            return
        functions = {
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "sin": lambda value: math.sin(math.radians(value))
            if self.angle_mode == "DEG" else math.sin(value),
            "cos": lambda value: math.cos(math.radians(value))
            if self.angle_mode == "DEG" else math.cos(value),
            "tan": lambda value: math.tan(math.radians(value))
            if self.angle_mode == "DEG" else math.tan(value),
            "abs": abs,
            "factorial": math.factorial,
        }
        try:
            value = self._safe_eval(source, functions)
            if not math.isfinite(float(value)):
                raise ValueError("Result is not a finite number.")
            shown = f"{value:.12g}" if isinstance(value, float) else str(value)
            self.result.set(f"= {shown}")
            self.expression.set(shown)
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
            messagebox.showerror("Calculation error", str(error), parent=self.root)

    def _safe_eval(self, source, functions):
        tree = ast.parse(source, mode="eval")

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.Name):
                if node.id == "pi":
                    return math.pi
                if node.id == "e":
                    return math.e
                raise ValueError(f"Unknown value: {node.id}")
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                operand = evaluate(node.operand)
                return operand if isinstance(node.op, ast.UAdd) else -operand
            if isinstance(node, ast.BinOp):
                left, right = evaluate(node.left), evaluate(node.right)
                operations = {
                    ast.Add: lambda: left + right,
                    ast.Sub: lambda: left - right,
                    ast.Mult: lambda: left * right,
                    ast.Div: lambda: left / right,
                    ast.FloorDiv: lambda: left // right,
                    ast.Mod: lambda: left % right,
                    ast.Pow: lambda: left ** right,
                }
                for operation, action in operations.items():
                    if isinstance(node.op, operation):
                        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                            raise ValueError("Exponent is too large.")
                        return action()
                raise ValueError("Unsupported operation.")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                function = functions.get(node.func.id)
                if function is None or node.keywords:
                    raise ValueError("Unsupported function.")
                return function(*(evaluate(argument) for argument in node.args))
            raise ValueError("Invalid expression.")

        return evaluate(tree)

    def _entry(self, parent, variable=None, value="", width=18):
        field = tk.Entry(
            parent,
            textvariable=variable,
            bg=self.ENTRY_BG,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            font=("Segoe UI", 12),
            width=width,
        )
        if variable is None:
            field.insert(0, value)
        return field

    def _section_title(self, parent, title, subtitle):
        self._label(parent, title, 17, bold=True).pack(anchor="w", pady=(8, 2))
        self._label(parent, subtitle, 9, self.MUTED).pack(anchor="w", pady=(0, 14))

    def _build_converter(self, parent):
        self._section_title(parent, "Unit conversion", "Convert common measurements")
        self.convert_category = tk.StringVar(value="Length")
        category_row = tk.Frame(parent, bg=self.BG)
        category_row.pack(fill="x", pady=(0, 12))
        for category in ("Length", "Weight", "Temp"):
            self._round_button(
                category_row,
                category,
                lambda value=category: self._set_convert_category(value),
                width=108,
                height=36,
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left", padx=3)
        self.convert_value = tk.StringVar(value="1")
        self.convert_value.trace_add("write", lambda *_: self._convert_units())
        self._label(parent, "Value", 9, self.MUTED).pack(anchor="w", pady=(8, 4))
        self._entry(parent, self.convert_value).pack(fill="x", ipady=8)
        units = tk.Frame(parent, bg=self.BG)
        units.pack(fill="x", pady=12)
        self.from_unit = ttk.Combobox(units, state="readonly", style="Dark.TCombobox")
        self.to_unit = ttk.Combobox(units, state="readonly", style="Dark.TCombobox")
        self.from_unit.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.to_unit.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.from_unit.bind("<<ComboboxSelected>>", lambda _event: self._convert_units())
        self.to_unit.bind("<<ComboboxSelected>>", lambda _event: self._convert_units())
        self._round_button(
            parent, "Convert", self._convert_units, width=128, height=42,
            color=self.ACCENT, active_color="#f5a17f", foreground="#282828",
        ).pack(pady=(2, 12))
        self.convert_result = self._label(parent, "1 m = 1 m", 14, bold=True)
        self.convert_result.pack(anchor="center", pady=8)
        self._set_convert_category("Length")

    def _set_convert_category(self, category):
        unit_sets = {
            "Length": ["Meters", "Kilometers", "Miles", "Feet"],
            "Weight": ["Grams", "Kilograms", "Pounds", "Ounces"],
            "Temp": ["Celsius", "Fahrenheit", "Kelvin"],
        }
        self.convert_category.set(category)
        options = unit_sets[category]
        self.from_unit.configure(values=options)
        self.to_unit.configure(values=options)
        self.from_unit.set(options[0])
        self.to_unit.set(options[1] if len(options) > 1 else options[0])
        self._convert_units()

    def _convert_units(self):
        if not hasattr(self, "convert_result"):
            return
        try:
            value = float(self.convert_value.get())
            if not math.isfinite(value):
                raise ValueError
            category = self.convert_category.get()
            source, target = self.from_unit.get(), self.to_unit.get()
            if category == "Length":
                factors = {"Meters": 1, "Kilometers": 1000, "Miles": 1609.344, "Feet": 0.3048}
                answer = value * factors[source] / factors[target]
            elif category == "Weight":
                factors = {"Grams": 1, "Kilograms": 1000, "Pounds": 453.59237, "Ounces": 28.349523125}
                answer = value * factors[source] / factors[target]
            else:
                answer = self._convert_temperature(value, source, target)
            self.convert_result.configure(
                text=f"{value:g} {source} = {answer:.8g} {target}"
            )
        except (ValueError, KeyError):
            self.convert_result.configure(text="Enter a valid number")

    @staticmethod
    def _convert_temperature(value, source, target):
        if source == "Celsius":
            celsius = value
        elif source == "Fahrenheit":
            celsius = (value - 32) * 5 / 9
        else:
            celsius = value - 273.15
        if target == "Celsius":
            return celsius
        if target == "Fahrenheit":
            return celsius * 9 / 5 + 32
        return celsius + 273.15

    def _build_graph(self, parent):
        self._section_title(parent, "Graph plotting", "Upload a CSV file to create a chart")
        self.graph_series = {}
        self.graph_file_label = self._label(parent, "No CSV file selected", 9, self.MUTED)
        self.graph_file_label.pack(anchor="w", pady=(0, 6))
        self._round_button(
            parent, "Upload CSV", self._upload_graph_csv, width=142, height=40,
        ).pack(anchor="w", pady=(0, 8))
        self.graph_column = ttk.Combobox(
            parent,
            state="disabled",
            style="Dark.TCombobox",
        )
        self.graph_column.pack(fill="x", pady=(0, 8))
        self.graph_column.bind(
            "<<ComboboxSelected>>", lambda _event: self._plot_graph()
        )
        self.graph_type = ttk.Combobox(
            parent,
            values=("Line", "Bar", "Scatter", "Pie"),
            state="readonly",
            style="Dark.TCombobox",
        )
        self.graph_type.set("Line")
        self.graph_type.pack(fill="x", pady=9)
        self.graph_type.bind("<<ComboboxSelected>>", lambda _event: self._plot_graph())
        self._round_button(
            parent, "Plot graph", self._plot_graph, width=142, height=40,
            color=self.ACCENT, active_color="#f5a17f", foreground="#282828",
        ).pack(pady=(0, 8))
        self.plot = tk.Canvas(
            parent, bg=self.PANEL, highlightthickness=0, height=285
        )
        self.plot.pack(fill="both", expand=True)
        self._plot_graph()

    def _upload_graph_csv(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Select a CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8-sig") as file:
                rows = list(csv.reader(file))
            if len(rows) < 2 or not rows[0]:
                raise ValueError("The CSV must have a header and at least one data row.")

            headers = [
                value.strip() or f"Column {index + 1}"
                for index, value in enumerate(rows[0])
            ]
            display_names = []
            seen_names = set()
            for index, header in enumerate(headers):
                name = header
                suffix = 2
                while name in seen_names:
                    name = f"{header} ({suffix})"
                    suffix += 1
                seen_names.add(name)
                display_names.append(name)

            series = {}
            for column, name in enumerate(display_names):
                values = []
                labels = []
                for row_number, row in enumerate(rows[1:], start=2):
                    if column >= len(row) or not row[column].strip():
                        continue
                    try:
                        value = float(row[column].strip())
                    except ValueError:
                        break
                    if not math.isfinite(value):
                        break
                    values.append(value)
                    labels.append(
                        row[0].strip() if row and row[0].strip()
                        else str(row_number - 1)
                    )
                else:
                    if values:
                        series[name] = (labels, values)

            if not series:
                raise ValueError("The CSV must contain at least one numeric column.")
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            messagebox.showerror("CSV upload error", str(error), parent=self.root)
            return

        self.graph_series = series
        columns = list(series)
        self.graph_column.configure(values=columns, state="readonly")
        self.graph_column.set(columns[0])
        self.graph_file_label.configure(text=path.split("/")[-1].split("\\")[-1])
        self._plot_graph()

    def _plot_graph(self):
        if not hasattr(self, "plot"):
            return
        self.plot.delete("all")
        selected_column = self.graph_column.get()
        if not selected_column or selected_column not in self.graph_series:
            self.plot.create_text(
                175, 130, text="Upload a CSV with numeric data",
                fill=self.MUTED, font=("Segoe UI", 10),
            )
            return
        labels, values = self.graph_series[selected_column]
        self.plot.update_idletasks()
        width = max(self.plot.winfo_width(), 320)
        height = max(self.plot.winfo_height(), 250)
        chart_type = self.graph_type.get()
        if chart_type == "Pie":
            if any(value < 0 for value in values) or sum(values) <= 0:
                self.plot.create_text(width / 2, height / 2, text="Pie values must be positive", fill=self.MUTED)
                return
            colors = ["#f28b62", "#7eb6a5", "#8ba6d9", "#d9c27e", "#c293cf", "#80c4d2"]
            start = 0
            for index, value in enumerate(values):
                extent = value / sum(values) * 360
                self.plot.create_arc(
                    width / 2 - 95, height / 2 - 95,
                    width / 2 + 95, height / 2 + 95,
                    start=start, extent=extent, fill=colors[index % len(colors)],
                    outline=self.PANEL,
                )
                start += extent
            self.plot.create_text(
                width / 2, height - 12,
                text=f"{selected_column} ({len(values)} values)",
                fill=self.TEXT, font=("Segoe UI", 9),
            )
            return
        left, right, top, bottom = 32, width - 16, 16, height - 42
        self.plot.create_line(left, top, left, bottom, fill="#858585")
        self.plot.create_line(left, bottom, right, bottom, fill="#858585")
        self.plot.create_text(
            (left + right) / 2, 10, text=selected_column,
            fill=self.TEXT, font=("Segoe UI", 9),
        )
        low, high = min(values), max(values)
        spread = high - low or 1
        points = [
            (
                left + index * (right - left) / max(len(values) - 1, 1),
                bottom - (value - low) / spread * (bottom - top),
            )
            for index, value in enumerate(values)
        ]
        if chart_type == "Bar":
            step = (right - left) / len(values)
            for index, (x, y) in enumerate(points):
                self.plot.create_rectangle(
                    left + index * step + step * 0.18, y,
                    left + index * step + step * 0.82, bottom,
                    fill=self.ACCENT, outline="",
                )
        elif chart_type == "Scatter":
            for x, y in points:
                self.plot.create_oval(x - 4, y - 4, x + 4, y + 4, fill=self.ACCENT, outline="")
        else:
            if len(points) > 1:
                self.plot.create_line(
                    *(coordinate for point in points for coordinate in point),
                    fill=self.ACCENT, width=2,
                )
            for x, y in points:
                self.plot.create_oval(x - 3, y - 3, x + 3, y + 3, fill=self.ACCENT, outline="")
        label_indexes = (
            list(range(len(labels)))
            if len(labels) <= 5
            else [round(index * (len(labels) - 1) / 4) for index in range(5)]
        )
        for index in label_indexes:
            x, _ = points[index]
            label = labels[index]
            if len(label) > 8:
                label = label[:7] + "..."
            self.plot.create_text(
                x, bottom + 12, text=label,
                fill=self.MUTED, font=("Segoe UI", 7),
            )

    def _build_bmi(self, parent):
        self._section_title(parent, "BMI calculator", "Check your body mass index")
        self.bmi_weight = tk.StringVar()
        self.bmi_height = tk.StringVar()
        self._label(parent, "Weight (kg)", 9, self.MUTED).pack(anchor="w", pady=(5, 4))
        self._entry(parent, self.bmi_weight).pack(fill="x", ipady=8)
        self._label(parent, "Height (cm)", 9, self.MUTED).pack(anchor="w", pady=(14, 4))
        self._entry(parent, self.bmi_height).pack(fill="x", ipady=8)
        self._round_button(
            parent, "Calculate BMI", self._calculate_bmi, width=164, height=44,
            color=self.ACCENT, active_color="#f5a17f", foreground="#282828",
        ).pack(pady=18)
        self.bmi_result = self._label(parent, "Enter your height and weight", 13, bold=True)
        self.bmi_result.pack(pady=12)

    def _calculate_bmi(self):
        try:
            weight = float(self.bmi_weight.get())
            height = float(self.bmi_height.get()) / 100
            if not math.isfinite(weight) or not math.isfinite(height) or weight <= 0 or height <= 0:
                raise ValueError
            bmi = weight / height**2
            if not math.isfinite(bmi):
                raise ValueError
            category = (
                "Underweight" if bmi < 18.5 else
                "Normal weight" if bmi < 25 else
                "Overweight" if bmi < 30 else "Obesity"
            )
            self.bmi_result.configure(text=f"BMI: {bmi:.1f}  •  {category}")
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a positive weight and height.", parent=self.root)

    def _build_gst(self, parent):
        self._section_title(parent, "GST calculator", "Calculate tax and the final amount")
        self.gst_amount = tk.StringVar()
        self.gst_rate = tk.StringVar(value="18")
        self._label(parent, "Amount before GST", 9, self.MUTED).pack(anchor="w", pady=(5, 4))
        self._entry(parent, self.gst_amount).pack(fill="x", ipady=8)
        self._label(parent, "GST rate (%)", 9, self.MUTED).pack(anchor="w", pady=(14, 4))
        rates = ttk.Combobox(
            parent,
            textvariable=self.gst_rate,
            values=("0", "5", "12", "18", "28"),
            state="readonly",
            style="Dark.TCombobox",
        )
        rates.pack(fill="x")
        self._round_button(
            parent, "Calculate GST", self._calculate_gst, width=164, height=44,
            color=self.ACCENT, active_color="#f5a17f", foreground="#282828",
        ).pack(pady=18)
        self.gst_result = self._label(parent, "GST and total will appear here", 12, bold=True)
        self.gst_result.pack(pady=12)

    def _calculate_gst(self):
        try:
            amount = float(self.gst_amount.get())
            rate = float(self.gst_rate.get())
            if not math.isfinite(amount) or not math.isfinite(rate) or amount < 0 or rate < 0:
                raise ValueError
            tax = amount * rate / 100
            if not math.isfinite(tax) or not math.isfinite(amount + tax):
                raise ValueError
            self.gst_result.configure(
                text=f"GST: {tax:.2f}\nTotal: {amount + tax:.2f}"
            )
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a valid non-negative amount.", parent=self.root)


if __name__ == "__main__":
    app_root = tk.Tk()
    SmartCalculator(app_root)
    app_root.mainloop()
