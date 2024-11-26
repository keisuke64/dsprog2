import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, expand=1, on_click=None):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = on_click
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, expand=1, on_click=None):
        super().__init__(text, expand, on_click)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, on_click=None):
        super().__init__(text, on_click=on_click)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, on_click=None):
        super().__init__(text, on_click=on_click)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK

class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        # Layout and Button Configuration
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        DigitButton(text="π", on_click=self.button_clicked),
                        ExtraActionButton(text="AC", on_click=self.button_clicked),
                        ExtraActionButton(text="+/-", on_click=self.button_clicked),
                        ExtraActionButton(text="% ", on_click=self.button_clicked),
                        ActionButton(text="/", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="e", on_click=self.button_clicked),
                        DigitButton(text="7", on_click=self.button_clicked),
                        DigitButton(text="8", on_click=self.button_clicked),
                        DigitButton(text="9", on_click=self.button_clicked),
                        ActionButton(text="*", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="sin", on_click=self.button_clicked),
                        DigitButton(text="4", on_click=self.button_clicked),
                        DigitButton(text="5", on_click=self.button_clicked),
                        DigitButton(text="6", on_click=self.button_clicked),
                        ActionButton(text="-", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="cos", on_click=self.button_clicked),
                        DigitButton(text="1", on_click=self.button_clicked),
                        DigitButton(text="2", on_click=self.button_clicked),
                        DigitButton(text="3", on_click=self.button_clicked),
                        ActionButton(text="+", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="tan", on_click=self.button_clicked),
                        DigitButton(text="0", expand=2, on_click=self.button_clicked),
                        DigitButton(text=".", on_click=self.button_clicked),
                        ActionButton(text="=", on_click=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")

        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/"):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.reset()

        elif data in ("%"):
            self.result.value = float(self.result.value) / 100
            self.reset()

        elif data in ("+/-"):
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)

            elif float(self.result.value) < 0:
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Calc App"
    calc = CalculatorApp()
    page.add(calc)

ft.app(target=main)
