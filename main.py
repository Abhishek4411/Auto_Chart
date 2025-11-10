import streamlit as st
import graphviz
import re
from datetime import datetime

st.set_page_config(
    page_title="Auto Chart",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background: #ffffff; }
    [data-testid="stHeader"] { display: none; }
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        font-size: 1.6rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }
    .example-box {
        background: #f5f5f5;
        padding: 0.8rem;
        border-radius: 4px;
        border: 1px solid #ddd;
        margin-top: 1rem;
        font-size: 11px;
        font-family: 'Courier New', monospace;
    }
    .stDownloadButton button {
        background: #ffffff;
        border: 1px solid #d0d0d0;
        color: #333;
        padding: 8px 16px;
        font-size: 13px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📊 Auto Chart</h1></div>', unsafe_allow_html=True)

def parse_diagram(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    nodes = {}
    edges = []
    counter = 1
    
    arrow_pattern = r'(.+?)\s*-+>\s*(.+?)(?:\s*:\s*(.+))?$'
    
    for line in lines:
        match = re.match(arrow_pattern, line)
        if match:
            source = match.group(1).strip()
            target = match.group(2).strip()
            label = match.group(3).strip() if match.group(3) else ""
            
            if source and source not in nodes:
                nodes[source] = str(counter)
                counter += 1
            
            if target and target not in nodes:
                nodes[target] = str(counter)
                counter += 1
            
            if source and target:
                edges.append({
                    'from': nodes[source],
                    'to': nodes[target],
                    'label': label
                })
    
    return nodes, edges

def create_diagram(nodes, edges, direction):
    dot = graphviz.Digraph()
    
    node_count = len(nodes)
    
    if node_count > 15:
        fontsize = '10'
        nodesep = '1.5'
        ranksep = '2.0'
        node_width = '1.5'
        node_height = '0.5'
    elif node_count > 10:
        fontsize = '11'
        nodesep = '1.8'
        ranksep = '2.5'
        node_width = '1.8'
        node_height = '0.55'
    elif node_count > 6:
        fontsize = '12'
        nodesep = '2.2'
        ranksep = '3.0'
        node_width = '2.0'
        node_height = '0.6'
    else:
        fontsize = '12'
        nodesep = '2.5'
        ranksep = '3.5'
        node_width = '2.0'
        node_height = '0.6'
    
    dot.attr(
        rankdir=direction,
        bgcolor='white',
        nodesep=nodesep,
        ranksep=ranksep,
        splines='ortho',
        pad='0.8',
        dpi='300',
        overlap='false',
        concentrate='false'
    )
    
    dot.attr('node',
        shape='box',
        style='rounded',
        fontname='Arial',
        fontsize=fontsize,
        margin='0.3,0.2',
        height=node_height,
        width=node_width,
        color='#000000',
        fontcolor='#000000',
        penwidth='2'
    )
    
    dot.attr('edge',
        fontname='Arial',
        fontsize=fontsize,
        color='#000000',
        fontcolor='#000000',
        penwidth='2',
        arrowsize='0.9',
        labeldistance='1.5',
        labelangle='0'
    )
    
    for name, node_id in nodes.items():
        dot.node(node_id, name)
    
    for edge in edges:
        if edge['label']:
            dot.edge(edge['from'], edge['to'], label=f" {edge['label']} ")
        else:
            dot.edge(edge['from'], edge['to'])
    
    return dot

default_text = """Client -> Load Balancer : HTTPS
Load Balancer -> Web Server 1 : Route
Load Balancer -> Web Server 2 : Route
Web Server 1 -> App Server : Forward
Web Server 2 -> App Server : Forward
App Server -> Auth Service : Validate
Auth Service -> User DB : Query
User DB -> Auth Service : Result
Auth Service -> App Server : Token
App Server -> Business Logic : Process
Business Logic -> Primary DB : Read
Business Logic -> Cache : Check
Cache -> Business Logic : Data
Primary DB -> Business Logic : Data
Business Logic -> Message Queue : Publish
Message Queue -> Worker 1 : Consume
Message Queue -> Worker 2 : Consume
Worker 1 -> Email Service : Send
Worker 2 -> Notification : Push
App Server -> Monitoring : Log"""

col1, col2 = st.columns([2, 8])

with col1:
    st.subheader("Layout Direction")
    direction = st.radio(
        "direction_choice",
        ["Top to Bottom", "Left to Right"],
        index=1,
        label_visibility="collapsed"
    )
    dir_code = "TB" if direction == "Top to Bottom" else "LR"
    
    st.subheader("Diagram Description")
    user_text = st.text_area(
        "diagram_input",
        value=default_text,
        height=320,
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <div class="example-box">
        <b>Format:</b> A -> B : Label<br><br>
        <b>Example:</b><br>
        User -> Server<br>
        Server -> Database : Query
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("Diagram Preview")
    
    if user_text and user_text.strip():
        nodes, edges = parse_diagram(user_text)
        
        if nodes:
            diagram = create_diagram(nodes, edges, dir_code)
            
            try:
                png_data = diagram.pipe(format='png')
                st.image(png_data, width='stretch')
                
                st.write("")
                
                col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 7])
                
                with col_a:
                    st.download_button(
                        label="⬇ PNG",
                        data=png_data,
                        file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png"
                    )
                
                with col_b:
                    svg_data = diagram.pipe(format='svg')
                    st.download_button(
                        label="⬇ SVG",
                        data=svg_data,
                        file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
                        mime="image/svg+xml"
                    )
                
                with col_c:
                    st.download_button(
                        label="⬇ DOT",
                        data=diagram.source,
                        file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dot",
                        mime="text/plain"
                    )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Check Graphviz installation")
        else:
            st.info("Use format: A -> B")
    else:
        st.info("👈 Enter diagram description")