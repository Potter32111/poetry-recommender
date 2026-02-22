from difflib import SequenceMatcher
import re

ru_stopwords = {"и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "человек", "чего", "раз", "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "об", "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между"}

t1 = "мороз и солнце день чудесный еще ты дремлешь друг прелестный пора красавица проснись"
t2 = "мороз солнце день чудесный сон це эээ ты дремлешь друг прелестный эмм пора красавица проснись"

print("Original text:   ", t1)
print("Recognized text: ", t2)
print("-" * 50)

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def advanced_evaluate(original: str, recognized: str, lang: str = "ru") -> float:
    orig_words = _normalize(original).split()
    rec_words = _normalize(recognized).split()
    
    if not orig_words or not rec_words:
        return 0.0
        
    stopwords = ru_stopwords if lang == "ru" else set()
    
    # We will score based on the character length of words matched
    # This naturally weights long "content" words higher than short prepositions
    total_weight = 0
    matched_weight = 0
    
    # Track matched recognizer words so we don't reuse them
    used_rec_indices = set()
    
    for i, o_word in enumerate(orig_words):
        word_weight = max(1, len(o_word))
        
        # Reduced penalty for stopwords if they are missed
        if o_word in stopwords:
            word_weight = 0.5 
            
        total_weight += word_weight
        
        best_match_idx = -1
        best_ratio = 0
        
        for j, r_word in enumerate(rec_words):
            if j in used_rec_indices:
                continue
                
            ratio = SequenceMatcher(None, o_word, r_word).ratio()
            if ratio > 0.75 and ratio > best_ratio:
                best_match_idx = j
                best_ratio = ratio
                
        if best_match_idx != -1:
            used_rec_indices.add(best_match_idx)
            # Give points proportional to match quality
            # E.g., ratio 0.8 on length 5 word gives 4 points out of 5
            matched_weight += (word_weight * best_ratio)
            
    return min(100.0, (matched_weight / total_weight) * 100) if total_weight > 0 else 0

print(f"Char ratio: {SequenceMatcher(None, t1, t2).ratio()*100:.1f}%")
print(f"Advanced word matching ratio: {advanced_evaluate(t1, t2):.1f}%")
