import json
import os
import re
from typing import Any

from ._base import split_data_list, split_text_by_length


def load_json_data(path_json: str, filename: str) -> dict:
    try:
        file_path = os.path.join(path_json, filename)
        if not os.path.exists(file_path):
            return {}

        with open(file_path, encoding="utf-8", newline="\n") as file:
            return json.load(file)

    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}


def update_json_file(full_json_cj: str, conferences_or_journals: str) -> dict[str, Any]:
    """Update and format JSON file containing conference/journal data.

    This function loads JSON data, processes and formats text fields by splitting
    long text into appropriate lengths, checks for duplicate abbreviations, and
    saves the updated data back to the file.

    Args:
        full_json_cj (str): Full path to the conferences/journals JSON file
        conferences_or_journals (str): Type of publication ('conferences' or 'journals').

    Returns:
        dict[str, Any]: Processed JSON data dictionary.
    """
    # Load Json Data
    json_dict = load_json_data(os.path.dirname(full_json_cj), os.path.basename(full_json_cj))

    # Process and format text fields in JSON data.
    for pub in json_dict:
        for flag in ["txt_abouts", "txt_remarks"]:
            data_list = [p for p in json_dict[pub].get(flag, []) if p.strip()]
            temps = []
            for line in split_data_list(r"(\n+)", ["".join(data_list)], "next"):
                temps.extend(split_text_by_length(line, 105))
            if temps:
                json_dict[pub].update({flag: temps})

        for abbr in json_dict[pub][conferences_or_journals]:
            for flag in ["txt_abouts", "txt_remarks"]:
                data_list = [i for i in json_dict[pub][conferences_or_journals][abbr].get(flag, []) if i.strip()]
                temps = []
                for line in split_data_list(r"(\n+)", ["".join(data_list)], "next"):
                    temps.extend(split_text_by_length(line, 97))
                if temps:
                    json_dict[pub][conferences_or_journals][abbr].update({flag: temps})

    # Generate standard form
    abbr_dict = generate_standard_form(json_dict, conferences_or_journals)

    _, flag = CheckAcronymAbbrAndFullDict().run(abbr_dict)

    # Save updated JSON
    if flag and json_dict:
        with open(full_json_cj, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(json_dict, indent=4, sort_keys=True, ensure_ascii=True))

    return json_dict


def generate_standard_form(json_dict: dict[str, Any], conferences_or_journals: str):
    # Check for duplicate abbreviations in the data.
    abbr_list = []
    for pub in json_dict:
        if conferences_or_journals in json_dict[pub]:
            for abbr in json_dict[pub][conferences_or_journals]:
                if abbr in abbr_list:
                    raise ValueError(f"Duplicate abbreviation: {abbr} in {conferences_or_journals} {pub}")
                abbr_list.append(abbr)

    # Extract abbreviation and name data from all publications
    abbr_dict: dict[str, dict[str, list[str]]] = {}
    for pub in json_dict:
        if conferences_or_journals in json_dict[pub]:
            for abbr, v in json_dict[pub][conferences_or_journals].items():
                # Store both abbreviated names and full names for each abbreviation
                abbr_dict.update({abbr: {"names_abbr": v.get("names_abbr", []), "names_full": v.get("names_full", [])}})

    return abbr_dict


class CheckAcronymAbbrAndFullDict:
    def __init__(self, names_abbr="names_abbr", names_full="names_full"):
        self.names_abbr = names_abbr
        self.names_full = names_full

    def run(self, dict_data: dict[str, dict[str, list[str]]]) -> tuple[dict[str, dict[str, list[str]]], bool]:
        # Check if each acronym has equal number of abbreviations and full forms
        dict_data, length_check = self._validate_lengths(dict_data)

        # Check for duplicate abbreviations or full forms across all acronyms
        dict_data, duplicate_check = self._check_duplicates(dict_data)

        # Check for matching patterns in both abbreviations and full forms
        dict_data, abbr_match_check = self._check_matches(dict_data, self.names_abbr)
        dict_data, full_match_check = self._check_matches(dict_data, self.names_full)

        return dict_data, all([length_check, duplicate_check, abbr_match_check, full_match_check])

    def _validate_lengths(self, dict_data):
        """Validate that each acronym has equal number of abbreviations and full forms."""
        valid_data, all_valid = {}, True
        for acronym, value_dict in dict_data.items():
            names_abbr = value_dict.get(self.names_abbr, [])
            names_full = value_dict.get(self.names_full, [])

            if len(names_abbr) != len(names_full):
                all_valid = False
                print(
                    f"Length mismatch in '{acronym}': {len(names_abbr)} abbreviations vs {len(names_full)} full forms"
                )
            else:
                valid_data[acronym] = value_dict
        return valid_data, all_valid

    def _check_duplicates(self, data):
        """Check for duplicate abbreviations or full forms across all acronyms."""
        valid_data = {}
        all_unique = True
        seen_abbrs = set()
        seen_fulls = set()

        for acronym, values in data.items():
            has_duplicate = False

            # Check for duplicate abbreviations
            abbrs_lower = {abbr.lower() for abbr in values.get(self.names_abbr, [])}
            for abbr in abbrs_lower:
                if abbr in seen_abbrs:
                    print(f"Duplicate abbreviation '{abbr}' found in '{acronym}'")
                    has_duplicate = True
                else:
                    seen_abbrs.add(abbr)

            # Check for duplicate full forms
            fulls_lower = {full.lower() for full in values.get(self.names_full, [])}
            for full in fulls_lower:
                if full in seen_fulls:
                    print(f"Duplicate full form '{full}' found in '{acronym}'")
                    has_duplicate = True
                else:
                    seen_fulls.add(full)

            if not has_duplicate:
                valid_data[acronym] = values
            else:
                all_unique = False

        return valid_data, all_unique

    def _check_matches(self, data, key_type: str):
        """Check for exact matches in abbreviations or full forms between different acronyms."""
        valid_data = {}
        no_matches = True
        acronyms_bak = sorted(data.keys())

        for acronyms in [acronyms_bak, acronyms_bak[::-1]]:
            for i, main_acronym in enumerate(acronyms):
                # Normalize items: lowercase and remove parentheses
                main_items = [
                    item.lower().replace("(", "").replace(")", "") for item in data[main_acronym].get(key_type, [])
                ]

                # Create exact match patterns
                patterns = [re.compile(f"^{item}$") for item in main_items]

                matches_found = []

                # Compare with other acronyms
                for other_acronym in acronyms[i + 1 :]:
                    other_items = [
                        item.lower().replace("(", "").replace(")", "") for item in data[other_acronym].get(key_type, [])
                    ]

                    # Find matching items
                    matching_items = [item for item in other_items if any(pattern.match(item) for pattern in patterns)]

                    if matching_items:
                        matches_found.append([main_acronym, other_acronym, matching_items])

                if matches_found:
                    no_matches = False
                    print(f"Found matches in {key_type}: {matches_found}")
                else:
                    valid_data[main_acronym] = data[main_acronym]

        return valid_data, no_matches
