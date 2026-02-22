import sys
from difflib import SequenceMatcher
import re

EN_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't",
    "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
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
    
    stopwords = EN_STOPWORDS
    
    # NEW ALGORITHM: Needleshank alignment
    # Instead of a strict sliding window that permanently advances and gets lost,
    # we just greedily find the *best* chronological sequence mapping we can, with wide boundaries.
    
    total_weight = 0.0
    matched_weight = 0.0
    used_rec_indices = set()
    
    # 1. Overall Accuracy
    for i, o_word in enumerate(orig_words):
        word_weight = max(1, len(o_word))
        if o_word in stopwords:
            word_weight = 0.5
            
        total_weight += word_weight
        best_match_idx = -1
        best_ratio = 0.0
        
        search_start = max(0, int((i/len(orig_words)) * len(rec_words)) - 15)
        search_end = min(len(rec_words), int((i/len(orig_words)) * len(rec_words)) + 25)
        
        for j in range(search_start, search_end):
            r_word = rec_words[j]
            if j in used_rec_indices:
                continue
            ratio = SequenceMatcher(None, o_word, r_word).ratio()
            if ratio > 0.65 and ratio > best_ratio:
                best_match_idx = j
                best_ratio = ratio
                
        if best_match_idx != -1:
            used_rec_indices.add(best_match_idx)
            matched_weight += (word_weight * best_ratio)
            
    accuracy = min(100.0, (matched_weight / total_weight) * 100.0) if total_weight > 0 else 0.0
    print(f"Overall Accuracy: {accuracy:.2f}%\n")

    # 2. Line misses
    original_lines = [line.strip() for line in original.strip().split("\n") if line.strip()]
    used_line_rec_indices = set()
    
    # Pre-calculate approximate word indices for each line
    line_word_counts = [len(_normalize(line).split()) for line in original_lines]
    
    cumulative_words = 0
    for l_idx, line in enumerate(original_lines):
        line_words = _normalize(line).split()
        if not line_words:
            continue
            
        line_total_weight = 0
        line_matched_weight = 0
        matches_debug = []
        
        # Approximate center of this line in the transcribed text
        percent_through = cumulative_words / len(orig_words) if orig_words else 0
        expected_rec_center = int(percent_through * len(rec_words))
        
        for o_word in line_words:
            word_weight = max(1, len(o_word))
            line_total_weight += word_weight
            
            best_m = -1
            best_r = 0.0
            
            search_start = max(0, expected_rec_center - 15)
            search_end = min(len(rec_words), expected_rec_center + len(line_words) + 20)
            
            for j in range(search_start, search_end):
                r_word = rec_words[j]
                if j in used_line_rec_indices:
                    continue
                ratio = SequenceMatcher(None, o_word, r_word).ratio()
                if ratio > 0.65 and ratio > best_r:
                    best_m = j
                    best_r = ratio
            
            if best_m != -1:
                used_line_rec_indices.add(best_m)
                line_matched_weight += (word_weight * best_r)
                matches_debug.append(f"{o_word}[{rec_words[best_m]}:{best_r:.2f}]")
            else:
                matches_debug.append(f"{o_word}[MISSED]")
                
        line_accuracy = (line_matched_weight / line_total_weight) if line_total_weight > 0 else 0
        status = "MISSED" if line_accuracy < 0.40 else "OK"
        if status == "MISSED":
            print(f"[{status}] Acc={line_accuracy:.2f} | {line}")
            print(f"   -> {' '.join(matches_debug)}")
        
        cumulative_words += len(line_words)

if __name__ == "__main__":
    t = "if you can keep your head will know about you oh is in where's and blame it on the you if you can trust yourself the norm and out you but make allowance for where the one aware of the though it into if you can evade in not be tired by weeds him or been laid the both you don't do in lies or been heated don't give way to heat him in the a don't look too good nor dog to ways if you can dream in love make your make doomsayer mustard if you can fumed and not make false your aim if you can meet he's doomed and is thus there and treat those two impostors just the same yours is the earth and there if him with and reduce more you will be and when my son"
    o = """If you can keep your head when all about you
Are losing theirs and blaming it on you,
If you can trust yourself when all men doubt you,
But make allowance for their doubting too;

If you can wait and not be tired by waiting,
Or being lied about, don't deal in lies,
Or being hated, don't give way to hating,
And yet don't look too good, nor talk too wise:

If you can dream — and not make dreams your master;
If you can think — and not make thoughts your aim;
If you can meet with Triumph and Disaster
And treat those two impostors just the same;

Yours is the Earth and everything that's in it,
And — which is more — you'll be a Man, my son!"""
    test_algorithm(o, t)
