import sys
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

def test_algorithm(original: str, transcribed: str):
    norm_transcribed = _normalize(transcribed)
    norm_original = _normalize(original)

    orig_words = norm_original.split()
    rec_words = norm_transcribed.split()
    
    stopwords = RU_STOPWORDS
    total_weight = 0.0
    matched_weight = 0.0
    used_rec_indices = set()
    
    current_rec_idx = 0
    
    for i, o_word in enumerate(orig_words):
        word_weight = max(1, len(o_word))
        if o_word in stopwords:
            word_weight = 0.5
            
        total_weight += word_weight
        best_match_idx = -1
        best_ratio = 0.0
        
        # Sliding window constraint for overall accuracy too!
        search_start = max(0, current_rec_idx - 5)
        search_end = min(len(rec_words), current_rec_idx + 15)
        
        for j in range(search_start, search_end):
            r_word = rec_words[j]
            if j in used_rec_indices:
                continue
            ratio = SequenceMatcher(None, o_word, r_word).ratio()
            if ratio > 0.75 and ratio > best_ratio:
                best_match_idx = j
                best_ratio = ratio
                
        if best_match_idx != -1:
            used_rec_indices.add(best_match_idx)
            matched_weight += (word_weight * best_ratio)
            current_rec_idx = max(current_rec_idx, best_match_idx + 1)
            
    accuracy = min(100.0, (matched_weight / total_weight) * 100.0) if total_weight > 0 else 0.0
    print(f"Overall Accuracy: {accuracy:.2f}%")

    original_lines = [line.strip() for line in original.strip().split("\n") if line.strip()]
    
    current_rec_idx = 0
    used_line_rec_indices = set()
    
    for line in original_lines:
        line_words = _normalize(line).split()
        if not line_words:
            continue
            
        line_total_weight = 0
        line_matched_weight = 0
        matches_debug = []
        
        for o_word in line_words:
            word_weight = max(1, len(o_word))
            line_total_weight += word_weight
            
            best_m = -1
            best_r = 0.0
            
            # Constrain window: look up to 10 words ahead of current position
            search_start = max(0, current_rec_idx - 5)
            search_end = min(len(rec_words), current_rec_idx + 15)
            
            for j in range(search_start, search_end):
                r_word = rec_words[j]
                if j in used_line_rec_indices:
                    continue
                ratio = SequenceMatcher(None, o_word, r_word).ratio()
                if ratio > 0.75 and ratio > best_r:
                    best_m = j
                    best_r = ratio
            
            if best_m != -1:
                used_line_rec_indices.add(best_m)
                line_matched_weight += (word_weight * best_r)
                matches_debug.append(f"{o_word}[{best_r:.2f}]")
                current_rec_idx = max(current_rec_idx, best_m + 1)
            else:
                matches_debug.append(f"{o_word}[MISSED]")
                
        line_accuracy = (line_matched_weight / line_total_weight) if line_total_weight > 0 else 0
        status = "MISSED" if line_accuracy < 0.45 else "OK"
        print(f"[{status}] Acc={line_accuracy:.2f} | {line}")

if __name__ == "__main__":
    t = "не выходя из комнаты не совершай ошибку зачем тебе солнце если ты куришь шибко за дверью бессмысленно все особенно возглас счастье только в уборную и сразу же возвращайся о не выходи из комнаты не вызывая мотора потому что пространство сделаны из коридора и кончается счётчиком а если войдёт живая милка пасть разевая лос вгоняя не раздеваясь не выходя из комнаты считай что тебе было что интересней на свете стены и стула зачем выходить оттуда куда вернёшься вечер таким же как ты был тем более искалеченный"
    # Note: Using multi-line string here to avoid newline sequence bugs
    o = """Не выходи из комнаты, не совершай ошибку.
Зачем тебе Солнце, если ты куришь Шипку?
За дверью бессмысленно всё, особенно — возглас счастья.
Только в уборную — и сразу же возвращайся.

О, не выходи из комнаты, не вызывай мотора.
Потому что пространство сделано из коридора
и кончается счётчиком. А если войдёт живая
милка, пасть разевая, — Loss выгоняй, не раздевая.

Не выходи из комнаты; считай, что тебя продуло.
Что интересней на свете стены и стула?
Зачем выходить оттуда, куда вернёшься вечером
таким же, каким ты был, тем более — искалеченным?"""
    test_algorithm(o, t)
