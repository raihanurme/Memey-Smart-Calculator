import customtkinter as ctk

from app.ui.theme import COLORS, FONT


class HistoryPanel(ctk.CTkFrame):
    def __init__(self, master, on_select, on_delete, on_clear, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=16, **kwargs)
        self.on_select = on_select
        self.on_delete = on_delete
        self.title = ctk.CTkLabel(
            self, text="Riwayat", font=(FONT, 18, "bold"), text_color=COLORS["text"]
        )
        self.title.pack(anchor="w", padx=16, pady=(14, 4))
        self.items = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.items.pack(fill="both", expand=True, padx=8, pady=6)
        self.clear_button = ctk.CTkButton(
            self,
            text="Hapus semua",
            font=(FONT, 14),
            fg_color=COLORS["operator"],
            hover_color=COLORS["operator_hover"],
            text_color=COLORS["text"],
            command=on_clear,
        )
        self.clear_button.pack(fill="x", padx=12, pady=(4, 12))

    def render(self, entries):
        for child in self.items.winfo_children():
            child.destroy()
        if not entries:
            ctk.CTkLabel(
                self.items,
                text="Belum ada perhitungan",
                font=(FONT, 14),
                text_color=COLORS["muted"],
            ).pack(anchor="w", padx=6, pady=8)
            return
        for index, entry in reversed(list(enumerate(entries))):
            row = ctk.CTkFrame(self.items, fg_color="transparent")
            row.pack(fill="x", padx=2, pady=4)
            ctk.CTkButton(
                row,
                text="{}\n= {}".format(entry.get("expression", ""), entry.get("result", "")),
                anchor="e",
                justify="right",
                font=(FONT, 14),
                height=54,
                fg_color=COLORS["number"],
                hover_color=COLORS["number_hover"],
                text_color=COLORS["text"],
                command=lambda value=entry.get("expression", ""): self.on_select(value),
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row,
                text="×",
                width=32,
                height=32,
                font=(FONT, 16),
                fg_color="transparent",
                hover_color=COLORS["danger"],
                text_color=COLORS["muted"],
                command=lambda item_index=index: self.on_delete(item_index),
            ).pack(side="right", padx=(4, 0))
