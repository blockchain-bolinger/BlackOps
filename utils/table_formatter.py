#!/usr/bin/env python3
"""
Tabellenformatierung
"""
def format_table(headers: list, rows: list) -> str:
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    line = '|' + '|'.join(f" {h:<{w}} " for h, w in zip(headers, col_widths)) + '|'
    
    result = [separator, line, separator]
    for row in rows:
        line = '|' + '|'.join(f" {str(c):<{w}} " for c, w in zip(row, col_widths)) + '|'
        result.append(line)
    result.append(separator)
    return '\n'.join(result)