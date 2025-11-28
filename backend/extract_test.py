from backend.agents.nodes.extract import extract_entities
from backend.agents.state import AgentState

tests = [
    "dus dairy milk add krde 10 rupiya waale",
    "4 pen kaat do bill me",
    "20rs wali 2 kurkure entry",
    "Chocolate add kar 5 ki",
    "pen 3 rakh diye",
    "2pc dairy milk 10rs",
    "3 Pepsi ₹35 wala",
    "5rs wali toffee 4",
    "bhai 2 dairy milk rakh diya, kal ka paisa baad me",
    "Abhi 50rs waali 1 Dairy milk bas",
    "chalo bhai 2 chocolate add hogai na?",
    "dary milkk 2 10rps",
    "choclate 3 add kr do 15",
    "mujhe hazar paan aani vimal shambhar pen pahije ahai",
    "2 pen aur 3 chocolate 10rs wali add karo",
    "KurKure 5 aur DairyMilk 2 entry",
] 

for msg in tests:
    state = AgentState(text=msg)
    state = extract_entities(state)
    print(f"{msg} -> {state["entities"]}")
