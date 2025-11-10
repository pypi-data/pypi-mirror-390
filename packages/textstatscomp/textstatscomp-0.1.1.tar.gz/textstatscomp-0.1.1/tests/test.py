from textstats import TextStats

# Sample text
text = """
Natural language processing is a fascinating field. 
It combines computer science and linguistics. 
Modern NLP uses machine learning extensively.
"""

# Create analyzer
stats = TextStats(text)

# Test basic functions
print("=== QUICK TESTS ===")
print(f"Word count: {stats.word_count()}")
print(f"Sentence count: {stats.sentence_count()}")
print(f"Lexical diversity: {stats.lexical_diversity():.3f}")
print(f"Average word length: {stats.average_word_length():.2f}")

# Full report
print("\n")
stats.print_report()