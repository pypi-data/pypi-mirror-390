import re
import string

# A small, built-in list of stopwords to avoid NLTK dependency
STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
])

def _count_syllables(word):
    """
    A simple heuristic to count syllables in a word.
    Not perfect, but good enough and dependency-free.
    """
    word = word.lower()
    
    # 1. Handle short words
    if len(word) <= 3:
        return 1
        
    # 2. Remove common silent endings
    word = re.sub(r'(es|ed|e)$', '', word)
    
    # 3. Count vowel groups (a, e, i, o, u, y)
    vowel_groups = re.findall(r'[aeiouy]+', word)
    
    # 4. A word must have at least one syllable
    count = len(vowel_groups)
    return count if count > 0 else 1

def profile(text: str) -> dict:
    """
    Generates a statistical profile of a given text.
    """
    
    # 1. Basic counts
    char_count = len(text)
    char_count_no_spaces = len(text.replace(' ', ''))
    
    # 2. Tokenize (split into words and sentences)
    # Simple regex for sentences (splits on . ! ?)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = len(sentences)
    
    # Simple regex for words (alphanumeric sequences)
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    if word_count == 0 or sentence_count == 0:
        # Handle empty text to avoid ZeroDivisionError
        return {
            'word_count': 0, 'sentence_count': 0, 'char_count': char_count,
            'char_count_no_spaces': char_count_no_spaces, 'avg_word_length': 0,
            'unique_word_count': 0, 'stopword_count': 0, 
            'punctuation_count': 0, 'flesch_reading_ease': 0
        }

    # 3. Word-level metrics
    unique_words = set(words)
    unique_word_count = len(unique_words)
    
    stopword_count = sum(1 for word in words if word in STOPWORDS)
    
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    
    avg_word_length = sum(len(word) for word in words) / word_count
    
    # 4. Readability (Flesch Reading Ease)
    # Formula: 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    total_syllables = sum(_count_syllables(word) for word in words)
    
    try:
        flesch_score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (total_syllables / word_count)
    except ZeroDivisionError:
        flesch_score = 0.0

    # 5. Compile the dictionary
    stats = {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'char_count': char_count,
        'char_count_no_spaces': char_count_no_spaces,
        'avg_word_length': round(avg_word_length, 2),
        'unique_word_count': unique_word_count,
        'stopword_count': stopword_count,
        'punctuation_count': punctuation_count,
        'flesch_reading_ease': round(flesch_score, 2)
    }
    
    return stats