import genanki

model_vocab = genanki.Model(
    1169959216,
    'Vocab Premine',
    sort_field_index=1,
    fields=[
        {'name': 'Id'},
        {'name': 'Word'},
        {'name': 'ReadInfo'},
        {'name': 'Frequency'},
        {'name': 'Content'},
        {'name': 'WordAudio'},
        {'name': 'ExampleSentences'},
        {'name': 'Pitch'}
    ],
    templates=[
        {
            'name': 'Default Vocab',
            'qfmt': '''
                <style>
                .meaning-list, .kanji-readings, .info-gloss, .word-card {  display: none;  }
                table.detailed-word .perc,  table.detailed-word .refs,  table.detailed-word .type, table.detailed-word .reading, .k1, .k2, .k3, .k4, .k5, .o1, .o2, .o3, .o4, .o5, .n1, .n2, .n3, .n4, .n5 { color: transparent; }
                </style>
                {{Content}}
                <script src="_jquery-2.2.2.min.js"></script>
                <script src="_jquery.bpopup.min.js"></script>
                <script src="_jquery.jeditable.mini.js"></script>
                <script src="_kanjax_with_koohii.js"></script>
            ''',
            'afmt': '''
                {{Content}}
                {{WordAudio}}
                <br>
                {{ExampleSentences}}
                <script src="_jquery-2.2.2.min.js"></script>
                <script src="_jquery.bpopup.min.js"></script>
                <script src="_jquery.jeditable.mini.js"></script>
                <script src="_kanjax_with_koohii.js"></script>
            '''
        }
    ],
    css='''
        .card {
        font-family: DejimaMincho;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
        }
        .kanji {
        font-size: 64px;
        margin-bottom: 0px;
        }
        table.detailed-word, table.kanji-readings {
            border-collapse: collapse;
            vertical-align: middle;
            text-align: center;
            margin: 0px auto;
        }
        table.kanji-readings { font-size: 13pt; }
        table.kanji-readings td { border-left: 1px solid #DDD; }
        table.kanji-readings td:first-child { border-left: none; }
        table.kanji-readings tr { border-top: 1px solid #DDD; }
        table.kanji-readings tr:first-child { border-top: none; }
        table.kanji-readings td { padding: 0.25em; }
        table.kanji-readings td:nth-child(3),
        table.kanji-readings td:nth-child(5) { font-size: 10pt; }

        table.detailed-word td { border-left: 1px solid #DDD; }
        table.detailed-word td:first-child { border-left: none; }
        /*table.detailed-word tr { border-top: 1px solid #DDD; }
        table.detailed-word tr:first-child { border-top: none; }*/
        table.detailed-word .reading { font-size: 20pt; }
        table.detailed-word .chars { font-size: 36pt;
            border-bottom: 1px solid #DDD; border-top: 1px solid #DDD; }
        table.detailed-word .type { font-size: 12pt; font-style: italic; }
        table.detailed-word .perc { font-size: 9pt; font-style: italic; }
        .type td { padding-top: 0.5em;}
        .pos-desc {  color: #007200;  }
        .word-card { text-align: center; }
        .info-gloss { text-align: center; }
        .word-card h3 { font-size: 30pt; font-weight: normal; margin-bottom: 0.3em; margin-top: 0.3em; }

        .o1 { color: #f00; }
        .o2 { color: #f40; }
        .o3 { color: #f70; }
        .o4 { color: #ea0; }
        .o5 { color: #ec0; }
        .k1 { color: #00f; }
        .k2 { color: #06b; }
        .k3 { color: #0aa; }
        .k4 { color: #0b4; }
        .k5 { color: #0f0; }
        .n1, .n2, .n3, .n4, .n5 { color: #e0e; }

        .jp, .kanji_popup { font-family: DejimaMincho; }
        @font-face { font-family: DejimaMincho;  src: url('_dejima-mincho-r227.ttf'); }
    '''
)