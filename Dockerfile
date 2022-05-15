FROM python:3.8
WORKDIR /opt/yanr
COPY . .
RUN pip install --no-cache-dir -r ./requirements/prod.txt
ENV PYTHONPATH="${PYTHONPATH}:/opt/yanr"
WORKDIR /opt/yanr/work
ENTRYPOINT ["python", "-m", "yanr"]
CMD ["url", "-s", "https://www.example.com", "-d", "example.html"]