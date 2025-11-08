import os

from .core._base import standardize_path
from .core.update_json import load_json_data, update_json_file
from .tools.generate_dict import GenerateDataDict
from .tools.write_dict import WriteDataToMd


def main_generate_md_files(
    full_json_c: str,
    full_json_j: str,
    full_json_k: str,
    path_output: str,
    path_spidered_bibs: str | None = None,
    keywords_category_name: str = "",
    for_vue: bool = True,
) -> None:
    """Generate comprehensive markdown documentation for academic publications.

    This function serves as the main entry point for processing conference and journal
    data from JSON files and generating various markdown documentation outputs. It
    handles both conference and journal data processing, creates categorized outputs,
    and generates statistics and publisher information files.

    The function processes three types of JSON files:
    - Conference data (full_json_c)
    - Journal data (full_json_j)
    - Keywords data (full_json_k)

    Args:
        full_json_c (str): Full path to the conferences JSON file containing
            conference publication data.
        full_json_j (str): Full path to the journals JSON file containing
            journal publication data.
        full_json_k (str): Full path to the keywords JSON file containing
            keyword categorization data.
        path_output (str): Output directory path where all generated markdown
            files will be saved.
        path_spidered_bibs (Optional[str], optional): Directory path containing
            spidered BibTeX files for additional data processing. Defaults to None.
        keywords_category_name (str, optional): Category name for filtering
            keywords. If provided, only keywords from this category will be
            processed. Defaults to "".
        for_vue (bool, optional): Whether to generate Vue.js-compatible format
            for date calculations and dynamic content. Defaults to True.

    Returns:
        None: This function does not return a value.
    """
    # Standardize all paths
    full_json_c = os.path.expanduser(full_json_c)
    full_json_j = os.path.expanduser(full_json_j)
    full_json_k = os.path.expanduser(full_json_k)

    path_output = standardize_path(path_output)

    path_spidered_bibs = standardize_path(path_spidered_bibs) if path_spidered_bibs else ""

    # Process keyword category name and load data
    keywords_category_name = keywords_category_name.lower().strip() if keywords_category_name else ""
    category_prefix = f"{keywords_category_name}_" if keywords_category_name else ""
    keywords_json = load_json_data(os.path.dirname(full_json_k), os.path.basename(full_json_k))
    keywords_list = keywords_json.get(f"{category_prefix}keywords", [])

    # Validate data availability
    if not keywords_list or not keywords_category_name:
        keywords_list, keywords_category_name = [], ""

    # Process both conferences and journals
    for cj, ia in zip(["conferences", "journals"], ["inproceedings", "article"], strict=True):
        # Update JSON data
        json_dict = {}
        if cj == "conferences":
            json_dict = update_json_file(full_json_c, cj)
        elif cj == "journals":
            json_dict = update_json_file(full_json_j, cj)
        if not json_dict:
            continue

        # Generate data dictionaries
        path_spidered_cj = os.path.join(path_spidered_bibs, cj.title())
        generater = GenerateDataDict(cj, ia, json_dict, for_vue, path_spidered_cj)
        publisher_meta_dict, publisher_abbr_meta_dict, keyword_abbr_meta_dict = generater.generate()
        if not (publisher_meta_dict and publisher_abbr_meta_dict and keyword_abbr_meta_dict):
            continue

        # Initialize writer and save all markdown files
        _path_output = os.path.join(path_output, f"{cj.title()}")
        save_data = WriteDataToMd(
            cj, ia, publisher_meta_dict, publisher_abbr_meta_dict, keyword_abbr_meta_dict, _path_output
        )
        # Save various documentation files
        save_data.save_introductions()
        save_data.save_categories(keywords_category_name, keywords_list)
        save_data.save_categories_separate_keywords()

        save_data.save_publishers()
        save_data.save_publishers_separate_abbrs()

        save_data.save_statistics(keywords_category_name, keywords_list)
        save_data.save_statistics_separate_abbrs()

    return None
