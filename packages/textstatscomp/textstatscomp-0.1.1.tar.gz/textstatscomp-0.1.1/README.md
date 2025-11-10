# TextStats

A lightweight Python package for text statistics and analysis.

# installation 
pip install textstatscomp

## Quick Start

from textstats import TextStats

text = "Your text here. This is a sample sentence."

Create analyzer
stats = TextStats(text)

Get statistics
print(f"Words: {stats.word_count()}")
print(f"Sentences: {stats.sentence_count()}")
print(f"Lexical Diversity: {stats.lexical_diversity()}")

Print full report
stats.print_report()
## Features

- Word, character, sentence, and paragraph counts
- Vocabulary analysis and lexical diversity
- Word frequency distribution
- Reading time estimation
- No external dependencies

## License

MIT License

