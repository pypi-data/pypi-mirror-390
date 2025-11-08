import os
import re

from ..core._base import standardize_path
from .generate_dict import conference_journal_header


def create_safe_filename(text: str) -> str:
    """Create a safe filename across all platforms."""
    # Remove or replace invalid characters
    safe_text = re.sub(r'[<>:"/\\|?*]', "_", text)
    # Remove leading/trailing spaces and dots
    safe_text = safe_text.strip(" .")
    # Ensure it's not empty
    return safe_text if safe_text else "unnamed"


def conference_journal_informations() -> tuple[list[str], list[str]]:
    """Generate informational content for conferences and journals.

    This function provides additional informational content that can be
    included in markdown documentation for conferences and journals.

    Returns:
        tuple: A tuple containing two lists:
            - conference_inf: List of informational strings for conferences
            - journal_inf: List of informational strings for journals

    Example:
        >>> conf_info, journal_info = conference_journal_informations()
        >>> print(conf_info[0])
        !> [List of Upcoming International Conferences](...)
    """
    conference_inf = [
        "!> [List of Upcoming International Conferences](https://internationalconferencealerts.com/all-events.php)\n\n",
        "!> [Conferences in Theoretical Computer Science](https://www.lix.polytechnique.fr/~hermann/conf.php)\n\n",
    ]
    journal_inf = []
    return conference_inf, journal_inf


class WriteDataToMd:
    """Class to write publication data to Markdown files.

    This class provides methods to generate various markdown documentation files
    from processed publication data, including introduction files, categorized
    listings, publisher information, and statistics.

    Attributes:
        cj (str): Type of publication ('conferences' or 'journals').
        ia (str): Publication type ('inproceedings' or 'article').
        publisher_meta_dict (dict): Publisher metadata dictionary.
        publisher_abbr_meta_dict (dict): Publisher abbreviation metadata dictionary.
        keyword_abbr_meta_dict (dict): Keyword-based metadata dictionary.
        path_output (str): Output directory path for generated files.

    Example:
        >>> writer = WriteDataToMd(
        ...     conferences_or_journals="conferences",
        ...     inproceedings_or_article="inproceedings",
        ...     publisher_meta_dict=pub_meta,
        ...     publisher_abbr_meta_dict=pub_abbr,
        ...     keyword_abbr_meta_dict=keyword_abbr,
        ...     path_output="/output"
        ... )
        >>> writer.save_introductions()
    """

    def __init__(
        self,
        conferences_or_journals: str,
        inproceedings_or_article: str,
        publisher_meta_dict: dict,
        publisher_abbr_meta_dict: dict,
        keyword_abbr_meta_dict: dict,
        path_output: str,
    ) -> None:
        """Initialize with publication data and output path.

        Args:
            conferences_or_journals (str): Type of publication ('conferences' or 'journals').
            inproceedings_or_article (str): Publication type ('inproceedings' or 'article').
            publisher_meta_dict (dict): Publisher metadata dictionary.
            publisher_abbr_meta_dict (dict): Publisher abbreviation metadata dictionary.
            keyword_abbr_meta_dict (dict): Keyword-based metadata dictionary.
            path_output (str): Output directory path for generated files.
        """
        self.cj = conferences_or_journals  # "conferences" or "journals"
        self.ia = inproceedings_or_article  # "inproceedings" or "article"
        self.publisher_meta_dict = publisher_meta_dict
        self.publisher_abbr_meta_dict = publisher_abbr_meta_dict
        self.keyword_abbr_meta_dict = keyword_abbr_meta_dict
        self.path_output = standardize_path(path_output)

        self._default_inf = [
            "- The data for TOP, CCF, CAS, JCR, and IF are sourced from [easyScholar](https://www.easyscholar.cc/).\n\n"
        ]

    def save_introductions(self) -> None:
        """Save introduction file with all conferences/journals list.

        This method generates a comprehensive markdown file containing all
        conferences or journals in a tabular format with appropriate headers
        and informational content.

        Returns:
            None: This method does not return a value.

        Note:
            The output file is saved as 'Introductions_{type}.md' in the output directory.
        """
        conference_header, journal_header = conference_journal_header()
        conference_inf, journal_inf = conference_journal_informations()

        data_list = [f"# {self.cj.title()}\n\n"]
        data_list.extend(self._default_inf)

        # Add appropriate headers based on type
        if self.cj.lower() == "conferences":
            data_list.extend(conference_inf)
            data_list.append("|  " + conference_header[0])
            data_list.append("|- " + conference_header[1])
        else:
            data_list.extend(journal_inf)
            data_list.append("|  " + journal_header[0])
            data_list.append("|- " + journal_header[1])

        # Add all publications to table
        idx = 1
        for publisher in self.publisher_abbr_meta_dict:
            for abbr in self.publisher_abbr_meta_dict[publisher]:
                row_info = self.publisher_abbr_meta_dict[publisher][abbr]["row_inf"]
                data_list.append(f"|{idx}{row_info}\n")
                idx += 1

        # Write to file
        output_file = os.path.join(self.path_output, f"Introductions_{self.cj.title()}.md")
        with open(output_file, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(data_list)

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def _default_or_customized_keywords(self, keywords_category_name: str, keywords_list: list[str]):
        """Get default or customized keywords based on category and provided list.

        This method returns either a filtered list of keywords based on the provided
        category and keyword list, or all available keywords sorted alphabetically.

        Args:
            keywords_category_name (str): The category name for keywords filtering.
            keywords_list (list[str]): List of keywords to filter by.

        Returns:
            list[str]: List of keywords to use for processing.

        Example:
            >>> writer._default_or_customized_keywords("ai", ["machine learning", "deep learning"])
            ["deep learning", "machine learning"]
        """
        keywords = list(self.keyword_abbr_meta_dict.keys())

        # Get and sort publication types
        if keywords_category_name and keywords_list:
            _keywords = []
            for keyword in keywords_list:
                if keyword in keywords:
                    _keywords.append(keyword)
            return _keywords
        else:
            # default
            return sorted(keywords)

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def save_categories(self, keywords_category_name: str, keywords_list: list[str]) -> None:
        """Save publications categorized by keywords.

        This method generates markdown files organizing publications by their
        keywords, creating separate sections for each keyword category.

        Args:
            keywords_category_name (str): The category name for keywords filtering.
            keywords_list (list[str]): List of keywords to include in the output.

        Returns:
            None: This method does not return a value.

        Note:
            The output file is saved as 'Categories_{type}_{category}.md' in the output directory.
        """
        conference_header, journal_header = conference_journal_header()
        data_list = [f"# {self.cj.title()}\n\n"]
        data_list.extend(self._default_inf)

        # Add publications for each category
        for keyword in self._default_or_customized_keywords(keywords_category_name, keywords_list):
            data_list.append(f"## {keyword}\n\n")

            # Add appropriate header
            if self.cj == "conferences":
                data_list.extend(conference_header)
            else:
                data_list.extend(journal_header)

            # Add all publications in this category
            for abbr in self.keyword_abbr_meta_dict[keyword]:
                data_list.append(self.keyword_abbr_meta_dict[keyword][abbr]["row_inf"] + "\n")
            data_list.append("\n")

        # Write to file
        category_postfix = f"_{keywords_category_name.title()}" if keywords_category_name else ""
        with open(
            os.path.join(self.path_output, f"Categories_{self.cj.title()}{category_postfix}.md"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.writelines(data_list)

        return None

    def save_categories_separate_keywords(self) -> None:
        """Save publications categorized by keywords in separate files.

        This method generates individual markdown files for each keyword category,
        creating separate files for better organization and navigation.

        Returns:
            None: This method does not return a value.

        Note:
            Each keyword gets its own file saved as '{keyword}.md' in the
            Categories_{type} subdirectory.
        """
        conference_header, journal_header = conference_journal_header()

        # Add publications for each category
        for keyword in self.keyword_abbr_meta_dict:
            data_list = [f"# {keyword}\n\n"]
            data_list.extend(self._default_inf)

            # Add appropriate header
            if self.cj == "conferences":
                data_list.extend(conference_header)
            else:
                data_list.extend(journal_header)

            # Add all publications in this category
            for abbr in self.keyword_abbr_meta_dict[keyword]:
                data_list.append(self.keyword_abbr_meta_dict[keyword][abbr]["row_inf"] + "\n")
            data_list.append("\n")

            # Write keyword-specific file
            path_key = standardize_path(os.path.join(self.path_output, f"Categories_{self.cj.title()}"))
            # Create safe filename by replacing invalid characters
            safe_keyword = create_safe_filename(keyword).replace(" ", "_")
            with open(os.path.join(path_key, f"{safe_keyword}.md"), "w", encoding="utf-8", newline="\n") as f:
                f.writelines(data_list)

        return None

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def save_publishers(self) -> None:
        """Save publisher overview file with basic information.

        This method generates a markdown file containing an overview of all
        publishers with their basic information, about pages, and links to
        detailed publisher-specific files.

        Returns:
            None: This method does not return a value.

        Note:
            The output file is saved as 'Publishers_{type}.md' in the output directory.
        """
        data_list_pub = [
            f"# Introductions of Publishers and {self.cj.title()}\n\n",
            "| |Publishers|About US|Conferences/Journals|Separate Links|\n",
            "|-|-         |-       |-                   |-             |\n",
        ]
        idx = 1

        # Add each publisher to table
        for pub in self.publisher_meta_dict:
            meta = self.publisher_meta_dict[pub]

            full_name_url, about_url, cj_url, local_url = "", "", "", ""
            if x := meta.get("full_name_url", ""):
                full_name_url = x
            if x := meta.get("url_conferences_or_journals", ""):
                cj_url = x
            if pub_intr_urls := meta.get("urls_about", []):
                about_url = f"[About US]({pub_intr_urls[0]})"

            local_url = f"[{pub}](data/{self.cj.title()}/Publishers_{self.cj.title()}/{pub}.md)"

            # Create table row
            row = f"| {idx} | {full_name_url} | {about_url} | {cj_url} | {local_url} |\n"
            data_list_pub.append(row)
            idx += 1

        # Write to file
        with open(
            os.path.join(self.path_output, f"Publishers_{self.cj.title()}.md"), "w", encoding="utf-8", newline="\n"
        ) as f:
            f.writelines(data_list_pub)
        return None

    def save_publishers_separate_abbrs(self) -> None:
        """Save detailed publisher information in separate files.

        This method generates individual markdown files for each publisher,
        containing detailed information about their conferences/journals,
        including about sections, remarks, and statistics.

        Returns:
            None: This method does not return a value.

        Note:
            Each publisher gets its own file saved as '{publisher}.md' in the
            Publishers_{type} subdirectory.
        """
        conference_header, journal_header = conference_journal_header()
        for pub in self.publisher_meta_dict:
            data_list = [f"# {pub}\n\n"]
            data_list.extend(self._default_inf)
            meta = self.publisher_meta_dict[pub]

            # Add about and remarks sections
            for flag in ["txt_remarks", "txt_abouts"]:
                if temps := meta.get(flag, []):
                    temps[-1] = f"{temps[-1].rstrip()}\n\n"
                if temps:
                    data_list.append(f"## {flag.title()}\n\n")
                    data_list.extend(temps)

            # Add each conference/journal abbreviation
            if pub not in self.publisher_abbr_meta_dict:
                continue

            for abbr in self.publisher_abbr_meta_dict[pub]:
                data_list.append(f"## {abbr}\n\n")

                # Add appropriate header
                if self.cj == "conferences":
                    data_list.extend(conference_header)
                else:
                    data_list.extend(journal_header)

                # Add row information
                row_info = self.publisher_abbr_meta_dict[pub][abbr]["row_inf"]
                data_list.append(f"{row_info}\n\n")

                # Add remarks and about for this abbreviation
                for flag in ["txt_remarks", "txt_abouts"]:
                    if temps := self.publisher_abbr_meta_dict[pub][abbr].get(flag, []):
                        temps[-1] = f"{temps[-1].rstrip()}\n\n"
                    if temps:
                        data_list.append(f"### {flag.split('_')[-1].title()}\n\n")
                        data_list.extend(temps)

                # Add statistics if available
                if statistics := self.publisher_abbr_meta_dict[pub][abbr].get("statistics", []):
                    data_list.extend(statistics)
                    data_list.append("\n")

            # Write publisher-specific file
            path_pub = standardize_path(os.path.join(self.path_output, f"Publishers_{self.cj.title()}"))
            with open(os.path.join(path_pub, f"{pub}.md"), "w", encoding="utf-8", newline="\n") as f:
                f.writelines(data_list)

        return None

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def save_statistics(self, keywords_category_name: str, keywords_list: list[str]) -> None:
        """Save statistics overview file for keywords.

        This method generates a markdown file containing statistics overview
        for all keywords with links to their detailed pages.

        Args:
            keywords_category_name (str): The category name for keywords filtering.
            keywords_list (list[str]): List of keywords to include in the output.

        Returns:
            None: This method does not return a value.

        Note:
            The output file is saved as 'Statistics_{type}_{category}.md' in the output directory.
        """
        data_list = [
            f"# Statistics of keywords in {self.cj.title()}\n\n",
            "| |keywords|Separate Links|\n",
            "|-|-      |-             |\n",
        ]
        idx = 1

        # Add publications for each category
        for keyword in self._default_or_customized_keywords(keywords_category_name, keywords_list):
            # Create safe filename for URL
            safe_keyword = create_safe_filename(keyword).replace(" ", "_")
            ll = os.path.join("data", self.cj.title(), f"Statistics_{self.cj.title()}", f"{safe_keyword}.md")
            local_url = f"[Link]({ll})"

            # Create table row
            row = f"| {idx} | {keyword} | {local_url} |\n"
            data_list.append(row)
            idx += 1

        # Write to file
        category_postfix = f"_{keywords_category_name.title()}" if keywords_category_name else ""
        with open(
            os.path.join(self.path_output, f"Statistics_{self.cj.title()}{category_postfix}.md"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.writelines(data_list)
        return None

    def save_statistics_separate_abbrs(self) -> None:
        """Save detailed statistics for each keyword in separate files.

        This method generates individual markdown files for each keyword,
        containing detailed statistics and publication information.

        Returns:
            None: This method does not return a value.

        Note:
            Each keyword gets its own file saved as '{keyword}.md' in the
            Statistics_{type} subdirectory.
        """
        conference_header, journal_header = conference_journal_header()

        # Add publications for each category
        for keyword in self.keyword_abbr_meta_dict:
            data_list = [f"# {keyword}\n\n"]

            for abbr in self.keyword_abbr_meta_dict[keyword]:
                data_list.append(f"## {abbr}\n\n")

                # Add appropriate header
                if self.cj == "conferences":
                    data_list.extend(conference_header)
                else:
                    data_list.extend(journal_header)

                # Add row information
                row_info = self.keyword_abbr_meta_dict[keyword][abbr]["row_inf"]
                data_list.append(f"{row_info}\n\n")

                # Add statistics if available
                if statistics := self.keyword_abbr_meta_dict[keyword][abbr].get("statistics", []):
                    data_list.extend(statistics)
                    data_list.append("\n")

            # Write publisher-specific file
            path_pub = standardize_path(os.path.join(self.path_output, f"Statistics_{self.cj.title()}"))
            # Create safe filename by replacing invalid characters
            safe_keyword = create_safe_filename(keyword).replace(" ", "_")
            with open(os.path.join(path_pub, f"{safe_keyword}.md"), "w", encoding="utf-8", newline="\n") as f:
                f.writelines(data_list)

        return None
