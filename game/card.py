class Card:

    def __init__(self, color, value):
        self.color = color
        self.value = value

    @property
    def image(self):

        color_names = {
            "red": "Red",
            "green": "Green",
            "blue": "Blue",
            "yellow": "Yellow",
            "wild": "Wild"
        }

        # Wild
        if self.color == "wild":

            if self.value == "wild":
                return "assets/card/Wild.png"

            if self.value == "wild4":
                return "assets/card/Wild_Draw.png"

        # Draw2
        if self.value == "draw2":
            return f"assets/card/{color_names[self.color]}_Draw.png"

        # Reverse
        if self.value == "reverse":
            return f"assets/card/{color_names[self.color]}_Reverse.png"

        # Skip
        if self.value == "skip":
            return f"assets/card/{color_names[self.color]}_Skip.png"

        # الأرقام
        return f"assets/card/{color_names[self.color]}_{self.value}.png"

    def __str__(self):

        colors = {
            "red": "🔴",
            "green": "🟢",
            "blue": "🔵",
            "yellow": "🟡",
            "wild": "⚫"
        }

        return f"{colors[self.color]} {self.value}"