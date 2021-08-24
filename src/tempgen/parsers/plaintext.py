from tempgen.parsers.parser import AbstractParser

class Parser(AbstractParser):
    def parse(self, path, container, parse_entry, find_matches):
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
            matches = find_matches(str(text))
            for match in matches:
                payload = parse_entry(match, path)
                container[payload['id']] = payload ## add check here for duplicates

    def replace(self, source_path, target_path, compute_match, replacements, update_external = False):
            text = ''
            with open(source_path, 'r', encoding='utf-8') as file:
                text = file.read()
                local_to_replace = compute_match(text, {}, replacements, source_path, update_external)
                for match, value in local_to_replace.items():
                    text = text.replace(match, value)
            with open(target_path, 'w', encoding='utf-8') as file:
                file.write(text)
