include: "main.smk"

rule compare:
    input:
        habr=rules.model_habr.output,
        news3d=rules.model_news3d.output
    output: "data/postprocessed/comparator/habr_news3d_2017.json"
    shell: "python -m yanr comparator -s {input.habr} -s2 {input.news3d} -d {output}"

rule view:
    input: rules.compare.output
    output: "data/viewer/comparator/habr_news3d_2017/result.json"
    shell: "python -m yanr viewer.comparator -s {input} -d {output}"