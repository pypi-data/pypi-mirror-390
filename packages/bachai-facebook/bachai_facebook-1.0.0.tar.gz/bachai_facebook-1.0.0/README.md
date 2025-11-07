# Facebook Scraper MCP 服务器

这是一个基于 Model Context Protocol (MCP) 的 Facebook Scraper API 服务器，提供了 8 个 Facebook 搜索相关的工具。

## 功能特性

本 MCP 服务器提供以下 8 个搜索工具：

1. **search_locations** - 搜索 Facebook 位置信息（地点、城市、国家等）
2. **search_video** - 搜索 Facebook 视频内容
3. **search_post** - 搜索 Facebook 公开帖子
4. **search_place** - 搜索 Facebook 地点（商家、景点、餐厅等）
5. **search_pages** - 搜索 Facebook 主页（公司、品牌、公众人物等）
6. **search_events** - 搜索 Facebook 公开活动和事件
7. **search_groups_posts** - 搜索 Facebook 公开群组帖子
8. **search_people** - 搜索 Facebook 公开用户资料

## 前置要求

- Python 3.10 或更高版本
- RapidAPI 账户和 API 密钥

## 安装步骤

1. **克隆或下载本项目**

```bash
cd facebook
```

2. **安装依赖包**

```bash
pip install -r requirements.txt
```

3. **设置 RapidAPI 密钥**

首先，你需要在 [RapidAPI](https://rapidapi.com/krasnoludkolo/api/facebook-scraper3/) 上订阅 Facebook Scraper3 API 并获取你的 API 密钥。

然后设置环境变量：

**Linux/Mac:**
```bash
export RAPIDAPI_KEY='你的API密钥'
```

**Windows (PowerShell):**
```powershell
$env:RAPIDAPI_KEY='你的API密钥'
```

**Windows (CMD):**
```cmd
set RAPIDAPI_KEY=你的API密钥
```

## 使用方法

### 1. 直接运行服务器

```bash
python server.py
```

### 2. 配置到 Claude Desktop

在 Claude Desktop 的配置文件中添加此服务器：

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Mac/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "facebook-scraper": {
      "command": "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": ["E:\\mcp\\facebook\\server.py"],
      "env": {
        "RAPIDAPI_KEY": "你的API密钥"
      }
    }
  }
}
```

### 3. 配置到 Cherry Studio

在 Cherry Studio 中配置此服务器：

**方法1：通过界面配置**
1. 打开 Cherry Studio
2. 进入 `设置` → `模型上下文协议（MCP）`
3. 点击 `添加服务器`
4. 填写以下信息：
   - **名称**: facebook-scraper
   - **命令**: `C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe`
   - **参数**: `E:\mcp\facebook\server.py`
   - **环境变量**: 
     - 键: `RAPIDAPI_KEY`
     - 值: `你的API密钥`

**方法2：直接编辑配置文件**

找到 Cherry Studio 的配置文件（通常在用户数据目录），添加以下配置：

```json
{
  "mcpServers": {
    "facebook-scraper": {
      "command": "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": [
        "E:\\mcp\\facebook\\server.py"
      ],
      "env": {
        "RAPIDAPI_KEY": "你的API密钥"
      },
      "disabled": false
    }
  }
}
```

**注意**：
- 请将 `E:\\mcp\\facebook\\server.py` 替换为你的实际项目路径
- 请将 `C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python313\\python.exe` 替换为你的Python 3.13安装路径
- 请将 `你的API密钥` 替换为你的实际RapidAPI密钥
- 配置完成后重启 Cherry Studio

### 4. 使用示例

配置完成后，重启客户端（Claude Desktop 或 Cherry Studio），你就可以使用以下命令：

- "搜索纽约的 Facebook 位置信息"
- "搜索关于人工智能的 Facebook 视频"
- "查找最新的科技相关 Facebook 帖子"
- "搜索巴黎的热门景点"
- "查找特斯拉的 Facebook 主页"
- "搜索本周末的音乐会活动"
- "查找编程相关的群组讨论"
- "搜索名为 John Smith 的用户"

## API 参考

### 所有工具的通用参数

- `query` (必需): 搜索关键词
- `limit` (可选): 返回结果数量限制，默认为 10

### 示例 cURL 命令

以下是 8 个接口对应的 cURL 命令示例：

#### 1. 搜索位置
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/locations?query=New%20York&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 2. 搜索视频
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/videos?query=technology&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 3. 搜索帖子
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/posts?query=artificial%20intelligence&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 4. 搜索地点
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/places?query=restaurant&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 5. 搜索主页
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/pages?query=Tesla&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 6. 搜索活动
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/events?query=concert&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 7. 搜索群组帖子
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/groups_posts?query=programming&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

#### 8. 搜索用户
```bash
curl --request GET \
  --url 'https://facebook-scraper3.p.rapidapi.com/search/people?query=John%20Smith&limit=10' \
  --header 'X-RapidAPI-Host: facebook-scraper3.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: 你的API密钥'
```

## 故障排查

### 问题：API 调用失败

**解决方案:**
1. 确认你已经在 RapidAPI 上订阅了 Facebook Scraper3 API
2. 检查 RAPIDAPI_KEY 环境变量是否正确设置
3. 确认你的 RapidAPI 订阅仍然有效且未超出配额限制

### 问题：Claude 无法识别工具

**解决方案:**
1. 确认 claude_desktop_config.json 配置文件格式正确
2. 重启 Claude Desktop 应用
3. 检查 server.py 的路径是否正确

## 技术架构

本项目基于以下技术：

- **MCP (Model Context Protocol)**: Anthropic 开发的协议，用于 AI 助手与外部工具的集成
- **httpx**: 现代异步 HTTP 客户端
- **RapidAPI**: Facebook Scraper3 API 的托管平台

## 许可证

本项目仅供学习和研究使用。使用 Facebook Scraper API 时，请遵守 Facebook 的服务条款和 RapidAPI 的使用政策。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [Facebook Scraper3 API 文档](https://rapidapi.com/krasnoludkolo/api/facebook-scraper3/)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)

