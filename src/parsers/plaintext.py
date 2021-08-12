def parse(path, container, parse_entry, find_matches):
	with open(path, 'r') as file:
		text = file.read()
		matches = find_matches(str(text))
		for match in matches:
			payload = parse_entry(match)
			container[payload['id']] = payload ## add check here for duplicates

def replace(source_path, target_path, compute_match, replacements, update_external = False):
	with open(path, 'rw') as file:
		text = file.read()
		local_to_replace = compute_match(text, {}, replacements, update_external)
		for match, value in local_to_replace.items():
			text = text.replace(match, value)
		file.write(text)
