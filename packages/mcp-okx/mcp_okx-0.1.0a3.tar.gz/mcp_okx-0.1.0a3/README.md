# 🆗 OKX MCP Server

<!-- mcp-name: io.github.aahl/mcp-okx -->


## 📲 Install

### Method 1: uvx
```yaml
{
  "mcpServers": {
    "mcp-okx": {
      "command": "uvx",
      "args": ["mcp-okx"],
      "env": {
        "OKX_API_KEY": "your-okx-api-key",
        "OKX_API_SECRET": "api-secret-key",
        "OKX_PASSPHRASE": "api-passphrase",
        "OKX_TRADE_FLAG": "1", # 0: Production trading, 1: Demo trading
        "OKX_BASE_URL": "https://www.okx.com", # Optional
        "MCP_AUTH_TOKEN": "your-custom-token"  # Default same as OKX_API_KEY
      }
    }
  }
}
```

### Method 2: Docker
```bash
mkdir /opt/mcp-okx
cd /opt/mcp-okx
wget https://raw.githubusercontent.com/aahl/mcp-okx/refs/heads/main/docker-compose.yml
docker-compose up -d
```
```yaml
{
  "mcpServers": {
    "mcp-okx": {
      "url": "http://0.0.0.0:8811/mcp", # Streamable HTTP
      "headers": {
        "Authorization": "Bearer your-okx-api-key-or-custom-token"
      }
    }
  }
}
```


### ⚙️ Environment variables

- `OKX_API_KEY`: API key of your OKX account. Please refer to [my api page](https://www.okx.com/account/my-api) regarding API Key creation.
- `OKX_API_SECRET`: API secret key of your OKX account.
- `OKX_PASSPHRASE`: API passphrase of your OKX account.
- `OKX_TRADE_FLAG`: 0: Production trading, 1: Demo trading
- `OKX_BASE_URL`: Base URL of OKX. Default: `https://www.okx.com`
- `MCP_AUTH_TOKEN`: Custom token for authentication. Default same as `OKX_API_KEY`


## 🛠️ Available Tools

<details>
<summary><strong>Account Tools</strong></summary>

- `account_config` - Get account configuration
- `account_balance` - Get account balance
- `account_positions` - Get account positions
- `account_position_risk` - Get account position risk

</details>

<details>
<summary><strong>Trading Tools</strong></summary>

- `place_order` - Place a new order
- `cancel_order` - Cancel an incomplete order
- `get_trade_order` - Get order details
- `get_order_list` - Get incomplete order list
- `get_orders_history` - Get Order History
- `close_positions` - Liquidate all positions

</details>
