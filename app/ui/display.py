import customtkinter as ctk

from app.ui.theme import COLORS, FONT


class CalculatorDisplay(ctk.CTkFrame):
    def __init__(self, master, expression, on_backspace, on_copy, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=18, **kwargs)
        self.expression = ctk.CTkEntry(
            self,
            textvariable=expression,
            font=(FONT, 20),
            justify="right",
            border_width=0,
            fg_color="transparent",
            text_color=COLORS["text"],
            placeholder_text="Ketik perhitungan...",
            placeholder_text_color=COLORS["muted"],
        )
        self.expression.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 4))
        self.preview = ctk.CTkLabel(
            self,
            text="",
            font=(FONT, 38, "bold"),
            anchor="e",
            text_color=COLORS["text"],
        )
        self.preview.grid(row=1, column=0, sticky="ew", padx=20, pady=(2, 2))
        self.tools = ctk.CTkFrame(self, fg_color="transparent")
        self.tools.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 2))
        ctk.CTkButton(
            self.tools,
            text="⌫",
            width=52,
            height=32,
            font=(FONT, 15),
            fg_color=COLORS["operator"],
            hover_color=COLORS["operator_hover"],
            text_color=COLORS["text"],
            command=on_backspace,
        ).pack(side="left")
        ctk.CTkButton(
            self.tools,
            text="Salin hasil",
            width=110,
            height=32,
            font=(FONT, 14),
            fg_color=COLORS["operator"],
            hover_color=COLORS["operator_hover"],
            text_color=COLORS["text"],
            command=on_copy,
        ).pack(side="right")
        self.status = ctk.CTkLabel(
            self,
            text="",
            font=(FONT, 14),
            anchor="e",
            text_color=COLORS["muted"],
        )
        self.status.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 12))
        self.grid_columnconfigure(0, weight=1)

    def set_preview(self, value, error=False):
        self.preview.configure(
            text=value,
            text_color=COLORS["error"] if error else COLORS["text"],
        )

    def set_status(self, value, error=False):
        self.status.configure(
            text=value,
            text_color=COLORS["error"] if error else COLORS["muted"],
        )
