import os
import re
from datetime import datetime
from typing import Any


def conference_journal_header() -> tuple[list[str], list[str]]:
    """Generate markdown table headers for conferences and journals.

    This function creates the appropriate markdown table headers for displaying
    conference and journal information in tabular format.

    Returns:
        tuple: A tuple containing two lists:
            - conference_header: Markdown table headers for conferences
            - journal_header: Markdown table headers for journals

    Example:
        >>> conf_header, journal_header = conference_journal_header()
        >>> print(conf_header[0])
        |Publishers|Full/Homepage|Abbr/About|Acronym/Archive|Period/DBLP|...
    """
    o = "|Publishers|Full/Homepage|Abbr/About|"
    t = "|-         |-            |-         |"
    conference_header = [
        f"{o}Acronym/Archive|Period/DBLP|Top|CCF|Submission|Days Left|Main Conf.|Days Left|Location|Keywords/Google|\n",
        f"{t}-              |-          |-  |-  |-         |-        |          |-        |-       |-              |\n",
    ]
    journal_header = [
        f"{o}Acronym/Issues|Period/DBLP|Top/Early|CCF|CAS|JCR|IF|Keywords/Google|\n",
        f"{t}-             |-          |-        |-  |-  |-  |- |-              |\n",
    ]
    return conference_header, journal_header


class GenerateDataDict:
    """Generate data dictionaries from JSON input for conferences and journals.

    This class processes JSON data containing conference or journal information
    and generates structured dictionaries for markdown table generation, including
    publisher metadata, keyword-based indexing, and Mermaid diagram data.

    Attributes:
        cj (str): Type of publication ('conferences' or 'journals').
        ia (str): Publication type ('inproceedings' or 'article').
        json_dict (dict): Input JSON data containing publication information.
        path_spidered_cj (Optional[str]): Path to spidered conference/journal data.
        for_vue (bool): Whether to generate Vue.js-compatible format.

    Example:
        >>> generator = GenerateDataDict(
        ...     conferences_or_journals="conferences",
        ...     inproceedings_or_article="inproceedings",
        ...     json_dict=publication_data,
        ...     for_vue=True
        ... )
        >>> publisher_meta, publisher_abbr, keyword_abbr = generator.generate()
    """

    def __init__(
        self,
        conferences_or_journals: str,
        inproceedings_or_article: str,
        json_dict: dict,
        for_vue: bool = True,
        path_spidered_conferences_or_journals: str | None = None,
    ) -> None:
        """Initialize the GenerateDataDict instance.

        Args:
            conferences_or_journals (str): Type of publication ('conferences' or 'journals').
            inproceedings_or_article (str): Publication type ('inproceedings' or 'article').
            json_dict (dict): Input JSON data containing publication information.
            for_vue (bool, optional): Whether to generate Vue.js-compatible format.
                Defaults to True.
            path_spidered_conferences_or_journals (Optional[str], optional): Path to
                spidered conference/journal data. Defaults to None.
        """
        self.cj = conferences_or_journals
        self.ia = inproceedings_or_article
        self.json_dict = json_dict

        self.path_spidered_cj = path_spidered_conferences_or_journals
        self.for_vue = for_vue

    def generate(self) -> tuple[dict, dict, dict]:
        """Generate publisher metadata and keyword-based publication information.

        This method processes the JSON data to create three main dictionaries:
        1. Publisher metadata with URLs and descriptions
        2. Publisher abbreviation metadata with detailed publication info
        3. Keyword-based metadata for easy searching and categorization

        Returns:
            tuple: A tuple containing three dictionaries:
                - publisher_meta_dict: Publisher metadata including URLs and descriptions
                - publisher_abbr_meta_dict: Publication details indexed by publisher and abbreviation
                - keyword_abbr_meta_dict: Publication details indexed by keywords

        Example:
            >>> generator = GenerateDataDict(...)
            >>> pub_meta, pub_abbr, keyword_abbr = generator.generate()
        """
        publisher_meta_dict, keyword_abbr_meta_dict, publisher_abbr_meta_dict = {}, {}, {}

        for publisher in self.json_dict:
            # Extract and clean about texts
            abouts = [p for p in self.json_dict[publisher].get("txt_abouts", []) if p.strip()]

            # Extract and clean about URLs
            urls_about = [p.strip() for p in self.json_dict[publisher].get("urls_about", []) if p.strip()]

            # Get full names
            names_full = self.json_dict[publisher].get("names_full", [])

            # Get homepage URLs
            urls_homepage = self.json_dict[publisher].get("urls_homepage", [])

            # Extract and clean conference/journal URLs
            urls_cj = [url.strip() for url in self.json_dict[publisher].get(f"urls_{self.cj}", []) if url.strip()]

            # Create publisher URL with markdown formatting if homepage exists
            publisher_url = f"[{publisher}]({urls_homepage[0]})" if urls_homepage else publisher

            # Create full name URL with markdown formatting if available
            if names_full:
                full_url = f"[{names_full[0]}]({urls_homepage[0]})" if urls_homepage else names_full[0]
            else:
                full_url = publisher

            # Extract and clean remarks
            remarks = [p for p in self.json_dict[publisher].get("txt_remarks", []) if p.strip()]

            # Update publisher metadata
            publisher_meta_dict.setdefault(publisher, {}).update(
                {
                    "full_name_url": full_url,
                    "txt_abouts": abouts,
                    "txt_remarks": remarks,
                    "urls_about": urls_about,
                    "url_conferences_or_journals": f"[{self.cj.title()}]({urls_cj[0]})" if urls_cj else "",
                }
            )

            # Process each abbreviation (conference/journal)
            for abbr in self.json_dict[publisher][self.cj]:
                abbr_dict = self.json_dict[publisher][self.cj][abbr]

                # Get conference/journal info and keywords
                temp_dict, keywords = self.conference_or_journal(publisher_url, abbr, abbr_dict)

                # Generate mermaid diagram data
                mermaid = self.generate_mermaid_data(publisher, abbr, self.ia)

                publisher_abbr_meta_dict.setdefault(publisher, {}).setdefault(abbr, {}).update(temp_dict)
                publisher_abbr_meta_dict.setdefault(publisher, {}).setdefault(abbr, {}).update({"statistics": mermaid})

                # Index by keywords for quick lookup
                for keyword in keywords:
                    keyword_abbr_meta_dict.setdefault(keyword, {}).setdefault(abbr, {}).update(temp_dict)
                    keyword_abbr_meta_dict.setdefault(keyword, {}).setdefault(abbr, {}).update({"statistics": mermaid})

        return publisher_meta_dict, publisher_abbr_meta_dict, keyword_abbr_meta_dict

    def conference_or_journal(self, publisher_url: str, abbr: str, abbr_dict: dict) -> tuple[dict[str, Any], list[str]]:
        """Process conference or journal data and generate formatted information.

        This method processes individual conference or journal data, validates
        name lengths, extracts information, formats URLs, and generates table
        row data for markdown output.

        Args:
            publisher_url (str): Publisher's URL for markdown linking.
            abbr (str): Abbreviation identifier for the publication.
            abbr_dict (dict): Dictionary containing publication details including
                names, URLs, dates, scores, and keywords.

        Returns:
            tuple: A tuple containing:
                - dict: Contains formatted about text, remarks, and table row data
                - list: Sorted list of keywords for the publication

        Raises:
            ValueError: If full and abbreviated names have mismatched lengths.

        Example:
            >>> result = generator.conference_or_journal(
            ...     "https://publisher.com", "ICML", conf_data
            ... )
            >>> abouts, keywords = result
        """
        # Validate full and abbreviated names match in length
        self._validate_name_lengths(abbr_dict)

        # Extract basic information
        full_name, abbr_name = self._extract_full_abbr_names(abbr_dict)
        url_home = self._extract_homepage_url(abbr_dict)
        period = self._format_period_with_dblp(abbr_dict)

        # Extract text content
        abouts = self._extract_text_content(abbr_dict, "txt_abouts")
        remarks = self._extract_text_content(abbr_dict, "txt_remarks")
        url_about = self._extract_first_url(abbr_dict, "urls_about")

        # Process keywords with Google search links
        keywords, keywords_url = self._process_keywords(abbr_dict)

        # Format top score with early access link if available
        top = self._format_top_score(abbr_dict)

        # Generate appropriate table row based on type
        row_inf = self._generate_table_row(
            publisher_url, full_name, abbr_name, url_home, url_about, period, top, keywords_url, abbr, abbr_dict
        )

        return {"txt_abouts": abouts, "txt_remarks": remarks, "row_inf": row_inf}, keywords

    def _validate_name_lengths(self, abbr_dict: dict) -> None:
        """Validate that full and abbreviated names arrays have equal length.

        This method ensures that the full names and abbreviated names arrays
        have the same length, which is required for proper data processing.

        Args:
            abbr_dict (dict): Dictionary containing publication data.

        Raises:
            ValueError: If the lengths of names_full and names_abbr don't match.
        """
        full_names = abbr_dict.get("names_full", [])
        abbr_names = abbr_dict.get("names_abbr", [])
        if len(full_names) != len(abbr_names):
            raise ValueError(f"Length mismatch: {len(full_names)} {full_names} vs {len(abbr_names)} abbreviated names")

        return None

    def _extract_full_abbr_names(self, abbr_dict: dict) -> tuple[str, str]:
        """Extract full and abbreviated names from dictionary.

        This method extracts the appropriate full and abbreviated names based on
        the publication type (conferences vs journals).

        Args:
            abbr_dict (dict): Dictionary containing publication data.

        Returns:
            tuple: A tuple containing (full_name, abbr_name).
        """
        # For journals: use first full name from list; for conferences: use single name
        full_name = abbr_dict.get("names_full", [""])[0] if self.cj == "journals" else abbr_dict.get("name", "")
        abbr_name = abbr_dict.get("names_abbr", [""])[0]
        return full_name, abbr_name

    def _extract_homepage_url(self, abbr_dict: dict[str, Any]) -> str:
        """Extract and clean homepage URL.

        Args:
            abbr_dict (dict[str, Any]): Dictionary containing publication data.

        Returns:
            str: The first valid homepage URL, or empty string if none found.
        """
        urls = [u.strip() for u in abbr_dict.get("urls_homepage", []) if u.strip()]
        return urls[0] if urls else ""

    def _format_period_with_dblp(self, abbr_dict: dict[str, Any]) -> str:
        """Format publication period with DBLP link if available.

        Args:
            abbr_dict (dict[str, Any]): Dictionary containing publication data.

        Returns:
            str: Formatted period string with optional DBLP link.
        """
        start_year = abbr_dict.get("year_start", "")
        end_year = abbr_dict.get("year_end", "")

        # Create period string (e.g., "2020 - 2023" or "2020 -")
        period = f"{start_year} - {end_year}" if start_year and end_year else f"{start_year} -" if start_year else ""

        # Add DBLP link if acronym available
        if acronym_dblp := abbr_dict.get("acronym_dblp", ""):
            journal_conf = "journals" if self.cj == "journals" else "conf"
            dblp_url = f"https://dblp.org/db/{journal_conf}/{acronym_dblp}/index.html"
            period = f"[{period}]({dblp_url})"

        return period

    def _extract_text_content(self, abbr_dict: dict[str, Any], key: str):
        """Extract and clean text content from dictionary.

        Args:
            abbr_dict (dict[str, Any]): Dictionary containing publication data.
            key (str): Key to extract text content from.

        Returns:
            list[str]: List of non-empty text content.
        """
        return [text for text in abbr_dict.get(key, []) if text.strip()]

    def _extract_first_url(self, abbr_dict: dict[str, Any], key: str):
        """Extract first URL from a list in dictionary.

        Args:
            abbr_dict (dict[str, Any]): Dictionary containing publication data.
            key (str): Key to extract URLs from.

        Returns:
            str: The first valid URL, or empty string if none found.
        """
        urls = [url.strip() for url in abbr_dict.get(key, []) if url.strip()]
        return urls[0].split(",")[0] if urls else ""

    def _process_keywords(self, abbr_dict: dict[str, Any]):
        """Process keywords and convert to Google search URLs.

        Args:
            abbr_dict (dict[str, Any]): Dictionary containing publication data.

        Returns:
            tuple: A tuple containing (keywords, keywords_url) where keywords
                is a sorted list of unique keywords and keywords_url is a list
                of markdown-formatted Google search links.
        """
        keywords_dict = abbr_dict.get("keywords_dict", {})

        # Clean and sort keywords
        cleaned_keywords = {}
        for category, words in keywords_dict.items():
            if category.strip():
                sorted_words = sorted({word.strip() for word in words if word.strip()})
                cleaned_keywords[category.strip()] = sorted_words

        # Flatten keywords and remove duplicates
        all_keywords = []
        for category, words in cleaned_keywords.items():
            if words:
                all_keywords.extend(words)
            else:
                all_keywords.append(category)
        all_keywords = sorted(set(all_keywords))
        # Create Google search links for each keyword
        google_base = "https://www.google.com/search?q="
        keywords_url = [f"[{keyword}]({google_base}" + re.sub(r"\s+", "+", keyword) + ")" for keyword in all_keywords]

        # For category
        # Flatten keywords and remove duplicates
        all_keywords = []
        for category, words in cleaned_keywords.items():
            all_keywords.extend(words)
            all_keywords.append(category)
        all_keywords = sorted(set(all_keywords))

        return all_keywords, keywords_url

    def _format_top_score(self, abbr_dict: dict[str, Any]):
        """Format top score with optional early access link.

        Args:
            abbr_dict (dict[str, Any]): Dictionary containing publication data.

        Returns:
            str: Formatted top score with optional early access link.
        """
        is_top = "True" if abbr_dict.get("score_top", False) else "False"
        url_early_access = abbr_dict.get("url_early_access", "")
        return self._format_link(is_top, url_early_access)

    def _format_link(self, text, url):
        """Format text as markdown link if URL provided.

        Args:
            text (str): Text to display.
            url (str): URL to link to.

        Returns:
            str: Markdown-formatted link or plain text if no URL provided.
        """
        return f"[{text}]({url})" if url else text

    def _generate_table_row(
        self,
        publisher_url: str,
        full_name: str,
        abbr_name: str,
        url_home: str,
        url_about: str,
        period: str,
        top: str,
        keywords: list[str],
        abbr: str,
        abbr_dict: dict[str, Any],
    ):
        """Generate appropriate table row based on publication type."""
        if self.cj == "conferences":
            return self._generate_for_conference(
                publisher_url, full_name, abbr_name, url_home, url_about, period, top, keywords, abbr, abbr_dict
            )
        else:
            return self._generate_for_journal(
                publisher_url, full_name, abbr_name, url_home, url_about, period, top, keywords, abbr, abbr_dict
            )

    # Conferences
    def _generate_for_conference(
        self,
        publisher_url: str,
        full_name: str,
        abbr_name: str,
        url_home: str,
        url_about: str,
        period: str,
        top: str,
        keywords: list[str],
        abbr: str,
        abbr_dict: dict[str, Any],
    ):
        """Generate a markdown table row for conference information.

        Args:
            publisher_url: URL of the publisher
            full_name: Full name of the conference
            abbr_name: Abbreviated name of the conference
            url_home: Homepage URL
            url_about: About page URL
            period: Conference period/frequency
            top: Conference ranking/tier
            keywords: List of keywords
            abbr: Conference abbreviation
            abbr_dict: Dictionary containing conference details

        Returns:
            str: Formatted markdown table row
        """
        # Get archive URL and format link
        archive_url = self._extract_first_url(abbr_dict, "urls_archive")
        archive_display = self._format_link(abbr, archive_url)

        # Process conference dates
        abstract_due, start_date, today = self._process_conference_dates(abbr_dict)

        # Format date indicators for Vue or standard display
        abstract_indicator, start_indicator = self._format_date_indicators(abstract_due, start_date, today)

        # Get year URL for start date link
        year_url = abbr_dict.get("conf_url", "")

        # Build and return markdown table row
        return self._build_conference_row(
            publisher_url,
            full_name,
            abbr_name,
            url_home,
            url_about,
            archive_display,
            period,
            top,
            abbr_dict,
            abstract_due,
            abstract_indicator,
            start_date,
            start_indicator,
            year_url,
            keywords,
        )

    def _process_conference_dates(self, abbr_dict: dict[str, Any]):
        """Parse and return conference dates."""
        # Parse abstract due date
        abstract_due = None
        if due_str := abbr_dict.get("conf_abstract_due", "").strip():
            abstract_due = datetime.strptime(due_str, "%d/%m/%Y").date()

        # Parse conference start date
        start_date = None
        if start_str := abbr_dict.get("conf_date_start", "").strip():
            start_date = datetime.strptime(start_str, "%d/%m/%Y").date()

        # Get today's date
        today = datetime.strptime(datetime.now().strftime("%d/%m/%Y"), "%d/%m/%Y").date()

        return abstract_due, start_date, today

    def _format_date_indicators(self, abstract_due, start_date, today) -> tuple[str, str]:
        """Format date indicators for display."""
        abstract_indicator, start_indicator = "", ""

        if self.for_vue:
            # Vue.js template format
            if abstract_due:
                abstract_indicator = f"**{{{{ diffDate('{abstract_due}') }}}}**"
            if start_date:
                start_indicator = f"**{{{{ diffDate('{start_date}') }}}}**"
        else:
            # Standard day count format
            if abstract_due:
                abstract_indicator = (abstract_due - today).days if today <= abstract_due else "Expired"
            if start_date:
                start_indicator = (start_date - today).days if today <= start_date else "Expired"

        return abstract_indicator, start_indicator

    def _build_conference_row(
        self,
        publisher_url: str,
        full_name: str,
        abbr_name: str,
        url_home: str,
        url_about: str,
        archive_display: str,
        period: str,
        top: str,
        abbr_dict: dict[str, Any],
        abstract_due,
        abstract_indicator: str,
        start_date,
        start_indicator: str,
        year_url: str,
        keywords: list[str],
    ) -> str:
        """Construct conference table row string."""
        # Format date strings
        abstract_date_str = abstract_due.strftime("%d/%m/%Y") if abstract_due else ""
        start_date_str = start_date.strftime("%d/%m/%Y") if start_date else ""

        # Format start date with link if available
        start_date_display = self._format_link(start_date_str, year_url) if start_date_str else ""

        # Build table row
        return (
            f"|{publisher_url}|"
            f"{self._format_link(full_name, url_home)}|"
            f"{self._format_link(abbr_name, url_about)}|"
            f"{archive_display}|"
            f"{period}|"
            f"{top}|"
            f"{abbr_dict.get('score_ccf', '')}|"
            f"{abstract_date_str}|"
            f"{abstract_indicator}|"
            f"{start_date_display}|"
            f"{start_indicator}|"
            f"{abbr_dict.get('conf_location', '').strip()}|"
            f"{'; '.join(keywords)}|"
        )

    # Journals
    def _generate_for_journal(
        self,
        publisher_url: str,
        full_name: str,
        abbr_name: str,
        url_home: str,
        url_about: str,
        period: str,
        top: str,
        keywords: list[str],
        abbr: str,
        abbr_dict: dict[str, Any],
    ) -> str:
        r"""Generate a markdown table row for journal information.

        Args:
            publisher_url: URL of the publisher
            full_name: Full name of the journal
            abbr_name: Abbreviated name of the journal
            url_home: Homepage URL
            url_about: About page URL
            period: Publication period/frequency
            top: Journal ranking/tier
            keywords: List of keywords
            abbr: Journal abbreviation
            abbr_dict: Dictionary containing journal details

        Returns:
            str: Formatted markdown table row
        """
        # Get issues URL and format link
        issues_url = self._extract_first_url(abbr_dict, "urls_issues")
        issues_display = self._format_link(abbr, issues_url)

        # Build and return markdown table row
        return self._build_journal_row(
            publisher_url, full_name, abbr_name, url_home, url_about, issues_display, period, top, abbr_dict, keywords
        )

    def _build_journal_row(
        self,
        publisher_url: str,
        full_name: str,
        abbr_name: str,
        url_home: str,
        url_about: str,
        issues_display: str,
        period: str,
        top: str,
        abbr_dict: dict[str, Any],
        keywords: list[str],
    ) -> str:
        """Construct journal table row string."""
        return (
            f"|{publisher_url}|"
            f"{self._format_link(full_name, url_home)}|"
            f"{self._format_link(abbr_name, url_about)}|"
            f"{issues_display}|"
            f"{period}|"
            f"{top}|"
            f"{abbr_dict.get('score_ccf', '')}|"
            f"{abbr_dict.get('score_cas', '')}|"
            f"{abbr_dict.get('score_jcr', '')}|"
            f"{abbr_dict.get('score_if', '')}|"
            f"{'; '.join(keywords)}|"
        )

    # Mermaid data
    def generate_mermaid_data(self, publisher: str, abbr: str, inproceedings_or_article: str) -> list[str]:
        """Generate Mermaid diagram data from spidered README files.

        This method reads spidered data from README files and generates
        Mermaid chart configuration for visualizing publication statistics.

        Args:
            publisher (str): Publisher name.
            abbr (str): Publication abbreviation.
            inproceedings_or_article (str): Publication type.

        Returns:
            list[str]: Mermaid chart configuration lines, or empty list if no data found.
        """
        path_spidered_cj = self.path_spidered_cj if self.path_spidered_cj else ""
        path_readme = os.path.join(path_spidered_cj, publisher, abbr, inproceedings_or_article)
        full_readme = os.path.expanduser(os.path.join(path_readme, "README.md"))
        if not os.path.exists(full_readme):
            return []

        mermaid, data_dict = [], {}
        # |AAAI|1980|95|Proceedings of the First National Conference on Artificial Intelligence|
        regex = re.compile(r"\|.*\|([0-9]+)\|([0-9]+)\|.*\|")
        with open(full_readme, encoding="utf-8", newline="\n") as file:
            data_list = file.readlines()
        for line in data_list:
            if mch := regex.search(line):
                data_dict.setdefault(mch.group(1), []).append(mch.group(2))
        data_dict = {year: sum([int(n) for n in data_dict[year]]) for year in data_dict}

        # Mermaid
        if len(data_dict) != 0:
            mermaid = ["```mermaid\n"]
            mermaid.extend(
                [
                    "---\n",
                    "config:\n",
                    "    xyChart:\n",
                    "        width: 1200\n",
                    "        height: 600\n",
                    "    themeVariables:\n",
                    "        xyChart:\n",
                    '            titleColor: "#ff0000"\n',
                    "---\n",
                ]
            )
            mermaid.extend(["xychart-beta\n", f'    title "{abbr}"\n'])

            x_axis, bar, line = [], [], []
            for year in data_dict:
                x_axis.append(int(year))
                bar.append(data_dict[year])
                line.append(data_dict[year])

            idx = next((i for i, year in enumerate(x_axis) if year >= 2000), len(x_axis))
            x_axis, bar, line = x_axis[idx:], bar[idx:], line[idx:]

            mermaid.append(f"    x-axis {x_axis}\n")
            mermaid.append('    y-axis "Number of Papers"\n')
            mermaid.append(f"    bar {bar}\n")
            mermaid.append(f"    line {line}\n")
            mermaid.append("```\n")

        return mermaid
