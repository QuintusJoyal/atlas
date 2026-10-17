"""Token budget enforcement via token counting."""
import tiktoken

class TokenCounter:
    def __init__(self, model="gpt-4"):
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.encoding = None
    
    def count(self, text):
        if not text:
            return 0
        if self.encoding:
            return len(self.encoding.encode(text))
        # fallback rough estimate
        return len(text.split()) * 1.3
    
    def enforce_budget(self, used, budget_cap, remaining):
        """Check if over budget - hard cap enforcement."""
        if used >= budget_cap:
            return False, "Hard cap exceeded"
        return True, "OK"
