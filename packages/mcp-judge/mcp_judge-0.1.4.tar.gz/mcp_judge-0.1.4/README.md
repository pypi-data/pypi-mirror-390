# 🧑‍⚖️ MCP Judge

An interactive interface for testing your MCP tools. This application helps you connect to an MCP server, list available tools, inspect their schemas, and run them with custom inputs, all from a clean, web-based UI.

## ✨ Features

* **Connect to any MCP Server:** Easily connect to a new MCP server by simply entering its URL.
* **Discover Tools:** View a list of all available tools and their descriptions.
* **Dynamic Input Forms:** The app automatically generates input forms based on the tool's `inputSchema`.
* **Live Tool Testing:** Run any tool with your specified inputs and see the output in real-time.

## 🆕 New Feature
* **Custom Headers Support:** You can now add custom request headers (like API tokens, authorization keys, or metadata) when connecting to an MCP server.
This makes it easy to test protected or authenticated MCP tools directly from the interface.

---

### 🚀 Installation

You can install `mcp-judge` directly from PyPI.

```bash
pip install mcp-judge
```

---

### 💻 How to Run

After installation, you can launch the application from your terminal with a single command:

```bash
mcp-judge
```
This will automatically start a local server and open the app in your default web browser.

---

### 🛠️ Usage

1.  **Enter Server URL:** On the left side of the screen, enter the URL of the MCP server you want to test and click **"Connect"**.
2.  **Optional Headers:** Click on “⚙️ Advanced Options (Custom Headers)” below the URL input if your MCP tools requires custom headers and header-based access is already configured in your MCP server.
    - Enter the header name (e.g., Authorization)
    - Enter the header value (e.g., Bearer your_api_token)
3.  **Select a Tool:** Once connected, a list of available tools will appear below. Choose the tool you want to test from the dropdown menu.
4.  **Provide Inputs:** The right side of the screen will show a form based on the selected tool's required inputs. Fill in the necessary details.
5.  **Run the Tool:** Click the **"Run Tool"** button to execute the tool. The output will be displayed in the **"Tool Result"** section below.

---

### 📄 Requirements

* Python 3.11+

---

## 🔌 Sample MCP Connections

### 1. Connected to Microsoft's Sample MCP

![Microsoft MCP](https://raw.githubusercontent.com/NilavoBoral/mcp-judge/main/screenshot_microsoft_mcp_v0.1.4.png)


### 2. Connected to Custom Test MCP

![Custom MCP](https://raw.githubusercontent.com/NilavoBoral/mcp-judge/main/screenshot_custom_mcp_v0.1.4.png)

---

## 🔗 Project Links

- 📂 [Source Code](https://github.com/NilavoBoral/mcp-judge)
