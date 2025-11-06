import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"
import streamlit as st
import graphviz
import re
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import requests
from datetime import datetime
import subprocess
import platform
import tempfile
import imageio
import numpy as np
from typing import List, Dict, Tuple, Optional

# Page config
st.set_page_config(
    page_title="AI Auto Diagram Workspace",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ---------- Define color variables (light mode defaults) ---------- */
:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #334155;
    --accent-color: #2563eb;
    --card-bg: #ffffff;
    --card-shadow: rgba(0, 0, 0, 0.05);
    --button-bg-start: #3b82f6;
    --button-bg-end: #60a5fa;
}

/* ---------- Dark mode overrides ---------- */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #121212;
        --bg-secondary: #1e1e1e;
        --text-primary: #e0e0e0;
        --text-secondary: #b3b3b3;
        --accent-color: #60a5fa;
        --card-bg: #1f1f1f;
        --card-shadow: rgba(255, 255, 255, 0.08);
        --button-bg-start: #2563eb;
        --button-bg-end: #3b82f6;
    }
}

/* ---------- Apply styles using the variables ---------- */
.stApp {
    background: var(--bg-primary);
    color: var(--text-primary);
    background-attachment: fixed;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Headers */
.main-header {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent-color) 0%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.05);
}

.sub-header {
    font-size: 1rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
}

/* Info Box */
.info-box {
    background: var(--card-bg);
    border-left: 5px solid var(--accent-color);
    padding: 1rem 1.2rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 10px var(--card-shadow);
}

/* TextArea styling */
.stTextArea textarea {
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.95rem;
    background: var(--bg-secondary);
    border-radius: 0.5rem;
    border: 1px solid #cbd5e1;
    color: var(--text-primary);
    padding: 0.6rem;
    box-shadow: inset 0 1px 2px var(--card-shadow);
}

/* Metric Cards */
.metric-card {
    background: var(--card-bg);
    padding: 1.2rem;
    border-radius: 0.8rem;
    box-shadow: 0 2px 6px var(--card-shadow);
    text-align: center;
    color: var(--text-primary);
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg, var(--button-bg-start) 0%, var(--button-bg-end) 100%);
    color: #ffffff;
    border: none;
    border-radius: 0.5rem;
    font-weight: 600;
    padding: 0.6rem 1rem;
    box-shadow: 0 3px 6px rgba(59,130,246,0.3);
    transition: all 0.2s ease-in-out;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, var(--button-bg-end) 0%, var(--button-bg-start) 100%);
    transform: translateY(-2px);
    box-shadow: 0 5px 12px rgba(59,130,246,0.35);
}

/* Pulse animation */
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.03); }
    100% { transform: scale(1); }
}
.pulse {
    animation: pulse 2.5s infinite;
}
</style>
""", unsafe_allow_html=True)


class OllamaLLM:
    """Ollama LLM integration for intelligent parsing"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = None
        self.available_models = []
        self.start_ollama_service()
        self.check_models()
    
    def start_ollama_service(self):
        """Start Ollama service if not running"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Try to start Ollama
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NO_WINDOW,
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["ollama", "serve"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            import time
            time.sleep(3)  # Wait for service to start
            return True
        except:
            return False
    
    def check_models(self):
        """Check available models and download if needed"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.available_models = [m["name"] for m in models]
                
                # Preferred small models for efficiency
                preferred_models = ["gemma2:2b", "phi3:mini", "llama3.2:1b", "tinyllama", "qwen2.5:0.5b"]
                
                for model in preferred_models:
                    if any(model.split(":")[0] in m for m in self.available_models):
                        self.model = model
                        break
                
                # If no preferred model found, try to pull a small one
                if not self.model and not self.available_models:
                    self.pull_model("gemma2:2b")
                elif self.available_models:
                    self.model = self.available_models[0]
        except:
            pass
    
    def pull_model(self, model_name):
        """Pull a model if not available"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300
            )
            if response.status_code == 200:
                self.model = model_name
                return True
        except:
            pass
        return False
    
    def parse_text(self, text: str, diagram_type: str = "architecture") -> Dict:
        """Use LLM to parse text into diagram structure"""
        if not self.model:
            return self.fallback_parser(text, diagram_type)
        
        prompt = f"""Convert this text into a {diagram_type} diagram structure.
Return ONLY valid JSON with nodes and edges. 
Nodes should have: id, label, type (user/database/service/process/decision/start/end/api/frontend/backend/gateway)
Edges should have: source, target, label (optional), style (optional: dashed/bold/dotted)

Text: {text}

JSON structure:
{{
  "nodes": [
    {{"id": "1", "label": "Name", "type": "service"}}
  ],
  "edges": [
    {{"source": "1", "target": "2", "label": "connects"}}
  ]
}}"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
        except:
            pass
        
        return self.fallback_parser(text, diagram_type)
    
    def fallback_parser(self, text: str, diagram_type: str) -> Dict:
        """Fallback parser when LLM is not available"""
        return enhanced_parse_input(text, diagram_type)

def enhanced_parse_input(text: str, diagram_type: str = "architecture") -> Dict:
    """Enhanced parsing with multiple patterns and diagram types"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    nodes = {}
    edges = []
    node_counter = 1
    
    # Extended patterns for various connection descriptions
    patterns = [
        # Standard arrows
        (r'(.+?)\s*-+>\s*(.+?)(?:\s*:\s*(.+))?$', 'solid'),
        (r'(.+?)\s*<-+\s*(.+?)(?:\s*:\s*(.+))?$', 'solid'),
        (r'(.+?)\s*<-+>\s*(.+?)(?:\s*:\s*(.+))?$', 'bold'),
        (r'(.+?)\s*\.+>\s*(.+?)(?:\s*:\s*(.+))?$', 'dotted'),
        (r'(.+?)\s*=+>\s*(.+?)(?:\s*:\s*(.+))?$', 'bold'),
        
        # Natural language patterns
        (r'(.+?)\s+(?:connects?|links?)\s+(?:to|with)\s+(.+?)(?:\s+(?:via|through|using)\s+(.+))?', 'solid'),
        (r'(.+?)\s+(?:calls?|invokes?|triggers?)\s+(.+?)(?:\s+(?:with|using)\s+(.+))?', 'solid'),
        (r'(.+?)\s+(?:uses?|requires?|depends on)\s+(.+)', 'dashed'),
        (r'(.+?)\s+(?:sends?|transmits?|pushes?)\s+(.+?)\s+to\s+(.+)', 'solid'),
        (r'(.+?)\s+(?:receives?|gets?|pulls?)\s+(.+?)\s+from\s+(.+)', 'solid'),
        (r'if\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+))?', 'solid'),
        (r'(.+?)\s+(?:flows?|goes?)\s+to\s+(.+)', 'solid'),
    ]
    
    # Process each line
    for line in lines:
        matched = False
        for pattern, style in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                source = groups[0].strip() if groups[0] else ""
                target = groups[1].strip() if len(groups) > 1 and groups[1] else ""
                label = groups[2].strip() if len(groups) > 2 and groups[2] else ""
                
                # Skip if we have a middle component (like "sends X to Y")
                if len(groups) > 2 and groups[1] and groups[2] and 'sends' in pattern:
                    label = groups[1]
                    target = groups[2]
                
                if source and target:
                    # Add nodes
                    if source not in nodes:
                        node_type = guess_advanced_node_type(source, diagram_type)
                        nodes[source] = {
                            'id': str(node_counter),
                            'label': source,
                            'type': node_type
                        }
                        node_counter += 1
                    
                    if target not in nodes:
                        node_type = guess_advanced_node_type(target, diagram_type)
                        nodes[target] = {
                            'id': str(node_counter),
                            'label': target,
                            'type': node_type
                        }
                        node_counter += 1
                    
                    # Add edge
                    edges.append({
                        'source': nodes[source]['id'],
                        'target': nodes[target]['id'],
                        'label': label,
                        'style': style
                    })
                    matched = True
                    break
        
        # If no pattern matched, treat as standalone node
        if not matched and line:
            # Check for node type hints
            node_type = 'default'
            node_label = line
            
            # Extract type hints like [database], {service}, etc.
            type_match = re.search(r'[\[\{\(](.+?)[\]\}\)]', line)
            if type_match:
                node_type = type_match.group(1).lower()
                node_label = re.sub(r'[\[\{\(].+?[\]\}\)]', '', line).strip()
            
            if node_label and node_label not in nodes:
                nodes[node_label] = {
                    'id': str(node_counter),
                    'label': node_label,
                    'type': guess_advanced_node_type(node_label, diagram_type) if node_type == 'default' else node_type
                }
                node_counter += 1
    
    return {
        'nodes': list(nodes.values()),
        'edges': edges
    }

def guess_advanced_node_type(name: str, diagram_type: str) -> str:
    """Advanced node type guessing based on name and diagram type"""
    lower = name.lower()
    
    # Flowchart specific
    if diagram_type == 'flowchart':
        if any(word in lower for word in ['start', 'begin', 'init']):
            return 'start'
        elif any(word in lower for word in ['end', 'finish', 'complete', 'done']):
            return 'end'
        elif '?' in name or any(word in lower for word in ['if', 'check', 'decision', 'condition']):
            return 'decision'
        elif any(word in lower for word in ['process', 'calculate', 'compute']):
            return 'process'
    
    # Architecture patterns
    patterns = {
        'user': ['user', 'client', 'customer', 'visitor'],
        'database': ['database', 'db', 'storage', 'repository', 'cache', 'redis', 'mongo', 'sql'],
        'api': ['api', 'endpoint', 'rest', 'graphql'],
        'gateway': ['gateway', 'proxy', 'loadbalancer', 'nginx'],
        'service': ['service', 'microservice', 'handler', 'processor'],
        'frontend': ['frontend', 'ui', 'react', 'angular', 'vue', 'web', 'mobile'],
        'backend': ['backend', 'server', 'application'],
        'queue': ['queue', 'kafka', 'rabbitmq', 'sqs', 'pubsub'],
        'cloud': ['aws', 'azure', 'gcp', 'cloud', 's3', 'lambda'],
        'security': ['auth', 'security', 'firewall', 'oauth', 'jwt'],
        'monitoring': ['monitor', 'logging', 'metrics', 'analytics', 'telemetry']
    }
    
    for node_type, keywords in patterns.items():
        if any(keyword in lower for keyword in keywords):
            return node_type
    
    return 'default'

def get_advanced_node_style(node_type: str, theme: str = 'default') -> Dict:
    """Get advanced node styling with themes"""
    themes = {
        'default': {
            'start': {'shape': 'ellipse', 'fillcolor': '#d4edda', 'color': '#28a745', 'style': 'filled,bold'},
            'end': {'shape': 'ellipse', 'fillcolor': '#f8d7da', 'color': '#dc3545', 'style': 'filled,bold'},
            'decision': {'shape': 'diamond', 'fillcolor': '#fff3cd', 'color': '#ffc107', 'style': 'filled'},
            'process': {'shape': 'box', 'fillcolor': '#d1ecf1', 'color': '#17a2b8', 'style': 'filled,rounded'},
            'user': {'shape': 'ellipse', 'fillcolor': '#dbeafe', 'color': '#3b82f6', 'style': 'filled'},
            'database': {'shape': 'cylinder', 'fillcolor': '#dcfce7', 'color': '#22c55e', 'style': 'filled'},
            'api': {'shape': 'component', 'fillcolor': '#fef3c7', 'color': '#f59e0b', 'style': 'filled'},
            'gateway': {'shape': 'hexagon', 'fillcolor': '#f3e8ff', 'color': '#a855f7', 'style': 'filled'},
            'service': {'shape': 'box3d', 'fillcolor': '#fed7aa', 'color': '#f97316', 'style': 'filled'},
            'frontend': {'shape': 'tab', 'fillcolor': '#fce7f3', 'color': '#ec4899', 'style': 'filled'},
            'backend': {'shape': 'component', 'fillcolor': '#fef3c7', 'color': '#eab308', 'style': 'filled'},
            'queue': {'shape': 'parallelogram', 'fillcolor': '#e0e7ff', 'color': '#6366f1', 'style': 'filled'},
            'cloud': {'shape': 'cloud', 'fillcolor': '#e0f2fe', 'color': '#0ea5e9', 'style': 'filled'},
            'security': {'shape': 'shield', 'fillcolor': '#fee2e2', 'color': '#ef4444', 'style': 'filled'},
            'monitoring': {'shape': 'doublecircle', 'fillcolor': '#f0fdf4', 'color': '#16a34a', 'style': 'filled'},
            'default': {'shape': 'box', 'fillcolor': '#f3f4f6', 'color': '#6b7280', 'style': 'filled,rounded'}
        },
        'neon': {
            'default': {'shape': 'box', 'fillcolor': '#1a1a2e', 'color': '#00ff00', 
                       'style': 'filled,rounded', 'fontcolor': '#00ff00'}
        },
        'minimal': {
            'default': {'shape': 'box', 'fillcolor': 'white', 'color': 'black', 
                       'style': 'filled', 'fontcolor': 'black'}
        }
    }
    
    theme_styles = themes.get(theme, themes['default'])
    return theme_styles.get(node_type, theme_styles.get('default', themes['default']['default']))

def create_advanced_diagram(data: Dict, config: Dict) -> graphviz.Digraph:
    """Create advanced diagram with multiple layout options"""
    # Create diagram with configuration
    dot = graphviz.Digraph(comment=config.get('title', 'Diagram'))
    
    # Set graph attributes
    dot.attr(
        rankdir=config.get('direction', 'TB'),
        splines=config.get('splines', 'ortho'),
        nodesep=str(config.get('node_spacing', 0.8)),
        ranksep=str(config.get('rank_spacing', 1.2)),
        bgcolor=config.get('bgcolor', 'transparent'),
        layout=config.get('layout_engine', 'dot')
    )
    
    # Default node attributes
    dot.attr('node', 
            fontname=config.get('font', 'Arial'),
            fontsize=str(config.get('font_size', 11)),
            margin='0.3,0.2',
            height=str(config.get('node_height', 0.8)),
            width=str(config.get('node_width', 2)))
    
    # Default edge attributes
    dot.attr('edge',
            fontname=config.get('font', 'Arial'),
            fontsize=str(config.get('edge_font_size', 10)),
            color=config.get('edge_color', '#6b7280'),
            penwidth=str(config.get('edge_width', 2)),
            arrowsize=str(config.get('arrow_size', 0.8)))
    
    # Add nodes with clustering if enabled
    clusters = {}
    if config.get('auto_cluster', False):
        for node in data.get('nodes', []):
            cluster_name = node.get('type', 'default')
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(node)
    
    # Add nodes (with or without clustering)
    if clusters:
        for cluster_name, cluster_nodes in clusters.items():
            with dot.subgraph(name=f'cluster_{cluster_name}') as c:
                c.attr(label=cluster_name.title(), style='rounded,filled', 
                      fillcolor='#f0f0f0', color='#d0d0d0')
                for node in cluster_nodes:
                    style = get_advanced_node_style(node.get('type', 'default'), 
                                                   config.get('theme', 'default'))
                    c.node(node['id'], node['label'], **style)
    else:
        for node in data.get('nodes', []):
            style = get_advanced_node_style(node.get('type', 'default'), 
                                           config.get('theme', 'default'))
            dot.node(node['id'], node['label'], **style)
    
    # Add edges with styles
    for edge in data.get('edges', []):
        edge_attrs = {}
        if edge.get('label'):
            edge_attrs['label'] = edge['label']
        if edge.get('style'):
            if edge['style'] == 'dashed':
                edge_attrs['style'] = 'dashed'
            elif edge['style'] == 'dotted':
                edge_attrs['style'] = 'dotted'
            elif edge['style'] == 'bold':
                edge_attrs['penwidth'] = '3'
        
        # Add curved edges for better aesthetics
        if config.get('curved_edges', False):
            edge_attrs['splines'] = 'curved'
        
        dot.edge(edge['source'], edge['target'], **edge_attrs)
    
    return dot

def export_to_png(dot: graphviz.Digraph) -> bytes:
    """Export diagram to PNG, suppressing Graphviz warnings."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return dot.pipe(format="png")

def create_animated_gif(dot: graphviz.Digraph, frames: int = 10, duration: float = 0.1) -> bytes:
    """Create animated GIF with node highlighting, suppressing Graphviz warnings."""
    import warnings
    import imageio, numpy as np
    from PIL import Image, ImageDraw
    from io import BytesIO

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        base_png = dot.pipe(format="png")

    base_img = Image.open(BytesIO(base_png))
    images = []
    for i in range(frames):
        img = base_img.copy()
        alpha = int(128 + 127 * np.sin(2 * np.pi * i / frames))
        overlay = Image.new("RGBA", img.size, (255, 255, 255, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay)
        images.append(np.array(img))

    output = BytesIO()
    imageio.mimsave(output, images, format="GIF", duration=duration, loop=0)
    return output.getvalue()


def main():
    # Initialize session state
    if 'llm' not in st.session_state:
        st.session_state.llm = OllamaLLM()
    if 'diagram_data' not in st.session_state:
        st.session_state.diagram_data = None
    if 'diagram' not in st.session_state:
        st.session_state.diagram = None

    # Header
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown('<div class="main-header">🎨 AI Auto Diagram</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Powered by Local LLM + Advanced Visualization</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.llm.model:
            st.success(f"🤖 LLM Active: {st.session_state.llm.model}")
        else:
            st.warning("📴 LLM Offline - Using fallback parser")

    # Sidebar configuration
    with st.sidebar:
        # Input & Diagram Type first
        st.markdown("## 📝 Input Method")
        diagram_type = st.selectbox(
            "Diagram Type",
            ["architecture", "flowchart", "sequence", "network", "mindmap", "er-diagram"]
        )
        input_method = st.radio(
            "Choose input method:",
            ["Text Description", "Structured Input", "Template"]
        )

        examples = {
            "architecture": """User -> API Gateway: HTTP Request
API Gateway -> Auth Service: Validate Token
Auth Service -> Database: Check Credentials
API Gateway -> Order Service: Process Order
Order Service -> Payment Gateway: Process Payment
Order Service -> Notification Service: Send Email
Order Service -> Database: Save Order""",
            "flowchart": """Start -> Get User Input
Get User Input -> Validate Input?
Validate Input? -> Process Data: Valid
Validate Input? -> Show Error: Invalid
Show Error -> Get User Input
Process Data -> Save to Database
Save to Database -> Send Notification
Send Notification -> End""",
            "sequence": """Client -> Server: Request
Server -> Database: Query
Database -> Server: Results
Server -> Cache: Store
Server -> Client: Response"""
        }

        if input_method == "Text Description":
            user_input = st.text_area(
                "Describe your diagram:",
                value=examples.get(diagram_type, examples["architecture"]),
                height=300,
                placeholder="Describe connections naturally...",
                help="Use arrows (->), natural language, or any description"
            )
        elif input_method == "Structured Input":
            st.markdown("#### Nodes")
            num_nodes = st.number_input("Number of nodes", 1, 50, 3)
            nodes = []
            for i in range(num_nodes):
                colA, colB = st.columns([3, 1])
                with colA:
                    label = st.text_input(f"Node {i+1} Label", f"Node {i+1}", key=f"node_{i}")
                with colB:
                    ntype = st.selectbox(
                        f"Type",
                        ["default", "user", "service", "database", "api", "process"],
                        key=f"type_{i}"
                    )
                nodes.append({"id": str(i+1), "label": label, "type": ntype})
            st.markdown("#### Edges")
            num_edges = st.number_input("Number of edges", 0, 100, 2)
            edges = []
            for i in range(num_edges):
                colA, colB, colC = st.columns(3)
                with colA:
                    source = st.selectbox(f"Source", range(1, num_nodes+1), key=f"src_{i}")
                with colB:
                    target = st.selectbox(f"Target", range(1, num_nodes+1), key=f"tgt_{i}")
                with colC:
                    label = st.text_input(f"Label", "", key=f"edge_label_{i}")
                edges.append({"source": str(source), "target": str(target), "label": label})
            user_input = None
            structured_data = {"nodes": nodes, "edges": edges}
        else:
            template = st.selectbox("Select Template", [
                "Microservices Architecture",
                "CI/CD Pipeline",
                "Machine Learning Pipeline",
                "Network Topology",
                "Database Schema",
                "Authentication Flow"
            ])
            user_input = examples.get(diagram_type, examples["architecture"])

        st.markdown("---")
        st.markdown("## 🎛️ Configuration")

        with st.expander("📐 Layout", expanded=False):
            direction = st.select_slider(
                "Direction",
                options=["LR", "RL", "TB", "BT"], value="TB",
                help="Left-Right, Right-Left, Top-Bottom, Bottom-Top"
            )
            layout_engine = st.selectbox(
                "Layout Engine",
                ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]
            )
            splines = st.selectbox(
                "Edge Style",
                ["ortho", "curved", "polyline", "spline", "none"]
            )
            node_spacing = st.slider("Node Spacing", 0.3, 2.0, 0.8)
            rank_spacing = st.slider("Rank Spacing", 0.5, 3.0, 1.2)
        with st.expander("🎨 Visual", expanded=False):
            theme = st.selectbox("Theme", ["default", "neon", "minimal", "dark", "pastel"])
            auto_cluster = st.checkbox("Auto Cluster by Type", value=False)
            curved_edges = st.checkbox("Curved Edges", value=False)
            font = st.selectbox("Font", ["Arial", "Helvetica", "Times", "Courier"])
            font_size = st.slider("Font Size", 8, 16, 11)
            node_width = st.slider("Node Width", 1.0, 4.0, 2.0)
            node_height = st.slider("Node Height", 0.5, 2.0, 0.8)
            edge_width = st.slider("Edge Width", 1, 5, 2)
            arrow_size = st.slider("Arrow Size", 0.5, 2.0, 0.8)
        with st.expander("💾 Export", expanded=False):
            export_format = st.multiselect(
                "Export Formats",
                ["PNG", "SVG", "PDF", "DOT", "GIF (Animated)"],
                default=["PNG", "GIF (Animated)"]
            )
            if "GIF (Animated)" in export_format:
                gif_frames = st.slider("GIF Frames", 5, 30, 10)
                gif_duration = st.slider("Frame Duration (s)", 0.05, 0.5, 0.1)

    # Main content area
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("🎨 Generate Diagram", type="primary", use_container_width=True):
            with st.spinner("Creating your diagram..."):
                config = {
                    'title': f'{diagram_type.title()} Diagram',
                    'direction': direction,
                    'layout_engine': layout_engine,
                    'splines': splines,
                    'node_spacing': node_spacing,
                    'rank_spacing': rank_spacing,
                    'theme': theme,
                    'auto_cluster': auto_cluster,
                    'curved_edges': curved_edges,
                    'font': font,
                    'font_size': font_size,
                    'node_width': node_width,
                    'node_height': node_height,
                    'edge_width': edge_width,
                    'arrow_size': arrow_size
                }
                if input_method == "Structured Input":
                    st.session_state.diagram_data = structured_data
                else:
                    st.session_state.diagram_data = st.session_state.llm.parse_text(user_input, diagram_type)
                if st.session_state.diagram_data:
                    st.session_state.diagram = create_advanced_diagram(st.session_state.diagram_data, config)
                    st.session_state.config = config

    with colB:
        if st.button("🔄 Regenerate with AI", use_container_width=True):
            if st.session_state.diagram_data:
                with st.spinner("AI is thinking..."):
                    if input_method != "Structured Input":
                        st.session_state.diagram_data = st.session_state.llm.parse_text(user_input, diagram_type)
                        st.session_state.diagram = create_advanced_diagram(st.session_state.diagram_data, st.session_state.config)

    # Display diagram or welcome screen
    if st.session_state.diagram:
        st.markdown("## 🖼️ Your Diagram")
        tab1, tab2, tab3 = st.tabs(["📊 Diagram", "📝 Source", "📈 Statistics"])
        with tab1:
            try:
                st.graphviz_chart(st.session_state.diagram, use_container_width=True)
            except:
                png_data = export_to_png(st.session_state.diagram)
                st.image(png_data, use_container_width=True)
        with tab2:
            st.code(st.session_state.diagram.source, language='dot')
        with tab3:
            if st.session_state.diagram_data:
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Nodes", len(st.session_state.diagram_data.get('nodes', [])))
                with c2:
                    st.metric("Edges", len(st.session_state.diagram_data.get('edges', [])))
                with c3:
                    node_types = set(n.get('type', 'default') for n in st.session_state.diagram_data.get('nodes', []))
                    st.metric("Node Types", len(node_types))
                with c4:
                    st.metric("Complexity",
                              f"{len(st.session_state.diagram_data.get('edges', [])) / max(len(st.session_state.diagram_data.get('nodes', [])), 1):.1f}")

        st.markdown("## 💾 Export Options")
        e1, e2, e3, e4, e5 = st.columns(5)
        with e1:
            if "PNG" in export_format:
                png_data = export_to_png(st.session_state.diagram)
                st.download_button(
                    label="📷 PNG",
                    data=png_data,
                    file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True
                )
        with e2:
            if "SVG" in export_format:
                svg_data = st.session_state.diagram.pipe(format='svg')
                st.download_button(
                    label="🎨 SVG",
                    data=svg_data,
                    file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
                    mime="image/svg+xml",
                    use_container_width=True
                )
        with e3:
            if "PDF" in export_format:
                pdf_data = st.session_state.diagram.pipe(format='pdf')
                st.download_button(
                    label="📄 PDF",
                    data=pdf_data,
                    file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with e4:
            if "DOT" in export_format:
                st.download_button(
                    label="📝 DOT",
                    data=st.session_state.diagram.source,
                    file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dot",
                    mime="text/plain",
                    use_container_width=True
                )
        with e5:
            if "GIF (Animated)" in export_format:
                with st.spinner("Creating animated GIF..."):
                    gif_data = create_animated_gif(
                        st.session_state.diagram,
                        frames=gif_frames if 'gif_frames' in locals() else 10,
                        duration=gif_duration if 'gif_duration' in locals() else 0.1
                    )
                    st.download_button(
                        label="🎬 GIF",
                        data=gif_data,
                        file_name=f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif",
                        mime="image/gif",
                        use_container_width=True
                    )

        st.markdown("## ⚡ Quick Actions")
        q1, q2, q3 = st.columns(3)
        with q1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.diagram.source)
                st.info("Select and copy the code above")
        with q2:
            if st.button("🔍 Zoom In", use_container_width=True):
                st.session_state.config['node_width'] *= 1.2
                st.session_state.config['node_height'] *= 1.2
                st.session_state.diagram = create_advanced_diagram(
                    st.session_state.diagram_data, st.session_state.config)
                st.rerun()
        with q3:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.diagram_data = None
                st.session_state.diagram = None
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.1); border-radius: 1rem; margin: 2rem 0;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🎨</div>
            <h2 style="color: var(--text-primary);">Welcome to AI Auto Diagram</h2>
            <p style="color: var(--text-secondary); font-size: 1.2rem;">
            Transform any text into beautiful diagrams instantly!</p>
            <br>
            <h3 style="color: var(--text-primary);">✨ Features</h3>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 2rem;">🤖</div>
                    <div style="color: var(--text-primary);">AI-Powered</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 2rem;">🎬</div>
                    <div style="color: var(--text-primary);">Animated GIFs</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 2rem;">📐</div>
                    <div style="color: var(--text-primary);">Multiple Layouts</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 2rem;">🎨</div>
                    <div style="color: var(--text-primary);">Custom Themes</div>
                </div>
            </div>
            <br>
            <p style="color: var(--text-secondary);">👈 Start by entering your diagram description in the sidebar!</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
