#!/usr/bin/env python3

import re
import os

INCLUDE = "#include [<\"](?:cstdio|stdio\.h)[>\"]"
PRINTF_CALL = 'printf\s*\((?P<tokens>".*")(?P<args>.*)\)'
PRINTF_TOKENS = '(?P<token>%[-\+ #0]?(?:\d+(?:\.\d+)?)?[hljztL]?[hl]?[diuoxXfFeEgGaAspn])'
PRINTF_ARGUMENTS = '(?:,\s*(?P<arg>[^,;]+))'
PRINTF_NEWLINES = '\\\\n'
IOSTREAM_ARG = '" << {} << "'
EMPTY_ARG = ' << ""|"" <<'
IOSTREAM_CALL = 'std::cout << {}'

rx_include = re.compile(INCLUDE)
rx_printf_call = re.compile(PRINTF_CALL)
rx_printf_tokens = re.compile(PRINTF_TOKENS)
rx_printf_arguments = re.compile(PRINTF_ARGUMENTS)
rx_printf_newlines = re.compile(PRINTF_NEWLINES)
rx_empty_arg = re.compile(EMPTY_ARG)

def process_include(line):
    m = rx_include.search(line)
    if not m:
        return

    return "//"+line+"#include <iostream>\n"

def process_call(line):
    m = rx_printf_call.search(line)
    if not m:
        return

    token_string = m.groupdict()["tokens"]
    arg_string = m.groupdict()["args"]

    tokens = rx_printf_tokens.findall(token_string)
    args = rx_printf_arguments.findall(arg_string)

    if len(tokens) != len(args):
        warning = "// FIXME: tokens/args mismatch?\n"
    else:
        warning = ""

    for i in range(min(len(tokens), len(args))):
        repl = IOSTREAM_ARG.format(args[i])
        token_string = rx_printf_tokens.sub(repl, token_string, 1)

    token_string = rx_printf_newlines.sub(IOSTREAM_ARG.format("std::endl"),
                                          token_string)
    token_string = rx_empty_arg.sub("", token_string)

    # If the original line is commented, comment the new line as well
    if re.match('\s*//\s*', line):
        new_line = line
        comment_string = "//"
    else:
        new_line = '//'+line
        comment_string = ""

    result = rx_printf_call.sub(IOSTREAM_CALL.format(token_string.strip()),
                                line)
    return new_line + warning + result

def process_file(file_path):
    content = "";
    with open(file_path, mode='r') as infile:
        for line in infile:
            if rx_include.search(line):
                line = process_include(line)
            if rx_printf_call.search(line):
                line = process_call(line)
            content += line
    with open(file_path, mode='w') as outfile:
        outfile.write(content)

def walk_dir(dir_path):
    abs_dir_path = os.path.abspath(dir_path)
    for file_path in os.listdir(abs_dir_path):
        abs_file_path = os.path.join(abs_dir_path, file_path)
        if os.path.isdir(abs_file_path):
            walk_dir(abs_file_path)
        elif os.path.basename(abs_file_path).endswith(".cpp"):
            process_file(abs_file_path)

def main():
    walk_dir(os.getcwd())

if __name__ == '__main__':
    main()
