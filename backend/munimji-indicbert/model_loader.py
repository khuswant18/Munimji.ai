# model_loader.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

MODEL_NAME = os.environ.get("INTENT_MODEL", "ai4bharat/indic-bert")

class IntentModel:
    def __init__(self, model_name=MODEL_NAME, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[model_loader] loading {model_name} on {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        # id2label might not exist for HF hub model; we create placeholder (will be overwritten if model has config)
        self.id2label = getattr(self.model.config, "id2label", None) or {i: str(i) for i in range(self.model.config.num_labels)}

    def predict(self, text, max_length=128):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=max_length)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.model(**inputs)
            logits = out.logits
            probs = torch.nn.functional.softmax(logits, dim=-1).squeeze(0)
            conf, idx = torch.max(probs, dim=-1)
            label = self.id2label.get(int(idx.item()), str(int(idx.item())))
            # convert probs to list of floats
            probs_list = probs.cpu().tolist()
        return {"intent": label, "confidence": float(conf.item()), "probs": probs_list}
