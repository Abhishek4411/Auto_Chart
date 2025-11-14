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
    .diagram-container {
        width: 100%;
        height: 800px;
        overflow: auto;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        background: #fafafa;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .diagram-container svg {
        width: auto !important;
        height: auto !important;
        min-width: 100%;
        display: block;
        margin: 0 auto;
    }
    .diagram-container img {
        width: auto !important;
        height: auto !important;
        max-width: none !important;
        display: block;
        margin: 0 auto;
    }
    .zoom-controls {
        text-align: center;
        margin-bottom: 10px;
        font-size: 12px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📊 Auto Chart</h1></div>', unsafe_allow_html=True)

def wrap_text(text, max_chars=20):
    """Wrap long text into multiple lines for better node display"""
    if len(text) <= max_chars:
        return text

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) <= max_chars:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(' '.join(current_line))

    return '\\n'.join(lines)

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

def create_diagram(nodes, edges, direction, auto_layout=True):
    """
    Create optimized diagram with better visibility and no crossovers
    Uses advanced Graphviz strategies for professional-quality diagrams
    """
    # Use dot engine with strict mode for better layout
    dot = graphviz.Digraph(engine='dot', strict=False)

    node_count = len(nodes)

    # Auto-detect optimal layout direction for complex diagrams
    if auto_layout and node_count > 12:
        direction = "TB"  # Force Top-to-Bottom for complex diagrams

    # Dynamic sizing based on complexity with improved metrics
    if node_count > 20:
        fontsize = '14'
        nodesep = '1.2'
        ranksep = '2.0'
        node_width = '2.5'
        node_height = '0.8'
        size = '24,36'
        max_text_chars = 18
    elif node_count > 15:
        fontsize = '15'
        nodesep = '1.5'
        ranksep = '2.4'
        node_width = '2.8'
        node_height = '0.85'
        size = '20,30'
        max_text_chars = 20
    elif node_count > 10:
        fontsize = '16'
        nodesep = '2.0'
        ranksep = '3.0'
        node_width = '3.0'
        node_height = '0.9'
        size = '18,26'
        max_text_chars = 22
    elif node_count > 6:
        fontsize = '17'
        nodesep = '2.5'
        ranksep = '3.5'
        node_width = '3.2'
        node_height = '0.95'
        size = '16,24'
        max_text_chars = 24
    else:
        fontsize = '18'
        nodesep = '3.0'
        ranksep = '4.0'
        node_width = '3.5'
        node_height = '1.0'
        size = '14,20'
        max_text_chars = 25

    # Core graph attributes with advanced layout strategies
    dot.attr(
        rankdir=direction,
        bgcolor='white',
        nodesep=nodesep,
        ranksep=ranksep,
        splines='spline',  # Smooth curves for fewer crossovers
        pad='1.2',
        dpi='300',
        size=f'{size}!',  # Force size instead of shrinking
        ratio='fill',  # Fill the size we specified
        overlap='false',
        overlap_scaling='15',  # Increased scaling for better separation
        sep='+0.8',  # More separation between components
        concentrate='false',  # Don't merge edges (prevents confusion)
        compound='true',  # Better edge routing
        newrank='true',  # Better ranking algorithm (dot only)
        remincross='true',  # Minimize edge crossings
        searchsize='150',  # More thorough layout search
        mclimit='20.0',  # Better edge routing limits
        ordering='out',  # Order nodes by outgoing edges
        nslimit='10',  # Network simplex limit for better ranking
        nslimit1='10',  # Additional ranking constraint
        center='true',  # Center the drawing
        margin='0.5',  # Margin around the diagram
        esep='+3',  # Edge separation
        smoothing='spring',  # Spring model for smoother layout
        beautify='true'  # Enable beautification
    )

    # Node styling with better visibility
    dot.attr('node',
        shape='box',
        style='rounded,filled',
        fillcolor='#f0f8ff',  # Light background for better contrast
        fontname='Arial Bold',
        fontsize=fontsize,
        margin='0.4,0.3',
        height=node_height,
        width=node_width,
        color='#2c3e50',
        fontcolor='#000000',
        penwidth='2.5'
    )

    # Edge styling for better visibility
    dot.attr('edge',
        fontname='Arial',
        fontsize=fontsize,
        color='#34495e',
        fontcolor='#2c3e50',
        penwidth='2.5',
        arrowsize='1.0',
        labeldistance='2.0',
        labelangle='0',
        labelfontsize=str(int(fontsize) - 2),
        minlen='1'  # Minimum edge length
    )

    # Add nodes with text wrapping for long names
    for name, node_id in nodes.items():
        wrapped_name = wrap_text(name, max_text_chars)
        dot.node(node_id, wrapped_name)

    # Add edges with wrapped labels
    for edge in edges:
        if edge['label']:
            wrapped_label = wrap_text(edge['label'], max_text_chars - 5)
            dot.edge(edge['from'], edge['to'], label=f"  {wrapped_label}  ")
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

    auto_layout = st.checkbox(
        "Auto-optimize layout for complex diagrams (12+ nodes → TB)",
        value=True,
        help="Automatically switches to Top-to-Bottom for diagrams with more than 12 nodes"
    )

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
            diagram = create_diagram(nodes, edges, dir_code, auto_layout)

            try:
                png_data = diagram.pipe(format='png')
                svg_data = diagram.pipe(format='svg').decode('utf-8')

                # Display info about auto-layout
                node_count = len(nodes)
                if auto_layout and node_count > 12 and dir_code == "LR":
                    st.info(f"ℹ️ Auto-optimized: Using Top-to-Bottom layout for better visibility ({node_count} nodes)")

                # Display SVG in scrollable container
                st.markdown(
                    '<div class="zoom-controls">💡 Scroll to pan • Use browser zoom (Ctrl/Cmd + +/-) for scaling</div>',
                    unsafe_allow_html=True
                )

                # Embed SVG in scrollable container
                st.markdown(
                    f'<div class="diagram-container">{svg_data}</div>',
                    unsafe_allow_html=True
                )

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
                    st.download_button(
                        label="⬇ SVG",
                        data=svg_data.encode('utf-8'),
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
