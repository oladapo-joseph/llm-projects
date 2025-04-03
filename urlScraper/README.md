# URL Scraper

## Project Overview
The **URL Scraper** is a powerful application designed to extract, process, and analyze URLs from web pages. Built with modern technologies, it leverages advanced machine learning techniques to provide intelligent filtering, semantic search, and efficient data management. The project is implemented in `app.py` and includes a user-friendly interface powered by Streamlit.

## Features
- **URL Extraction**: Automatically scrapes all URLs from a given webpage.
- **Semantic Filtering**: Uses embeddings to filter URLs based on context and relevance.
- **Vectorstore Integration**: Stores and manages embeddings for efficient similarity searches.
- **Streamlit Interface**: Provides an interactive and intuitive web-based UI.
- **Export Options**: Save results in CSV or JSON formats.
- **Error Handling**: Gracefully handles broken links and inaccessible pages.
- **Customizable**: Easily extendable to include additional features.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/urlScraper.git
    ```
2. Navigate to the project directory:
    ```bash
    cd urlScraper
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Run the application:
    ```bash
    streamlit run app.py
    ```
2. Open the provided URL in your browser to access the Streamlit interface.
3. Input the target URL or list of URLs.
4. View, filter, and export the extracted URLs.

## Key Concepts and Technologies

### Large Language Models (LLMs)
The application uses state-of-the-art LLMs, such as OpenAI's GPT models, to analyze and process text data. These models enable intelligent filtering and categorization of URLs based on semantic meaning.

### Embeddings
URLs and their metadata are converted into vector embeddings using tools like OpenAI's embedding models. This allows for advanced semantic search and contextual filtering.

### Vectorstore
The project integrates **FAISS (Facebook AI Similarity Search)** as a vectorstore to store and manage embeddings. This ensures efficient similarity searches and makes queries reusable even after the application is stopped.

### Streamlit
The application is built with Streamlit, providing a simple and interactive web-based interface. This makes the tool accessible to both technical and non-technical users.

## Use Cases
- **Web Scraping**: Gather and filter URLs for further data extraction.
- **SEO Analysis**: Analyze and categorize links for SEO purposes.
- **Data Analysis**: Extract and process URLs for research or analytics.
- **Semantic Search**: Perform context-aware searches on extracted URLs.

## Future Enhancements
- Add support for multi-threaded scraping to improve performance.
- Expand the Streamlit interface with additional visualization options.
- Integrate with external APIs for real-time data processing.
- Implement user authentication for secure access.

## Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License.
