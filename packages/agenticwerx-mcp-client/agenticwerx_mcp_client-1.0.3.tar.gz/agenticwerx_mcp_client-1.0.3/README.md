# AgenticWerx MCP Client

[![PyPI version](https://badge.fury.io/py/agenticwerx-mcp-client.svg)](https://badge.fury.io/py/agenticwerx-mcp-client)
[![Python Support](https://img.shields.io/pypi/pyversions/agenticwerx-mcp-client.svg)](https://pypi.org/project/agenticwerx-mcp-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) client that connects to the AgenticWerx Lambda MCP server using JSON-RPC 2.0 protocol to provide code analysis and rule management capabilities.

## 🚀 Quick Start

### For IDE Users

Add this configuration to your MCP-compatible IDE (Kiro, Amazon Q Developer, etc.):

```json
{
  "mcpServers": {
    "agenticwerx": {
      "command": "uvx",
      "args": ["agenticwerx-mcp-client@latest", "--api-key", "${AGENTICWERX_API_KEY}"],
      "env": {
        "AGENTICWERX_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Get Your API Key

1. Visit [AgenticWerx Dashboard](https://agenticwerx.com/dashboard)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key to your MCP configuration

## 🛠️ Available Tools

The AgenticWerx MCP client provides a simple tool for code analysis:

### **analyze**
Analyze code using AgenticWerx rules from the server.

**Parameters:**
- `packageId` (optional): Specific package ID to use rules from a specific package

**Example:**
```json
{
  "tool": "analyze",
  "packageId": "stripe-integration-excellence-pack"
}
```

The tool connects to AgenticWerx services and retrieves the rules, which are then processed and returned to your IDE.

## 🔗 Simple Connection

This client acts as a simple bridge between your IDE and AgenticWerx services. It retrieves rules and passes them back to your IDE for code analysis.

## 🔧 Installation Methods

### Method 1: UVX (Recommended)
No installation needed! Your IDE will automatically download and run the client:

```bash
uvx agenticwerx-mcp-client@latest --api-key your_key_here
```

### Method 2: pip install
```bash
pip install agenticwerx-mcp-client
agenticwerx-mcp-client --api-key your_key_here
```

### Method 3: From Source
```bash
git clone https://github.com/agenticwerx/mcp-client.git
cd mcp-client
pip install -e .
agenticwerx-mcp-client --api-key your_key_here
```

## 📋 IDE Configuration Examples

### Kiro IDE
```json
{
  "mcpServers": {
    "agenticwerx": {
      "command": "uvx",
      "args": ["agenticwerx-mcp-client@latest", "--api-key", "${AGENTICWERX_API_KEY}"],
      "env": {
        "AGENTICWERX_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Amazon Q Developer
```json
{
  "mcpServers": {
    "agenticwerx": {
      "command": "uvx",
      "args": ["agenticwerx-mcp-client@latest", "--api-key", "${AGENTICWERX_API_KEY}"],
      "env": {
        "AGENTICWERX_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### VS Code (with MCP extension)
```json
{
  "mcp.servers": {
    "agenticwerx": {
      "command": "uvx",
      "args": ["agenticwerx-mcp-client@latest", "--api-key", "${AGENTICWERX_API_KEY}"],
      "env": {
        "AGENTICWERX_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 🔒 Security & Privacy

- **API Key Security:** Your API key is only used to authenticate with AgenticWerx services
- **Code Privacy:** Code analysis happens securely through encrypted connections
- **No Data Storage:** Your code is analyzed in real-time and not stored on our servers
- **Local Processing:** The MCP client runs locally on your machine

## 🚀 Features

- ✅ **Simple Connection:** Connects your IDE to AgenticWerx services
- ✅ **Rule Retrieval:** Fetches rules from the server
- ✅ **MCP Compatible:** Works with any MCP-compatible IDE
- ✅ **Zero Configuration:** Just add your API key
- ✅ **Lightweight:** Minimal overhead, just passes data through

## 📊 Example Output

```json
{
  "tool": "analyze",
  "packageId": "stripe-integration-excellence-pack",
  "rules": {
    "rules": [
      {
        "id": "rule-1",
        "name": "Security Rule",
        "description": "Prevents security vulnerabilities",
        "pattern": "eval\\(",
        "message": "Avoid using eval() as it can lead to code injection"
      }
    ],
    "metadata": {
      "package_name": "Security Rules",
      "version": "1.0.0",
      "total_rules": 1
    }
  }
}
```

## 🛠️ Technical Requirements

### Runtime Requirements
- Python 3.8+
- httpx >= 0.25.0
- mcp >= 1.0.0
- pydantic >= 2.0.0

### Installation
```bash
# Via uvx (recommended)
uvx agenticwerx-mcp-client@latest --api-key your_key_here

# Via pip
pip install agenticwerx-mcp-client
```

## 📚 Documentation

- [Full Documentation](https://docs.agenticwerx.com/mcp-client)
- [API Reference](https://docs.agenticwerx.com/api)
- [Rule Package Catalog](https://agenticwerx.com/packages)
- [IDE Integration Guides](https://docs.agenticwerx.com/integrations)

## 🆘 Support

- **Documentation:** [docs.agenticwerx.com](https://docs.agenticwerx.com)
- **Email Support:** [support@agenticwerx.com](mailto:support@agenticwerx.com)
- **Community:** [Discord Server](https://discord.gg/agenticwerx)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** This is a proprietary package developed and maintained exclusively by AgenticWerx. We do not accept external contributions at this time.

## 🔄 Changelog

### v1.0.0 (2025-01-XX)
- Initial release
- Full MCP protocol support
- Rule retrieval tools
- Multi-language support
- Real-time code feedback

---

**Built with ❤️ by the AgenticWerx Team**

*Making code quality accessible to every developer, in every IDE, for every language.*