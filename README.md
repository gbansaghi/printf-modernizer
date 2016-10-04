# printf-modernizer
Upgrades `printf` calls to `std::cout`.

## Usage
Run `python3 modernizer.py` from the root directory of your project. The script recursively checks all directories for `.cpp` files and processes them.

## About
A while ago, I refactored the logging facility of another project from `printf`-style variadic function calls to an `ostream`-derived solution. After the upgrade was complete, I wanted to automate the conversion to the new syntax. I thought a simple regex would be enough, but as it turns out, [that is impossible][stackoverflow]. Essentially, there is no way to tell a regex to "replace every match from one capturing group with the corresponding match of another capturing group", i.e. replace every token (such as `%s`) in the `printf` call with the corresponding argument. Indeed, the solution required three regular expressions to recognize and parse `printf` calls:

 - First, the script checks for anything that appears to be a `printf` call, capturing the format string and the arguments in named subgroups:
   ```
   printf\s*\((?P<tokens>".*")(?P<args>.*)\)
   ```
   
 - From the format string (the `tokens` group in the above regex), it extracts the tokens:
   ```
   (?P<token>%[-\+ #0]?(?:\d+(?:\.\d+)?)?[hljztL]?[hl]?[diuoxXfFeEgGaAspn])
   ```
   This actually matches a superset of valid tokens (such as `%lls`, i.e. `long long string`), however, since we are only interested in the presence (rather than the type) of the token, this is not a problem.
   
 - From the comma-delimited argument string, the arguments are parsed by:
   ```
   (?:,\s*(?P<arg>[^,;]+))
   ```

Ideally, the second and third regexes parse an equal number of elements (if this is not the case, a `// FIXME:` comment is inserted). Each token is then replaced by the corresponding argument, surrounded by `<<` operators and double quotes. Newlines are replaced with `std::endl` (this is more of a personal pet peeve).

At this point, the results are almost perfect, except for tokens at the very start or end, or right next to each other. In these cases, the regex results in an empty string being inserted into the stream. E.g.:

```c++
printf("%d is the magic number", 3);
```

would become

```c++
std::cout << "" << 3 << "is the magic number";
```

A final regex finds these occurrences and removes them. The original line is commented out (if it was not already) and the new line is inserted after it (commented out, if the original was commented).

*Note: the script reads the source files line by line, so multiline invocations of `printf` are not detected.*

[stackoverflow]: http://stackoverflow.com/questions/38257158/regex-for-replacing-printf-style-calls-with-ostream-left-shift-syntax
