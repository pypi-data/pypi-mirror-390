from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud(freqs, width=800, height=400, bg_color='white', cmap='viridis'):
    """
    Generate a WordCloud object from word frequencies.
    Parameters:
        freqs: dict or Counter - word frequencies
        width, height: int - image size
        bg_color: str - background color
        cmap: str - color map
    Returns:
        WordCloud object
    """
    wc = WordCloud(
        width=width,
        height=height,
        background_color=bg_color,
        colormap=cmap
    ).generate_from_frequencies(freqs)
    return wc

def show_wordcloud(wordcloud):
    """
    Display the generated WordCloud using Matplotlib.
    """
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
