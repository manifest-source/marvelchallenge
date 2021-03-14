# Start with a small, Python-ready Debian stable image
FROM python:3.9-slim-buster

# Our server will listen on port 5000
EXPOSE 5000/tcp

# Make sure we have the necessary packages
RUN pip install Flask \
    requests \
    validators

# Normally more care/discussion about deploy location would be warranted
# but here we're just going to settle on /usr/local/...
RUN mkdir /usr/local/marvel
COPY src/ /usr/local/marvel/

# Launch on start
ENTRYPOINT ["sh", "/usr/local/marvel/startserver.sh"]