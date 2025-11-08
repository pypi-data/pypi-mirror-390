# Genepy CLI

This is the HackInScience/Genepy command line client.

```bash
$ genepy list exercises
                    Exercises
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Done ┃ Title                                   ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│      │ Django view                             │
│      │ Hello World                             │
│      │ Print 42                                │
│      │ Number of seconds in a year             │
│      │ Using operators                         │
└──────┴─────────────────────────────────────────┘
```

This is currently usefull mostly for teachers to download/upload exercises:

```bash
$ genepy pull --page nsi
$ tree nsi
nsi
├── distance
│   ├── check.py
│   ├── initial_solution.py
│   ├── meta
│   ├── wording_en.md
│   └── wording_fr.md
└── print-42
    ├── check.py
    ├── initial_solution.py
    ├── meta
    ├── wording_en.md
    └── wording_fr.md

3 directories, 10 files
$ genepy -v push
INFO:genepy:[fr] Uploading 'Print 42'
INFO:genepy:[en] Uploading 'Print 42'
INFO:genepy:[fr] Uploading 'Distance'
INFO:genepy:[en] Uploading 'Distance'
```
