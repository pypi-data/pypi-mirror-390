# Wordwiz — Text Frequency & Word Cloud Generator

**Wordwiz** is a lightweight Python toolkit for analyzing and visualizing text data.

It allows you to:
- Preprocess and clean text  
- Generate word frequency statistics  
- Create customizable word clouds  

---

## Features

- Beginner-friendly API  
- Automatic stopword and punctuation removal  
- Word frequency counting and summary stats  
- Beautiful word cloud visualizations with custom colors and themes  
- Works with any text source, including `.txt` files  

---

## Installation

Install from PyPI:
```bash
pip install wordwiz
```

Upgrade to the latest version:
```bash
pip install --upgrade wordwiz
```

---

## Usage Example

```python
from wordwiz import get_word_frequencies, generate_wordcloud, show_wordcloud, show_basic_stats

text = """
Python makes data analysis simple and fun.
Machine learning, natural language processing, and visualization 
are powerful with Python and its amazing ecosystem of libraries.
"""

# Step 1: Compute word frequencies
freqs = get_word_frequencies(text)

# Step 2: View text stats
show_basic_stats(freqs)

# Step 3: Create and display the word cloud
wc = generate_wordcloud(freqs, bg_color='black', cmap='plasma')
show_wordcloud(wc)
```

### Example Output
```
📊 TEXT STATS
Total words (after cleaning): 18
Unique words: 13
Top 5 most common words:
  • python: 2
  • makes: 1
  • data: 1
  • analysis: 1
  • simple: 1
```
🖼️ *A colorful word cloud will be displayed.*

---

## Customization

Adjust visualization options:
```python
wc = generate_wordcloud(
    freqs,
    width=1000,
    height=500,
    bg_color='white',
    cmap='cool'
)
show_wordcloud(wc)
```

Show only the top 30 words:
```python
top_words = dict(freqs.most_common(30))
wc = generate_wordcloud(top_words)
show_wordcloud(wc)
```

Upload and preprocess a document:
```python
file_path = "example.docx"  # or "notes.txt"
text = read_file(file_path)
clean_tokens = preprocess_text(text)
```

---

## Function Reference

| Function | Description |
|-----------|--------------|
| `preprocess_text(text)` | Cleans text (lowercase, tokenize, remove stopwords) |
| `get_word_frequencies(text)` | Returns a Counter with word frequency counts |
| `generate_wordcloud(freqs, ...)` | Creates a WordCloud object from frequencies |
| `show_wordcloud(wc)` | Displays the generated word cloud |
| `show_basic_stats(freqs, top_n=5)` | Prints word statistics and top frequent words |

---

## Ideal For

- Text data exploration and EDA  
- NLP preprocessing pipelines  
- Sentiment or content analysis (tweets, reviews, blogs)  
- Academic or presentation-ready visualizations  

---

## Requirements

- Python ≥ 3.8  
- Dependencies: `nltk`, `wordcloud`, `matplotlib`  

Installed automatically when you run:
```bash
pip install wordwiz
```

---

## License

Licensed under the **MIT License**.  
See the full text in [`LICENSE.txt`](LICENSE.txt).

---

## Author

**Dhruv Marwal**  
📧 dhruvmarwal@gmail.com  
🌐 [GitHub](https://github.com/DhruvMarwal)

---

## ⭐ Support

If you like **WordViz**, please ⭐ it on GitHub — it helps others discover it!  
Feedback, ideas, or issues → [Open an Issue](https://github.com/dhruvmarwal/wordviz/issues)
