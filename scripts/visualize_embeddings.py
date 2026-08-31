import json
import numpy as np
import umap
import plotly.express as px
import pandas as pd

with open('data/embedding/embedding_wiki.json') as f:
    chunks = json.load(f)

embeddings = np.array([chunk['embedding'] for chunk in chunks])
artists = [chunk['artist'] for chunk in chunks]

reducer = umap.UMAP(n_components=2, random_state=42)
embedding_2d = reducer.fit_transform(embeddings)

highlight_artists = ['Nas', 'Dr. Dre', 'Wu-Tang Clan', 'Jay-Z', 'Lauryn Hill', 'Fugees', 'GZA', 'Method Man', 'Ghostface Killah', 'Raekwon', 'Ol\' Dirty Bastard', 'Tupac Shakur', 'The Notorious B.I.G.', 'Snoop Dogg', 'Warren G', 'Ice Cube', 'Blackstreet']

# build a color category: highlighted artist name, or "Other"
color_group = [artist if artist in highlight_artists else 'Other' for artist in artists]

df = pd.DataFrame({
    'x': embedding_2d[:, 0],
    'y': embedding_2d[:, 1],
    'artist': artists,
    'group': color_group
})

fig = px.scatter(
    df, x='x', y='y', color='group',
    hover_data=['artist'],
    title='UMAP Projection of Wikipedia Chunk Embeddings',
    template='plotly_white',
    color_discrete_map={'Other': 'lightgray'}
)

fig.write_html('scripts/embedding_visualization.html')
fig.write_image('scripts/embedding_visualization.png')
fig.show()