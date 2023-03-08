from typing import Callable, List, Tuple, Dict
from pathlib import Path
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import torch
import numpy as np

from .embed import Embedder, SBERTEmbedder
from .comparator import Comparator
from .reviewed_preprint import ReviewedPreprint
from .utils import split_paragraphs

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class ComparisonVis:

    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        logging.info(f"embedder :\n{embedder.model}")
        self.comp = Comparator(self.embedder)
        

    def get_comparison(self, doc1_chunks: List[str], doc2_chunks: List[str]) -> float:
        """Get the similarity matrix between two documents, each segemented into chunks (i.e. paragraphs or sentences).
        Args:
            doc1_chunks: The first document, segmented into chunks.
            doc2_chunks: The second document, segmented into chunks.
        Returns:
            The similarity matrix between the two documents.
        """
        if doc1_chunks is not None and doc2_chunks is not None:
            sim_matrix = self.comp.compare_dot(doc1_chunks, doc2_chunks)
            # sim_matrix = torch.rand(len(doc1_chunks), len(doc2_chunks))
            sim_mat = sim_matrix.numpy()
        else:
            # sim_matrix = []
            sim_mat = np.array([])
        return sim_matrix
    
REV_PREPRINT = ReviewedPreprint(doi="10.1101/2021.05.12.443743")
try:
    REV_PREPRINT.from_dir(Path("/data/demo_rev_preprint"))
except FileNotFoundError:
    REV_PREPRINT = ReviewedPreprint(doi="10.1101/2021.05.12.443743") 
    REV_PREPRINT.save(Path("/data/demo_rev_preprint"))

DOC = [
    REV_PREPRINT.review_process.reviews[0].text,
    REV_PREPRINT.preprint.results,
]
CHUNKING_FN = split_paragraphs
CHUNKS = [CHUNKING_FN(doc) for doc in DOC]
EMBEDDER = SBERTEmbedder()
COMPARATOR = ComparisonVis(embedder=EMBEDDER)
SIM_MATRIX = COMPARATOR.get_comparison(*CHUNKS)
CUTOFF = 0.8

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
# app = Dash(__name__)

styles = {
    'pre': {
        'font-family': 'menlo, courier, monospace',
    },
    'doc-input': [{
        'width': '100%',
        'height': '250px'
    },
    {
        'width': '100%',
        'height': '250px'
    }],
}


app.layout = html.Div([

    dcc.Store(id='list-0'),
    dcc.Store(id='list-1'),
    dcc.Store(id='selected-chunk-indx-0'),
    # dcc.Store(id='selected-chunk-0'),
    dcc.Store(id='selected-chunk-indx-1'),
    # dcc.Store(id='selected-chunk-1'),
    dcc.Store(id='sim-matrix'),

    html.Div(className='row', children=[
        html.Div(className="six columns", children=[
            html.H4("Document 1"),
            dcc.Textarea(
                id="sample-0",
                placeholder="type your review here...",
                value=DOC[0],
                style=styles['doc-input'][0],
            ),
        ]),
        html.Div(className="six columns", children=[
            html.H4("Document 2"),
            dcc.Textarea(
                id="sample-1",
                placeholder="type your sentence here...",
                value=DOC[1],
                style=styles['doc-input'][1],
            ),
        ]),
    ]),
    html.Div(className='row', children=[
        html.Button('Submit', id='submit', n_clicks=0),
    ]),
    html.Div(className='row', children=[
        html.H4("Similarity matrix"),
        dcc.Graph(
            id='heatmap',
            figure=px.imshow([[0, 0.5, 1.0], [0, 1.0, 0.5]]),
        )
    ]),
    html.Div(className='row', children=[
        dcc.Input(id='cutoff', type='range', min=0, max=1.0, value=CUTOFF, step=0.005),
    ]),
    html.Div(className='row', children=[
        html.Span("Selected index: "),
        html.Span(id='hover-data', style=styles['pre'])
    ]),
    html.Div(className='row', children=[
        html.Div(className="six columns", children=[
            html.Span("Selected paragraph from document 1:"),
            html.Span(id='selected-chunk-0')
        ]),
        html.Div(className="six columns", children=[
            html.Span("Selected paragraph from document 2:"),
            html.Span(id='selected-chunk-1')
        ]),
    ])
])


@app.callback(
    Output('sim-matrix', 'data'),
    Output('list-0', 'data'),
    Output('list-1', 'data'),
    Input('submit', 'n_clicks'),
    State('sample-0', 'value'),
    State('sample-1', 'value'),

)
def get_input(n_clicks, sample_0, sample_1):
    chunks = [
        CHUNKING_FN(sample_0),
        CHUNKING_FN(sample_1),
    ]
    new_sim_matrix = COMPARATOR.get_comparison(*chunks)
    return new_sim_matrix, chunks[0], chunks[1]

@app.callback(
    Output('heatmap', 'figure'),
    Input('sim-matrix', 'data'),  # makes it trigger on every change?
    Input('cutoff', 'value'),
)
def update_figure(sim_matrix, cutoff):
    # fig = go.Figure(data=go.Heatmap(
    #     z=sim_matrix,
    #     colorscale='Viridis',
    # ))
    cutoff = float(cutoff)
    sim_matrix = torch.tensor(sim_matrix)
    sim_matrix = torch.clamp(sim_matrix, cutoff, 1.0)
    fig = px.imshow(sim_matrix)
    return fig


@app.callback(
    Output('hover-data', 'children'),
    Output('selected-chunk-indx-0', 'data'),
    Output('selected-chunk-indx-1', 'data'),
    Input('heatmap', 'hoverData')
)
def display_hover_data(hoverData):
    logging.debug(f"hoverData: {hoverData}")
    x = hoverData['points'][0]['x'] if hoverData else ""
    y = hoverData['points'][0]['y'] if hoverData else ""
    span = html.Span(f"({x}, {y})")
    return span, y, x # x is the index of the chunk in doc 1, y is the index of the chunk in doc 0

@app.callback(
    Output('selected-chunk-0', 'children'),
    Output('selected-chunk-1', 'children'),
    Input('selected-chunk-indx-0', 'data'),
    Input('selected-chunk-indx-1', 'data'),
    Input('list-0', 'data'),
    Input('list-1', 'data'),
)
def get_selected_chunk(selected_0, selected_1, list_0, list_1):
    if selected_0 is None:
        return "", ""
    return html.P(list_0[selected_0]), html.P(list_1[selected_1])


if __name__ == '__main__':

    app.run_server(host="0.0.0.0", port=8050, use_reloader=True)
