from difflib import SequenceMatcher
import re

RU_STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", 
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за", 
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", 
    "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", 
    "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", 
    "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", 
    "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", 
    "сам", "чтоб", "без", "будто", "человек", "чего", "раз", "тоже", "себе", "под", 
    "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой", 
    "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", 
    "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", 
    "два", "об", "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", 
    "нас", "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", 
    "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", 
    "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между"
}

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def test_line_misses(original: str, recognized: str):
    original_lines = [line.strip() for line in original.strip().split("\n") if line.strip()]
    rec_words = _normalize(recognized).split()
    
    used_line_rec_indices = set()
    missed_lines = []
    
    print("RECOGNIZED WORDS:", rec_words)
    print("-" * 50)
    
    for line in original_lines:
        line_words = _normalize(line).split()
        if not line_words:
            continue
            
        line_total_weight = 0
        line_matched_weight = 0
        matches = []
        
        for o_word in line_words:
            word_weight = max(1, len(o_word))
            line_total_weight += word_weight
            
            best_m = -1
            best_r = 0.0
            
            # BIG FIX HYPOTHESIS:
            # We are currently only looking forward from the last used index? 
            # No, we iterate over all rec_words, but wait!
            # If the user speaks a stanza and STT drops a word, our logic might skip?
            # Actually, `used_line_rec_indices` prevents reusing words the user spoke.
            # But what if a word appears twice? E.g., "и" "и". 
            
            for j, r_word in enumerate(rec_words):
                if j in used_line_rec_indices:
                    continue
                ratio = SequenceMatcher(None, o_word, r_word).ratio()
                if ratio > 0.75 and ratio > best_r:
                    best_m = j
                    best_r = ratio
                    
            if best_m != -1:
                used_line_rec_indices.add(best_m)
                line_matched_weight += (word_weight * best_r)
                matches.append(f"{o_word}({best_r:.2f}->{rec_words[best_m]})")
            else:
                matches.append(f"{o_word}(FAILED)")
                
        line_accuracy = (line_matched_weight / line_total_weight) if line_total_weight > 0 else 0
        status = "MISSED" if line_accuracy < 0.45 else "OK"
        print(f"[{status}] Acc: {line_accuracy:.2f} | Line: '{line}'")
        print(f"       Matches: {', '.join(matches)}")

if __name__ == "__main__":
    t1 = """Мороз и солнце; день чудесный!
Еще ты дремлешь, друг прелестный -
Пора, красавица, проснись:"""
    t2 = "мороз и солнце день чудесный еще ты дремлешь друг прелестный пора красавица проснись"
    test_line_misses(t1, t2)
