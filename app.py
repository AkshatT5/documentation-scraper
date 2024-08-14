import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urljoin, urlparse
import io
import re
from xhtml2pdf import pisa
import html2text
import json
import os
import cssutils
import logging
from functools import lru_cache

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
cssutils.log.setLevel(logging.CRITICAL)

USER_AGENT = "DocumentationScraper/1.0 (+https://github.com/yourusername/documentation-scraper)"

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def is_relevant_url(url, base_url):
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    irrelevant_patterns = ['/blog/', '/archive/', '/old-versions/', '/deprecated/']
    return (
            url.startswith(base_url) and
            not any(pattern in path for pattern in irrelevant_patterns) and
            not path.endswith(('.pdf', '.zip', '.png', '.jpg', '.jpeg', '.gif'))
    )

def scrape_documentation(start_url, base_url, single_page=False, max_pages=5000, max_depth=10, time_limit_minutes=60):
    driver = setup_selenium()
    visited = set()
    to_visit = [(start_url, 0)]
    content = []
    start_time = time.time()
    end_time = start_time + (time_limit_minutes * 60)

    try:
        while to_visit and len(visited) < max_pages and time.time() < end_time:
            url, depth = to_visit.pop(0)
            if url in visited or (not single_page and depth > max_depth):
                continue

            st.text(f"Scraping: {url}")
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                st.warning(f"Timeout while loading {url}. Skipping...")
                continue

            main_content = None
            for selector in ['main', 'article', '.content', '#content', '.documentation', '#documentation']:
                try:
                    main_content = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if main_content:
                page_content = main_content.get_attribute('outerHTML')
            else:
                page_content = driver.find_element(By.TAG_NAME, "body").get_attribute('outerHTML')

            title = driver.title

            styles = driver.find_elements(By.TAG_NAME, "style")
            css_content = "\n".join([style.get_attribute('textContent') for style in styles])

            h = html2text.HTML2Text()
            h.ignore_links = False
            markdown_content = h.handle(page_content)

            content.append({
                "url": url,
                "title": title,
                "html_content": page_content,
                "markdown_content": markdown_content,
                "css": css_content
            })

            if single_page:
                break

            if depth < max_depth:
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and is_relevant_url(href, base_url) and href not in visited:
                            to_visit.append((href, depth + 1))
                    except:
                        continue

            visited.add(url)
            time.sleep(1)

        if time.time() >= end_time:
            st.warning(f"Scraping stopped due to time limit ({time_limit_minutes} minutes)")
        elif len(visited) >= max_pages:
            st.warning(f"Scraping stopped after reaching maximum number of pages ({max_pages})")

    finally:
        driver.quit()

    return content

@lru_cache(maxsize=100)
def clean_css(css_content):
    css_content = re.sub(r':[^{]+{', '{', css_content)
    
    open_brackets = css_content.count('{')
    close_brackets = css_content.count('}')
    if open_brackets > close_brackets:
        css_content += '}' * (open_brackets - close_brackets)
    
    try:
        sheet = cssutils.parseString(css_content)
        return sheet.cssText.decode()
    except:
        return "body { font-family: Arial, sans-serif; }"

def create_pdf(content):
    buffer = io.BytesIO()
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            pre {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }}
            code {{ font-family: Courier, monospace; }}
        </style>
    </head>
    <body>
    """
    
    for item in content:
        html_content += f"<h1>{item['title']}</h1>"
        html_content += f"<p><em>{item['url']}</em></p>"
        html_content += item['html_content']
        try:
            cleaned_css = clean_css(item['css'])
            html_content += f"<style>{cleaned_css}</style>"
        except Exception as e:
            logging.error(f"Failed to process CSS for {item['url']}: {str(e)}")
            st.warning(f"Failed to process CSS for {item['url']}. Skipping CSS for this page.")
        html_content += "<div style='page-break-after: always;'></div>"
    
    html_content += "</body></html>"

    pdf = None
    try:
        pdf = pisa.CreatePDF(html_content, dest=buffer)
    except Exception as e:
        logging.error(f"Failed to generate PDF: {str(e)}")
        st.error(f"Failed to generate PDF: {str(e)}")
        return None
    
    if pdf.err:
        logging.error(f"Error creating PDF: {pdf.err}")
        st.error(f"Error creating PDF: {pdf.err}")
        return None
    
    buffer.seek(0)
    return buffer

def save_markdown(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in content:
            f.write(f"# {item['title']}\n\n")
            f.write(f"URL: {item['url']}\n\n")
            f.write(item['markdown_content'])
            f.write("\n\n---\n\n")

def save_json(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

st.title('Comprehensive Documentation Scraper')

st.sidebar.header('Scraping Options')
start_url = st.sidebar.text_input('Enter the URL of the documentation:')
single_page = st.sidebar.checkbox('Scrape only this single page')

if not single_page:
    max_pages = st.sidebar.slider('Maximum number of pages to scrape', 1, 5000, 1000)
    max_depth = st.sidebar.slider('Maximum depth of scraping', 1, 20, 10)
    time_limit = st.sidebar.slider('Time limit for scraping (minutes)', 1, 120, 60)
else:
    max_pages = 1
    max_depth = 0
    time_limit = 1

if st.sidebar.button('Scrape Documentation'):
    if start_url:
        base_url = '/'.join(start_url.split('/')[:3])

        with st.spinner('Scraping documentation... This may take a while.'):
            content = scrape_documentation(start_url, base_url, single_page, max_pages, max_depth, time_limit)

        st.success(f"Scraped {len(content)} pages")

        st.subheader('Scraping Summary')
        st.write(f"Total pages scraped: {len(content)}")
        st.write(f"First page title: {content[0]['title']}")

        with st.spinner('Generating PDF... This may take a moment.'):
            pdf = create_pdf(content)

        if pdf:
            st.download_button(
                label="Download Full Documentation as PDF",
                data=pdf,
                file_name="documentation.pdf",
                mime="application/pdf",
                key="pdf_download"
            )
        else:
            st.error("Failed to generate PDF. Please check the logs for more information.")

        markdown_filename = "documentation.md"
        save_markdown(content, markdown_filename)
        with open(markdown_filename, "rb") as file:
            st.download_button(
                label="Download as Markdown",
                data=file,
                file_name=markdown_filename,
                mime="text/markdown",
                key="markdown_download"
            )

        json_filename = "documentation.json"
        save_json(content, json_filename)
        with open(json_filename, "rb") as file:
            st.download_button(
                label="Download as JSON",
                data=file,
                file_name=json_filename,
                mime="application/json",
                key="json_download"
            )

    else:
        st.error('Please enter a valid URL')