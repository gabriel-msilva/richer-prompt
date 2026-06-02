from richer_prompt import MultiSelect, Option, Select, Tabs

Tabs.ask("Choose a protein:", ["Ham", "Chicken", "Tofu"])

Select.ask(
    "Choose a bread:",
    [
        Option("white", label="White", description="Soft and fluffy"),
        Option("whole_wheat", label="Whole wheat", description="Nutty and hearty"),
        Option("sourdough", label="Sourdough", description="Tangy and crusty"),
    ],
)

MultiSelect.ask("Any toppings?", ["Lettuce", "Tomato", "Onion", "Pickles"])
