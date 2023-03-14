from typing import Callable, List, Tuple, Dict
from pathlib import Path
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import torch
import numpy as np

from .embed import Embedder, SBERTEmbedder, BarlowParagraphEmbedder
from .comparator import Comparator
from .reviewed_preprint import ReviewedPreprint
from .utils import split_paragraphs, split_sentences, split_sentences_nltk, stringify_doi

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
        if doc1_chunks and doc2_chunks:
            sim_matrix = self.comp.compare_dot(doc1_chunks, doc2_chunks)
            # sim_matrix = torch.rand(len(doc1_chunks), len(doc2_chunks))
            # sim_mat = sim_matrix.numpy()
        else:
            # empty tensor
            sim_matrix = torch.tensor([[0] * 20] * 15)
        return sim_matrix
    
DEFAULT_DOI = "10.1101/2021.05.12.443743"
DEFAULT_SAVE = Path("/data/demo_default_rev_preprint")
try:
    logging.info(f"Loading preprint {DEFAULT_DOI} from disk...")
    DEFAULT_REV_PREPRINT = ReviewedPreprint().from_dir(DEFAULT_SAVE / stringify_doi(DEFAULT_DOI))
except FileNotFoundError:
    logging.info(f"Preprint {DEFAULT_DOI} not found on disk, downloading...")
    DEFAULT_REV_PREPRINT = ReviewedPreprint(doi=DEFAULT_DOI) 
    logging.info(f"Preprint {DEFAULT_DOI} downloaded, saving to disk...")
    DEFAULT_REV_PREPRINT.save(DEFAULT_SAVE)

DEFAULT_REVIEW_IDX = 0
DEFAULT_SECTION = "results"
DEFAULT_DOC = [
    DEFAULT_REV_PREPRINT.review_process.reviews[DEFAULT_REVIEW_IDX].text,
    DEFAULT_REV_PREPRINT.preprint.sections[DEFAULT_SECTION],
]
CHUNKING_FNS = {
    "paragraphs": split_paragraphs,
    "sentences": split_sentences,  # split_sentences_nltk
}
# EMBEDDER = SBERTEmbedder()
EMBEDDER = BarlowParagraphEmbedder()
COMPARATOR = ComparisonVis(embedder=EMBEDDER)
DEFAULT_CUTOFF = 0.5
DEFAULT_SIM_MATRIX = torch.tensor([[0] * 20] * 15)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
# app = Dash(__name__)

styles = {
    'pre': {
        'font-family': 'menlo, courier, monospace',
    },
    'doc': [{
        'width': '95%',
        'height': '250px'
    },
    {
        'width': '95%',
        'height': '250px'
    }],

}


app.layout = html.Div([

    dcc.Store(id='selected-section', data=DEFAULT_SECTION),
    dcc.Store(id='selected-review', data=DEFAULT_REVIEW_IDX),
    dcc.Store(id='list-0'),
    dcc.Store(id='list-1'),
    dcc.Store(id='selected-chunk-indx-0', data=0),
    # dcc.Store(id='selected-chunk-0'),
    dcc.Store(id='selected-chunk-indx-1', data=0),
    # dcc.Store(id='selected-chunk-1'),
    dcc.Store(id='sim-matrix'),

    html.Div(className='row', children=[
        dcc.Input(id='preprint-doi', placeholder="DOI of reviewed preprint" , type='text', value=DEFAULT_REV_PREPRINT.doi),
        html.Button('Submit', id='submit-doi', n_clicks=0),
    ]),
    html.Div(className='row', children=[
        html.Div(className="six columns", children=[
            html.H4("Review"),
            dcc.Dropdown({str(i): f"review {i+1}" for i in range(3)}, str(DEFAULT_REVIEW_IDX), id='review', searchable=False),
            dcc.Textarea(
                id="sample-0",
                placeholder="type your review here...",
                value=DEFAULT_DOC[0],
                style=styles['doc'][0],
                readOnly=True,
            ),
        ]),
        html.Div(className="six columns", children=[
            html.H4("Preprint"),
            dcc.Dropdown(['introduction', 'methods', 'results', 'figures', 'discussion'], DEFAULT_SECTION, id='section', searchable=False),
            dcc.Textarea(
                id="sample-1",
                placeholder="type your sentence here...",
                value=DEFAULT_DOC[1],
                style=styles['doc'][1],
                readOnly=True,
            ),
        ])
    ]),
    # html.Div(className='row', children=[
    #     html.Button('Submit changes', id='submit-changes', n_clicks=0),
    # ]),
    html.Div(className='row', children=[
        html.Div(className="six columns", children=[
            dcc.Dropdown(['paragraphs', 'sentences'], 'paragraphs', id='split-fn-0', searchable=False),
        ]),
        html.Div(className="six columns", children=[
            dcc.Dropdown(['paragraphs', 'sentences'], 'paragraphs', id='split-fn-1', searchable=False),
        ])
    ]),
    html.Div(className='row', children=[
        html.H4("Similarity matrix"),
    ]),
    html.Div(className='row', children=[
        html.Div(className="four columns", children=[
            html.Span("Cutoff: "),
        ]),
        html.Div(className="four columns", children=[
            dcc.Slider(id='cutoff',min=0, max=1, marks=None, value=DEFAULT_CUTOFF, step=0.005, tooltip={"placement": "top", "always_visible": True}),
        ]),
    ]),
    html.Div(className='row', children=[
        dcc.Graph(
            id='heatmap',
            # figure=px.imshow(DEFAULT_SIM_MATRIX, template='seaborn'),
        )
    ]),
    html.Div(className='row', children=[
        html.Div(className="six columns", children=[
            html.Span("Selected index: "),
            html.Span(id='hover-data')
        ]),
    ]),
    html.Div(className='row', children=[
        html.Div(className="six columns", children=[
            html.H4("Selected paragraph from document 1:"),
            html.Textarea(id='selected-chunk-0', readOnly=True, style=styles['doc'][0],)
        ]),
        html.Div(className="six columns", children=[
            html.H4("Selected paragraph from document 2:"),
            html.Textarea(id='selected-chunk-1', readOnly=True, style=styles['doc'][1],)
        ]),
    ])
])


@app.callback(
    Output('selected-review', 'data'),
    Input('review', 'value'),
)
def get_input(review):
    return review

@app.callback(
    Output('selected-section', 'data'),
    Input('section', 'value'),
)
def get_input(section):
    return section

@app.callback(
    Output('sample-0', 'value'),
    Output('sample-1', 'value'),
    Input('submit-doi', 'n_clicks'),
    Input('selected-section', 'data'),
    Input('selected-review', 'data'),
    State('preprint-doi', 'value'),
)
def get_input(n_clicks, selected_section, selected_review, doi):
    rev_preprint = ReviewedPreprint(doi=doi)  # ouch need to be cached in State?
    # rev_preprint.save(DEFAULT_SAVE / stringify_doi(doi))
    review = None
    if selected_section and selected_review:
        if selected_review is not None:
            selected_review = int(selected_review)
        else:
            selected_review = DEFAULT_REVIEW_IDX
        if selected_review < len(rev_preprint.review_process.reviews):
            review = rev_preprint.review_process.reviews[selected_review].text
    review = "no review found" if review is None else review
    section = rev_preprint.preprint.sections.get(selected_section, None)
    section = "no results section found" if section is None else section
    return review, section

@app.callback(
    Output('sim-matrix', 'data'),
    Output('list-0', 'data'),
    Output('list-1', 'data'),
    Input('split-fn-0', 'value'),
    Input('split-fn-1', 'value'),
    Input('sample-0', 'value'),
    Input('sample-1', 'value'),
)
def get_input(split_fn_0, split_fn_1, sample_0, sample_1):
    chunks = [
        CHUNKING_FNS[split_fn_0](sample_0),
        CHUNKING_FNS[split_fn_1](sample_1),
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
    fig = px.imshow(
        sim_matrix,
        template="seaborn",
        # marginal_y="box"
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.update_yaxes(visible=False, showticklabels=False)
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
    Output('selected-chunk-0', 'value'),
    Output('selected-chunk-1', 'value'),
    Input('selected-chunk-indx-0', 'data'),
    Input('selected-chunk-indx-1', 'data'),
    Input('list-0', 'data'),
    Input('list-1', 'data'),
)
def get_selected_chunk(selected_0, selected_1, list_0, list_1):
    if selected_0 is not None and isinstance(selected_0, int) and list_0 and selected_0 < len(list_0):
        selected_chunk_0 = list_0[selected_0]
    else:
        selected_chunk_0 = ""
    if selected_1 is not None and isinstance(selected_1, int) and list_1 and selected_1 < len(list_1):
        selected_chunk_1 = list_1[selected_1]
    else:
        selected_chunk_1 = ""
    return selected_chunk_0, selected_chunk_1


if __name__ == '__main__':

    app.run_server(host="0.0.0.0", port=8050, use_reloader=True)
