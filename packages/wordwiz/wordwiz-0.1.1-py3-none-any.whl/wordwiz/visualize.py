from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud(
    freqs,
    width=1000, height=500,
    bg_color='white', cmap='Viridis'
):
    """
    Generate a WordCloud object from word frequencies.
    
    Parameters:
        freqs (dict or Counter): Word frequencies.
        width (int): Width of the word cloud image.
        height (int): Height of the word cloud image.
        bg_color (str): Background color (default: white).
        cmap (str): Matplotlib colormap (default: Set2).
        
    Returns:
        WordCloud: Generated word cloud object.
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
