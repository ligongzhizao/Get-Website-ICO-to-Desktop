# Get-Website-ICO-to-Desktop

一个用于自动获取网页图标（Favicon）并转换为标准的 `.ico` 桌面图标格式的 Python 脚本。

[English Version](#english-version)

## 设计背景

在 Windows 系统中，将网页保存为桌面快捷方式时，默认通常只显示浏览器的通用图标。如果手动下载网页图标，又常遇到格式不兼容（如非 .ico 格式）导致无法正常显示的问题。

本项目提供了一个简单直接的自动化流程，它的核心特点包括：

- 自动解析并下载目标网址的高质量网站图标。
- 遇到访问限制（如 403 错误或反爬机制）时，自动回退并调用备用 API 尝试获取资源。
- 将获取到的图像统一格式化并转换为标准的 Windows `.ico` 格式，确保在桌面完美兼容显示。

<img width="748" height="708" alt="IMG_202604283288_748x708" src="https://github.com/user-attachments/assets/31d8979d-8b98-4b1a-a1c1-a3be5a06d98c" />
<img width="741" height="628" alt="image" src="https://github.com/user-attachments/assets/a75d2344-9106-45b9-ad73-5c501e5f17f7" />
<img width="2816" height="1536" alt="Gemini_Generated_Image_b0ohj5b0ohj5b0oh" src="https://github.com/user-attachments/assets/4532814b-b29e-422f-bfbe-30a657f762d6" />

## 使用教程

### Windows 用户（推荐）

1. 在本项目的 Releases 页面下载最新的 zip 压缩包。
2. 解压文件。
3. 运行 `Get-Website-ICO-to-Desktop.exe`，按提示输入目标网址即可。

### 开发者及其他平台用户

如果你使用其他操作系统或希望直接运行源码：

1. 确保已安装 Python 3.10 - 3.12 之间的版本。
2. 运行 `pip install -r requirements.txt` 安装依赖库。
3. 执行主程序：`python main.py`。

### 自行编译打包

如果需要自行编译打包为独立的可执行文件：

1. 运行 `pip install nuitka zstandard` 安装打包工具。
2. 确保系统已安装 MSVC 编译工具链。
3. 运行项目根目录下的 `build_win.bat` 开始编译过程。

## 友情链接

linux.do 社区：<https://linux.do/>

---

<a id="english-version"></a>

# English Version

A Python tool that automatically fetches website icons (favicons) and converts them into standard `.ico` format for desktop shortcuts.

## Background

When creating desktop shortcuts for websites on Windows, the OS usually assigns a generic browser icon. If you manually download a site's favicon, it often fails to display properly due to format incompatibilities (e.g., being a png or webp rather than a true .ico file).

This project automates the entire process:

- Parses the provided URL and locates the highest quality website icon.
- Features a built-in multi-stage fallback mechanism. If the main website blocks the download (like 403 Forbidden errors), it automatically switches to alternative APIs to fetch the icon.
- Converts the downloaded image data directly into a standard Windows `.ico` format for seamless desktop display compatibility.

## Usage

### For Windows Users (Recommended)

1. Download the latest `.zip` file from the Releases page.
2. Extract the archive.
3. Run `Get-Website-ICO-to-Desktop.exe` and follow the prompt to enter a URL.

### For Developers / Other Platforms

If you are using a non-Windows OS or prefer to run the source code:

1. Ensure Python 3.10 - 3.12 is installed.
2. Run `pip install -r requirements.txt` to install dependencies.
3. Run the script: `python main.py`.

### Build from Source

To compile the application into a standalone Windows executable:

1. Run `pip install nuitka zstandard`.
2. Ensure you have the MSVC build tools installed on your system.
3. Execute `build_win.bat` to compile the binary.

## Links

linux.do Community: <https://linux.do/>
