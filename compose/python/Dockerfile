# Set base image (host OS)
FROM python:3.10 AS compile-image

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# Install any dependencies
# RUN apk update && apk add python3-dev gcc libc-dev
RUN pip install --upgrade pip
#&& pip install -r /requirements.txt
RUN pip install python-dotenv
RUN pip install spacy
RUN pip install torch
RUN pip install requests
# check it out https://github.com/jd/tenacity
RUN pip install tenacity  
RUN pip install lxml
RUN pip install openai
RUN pip install openai[pinecone-client]
RUN pip install openai[datasets]
RUN pip install openai[embeddings]
RUN pip install sentence-transformers
RUN pip install transformers
RUN pip install jupyterlab
# RUN pip install ipykernel
 # for jupyter lab 
RUN pip install ipywidgets>=7.6
RUN pip install jupyterlab-widgets
RUN pip install plotly==5.10.0
RUN python -m spacy download en_core_web_sm
# for plotting
RUN pip install plotly
RUN pip install dash==2.5.0
RUN pip install jupyter-dash

FROM python:3.10-slim AS build-image

COPY --from=compile-image /opt/venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# By default, listen on port 8000
EXPOSE 8888/tcp
