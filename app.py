import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os
import re
from bs4 import BeautifulSoup
import requests

# Page config
st.set_page_config(
    page_title="Serbian NER Viewer", 
    page_icon="🗺️", 
    layout="wide"
)

st.title("🗺️ Serbian Named Entity Recognition Viewer")
st.markdown("View NER results and explore geographic entities on an interactive map")

@st.cache_data
def load_html_file(file_path):
    """Load and parse HTML file with NER results"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

@st.cache_data
def extract_all_entities_from_html(html_content):
    """Extract all entities from HTML for statistics"""
    soup = BeautifulSoup(html_content, 'html.parser')
    entity_type_counts = {}
    
    # Find all entity marks
    entity_marks = soup.find_all('mark', class_='entity')
    
    for mark in entity_marks:
        # Find the span with entity type and link
        span = mark.find('span')
        if span:
            span_text = span.get_text().strip()
            
            # Extract entity type (first word before the link)
            entity_type = span_text.split()[0] if span_text else ""
            
            if entity_type:
                if entity_type in entity_type_counts:
                    entity_type_counts[entity_type] += 1
                else:
                    entity_type_counts[entity_type] = 1
    
    return entity_type_counts

@st.cache_data
def extract_geographic_entities_from_html(html_content):
    """Extract geographic entities from HTML and get their coordinates"""
    soup = BeautifulSoup(html_content, 'html.parser')
    entities = []
    seen_qids = {}  # Cache for already processed QIDs
    entity_counts = {}  # Count occurrences of each entity
    
    # Find all entity marks
    entity_marks = soup.find_all('mark', class_='entity')
    
    for mark in entity_marks:
        # Get the entity text (first text node)
        entity_text = mark.contents[0].strip() if mark.contents else ""
        
        # Find the span with entity type and link
        span = mark.find('span')
        if span:
            span_text = span.get_text().strip()
            
            # Extract entity type (first word before the link)
            entity_type = span_text.split()[0] if span_text else ""
            
            # Only process location entities for mapping
            if entity_type == 'LOC':
                # Find the link within the span
                link = span.find('a')
                if link:
                    entity_url = link.get('href', '')
                    
                    # Extract QID from Wikidata URL
                    qid_match = re.search(r'Q\d+', entity_url)
                    if qid_match:
                        qid = qid_match.group()
                        
                        # Count occurrences
                        entity_key = f"{qid}_{entity_text}"
                        if entity_key in entity_counts:
                            entity_counts[entity_key] += 1
                        else:
                            entity_counts[entity_key] = 1
                        
                        # Check if we already processed this QID
                        if qid in seen_qids:
                            # Update the existing entry with new occurrence count
                            for entity in entities:
                                if entity['qid'] == qid:
                                    entity['occurrences'] = entity_counts[entity_key]
                                    # Add this text variant if it's different
                                    if entity_text not in entity['text_variants']:
                                        entity['text_variants'].append(entity_text)
                                    break
                        else:
                            # First time seeing this QID - fetch coordinates
                            coords = get_wikidata_coordinates_simple(qid)
                            if coords:
                                entities.append({
                                    'text': entity_text,
                                    'text_variants': [entity_text],  # Track different text forms
                                    'type': entity_type,
                                    'qid': qid,
                                    'lat': coords['lat'],
                                    'lon': coords['lon'],
                                    'label': coords.get('label', entity_text),
                                    'description': coords.get('description', ''),
                                    'occurrences': entity_counts[entity_key]
                                })
                                seen_qids[qid] = coords
    
    return entities

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_wikidata_coordinates_simple(qid):
    """Simple, direct approach to get coordinates from Wikidata"""
    
    # Direct, simple request to Wikidata
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    
    try:
        # Simple requests call with proper User-Agent header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entity_data = data['entities'][qid]
            
            # Extract label
            label = qid  # fallback to QID
            if 'labels' in entity_data:
                if 'en' in entity_data['labels']:
                    label = entity_data['labels']['en']['value']
                elif 'sr' in entity_data['labels']:
                    label = entity_data['labels']['sr']['value']
                elif entity_data['labels']:
                    # Get first available label
                    first_lang = list(entity_data['labels'].keys())[0]
                    label = entity_data['labels'][first_lang]['value']
            
            # Extract description
            description = ''
            if 'descriptions' in entity_data:
                if 'en' in entity_data['descriptions']:
                    description = entity_data['descriptions']['en']['value']
                elif 'sr' in entity_data['descriptions']:
                    description = entity_data['descriptions']['sr']['value']
                elif entity_data['descriptions']:
                    first_lang = list(entity_data['descriptions'].keys())[0]
                    description = entity_data['descriptions'][first_lang]['value']
            
            # Extract coordinates
            if 'claims' in entity_data and 'P625' in entity_data['claims']:
                coords_claim = entity_data['claims']['P625'][0]
                if 'mainsnak' in coords_claim and 'datavalue' in coords_claim['mainsnak']:
                    coordinates = coords_claim['mainsnak']['datavalue']['value']
                    result = {
                        'lat': coordinates['latitude'],
                        'lon': coordinates['longitude'],
                        'label': label,
                        'description': description
                    }
                    return result
            
            # No coordinates found - return None (will be cached by Streamlit)
            return None
            
        else:
            st.warning(f"HTTP {response.status_code} for {qid}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network error for {qid}: {str(e)}")
        st.info("💡 Try these solutions:")
        st.info("1. Check your internet connection")
        st.info("2. Try running: pip install --upgrade requests urllib3")
        st.info("3. If on corporate network, check proxy settings")
        return None
    except Exception as e:
        st.error(f"Unexpected error for {qid}: {str(e)}")
        return None

def create_map(entities):
    """Create a Folium map with entity markers"""
    if not entities:
        # Default map centered on Serbia
        m = folium.Map(location=[44.0, 21.0], zoom_start=7)
        return m
    
    # Calculate center of all entities
    lats = [e['lat'] for e in entities]
    lons = [e['lon'] for e in entities]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    
    # Color mapping for entity types
    colors = {
        'LOC': 'green',
        'PERS': 'blue',
        'ORG': 'red',
        'EVENT': 'purple',
        'WORK': 'orange',
        'DEMO': 'pink',
        'ROLE': 'gray'
    }
    
    # Add markers
    for entity in entities:
        color = colors.get(entity['type'], 'black')
        
        # Create text variants display
        text_variants = ", ".join(entity['text_variants']) if len(entity['text_variants']) > 1 else entity['text']
        
        popup_text = f"""
        <b>{entity['label']}</b><br>
        Type: {entity['type']}<br>
        Text in document: {text_variants}<br>
        Occurrences: {entity['occurrences']}<br>
        Description: {entity['description']}<br>
        <a href="https://www.wikidata.org/entity/{entity['qid']}" target="_blank">Wikidata</a>
        """
        
        folium.Marker(
            location=[entity['lat'], entity['lon']],
            popup=folium.Popup(popup_text, max_width=350),
            tooltip=f"{entity['label']} ({entity['occurrences']}x)",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    return m

def main():
    # Sidebar for file selection
    st.sidebar.header("📁 File Selection")
    
    # Look for HTML files in eval and Examples folders and subfolders
    html_files = []
    search_folders = ['examples', 'sample_data']
    
    for folder in search_folders:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.html'):
                        html_files.append(os.path.join(root, file))
    
    # Sort files to group by subfolder
    html_files.sort()
    
    if not html_files:
        st.error("No HTML files found! Please upload your NER HTML files to the 'examples' or 'sample_data' folder.")
        st.info("Expected folder structure:")
        st.code("""
examples/
├── subfolder1/
│   ├── document1.html
│   └── document2.html
├── subfolder2/
│   └── document3.html
└── single_file.html

sample_data/
├── test1.html
└── test2.html
        """)
        return
    
    selected_file = st.sidebar.selectbox(
        "Choose an HTML file:",
        html_files,
        format_func=lambda x: x.replace('\\', '/') if '\\' in x else x  # Show full path with forward slashes
    )
    
    if selected_file:
        # Load and display file info
        st.sidebar.success(f"Selected: {selected_file.replace(os.sep, '/')}")
        
        # Show file size and modification time
        # Show file size and modification time
        if os.path.exists(selected_file):
            file_size = os.path.getsize(selected_file)
            file_size_kb = file_size / 1024
            mod_time = os.path.getmtime(selected_file)
            from datetime import datetime
            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            st.sidebar.info(f"Size: {file_size_kb:.1f} KB")
            st.sidebar.info(f"Last modified: {mod_time_str}")
        
        # Main content area
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📄 NER Results")
            
            # Load HTML content
            html_content = load_html_file(selected_file)
            
            # Display HTML (entity highlighting)
            st.components.v1.html(html_content, height=600, scrolling=True)
            
            # Show file stats
            with st.expander("📊 File Statistics"):
                # Try to load corresponding stats file
                stats_file = selected_file.replace('.html', '_stats.json')
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        stats = json.load(f)
                    
                    st.json(stats)
                else:
                    st.info("No statistics file found")
        
        with col2:
            st.header("🗺️ Geographic Entities")
            
            # Add simple info about the feature
            st.info("📡 Fetching coordinates from Wikidata. Results are cached for better performance.")
            
            # Test connection button
            if st.button("🔍 Test Wikidata Connection"):
                with st.spinner("Testing connection to Wikidata..."):
                    test_result = get_wikidata_coordinates_simple("Q46")  # Test with Europe
                    if test_result:
                        st.success(f"✅ Connection successful! Found: {test_result['label']}")
                    else:
                        st.error("❌ Connection failed. Check network or see troubleshooting below.")
                        st.info("💡 Troubleshooting:")
                        st.info("• Check internet connection")
                        st.info("• Try: pip install --upgrade requests urllib3")
                        st.info("• Corporate network? Check proxy settings")
            
            # Extract entities and create map
            with st.spinner("Extracting geographic entities and fetching coordinates..."):
                geographic_entities = extract_geographic_entities_from_html(html_content)
            
            # Extract all entities for statistics
            all_entity_counts = extract_all_entities_from_html(html_content)
            
            if geographic_entities:
                # Display entity table for geographic entities
                df = pd.DataFrame(geographic_entities)
                st.dataframe(df[['text', 'type', 'label', 'description', 'occurrences']], height=200)
                
                # Create and display map
                m = create_map(geographic_entities)
                st_folium(m, width=700, height=400)
            else:
                st.warning("No geographic entities found with coordinates")
                # Still show a default map
                default_map = create_map([])
                st_folium(default_map, width=700, height=400)
            
            # Show entity type distribution (all entity types)
            st.subheader("📊 Entity Type Distribution")
            if all_entity_counts:
                # Convert to DataFrame for better visualization
                entity_df = pd.DataFrame(list(all_entity_counts.items()), columns=['Entity Type', 'Count'])
                entity_df = entity_df.sort_values('Count', ascending=False)
                
                # Display as bar chart
                st.bar_chart(entity_df.set_index('Entity Type'))
                
                # Also show as a table
                st.dataframe(entity_df, height=200)
            else:
                st.warning("No entities found in the document")

if __name__ == "__main__":
    main()
