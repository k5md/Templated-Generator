def replace(p, d):
    for replaced, replacement in d.items():
        paragraph_replace_text(p, replaced, replacement)

def paragraph_replace_text(paragraph, str, replace_str):
    """Return `paragraph` after replacing all matches for `regex` with `replace_str`.

    `regex` is a compiled regular expression prepared with `re.compile(pattern)`
    according to the Python library documentation for the `re` module.
    """
    # --- store how many times the string was replaced ---
    count = 0
    # --- a paragraph may contain more than one match, loop until all are replaced ---
    search_pos = 0
    while paragraph.text.find(str, search_pos) != -1:
        match = { "start": paragraph.text.find(str, search_pos), "end": paragraph.text.find(str, search_pos) + len(str) }
        search_pos = match['end']
        # --- calculate how much characters must be shifted to fix the match ---
        padding = (len(replace_str) - (match["end"] -match['start']) ) *count

        # --- when there's a match, we need to modify run.text for each run that
        # --- contains any part of the match-string.
        runs = iter(paragraph.runs)
        start, end = match['start'] + padding , match["end"] + padding

        # --- Skip over any leading runs that do not contain the match ---
        for run in runs:
            run_len = len(run.text)
            if start < run_len:
                break
            start, end = start - run_len, end - run_len

        # --- Match starts somewhere in the current run. Replace match-str prefix
        # --- occurring in this run with entire replacement str.
        run_text = run.text
        run_len = len(run_text)
        run.text = "%s%s%s" % (run_text[:start], replace_str, run_text[end:])
        end -= run_len  # --- note this is run-len before replacement ---

        # --- Remove any suffix of match word that occurs in following runs. Note that
        # --- such a suffix will always begin at the first character of the run. Also
        # --- note a suffix can span one or more entire following runs.
        for run in runs:  # --- next and remaining runs, uses same iterator ---
            if end <= 0:
                break
            run_text = run.text
            run_len = len(run_text)
            run.text = run_text[end:]
            end -= run_len
        count += 1
    # --- optionally get rid of any "spanned" runs that are now empty. This
    # --- could potentially delete things like inline pictures, so use your judgement.
    # for run in paragraph.runs:
    #     if run.text == "":
    #         r = run._r
    #         r.getparent().remove(r)
    return paragraph