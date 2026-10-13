import math
import re
import tkinter as tk
from datetime import datetime
from decimal import Decimal, InvalidOperation

import customtkinter as ctk

from app.core.converter import convert
from app.core.functions import CalculationError
from app.core.parser import Calculator, format_decimal
from app.storage.settings import DEFAULT_SETTINGS, JsonStorage
from app.ui.display import CalculatorDisplay
from app.ui.history_panel import HistoryPanel
from app.ui.keypad import Keypad
from app.ui.theme import COLORS, FONT


class CalculatorApp(ctk.CTk):
    def __init__(self):
        try:
            self.storage = JsonStorage()
            self.settings = self.storage.load_settings()
            self.history = self.storage.load_history()
            startup_warning = ""
        except (OSError, ValueError) as error:
            self.storage = JsonStorage()
            self.settings = dict(DEFAULT_SETTINGS)
            self.history = []
            startup_warning = "Data lokal tidak dapat dibaca: {}".format(error)

        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("Memey Smart Calculator")
        self.minsize(360, 560)
        self.geometry(self.settings.get("geometry", "900x650"))
        self.attributes("-topmost", bool(self.settings.get("always_on_top", False)))
        self.calculator = Calculator()
        self.calculator.angle_mode = self.settings["angle_mode"]
        self.expression = tk.StringVar()
        self.scientific_mode = False
        self.history_requested = False
        self._resize_after_id = None
        self._history_visible = False

        self.configure(fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_interface()
        self.expression.trace_add("write", self._on_expression_changed)
        self.bind("<Configure>", self._schedule_responsive_layout)
        self.bind_all("<Return>", self._on_enter)
        self.bind_all("<KP_Enter>", self._on_enter)
        self.bind_all("<Escape>", self._on_escape)
        self.bind_all("<Control-c>", self._on_copy)
        self.bind_all("<Control-C>", self._on_copy)
        self.bind_all("<Control-h>", self._on_history_shortcut)
        self.bind_all("<Control-H>", self._on_history_shortcut)
        self.bind_all("<Control-t>", self._on_theme_shortcut)
        self.bind_all("<Control-T>", self._on_theme_shortcut)
        self.bind_all("<Control-m>", self._on_mode_shortcut)
        self.bind_all("<Control-M>", self._on_mode_shortcut)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.history_panel.render(self.history)
        self._on_expression_changed()
        self.after(150, self._responsive_layout)
        if startup_warning:
            self.display.set_status(startup_warning, error=True)

    def _build_interface(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        self.header.grid_columnconfigure(0, weight=1)
        title_row = ctk.CTkFrame(self.header, fg_color="transparent")
        title_row.pack(fill="x")
        ctk.CTkLabel(
            title_row,
            text="Memey Smart Calculator",
            font=(FONT, 18, "bold"),
            text_color=COLORS["text"],
        ).pack(side="left", padx=(4, 0))
        self.theme_button = self._toolbar_button(title_row, "☼", self._toggle_theme)
        self.theme_button.pack(side="right", padx=(4, 0))
        self.history_button = self._toolbar_button(title_row, "☰", self._toggle_history)
        self.history_button.pack(side="right", padx=(4, 0))

        actions = ctk.CTkFrame(self.header, fg_color="transparent")
        actions.pack(fill="x", pady=(8, 0))
        self.mode_button = self._toolbar_button(actions, "Mode: Standar", self._toggle_mode)
        self.mode_button.pack(side="left", fill="x", expand=True, padx=3)
        self.angle_button = self._toolbar_button(
            actions, self.calculator.angle_mode, self._toggle_angle
        )
        self.angle_button.pack(side="left", padx=3)
        self.converter_button = self._toolbar_button(actions, "⇄ Unit", self._open_converter)
        self.converter_button.pack(side="left", padx=3)
        self.discount_button = self._toolbar_button(actions, "Harga", self._open_discount_tool)
        self.discount_button.pack(side="left", padx=3)
        self.topmost_button = self._toolbar_button(actions, "↑", self._toggle_topmost)
        self.topmost_button.pack(side="left", padx=3)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 16))
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.calculator_area = ctk.CTkFrame(self.content, fg_color="transparent")
        self.calculator_area.grid(row=0, column=0, sticky="nsew", padx=(0, 0))
        self.calculator_area.grid_rowconfigure(1, weight=1)
        self.calculator_area.grid_columnconfigure(0, weight=1)

        self.display = CalculatorDisplay(
            self.calculator_area,
            self.expression,
            self._delete_last_character,
            self._copy_result,
        )
        self.display.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.keypad = Keypad(self.calculator_area, self._on_keypad_press)
        self.keypad.grid(row=1, column=0, sticky="nsew")
        self.history_panel = HistoryPanel(
            self.content,
            self._reuse_history,
            self._delete_history_entry,
            self._clear_history,
            width=250,
        )

    @staticmethod
    def _toolbar_button(master, text, command):
        return ctk.CTkButton(
            master,
            text=text,
            height=36,
            font=(FONT, 14),
            corner_radius=10,
            fg_color=COLORS["operator"],
            hover_color=COLORS["operator_hover"],
            text_color=COLORS["text"],
            command=command,
        )

    def _on_keypad_press(self, key):
        self.display.set_status("")
        if key == "C":
            self.expression.set("")
        elif key == "=":
            self._calculate()
        elif key == "⌫":
            self._delete_last_character()
        elif key == "±":
            self._toggle_sign()
        elif key == "()":
            text = self.expression.get()
            if text.count("(") > text.count(")") and text.rsplit("(", 1)[-1].count(")") == 0:
                self.expression.set(text + ")")
            else:
                self.expression.set(text + "()")
                self.display.expression.icursor(len(text) + 1)
        elif key == "x²":
            self.expression.set(self.expression.get() + "²")
        elif key == "xʸ":
            self.expression.set(self.expression.get() + "^")
        elif key == "n!":
            text = self.expression.get()
            self.expression.set("factorial({})".format(text) if text else "factorial()")
        elif key in ("sin", "cos", "tan", "log", "ln", "√"):
            function = "sqrt" if key == "√" else key
            text = self.expression.get()
            self.expression.set(text + function + "()")
            self.display.expression.icursor(len(text) + len(function) + 1)
        elif key in ("π", "e", "ans"):
            self.expression.set(self.expression.get() + key)
        else:
            self.expression.set(self.expression.get() + key)
        self.display.expression.focus_set()

    def _toggle_sign(self):
        text = self.expression.get()
        if not text:
            self.expression.set("-")
            return
        match = re.search(r"(?<![\w.])-?\d+(?:[.,]\d+)?(?!.*\d)", text)
        if match:
            start, end = match.span()
            number = match.group()
            replacement = number[1:] if number.startswith("-") else "-" + number
            self.expression.set(text[:start] + replacement + text[end:])
        else:
            self.expression.set("-(" + text + ")")

    def _on_expression_changed(self, *_args):
        text = self.expression.get().strip()
        if not text:
            self.display.set_preview("")
            return
        candidate = text
        if candidate.count("(") > candidate.count(")"):
            candidate += ")" * min(8, candidate.count("(") - candidate.count(")"))
        try:
            result = self.calculator.evaluate(candidate)
            self.display.set_preview(format_decimal(result))
            self.display.set_status("")
            self._fit_result_font(format_decimal(result))
        except CalculationError as error:
            if "dibagi nol" in str(error) or "terlalu besar" in str(error):
                self.display.set_preview(str(error), error=True)
                self.display.set_status("", error=True)
            else:
                self.display.set_preview("")

    def _fit_result_font(self, value):
        width = max(self.display.winfo_width() - 48, 240)
        font_size = max(18, min(42, int(width * 0.72 / max(len(value), 1))))
        self.display.preview.configure(font=(FONT, font_size, "bold"))

    def _calculate(self):
        text = self.expression.get().strip()
        if not text:
            self.display.set_status("Masukkan ekspresi terlebih dahulu", error=True)
            return
        candidate = text
        if candidate.count("(") > candidate.count(")"):
            candidate += ")" * min(8, candidate.count("(") - candidate.count(")"))
        try:
            result = self.calculator.calculate(candidate)
        except CalculationError as error:
            self.display.set_preview(str(error), error=True)
            self.display.set_status(str(error), error=True)
            return
        formatted = format_decimal(result)
        self.display.set_preview(formatted)
        self.display.set_status("Tersimpan di riwayat")
        self._add_history(text, formatted)

    def _add_history(self, expression, result):
        self.history.append(
            {
                "expression": expression,
                "result": result,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        )
        self.history = self.history[-100:]
        self.history_panel.render(self.history)
        self._persist_history()

    def _persist_history(self):
        try:
            self.storage.save_history(self.history)
        except OSError as error:
            self.display.set_status(
                "Riwayat hanya berlaku selama sesi ini: {}".format(error), error=True
            )

    def _reuse_history(self, expression):
        self.expression.set(expression)
        self.display.expression.focus_set()

    def _delete_history_entry(self, index):
        if 0 <= index < len(self.history):
            del self.history[index]
            self.history_panel.render(self.history)
            self._persist_history()

    def _clear_history(self):
        self.history = []
        self.history_panel.render(self.history)
        self._persist_history()

    def _toggle_theme(self):
        sequence = ("system", "light", "dark")
        current = self.settings.get("theme", "system")
        self.settings["theme"] = sequence[(sequence.index(current) + 1) % len(sequence)]
        ctk.set_appearance_mode(self.settings["theme"])
        self._save_settings()

    def _toggle_mode(self):
        self.scientific_mode = not self.scientific_mode
        self.mode_button.configure(
            text="Mode: Ilmiah" if self.scientific_mode else "Mode: Standar"
        )
        self._responsive_layout()

    def _toggle_angle(self):
        self.calculator.angle_mode = "RAD" if self.calculator.angle_mode == "DEG" else "DEG"
        self.settings["angle_mode"] = self.calculator.angle_mode
        self.angle_button.configure(text=self.calculator.angle_mode)
        self._save_settings()
        self._on_expression_changed()

    def _toggle_topmost(self):
        value = not bool(self.settings.get("always_on_top", False))
        self.settings["always_on_top"] = value
        self.attributes("-topmost", value)
        self.topmost_button.configure(text="↑ On" if value else "↑")
        self._save_settings()

    def _toggle_history(self):
        self.history_requested = not self.history_requested
        self._responsive_layout()

    def _responsive_layout(self):
        width = self.winfo_width()
        wide = width > 720
        self.keypad.layout_scientific(self.scientific_mode, wide)
        show_history = wide or self.history_requested
        if show_history:
            self.calculator_area.grid_configure(row=0, column=0, sticky="nsew", padx=(0, 10))
            self.content.grid_columnconfigure(0, weight=4 if wide else 1)
            self.history_panel.grid(row=0, column=1, sticky="nsew")
            self.content.grid_columnconfigure(1, weight=1)
            self._history_visible = True
        else:
            self.history_panel.grid_forget()
            self.content.grid_columnconfigure(0, weight=1)
            self.content.grid_columnconfigure(1, weight=0)
            self.calculator_area.grid_configure(padx=(0, 0))
            self._history_visible = False

    def _schedule_responsive_layout(self, event):
        if event.widget is not self:
            return
        if self._resize_after_id is not None:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(100, self._responsive_layout)

    def _on_enter(self, _event=None):
        self._calculate()
        return "break"

    def _on_escape(self, _event=None):
        self.expression.set("")
        self.display.set_status("")
        return "break"

    def _on_copy(self, _event=None):
        self._copy_result()
        return "break"

    def _copy_result(self):
        value = self.display.preview.cget("text")
        if value:
            self.clipboard_clear()
            self.clipboard_append(value.replace(",", ""))
            self.display.set_status("Hasil disalin")

    def _delete_last_character(self):
        text = self.expression.get()
        cursor = self.display.expression.index(tk.INSERT)
        if cursor > 0:
            self.expression.set(text[:cursor - 1] + text[cursor:])
            self.display.expression.icursor(cursor - 1)

    def _on_history_shortcut(self, _event=None):
        self._toggle_history()
        return "break"

    def _on_theme_shortcut(self, _event=None):
        self._toggle_theme()
        return "break"

    def _on_mode_shortcut(self, _event=None):
        self._toggle_mode()
        return "break"

    def _save_settings(self):
        try:
            self.storage.save_settings(self.settings)
        except OSError as error:
            self.display.set_status(
                "Pengaturan tidak dapat disimpan: {}".format(error), error=True
            )

    def _on_close(self):
        try:
            self.settings["geometry"] = self.geometry()
            self._save_settings()
        finally:
            self.destroy()

    def _open_converter(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Konverter satuan")
        dialog.geometry("380x340")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(1, weight=1)

        category = tk.StringVar(value="length")
        source = tk.StringVar(value="m")
        target = tk.StringVar(value="km")
        amount = tk.StringVar(value="1")
        result = tk.StringVar(value="")
        units = {
            "length": ("mm", "cm", "m", "km", "in", "ft", "mi"),
            "mass": ("mg", "g", "kg", "lb", "oz"),
            "temperature": ("c", "f", "k"),
            "volume": ("ml", "l", "m3", "cup"),
        }

        ctk.CTkLabel(
            dialog, text="Konverter satuan", font=(FONT, 20, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 12), sticky="w")
        ctk.CTkLabel(dialog, text="Kategori", font=(FONT, 14)).grid(
            row=1, column=0, padx=18, pady=7, sticky="w"
        )
        category_menu = ctk.CTkOptionMenu(
            dialog,
            values=list(units),
            variable=category,
            command=lambda _value: refresh_units(),
        )
        category_menu.grid(row=1, column=1, padx=18, pady=7, sticky="ew")
        ctk.CTkLabel(dialog, text="Nilai", font=(FONT, 14)).grid(
            row=2, column=0, padx=18, pady=7, sticky="w"
        )
        ctk.CTkEntry(dialog, textvariable=amount, font=(FONT, 16)).grid(
            row=2, column=1, padx=18, pady=7, sticky="ew"
        )
        source_menu = ctk.CTkOptionMenu(dialog, variable=source, values=list(units["length"]))
        target_menu = ctk.CTkOptionMenu(dialog, variable=target, values=list(units["length"]))
        source_menu.grid(row=3, column=1, padx=18, pady=7, sticky="ew")
        target_menu.grid(row=4, column=1, padx=18, pady=7, sticky="ew")
        ctk.CTkLabel(dialog, text="Dari / ke", font=(FONT, 14)).grid(
            row=3, column=0, rowspan=2, padx=18, pady=7, sticky="w"
        )
        output_label = ctk.CTkLabel(dialog, textvariable=result, font=(FONT, 18, "bold"))
        output_label.grid(row=6, column=0, columnspan=2, padx=18, pady=8)
        status = ctk.CTkLabel(dialog, text="", font=(FONT, 14), text_color=COLORS["error"])
        status.grid(row=7, column=0, columnspan=2, padx=18, pady=(0, 4))

        def refresh_units(_value=None):
            values = list(units[category.get()])
            source_menu.configure(values=values)
            target_menu.configure(values=values)
            source.set(values[0])
            target.set(values[-1])
            status.configure(text="")
            result.set("")

        def do_convert():
            try:
                numeric_value = float(amount.get().replace(",", "."))
                if not math.isfinite(numeric_value):
                    raise ValueError("Nilai harus berupa angka terbatas")
                converted = convert(numeric_value, source.get(), target.get(), category.get())
            except (ValueError, InvalidOperation) as error:
                status.configure(text=str(error) or "Masukkan angka yang valid")
                return
            result.set("{:,.8g} {}".format(converted, target.get()))
            status.configure(text="")

        ctk.CTkButton(
            dialog, text="Konversi", font=(FONT, 16), command=do_convert
        ).grid(row=5, column=0, columnspan=2, padx=18, pady=8, sticky="ew")

    def _open_discount_tool(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Kalkulator diskon dan pajak")
        dialog.geometry("390x360")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(1, weight=1)
        price = tk.StringVar()
        discount = tk.StringVar(value="0")
        tax = tk.StringVar(value="0")
        result = tk.StringVar(value="")
        ctk.CTkLabel(
            dialog, text="Diskon & pajak", font=(FONT, 20, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 10), sticky="w")
        for row, label, variable in (
            (1, "Harga awal", price),
            (2, "Diskon (%)", discount),
            (3, "Pajak / PPN (%)", tax),
        ):
            ctk.CTkLabel(dialog, text=label, font=(FONT, 14)).grid(
                row=row, column=0, padx=18, pady=7, sticky="w"
            )
            ctk.CTkEntry(dialog, textvariable=variable, font=(FONT, 16)).grid(
                row=row, column=1, padx=18, pady=7, sticky="ew"
            )
        status = ctk.CTkLabel(dialog, text="", font=(FONT, 14), text_color=COLORS["error"])
        status.grid(row=5, column=0, columnspan=2, padx=18, pady=4)

        def calculate_price():
            try:
                original = Decimal(price.get().replace(",", "."))
                discount_rate = Decimal(discount.get().replace(",", "."))
                tax_rate = Decimal(tax.get().replace(",", "."))
                if not all(value.is_finite() for value in (original, discount_rate, tax_rate)):
                    raise ValueError("Masukkan angka yang valid")
                if original < 0 or not 0 <= discount_rate <= 100 or tax_rate < 0:
                    raise ValueError("Harga/pajak harus positif dan diskon 0–100%")
                final_price = original * (1 - discount_rate / 100) * (1 + tax_rate / 100)
            except (InvalidOperation, ValueError) as error:
                status.configure(text=str(error) or "Masukkan angka yang valid")
                result.set("")
                return
            result.set("Total: {}".format(format_decimal(final_price)))
            status.configure(text="")

        ctk.CTkButton(
            dialog, text="Hitung total", font=(FONT, 16), command=calculate_price
        ).grid(row=4, column=0, columnspan=2, padx=18, pady=8, sticky="ew")
        ctk.CTkLabel(
            dialog, textvariable=result, font=(FONT, 19, "bold"), text_color=COLORS["text"]
        ).grid(row=6, column=0, columnspan=2, padx=18, pady=(6, 16))
