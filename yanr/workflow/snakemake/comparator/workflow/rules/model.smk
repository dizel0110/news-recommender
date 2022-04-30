rule get_work2vec:
    output: "data/models/word2vec/news_upos_cbow_300_2_2017.bin"
    shell: "python -m yanr url -s https://rusvectores.org/static/models/news_upos_cbow_300_2_2017.bin.gz -d {output}"
