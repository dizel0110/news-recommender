include: "model.smk"

rule parse_habr:
    output: "data/parsed/habr.json"
    shell: "python -m yanr habr -s https://habr.com/ru/all/ -d {output}"

rule clean_habr:
    input: rules.parse_habr.output
    output: "data/preprocessed/cleaner/habr.json"
    shell: "python -m yanr cleaner -s {input} -d {output}"

rule morph_habr:
    input: rules.clean_habr.output
    output: "data/preprocessed/morpher/habr.json"
    shell: "python -m yanr morpher -s {input} -d {output}"

rule encode_habr:
    input:
        source=rules.morph_habr.output,
        model=rules.get_work2vec.output
    output: "data/encodings/work2vec/habr.json"
    shell: "python -m yanr encoder.word2vec -s {input.source} -d {output} -m {input.model}"

rule decode_habr:
    input:
        source=rules.encode_habr.output,
        model=rules.get_work2vec.output
    output: "data/decodings/work2vec/habr.json"
    shell: "python -m yanr decoder.word2vec -s {input.source} -d {output} -m {input.model}"

rule model_habr:
    input:
        source=rules.decode_habr.output,
        model=rules.get_work2vec.output
    output: "data/embeddings/work2vec/habr.json"
    shell: "python -m yanr word2vec -s {input.source} -d {output} -m {input.model}"

rule parse_news3d:
    output: "data/parsed/news3d.json"
    shell: "python -m yanr news3d -s https://3dnews.ru/news/rss/ -d {output}"

rule clean_news3d:
    input: rules.parse_news3d.output
    output: "data/preprocessed/cleaner/news3d.json"
    shell: "python -m yanr cleaner -s {input} -d {output}"

rule morph_news3d:
    input: rules.clean_news3d.output
    output: "data/preprocessed/morpher/news3d.json"
    shell: "python -m yanr morpher -s {input} -d {output}"

rule encode_news3d:
    input:
        source=rules.morph_news3d.output,
        model=rules.get_work2vec.output
    output: "data/encodings/work2vec/news3d.json"
    shell: "python -m yanr encoder.word2vec -s {input.source} -d {output} -m {input.model}"

rule decode_news3d:
    input:
        source=rules.encode_news3d.output,
        model=rules.get_work2vec.output
    output: "data/decodings/work2vec/news3d.json"
    shell: "python -m yanr decoder.word2vec -s {input.source} -d {output} -m {input.model}"

rule model_news3d:
    input:
        source=rules.decode_news3d.output,
        model=rules.get_work2vec.output
    output: "data/embeddings/work2vec/news3d.json"
    shell: "python -m yanr word2vec -s {input.source} -d {output} -m {input.model}"