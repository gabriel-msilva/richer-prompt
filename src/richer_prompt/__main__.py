from richer_prompt import Choice, MultiSelect, Select, Tabs

Tabs.ask("Choose a protein:", ["Ham", "Chicken", "Tofu"])

Select.ask(
    "Choose a bread:",
    [
        Choice("white", label="White", description="Soft and fluffy"),
        Choice("whole_wheat", label="Whole wheat", description="Nutty and hearty"),
        Choice("sourdough", label="Sourdough", description="Tangy and crusty"),
    ],
)

MultiSelect.ask("Any toppings?", ["Lettuce", "Tomato", "Onion", "Pickles"])
