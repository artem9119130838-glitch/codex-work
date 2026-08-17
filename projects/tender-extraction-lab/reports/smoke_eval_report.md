# Smoke Eval Report

- Timestamp: 2026-05-29 21:48:56
- ProjectRoot: E:\\Codex_Work\\projects\\tender-extraction-lab

## Gold XLSX present

- Status: OK
- Details: E:\Codex_Work\projects\tender-extraction-lab\data\gold\19-05\Сводка_лотов_верная 19-05.xlsx

## Tries results present

- Status: OK
- Details: E:\\Codex_Work\\projects\\tender-extraction-lab\legacy\\old_project\\ACT\\tries\\results.jsonl

## Legacy extractor present

- Status: OK
- Details: E:\\Codex_Work\\projects\\tender-extraction-lab\legacy\\old_project\\ACT\\tender_min_context_extractor_v1.py

## Eval script help runs

- Status: OK
- Details: Captured -h output

### eval_min_context_vs_gold_19_05.py -h

~~~text
usage: eval_min_context_vs_gold_19_05.py [-h] [--only-lot ONLY_LOT]
                                         gold_xlsx lots_root extractor_py
                                         out_md [sample_n]

Eval extractor output vs human-gold (19-05).

positional arguments:
  gold_xlsx            Path to gold XLSX
  lots_root            Lots root folder containing lot subfolders
  extractor_py         Extractor .py to run (prints JSONL)
  out_md               Output markdown report path
  sample_n             How many mismatches to print (default: 15)

options:
  -h, --help           show this help message and exit
  --only-lot ONLY_LOT  (optional) Evaluate exactly one lot folder name
~~~

