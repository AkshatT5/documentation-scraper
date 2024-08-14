Here's the corrected README.md code formatted for GitHub:

# Comprehensive Documentation Scraper

## Description

The Comprehensive Documentation Scraper is a powerful tool designed to extract and process documentation from websites. It uses web scraping techniques to gather content and provides output in multiple formats including PDF, Markdown, and JSON. This tool is particularly useful for developers, technical writers, and anyone who needs to capture and reformat online documentation.

## Features

- Web scraping of documentation sites
- Intelligent content extraction
- Configurable scraping depth and page limits
- Time-limited scraping to prevent overlong operations
- Output in multiple formats:
  - PDF (with preserved styling)
  - Markdown (for easy reading and editing)
  - JSON (for structured data and further processing)
- User-friendly Streamlit interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/AkshatT5/documentation-scraper.git
   cd documentation-scraper
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually http://localhost:8501).

3. Enter the URL of the documentation you want to scrape in the sidebar.

4. Configure the scraping options:
   - Check "Scrape only this single page" if you want to limit scraping to just the initial URL.
   - Adjust the maximum number of pages to scrape.
   - Set the maximum depth for link following.
   - Set a time limit for the scraping operation.

5. Click "Scrape Documentation" to start the process.

6. Once scraping is complete, you can download the results in PDF, Markdown, or JSON format.

## Output Formats

### PDF

The PDF output preserves the styling of the original documentation and is suitable for reading or printing.

### Markdown

The Markdown output provides a clean, readable text format that's easy to edit or incorporate into other documents.

### JSON

The JSON output offers a structured data format, ideal for further processing or integration with other tools. It includes the following for each scraped page:

- URL
- Title
- HTML content
- Markdown content
- CSS styles

## Deployment

This app is deployed on Streamlit Cloud. You can access it from [here](https://documentation-scraper-jac9rhbkvqwzgmdg8gsctu.streamlit.app).

To deploy your own instance:

1. Fork this repository to your GitHub account.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud).
3. Click on "New app" and select your forked repository.
4. Select the main branch and enter: `app.py` as the main file path.
5. Click "Deploy".

## Contributing

Contributions to the Comprehensive Documentation Scraper are welcome! Here's how you can contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear, descriptive commit messages.
4. Push your changes to your fork.
5. Submit a pull request to the main repository.

Please ensure that your code adheres to the existing style and that you have tested your changes thoroughly.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web app framework
- [Selenium](https://www.selenium.dev/) for web scraping
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf) for PDF generation
- All other open-source libraries used in this project
