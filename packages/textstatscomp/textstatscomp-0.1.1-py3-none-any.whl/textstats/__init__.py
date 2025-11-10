# src/textstats/__init__.py
import re
from collections import Counter
from typing import Dict, List, Tuple


class TextStats:
    
    
    def __init__(self, text: str):
        self.text = text
        self.words = self._extract_words()
        self.sentences = self._extract_sentences()
    
    def _extract_words(self) -> List[str]:
        
        text = self.text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [word for word in text.split() if word]
    
    def _extract_sentences(self) -> List[str]:
       
        sentences = re.split(r'[.!?]+', self.text)
        return [s.strip() for s in sentences if s.strip()]
    
    # Basic Statistics
    def word_count(self) -> int:
        
        return len(self.words)
    
    def character_count(self, include_spaces: bool = True) -> int:
        
        if include_spaces:
            return len(self.text)
        return len(self.text.replace(' ', ''))
    
    def sentence_count(self) -> int:
        
        return len(self.sentences)
    
    def paragraph_count(self) -> int:
       
        paragraphs = [p for p in self.text.split('\n\n') if p.strip()]
        return len(paragraphs)
    
    # Vocabulary Analysis
    def unique_word_count(self) -> int:
        
        return len(set(self.words))
    
    def lexical_diversity(self) -> float:
        
        if not self.words:
            return 0.0
        return len(set(self.words)) / len(self.words)
    
    def word_frequency(self, top_n: int = None) -> Dict[str, int]:
        
        counter = Counter(self.words)
        if top_n:
            return dict(counter.most_common(top_n))
        return dict(counter)
    
    def rare_words(self, threshold: int = 1) -> List[str]:
       
        counter = Counter(self.words)
        return [word for word, count in counter.items() if count <= threshold]
    
    def most_common_words(self, n: int = 10) -> List[Tuple[str, int]]:
       
        counter = Counter(self.words)
        return counter.most_common(n)
    
    # Length Statistics
    def average_word_length(self) -> float:
        
        if not self.words:
            return 0.0
        return sum(len(word) for word in self.words) / len(self.words)
    
    def average_sentence_length(self) -> float:
        
        if not self.sentences:
            return 0.0
        return len(self.words) / len(self.sentences)
    
    def longest_words(self, n: int = 10) -> List[Tuple[str, int]]:
        
        word_lengths = [(word, len(word)) for word in set(self.words)]
        return sorted(word_lengths, key=lambda x: x[1], reverse=True)[:n]
    
    def shortest_words(self, n: int = 10) -> List[Tuple[str, int]]:
        
        word_lengths = [(word, len(word)) for word in set(self.words)]
        return sorted(word_lengths, key=lambda x: x[1])[:n]
    
    def word_length_distribution(self) -> Dict[int, int]:
        
        lengths = [len(word) for word in self.words]
        return dict(Counter(lengths))
    
    # Reading Time
    def reading_time(self, wpm: int = 200) -> Dict[str, float]:
       
        minutes = len(self.words) / wpm
        return {
            'minutes': round(minutes, 2),
            'seconds': round(minutes * 60, 0),
            'formatted': f"{int(minutes)} min" if minutes >= 1 else f"{int(minutes * 60)} sec"
        }
    
    # Special Character Analysis
    def digit_count(self) -> int:
        
        return sum(char.isdigit() for char in self.text)
    
    def uppercase_count(self) -> int:
        
        return sum(char.isupper() for char in self.text)
    
    def lowercase_count(self) -> int:
        
        return sum(char.islower() for char in self.text)
    
    def special_char_count(self) -> int:
        
        return sum(not char.isalnum() and not char.isspace() for char in self.text)
    
    # Comprehensive Report
    def get_all_stats(self) -> Dict:
        
        return {
            'basic': {
                'characters': self.character_count(include_spaces=True),
                'characters_no_spaces': self.character_count(include_spaces=False),
                'words': self.word_count(),
                'sentences': self.sentence_count(),
                'paragraphs': self.paragraph_count(),
                'digits': self.digit_count(),
                'uppercase_letters': self.uppercase_count(),
                'lowercase_letters': self.lowercase_count(),
                'special_characters': self.special_char_count()
            },
            'vocabulary': {
                'unique_words': self.unique_word_count(),
                'lexical_diversity': round(self.lexical_diversity(), 4),
                'rare_words_count': len(self.rare_words()),
                'top_10_words': self.most_common_words(10)
            },
            'averages': {
                'avg_word_length': round(self.average_word_length(), 2),
                'avg_sentence_length': round(self.average_sentence_length(), 2)
            },
            'reading_time': self.reading_time()
        }
    
    def print_report(self):
        
        stats = self.get_all_stats()
        
        print("=" * 50)
        print("TEXT STATISTICS REPORT")
        print("=" * 50)
        
        print("\n BASIC COUNTS:")
        for key, value in stats['basic'].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n VOCABULARY:")
        for key, value in stats['vocabulary'].items():
            if key != 'top_10_words':
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n  Top 10 Words:")
        for word, count in stats['vocabulary']['top_10_words']:
            print(f"    '{word}': {count}")
        
        print("\nAVERAGES:")
        for key, value in stats['averages'].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nREADING TIME: {stats['reading_time']['formatted']}")
        print("=" * 50)


# Convenience function
def analyze_text(text: str) -> Dict:
    """Quick analysis function."""
    analyzer = TextStats(text)
    return analyzer.get_all_stats()


# Expose main classes/functions
__all__ = ['TextStats', 'analyze_text']
__version__ = '0.1.0'
