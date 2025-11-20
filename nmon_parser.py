# nmon_parser.py
# A lightweight NMON parser that converts sections to pandas DataFrames.

import pandas as pd
import re
from io import StringIO

class NMONParser:
    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.sections = {}

    def parse(self):
        lines = self.file_obj.read().splitlines()

        current_section = None
        section_data = []

        for line in lines:
            # Detect section headers, e.g., 'CPU_ALL, ...'
            if re.match(r"^[A-Z0-9_]+,", line):
                parts = line.split(',')
                section_name = parts[0]

                # Save previous section
                if current_section and section_data:
                    self._save_section(current_section, section_data)

                # Start new section
                current_section = section_name
                section_data = [parts]
            else:
                if current_section:
                    parts = line.split(',')
                    section_data.append(parts)

        # Save last section
        if current_section and section_data:
            self._save_section(current_section, section_data)

        return self.sections

    def _save_section(self, name, raw_rows):
        # Normalize rows to uniform length
        max_len = max(len(r) for r in raw_rows)
        normalized = [r + [''] * (max_len - len(r)) for r in raw_rows]

        df = pd.DataFrame(normalized[1:], columns=normalized[0])
        self.sections[name] = df
