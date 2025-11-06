import streamlit as st
import graphviz
import re

# Page config
st.set_page_config(
    page_title="Auto Diagram Workspace",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalistic design
st.markdown("""
<style>
    .stApp {
        background-color: #f9fafb;
    }
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

def guess_node_type(name):
    """Guess the node type based on name"""
    lower = name.lower()
    if 'user' in lower or 'client' in lower:
        return 'user'
    elif 'database' in lower or 'db' in lower or 'storage' in lower:
        return 'database'
    elif 'api' in lower or 'gateway' in lower:
        return 'gateway'
    elif 'service' in lower:
        return 'service'
    elif 'frontend' in lower or 'ui' in lower:
        return 'frontend'
    elif 'backend' in lower:
        return 'backend'
    return 'default'

def get_node_style(node_type):
    """Get node styling based on type"""
    styles = {
        'user': {'fillcolor': '#dbeafe', 'color': '#3b82f6'},
        'database': {'fillcolor': '#dcfce7', 'color': '#22c55e'},
        'gateway': {'fillcolor': '#f3e8ff', 'color': '#a855f7'},
        'service': {'fillcolor': '#fed7aa', 'color': '#f97316'},
        'frontend': {'fillcolor': '#fce7f3', 'color': '#ec4899'},
        'backend': {'fillcolor': '#fef3c7', 'color': '#eab308'},
        'default': {'fillcolor': '#f3f4f6', 'color': '#6b7280'}
    }
    return styles.get(node_type, styles['default'])

def parse_input(text):
    """Parse input text and extract nodes and edges"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    nodes = {}
    edges = []
    
    # Patterns to match different connection formats
    patterns = [
        r'(.+?)\s*->\s*(.+)',
        r'(.+?)\s+connects to\s+(.+)',
        r'(.+?)\s+calls\s+(.+)',
        r'(.+?)\s+uses\s+(.+)',
        r'(.+?)\s+sends to\s+(.+)'
    ]
    
    for line in lines:
        matched = False
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                source = match.group(1).strip()
                target = match.group(2).strip()
                
                if source not in nodes:
                    nodes[source] = guess_node_type(source)
                if target not in nodes:
                    nodes[target] = guess_node_type(target)
                
                edges.append((source, target))
                matched = True
                break
    
    return nodes, edges

def create_diagram(nodes, edges):
    """Create a Graphviz diagram"""
    dot = graphviz.Digraph(comment='Architecture Diagram')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1.2')
    dot.attr('node', shape='box', style='filled,rounded', fontname='Arial', 
             fontsize='11', margin='0.3,0.2', height='0.8', width='2')
    dot.attr('edge', color='#6b7280', penwidth='2', arrowsize='0.8')
    
    # Add nodes with styling
    for node_name, node_type in nodes.items():
        style = get_node_style(node_type)
        dot.node(node_name, node_name, 
                fillcolor=style['fillcolor'], 
                color=style['color'],
                fontcolor='#1f2937')
    
    # Add edges
    for source, target in edges:
        dot.edge(source, target)
    
    return dot

# Main UI
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('<div class="main-header">✨ Auto Diagram</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate architecture diagrams from text</div>', unsafe_allow_html=True)

with col2:
    download_col, clear_col = st.columns([1, 5])
    with download_col:
        if 'diagram' in st.session_state and st.session_state.diagram:
            st.download_button(
                label="📥 Export",
                data=st.session_state.diagram.source,
                file_name="architecture_diagram.dot",
                mime="text/plain",
                use_container_width=True
            )

# Sidebar for input
with st.sidebar:
    st.markdown("### 📝 Describe Your Architecture")
    
    st.markdown("""
    <div class="info-box">
        <strong>💡 How to use:</strong><br>
        Use simple text to describe connections:<br>
        <code>A -> B</code><br>
        <code>A connects to B</code><br>
        <code>A calls B</code>
    </div>
    """, unsafe_allow_html=True)
    
    default_text = """User -> API Gateway -> Authentication Service
API Gateway -> Order Service -> Database
API Gateway -> Payment Service -> Payment Gateway
Order Service -> Notification Service"""
    
    user_input = st.text_area(
        "Enter connections:",
        value=default_text,
        height=400,
        placeholder="User -> API Gateway\nAPI Gateway -> Service\nService -> Database",
        label_visibility="collapsed"
    )
    
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #6b7280;">
        <strong>Recognized Components:</strong><br>
        🔵 User/Client<br>
        🟢 Database/Storage<br>
        🟣 API/Gateway<br>
        🟠 Service<br>
        🔴 Frontend/UI<br>
        🟡 Backend<br>
    </div>
    """, unsafe_allow_html=True)

# Main content area
if user_input.strip():
    nodes, edges = parse_input(user_input)
    
    if nodes and edges:
        diagram = create_diagram(nodes, edges)
        st.session_state.diagram = diagram
        
        st.markdown("### 🎨 Your Architecture Diagram")
        
        # Display the diagram
        st.graphviz_chart(diagram, use_container_width=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Components", len(nodes))
        with col2:
            st.metric("Connections", len(edges))
        with col3:
            st.metric("Layers", "Auto")
        
    else:
        st.info("👆 Start typing in the sidebar to generate your diagram")
else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem; color: #9ca3af;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">✨</div>
        <div style="font-size: 1.25rem; margin-bottom: 0.5rem;">Start typing to generate your diagram</div>
        <div style="font-size: 0.875rem;">Use the sidebar to describe your architecture</div>
    </div>
    """, unsafe_allow_html=True)