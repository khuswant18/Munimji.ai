# chatbot_backend/__init__.py
# Lazy import to avoid loading heavy dependencies when only db is needed
def get_chatbot():
    from .app import graph
    return graph