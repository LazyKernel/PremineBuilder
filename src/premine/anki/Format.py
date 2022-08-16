import re
import jaconv
from premine.data_sources.General import General
from premine.anki.static_data import voicing_map

class Format:

    template = '<table class="detailed-word"><tr class="reading">{reading}</tr><tr class="chars">{chars}</tr><tr class="type">{types}</tr><tr class="perc">{perc}</tr><tbody></tbody></table><div class="info-gloss"><ol class="gloss-definitions">{glossary}</ol></div>'

    kanji_regex = re.compile(r'[一-龯]+')

    def __init__(self) -> None:
        self.general = General()

    def parse_content(self, word: str, reading: str, glossaries: list):
        word_parts = self.parse_word_parts(word)
        readings, read_types = self.parse_readings_and_types(word_parts, reading)
        perc = ['' for _ in word_parts]
        final_form = Format.template.format(
            reading=self._table_wrap(readings),
            chars=self._table_wrap(word_parts),
            types=self._table_wrap(read_types),
            perc=self._table_wrap(perc),
            glossary=self._list_wrap(glossaries)
        )
        return final_form

    def _table_wrap(self, contents: list) -> str:
        return ''.join([f'<td>{content}</td>' for content in contents])

    def _list_wrap(self, contents: list) -> str:
        return ''.join([f'<li><span class="gloss-desc">{content}</span></li>' for content in contents])

    def parse_word_parts(self, word: str) -> list:
        word_parts = []
        current_part = ''
        for char in word:
            # if current char kanji
            if Format.kanji_regex.search(char):
                if current_part:
                    word_parts.append(current_part)
                    current_part = ''
                word_parts.append(char)
            else:
                current_part += char
        
        if current_part:
            word_parts.append(current_part)

        return word_parts
        
    def parse_readings_and_types(self, word_parts: list, reading: str) -> tuple:
        consumed_reading = reading
        readings = []
        read_types = []
        for part in word_parts:
            if Format.kanji_regex.search(part):
                results = self.general.get_kanji_info(part)
                for res in results:
                    for r in res['onyomi']:
                        norm = jaconv.kata2hira(r)
                        alternatives = self.get_alternative_readings(norm)
                        for alt in alternatives:
                            if consumed_reading.startswith(alt):
                                # correct reading
                                readings.append(alt)
                                read_types.append('On')
                                consumed_reading = consumed_reading.replace(alt, '', 1)
                    
                    for r in res['kunyomi']:
                        # kunyomi have dot to show where the kanji ends
                        dot_split = r.split('.')
                        norm = jaconv.kata2hira(dot_split[0])
                        if consumed_reading.startswith(norm):
                            # correct reading
                            readings.append(norm)
                            read_types.append('Kun')
                            consumed_reading = consumed_reading.replace(norm, '', 1)
            else:
                consumed_reading = consumed_reading.replace(part, '', 1)
                readings.append(part)
                read_types.append('')

        return readings, read_types

    def get_alternative_readings(self, word: str) -> tuple[str]:
        alternatives = [word]
        # reading ends in tsu
        if word[-1] == 'つ' and len(word) > 1:
            alternatives.append(word[:-1] + 'っ')
        # reading ends in ku
        if word[-1] == 'く' and len(word) > 1:
            alternatives.append(word[:-1] + 'っ')
        # consonant voicings in the beginning
        if word[0] in voicing_map:
            alternatives.extend([voiced + word[1:] for voiced in voicing_map[word[0]]])
        return tuple(alternatives)
