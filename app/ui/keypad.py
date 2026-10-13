import customtkinter as ctk

from app.ui.theme import COLORS, FONT


class Keypad(ctk.CTkFrame):
    KEYS = (
        ("C", "()", "%", "÷"),
        ("7", "8", "9", "×"),
        ("4", "5", "6", "−"),
        ("1", "2", "3", "+"),
        ("±", "0", ".", "="),
    )

    SCIENTIFIC_KEYS = (
        ("sin", "cos", "tan"),
        ("log", "ln", "√"),
        ("x²", "xʸ", "n!"),
        ("π", "e", "ans"),
    )

    def __init__(self, master, on_press, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_press = on_press
        self.standard = ctk.CTkFrame(self, fg_color="transparent")
        self.standard.grid(row=0, column=0, sticky="nsew")
        for row_index, row in enumerate(self.KEYS):
            self.standard.grid_rowconfigure(row_index, weight=1, uniform="keys")
            for column_index, label in enumerate(row):
                if row_index == 0:
                    color = COLORS["operator"]
                    hover = COLORS["operator_hover"]
                elif label == "=":
                    color = COLORS["accent"]
                    hover = COLORS["accent_hover"]
                elif label in ("÷", "×", "−", "+"):
                    color = COLORS["operator"]
                    hover = COLORS["operator_hover"]
                else:
                    color = COLORS["number"]
                    hover = COLORS["number_hover"]
                button = ctk.CTkButton(
                    self.standard,
                    text=label,
                    font=(FONT, 18),
                    corner_radius=12,
                    fg_color=color,
                    hover_color=hover,
                    text_color=COLORS["text"],
                    command=lambda key=label: self.on_press(key),
                )
                button.grid(
                    row=row_index,
                    column=column_index,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                )
                self.standard.grid_columnconfigure(column_index, weight=1, uniform="keys")

        self.scientific = ctk.CTkFrame(self, fg_color="transparent")
        for row_index, row in enumerate(self.SCIENTIFIC_KEYS):
            self.scientific.grid_rowconfigure(row_index, weight=1, uniform="science")
            for column_index, label in enumerate(row):
                button = ctk.CTkButton(
                    self.scientific,
                    text=label,
                    font=(FONT, 16),
                    corner_radius=12,
                    fg_color=COLORS["operator"],
                    hover_color=COLORS["operator_hover"],
                    text_color=COLORS["text"],
                    command=lambda key=label: self.on_press(key),
                )
                button.grid(
                    row=row_index,
                    column=column_index,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                )
                self.scientific.grid_columnconfigure(column_index, weight=1, uniform="science")

    def layout_scientific(self, enabled, wide):
        self.standard.grid_forget()
        self.scientific.grid_forget()
        if enabled and wide:
            self.scientific.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
            self.standard.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
            self.grid_columnconfigure(0, weight=3)
            self.grid_columnconfigure(1, weight=4)
        elif enabled:
            self.scientific.grid(row=0, column=0, sticky="ew", pady=(0, 4))
            self.standard.grid(row=1, column=0, sticky="nsew")
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
        else:
            self.standard.grid(row=0, column=0, sticky="nsew")
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1 if enabled and not wide else 0)
