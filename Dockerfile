FROM python:3.9-bullseye

RUN apt-get update -y && apt-get install -y inkscape latexmk texlive texlive-latex-extra

WORKDIR /pld

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src src
COPY main.py main.py

RUN mkdir -p /pld/build
CMD ["python", "main.py"]
