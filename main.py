from __future__ import annotations

import io
import os
import sys

import requests
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm
from urllib.parse import urljoin, urlparse


def get_save_dir() -> str:
    """返回图标保存目录：Users 目录下的 downloaded_icons 文件夹（支持用户移动桌面路径）。"""
    return os.path.join(os.path.expanduser("~"), "downloaded_icons")


def choose_best_icon(soup: BeautifulSoup) -> str | None:
    """从 BeautifulSoup 解析结果中挑选最高质量的图标 URL。

    优先级：apple-touch-icon (180x180 > 其他) > 明确 sizes 的 icon > 普通 icon。
    返回选中的原始 href 值（可能是相对 URL），未找到则返回 None。
    """
    candidates: list[tuple[int, str]] = []  # [(priority, href), ...]

    for link in soup.find_all("link", href=True):
        rel_vals = link.get("rel")
        if not rel_vals:
            continue
        # bs4 中 rel 是多值属性，始终返回 list；显式转 str 防止类型推断问题
        rel_lower = {str(v).lower() for v in rel_vals}
        href_raw = link.get("href")
        if not href_raw:
            continue
        href = str(href_raw)

        if "apple-touch-icon" in rel_lower:
            sizes = str(link.get("sizes", ""))
            size_num = 0
            if sizes:
                try:
                    size_num = int(sizes.lower().split("x")[0])
                except (ValueError, IndexError):
                    pass
            priority = 1000 + size_num  # apple-touch-icon 基础分高
            candidates.append((priority, href))
        elif "icon" in rel_lower:
            sizes = str(link.get("sizes", ""))
            size_num = 32  # 默认 32x32
            if sizes and "x" in sizes:
                try:
                    size_num = int(sizes.lower().split("x")[0])
                except (ValueError, IndexError):
                    pass
            candidates.append((size_num, href))

    if not candidates:
        return None

    # 返回 priority 最高的
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def fetch_and_save_icon(
    icon_url: str, save_path: str, headers: dict[str, str], label: str
) -> None:
    """下载图标并转换为 .ico 格式保存。"""
    print(f"[下载] {label}: {icon_url}")

    with requests.get(icon_url, headers=headers, stream=True, timeout=15) as resp:
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            raise ValueError("服务器返回了网页而非图片（可能是人机验证页面）")

        total_size = int(resp.headers.get("content-length", 0))
        buffer = io.BytesIO()

        with tqdm(
            desc=f"  {label}",
            total=total_size if total_size > 0 else None,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=False,
        ) as bar:
            for chunk in resp.iter_content(chunk_size=4096):
                buffer.write(chunk)
                bar.update(len(chunk))

    buffer.seek(0)
    try:
        img = Image.open(buffer)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.save(save_path, format="ICO")
        print(f"[完成] 图标已保存至: {save_path}")
    except Exception:
        raise ValueError("下载的文件不是有效的图片格式，无法转换为 .ico")


def _make_headers(referer: str) -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": referer,
    }


def download_and_convert_favicon(url: str) -> str | None:
    """主流程：从给定网址获取图标并保存。返回成功保存的文件路径，失败返回 None。"""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    domain = urlparse(url).netloc
    if not domain:
        print("错误：无效的网址格式，无法提取域名。")
        return None

    save_dir = get_save_dir()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{domain}.ico")

    headers = _make_headers(url)

    # ---- 阶段1：解析网页 HTML，按质量优先级选取图标 ----
    print(f"\n[阶段1] 解析网页: {url}")
    favicon_url: str | None = None
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        # 强制设置编码，避免中文或其他非 UTF-8 页面乱码
        if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding

        soup = BeautifulSoup(resp.text, "html.parser")
        best_href = choose_best_icon(soup)
        if best_href:
            favicon_url = urljoin(url, best_href)
        else:
            favicon_url = urljoin(url, "/favicon.ico")

        print(f"[阶段1] 选定图标地址: {favicon_url}")
        fetch_and_save_icon(favicon_url, save_path, headers, domain)
        return save_path

    except requests.exceptions.SSLError:
        print("[阶段1] SSL 证书验证失败，已跳过。")
    except requests.exceptions.ConnectionError:
        print("[阶段1] 无法连接到服务器（DNS 解析失败或网络不通）。")
    except requests.exceptions.Timeout:
        print("[阶段1] 请求超时。")
    except requests.exceptions.HTTPError as e:
        print(
            f"[阶段1] 服务器返回错误状态码: {e.response.status_code if e.response is not None else '?'}"
        )
    except requests.exceptions.RequestException as e:
        print(f"[阶段1] 网络请求失败: {e}")
    except ValueError as e:
        print(f"[阶段1] {e}")
    except Exception as e:
        print(f"[阶段1] 未预期的错误: {e}")

    # ---- 阶段2：国内可访问的备用 API (api.iowen.cn) ----
    print("[阶段2] 尝试国内 API (iowen) ...")
    try:
        iowen_url = f"https://api.iowen.cn/favicon/?url={domain}"
        fetch_and_save_icon(iowen_url, save_path, headers, f"{domain} (iowen)")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"[阶段2] 网络请求失败: {e}")
    except ValueError as e:
        print(f"[阶段2] {e}")
    except Exception as e:
        print(f"[阶段2] 未预期的错误: {e}")

    # ---- 阶段3：DuckDuckGo 备用 API ----
    print("[阶段3] 尝试 DuckDuckGo API ...")
    try:
        ddg_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        fetch_and_save_icon(ddg_url, save_path, headers, f"{domain} (DuckDuckGo)")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"[阶段3] 网络请求失败: {e}")
    except ValueError as e:
        print(f"[阶段3] {e}")
    except Exception as e:
        print(f"[阶段3] 未预期的错误: {e}")

    # ---- 阶段4：Google 备用 API ----
    print("[阶段4] 尝试 Google Favicons API ...")
    try:
        google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        fetch_and_save_icon(google_url, save_path, headers, f"{domain} (Google)")
    except requests.exceptions.RequestException as e:
        print(f"[阶段4] 网络请求失败: {e}")
    except ValueError as e:
        print(f"[阶段4] {e}")
    except Exception as e:
        print(f"[阶段4] 未预期的错误: {e}")

    # 判断最终是否有文件生成
    if os.path.exists(save_path):
        print(f"[结果] 图标最终成功保存至: {save_path}")
        return save_path
    else:
        print("[结果] 所有尝试均失败，未能获取该网站图标。")
        return None


def open_folder(path: str) -> None:
    """在系统的文件管理器中打开指定的文件夹并选中该文件（如果可能）。"""
    import subprocess

    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", os.path.normpath(path)])
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", path])
        else:
            subprocess.run(["xdg-open", os.path.dirname(path)])
    except Exception as e:
        print(f"无法打开文件夹: {e}")


def main() -> None:
    print("网站图标抓取工具")
    print(f"保存目录: {get_save_dir()}")
    print("输入 'q' 退出，Ctrl+C 也可随时中断。")
    while True:
        try:
            target = input("\n请输入网址: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            break
        if target.lower() == "q":
            break
        if target:
            try:
                saved_path = download_and_convert_favicon(target)
                if saved_path:
                    ans = input("是否打开所在文件夹？(y/N): ").strip().lower()
                    if ans == "y":
                        open_folder(saved_path)
            except KeyboardInterrupt:
                print("\n已取消当前操作。")
                continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已终止。")
        sys.exit(0)
