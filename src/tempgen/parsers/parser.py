from abc import ABC, abstractmethod

class AbstractParser(ABC):
    @abstractmethod
    def parse(self, path, container, parse_entry, find_matches):
        """Parse file accessible via path property

        A general implementation of parse method should include following steps:
        1. Open file
        2. Read file data and transform it's meaningful content into string or an iterable of strings
        3. Call of find_matches function on such strings, resulting in an array of matches
        4. For each match found one should call parse_entry, resulting in an entry dictionary
        5. For each entry use entry "id" property as key and payload as value to populate the container provided

        Parameters
        ----------
        path : str
            Absolute path to file to be parsed
        container : Dict[str, [Dict[str, Any]]]
            Dictionary to be populated with parsed entries, contains key-value pairs with entry id property as key and entry payload dictionary as value
        parse_entry : callable
            Function that extracts entry (current implementation uses json parse) from matching string, returns entry payload dictionary
        find_matches : callable
            Function that searches the entry string for matches (that is, {{VALID_JSON_OBJECT}} patterns), returns array of matching substrings
        """
        pass
    
    @abstractmethod
    def replace(self, source_path, target_path, compute_match, replacements, update_external = False):
        """Replace file contents

        A general implementation of replace method should include following steps:
        1. Open file accessible via source_path in read mode
        2. Read file data and transform it so its text content becomes available for editing
        3. For each string in obtained text call compute_match, it results in an dictionary with {{VALID_JSON_OBJECT}} patterns as keys and computed substitutions as values
        4. For each match, value in the dictionary, replace match with value in text
        5. Create file at target_path and write modified text

        Parameters
        ----------
        source_path : str
            Absolute path to file to be parsed
        target_path : str
            Absolute path to file to be generated
        compute_match : callable
            Function that
                1. searches the entry string for matches (that is, {{VALID_JSON_OBJECT}} patterns)
                2. finds entry id in replacements dictionary
                3. populates to_replace dictionary parameter with "{{VALID_JSON_OBJECT}}" as key and replacement string as value
                4. if update_external is True, it updates external resources with replacement string
                5. returns to_replace dictionary
        replacements : Dict[str, str]
            Dictionary containing pairs of "{{VALID_JSON_OBJECT}}" keys and their replacements as values
        update_external : bool, optional
            Boolean, indicating whether external resources should be updated
        """
        pass
