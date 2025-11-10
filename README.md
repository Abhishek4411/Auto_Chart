#  Auto Chart

A clean, minimal, real-time Auto Chart with a  black and white design. Type your diagram description and see instant results.

## Features

- **Real-time Preview**: Diagrams update instantly as you type
- **Clean  Design**: Black and white color scheme
- **Simple Syntax**: Use arrows `->` to connect components
- **Auto-scaling**: Automatically adjusts sizing for large diagrams
- **Clean Layout**: Non-overlapping elements with proper spacing
- **30/70 Split**: Efficient space utilization with input panel at 30% and preview at 70%
- **Multiple Exports**: Download as PNG, SVG, or DOT format
- **Two Layouts**: Top-to-Bottom or Left-to-Right direction

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Graphviz** (system package)

#### Install Graphviz

**Windows:**
```bash
choco install graphviz
```
Or download from: https://graphviz.org/download/

**macOS:**
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install graphviz
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the Application

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

### Diagram Syntax

Use simple arrow notation to connect components:

```
Component A -> Component B
Component B -> Component C : Label
Component C -> Component D
```

### Examples

**Simple Flow:**
```
User -> Server
Server -> Database : Query
Database -> Server : Results
Server -> User : Response
```

**Complex Architecture:**
```
Client -> Load Balancer : HTTPS Request
Load Balancer -> Web Server 1
Load Balancer -> Web Server 2
Web Server 1 -> Application Server : API Call
Web Server 2 -> Application Server : API Call
Application Server -> Authentication Service : Verify Token
Authentication Service -> User Database : Query User
User Database -> Authentication Service : User Data
Authentication Service -> Application Server : Auth Result
Application Server -> Business Logic Layer : Process Request
Business Logic Layer -> Data Access Layer
Data Access Layer -> Primary Database : Read/Write
Data Access Layer -> Cache Server : Check Cache
Cache Server -> Data Access Layer : Cache Hit/Miss
Primary Database -> Replication Server : Sync Data
Replication Server -> Backup Database
Business Logic Layer -> Message Queue : Async Task
Message Queue -> Worker Service 1
Message Queue -> Worker Service 2
Worker Service 1 -> Notification Service
Worker Service 2 -> Email Service
Application Server -> Logging Service : Log Events
Application Server -> Monitoring Service : Metrics
Monitoring Service -> Alert System
```

## Design Philosophy

- **Minimal**: No unnecessary features or options
- ****: Clean black and white design
- **Efficient**: Auto-scaling for diagrams of any size
- **Instant**: Real-time updates without button clicks
- **Clear**: Non-overlapping elements with proper spacing

## Auto-scaling

The application automatically adjusts:
- Font sizes based on node count
- Spacing between nodes and ranks
- Overall layout to prevent overlapping
- Keeps diagrams readable even with 20+ nodes

## Export Options

- **PNG**: High-quality raster image for presentations
- **SVG**: Scalable vector graphics for editing
- **DOT**: Raw Graphviz format for advanced customization

## Tips

- Keep component names concise for better layout
- Use labels (`:`) to describe connections
- The diagram updates automatically as you type
- Switch between TB and LR layouts for different perspectives
- Large diagrams automatically scale down for readability

## Troubleshooting

**Graphviz not found error:**
- Ensure Graphviz is installed on your system
- Windows: Add Graphviz bin folder to PATH
- Restart terminal/IDE after installation

**Diagram not updating:**
- Check that your syntax uses `->` for connections
- Each connection should be on a new line

## License

MIT License - feel free to use and modify.