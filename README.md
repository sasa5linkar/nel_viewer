# 🗺️ Serbian Named Entity Recognition Viewer

An interactive Streamlit web application for visualizing Named Entity Recognition (NER) results from Serbian texts, with automatic geographic entity mapping using Wikidata.

## Features

- 📄 **HTML NER Visualization**: Display NER-processed HTML files with highlighted entities
- 🗺️ **Interactive Maps**: Automatic mapping of geographic entities using Folium
- 🔗 **Wikidata Integration**: Fetch real coordinates and descriptions for location entities
- 📊 **Analytics**: Entity statistics and occurrence counting
- ⚡ **Smart Caching**: Streamlit-based caching for optimal performance
- 🌐 **Cloud-Ready**: Designed for Streamlit Community Cloud deployment

## Demo

You can see a live demo of this application at: [Your Streamlit Cloud URL]

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/serbian-ner-viewer.git
   cd serbian-ner-viewer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your HTML files**
   - Place your NER-processed HTML files in the `examples/` folder
   - Files should contain entities marked with `<mark class="entity">` tags
   - Location entities should have Wikidata QIDs in links

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Select an HTML file from the sidebar
   - Explore the results and map!

### Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

3. **Deploy your app**:
   - Click "New app"
   - Select your forked repository
   - Set main file: `app.py`
   - Click "Deploy"

4. **Add your data**:
   - Upload your NER HTML files to the `examples/` folder via GitHub
   - Commit and push - your app will automatically update

## File Format

Your HTML files should follow this structure:

```html
<mark class="entity" style="...">
    EntityText
    <span style="...">LOC
        <a href="https://www.wikidata.org/entity/Q123">Q123</a>
    </span>
</mark>
```

Where:
- `EntityText` is the text found in the document
- `LOC` indicates a location entity
- `Q123` is the Wikidata QID for the entity

## Example Data

The repository includes sample HTML files in the `examples/` folder:
- `serbian_geography.html` - Sample Serbian geography text
- `european_cities.html` - Sample European cities text

## Technology Stack

- **Frontend**: Streamlit
- **Mapping**: Folium + streamlit-folium  
- **Data Processing**: pandas, BeautifulSoup
- **APIs**: Wikidata REST API
- **Deployment**: Streamlit Community Cloud

## How It Works

1. **File Selection**: Choose an HTML file from the sidebar
2. **Entity Extraction**: Parse HTML to find location entities with Wikidata QIDs
3. **Coordinate Fetching**: Query Wikidata API for geographic coordinates
4. **Map Generation**: Create interactive Folium map with entity markers
5. **Analytics**: Display entity tables and statistics

## Features in Detail

### 🔍 Entity Processing
- Extracts only location entities (`LOC` type)
- Handles duplicate entities intelligently
- Counts entity occurrences across documents
- Tracks text variants of the same entity

### 🗺️ Interactive Mapping
- Color-coded markers by entity type
- Popup information with entity details
- Tooltips showing entity names and frequencies
- Automatic map centering and zoom

### ⚡ Performance
- Streamlit caching for API responses (1-hour TTL)
- Efficient duplicate detection
- Minimal API calls per entity
- Responsive UI with loading indicators

### 🌐 Network Resilience
- Proper User-Agent headers for API requests
- Comprehensive error handling
- Network troubleshooting guidance
- Graceful fallbacks for missing data

## Troubleshooting

### No entities found
- Ensure HTML files have proper entity markup
- Check that location entities have valid Wikidata QIDs
- Use the "Test Wikidata Connection" button

### Network errors
- Check internet connection
- Try upgrading requests: `pip install --upgrade requests urllib3`
- Corporate networks may require proxy configuration

### Performance issues
- Large files may take time to process
- Consider splitting large documents
- Cached results will be faster on subsequent loads

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Wikidata for providing geographic data
- Streamlit team for the excellent framework
- Serbian NLP community for inspiration

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Contact [your-email@example.com]

---

Made with ❤️ for the Serbian NLP community
