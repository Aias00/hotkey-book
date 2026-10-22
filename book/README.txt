HotKey 源码实战：从热点探测到集群治理

在线阅读：https://aias00.github.io/hotkey-book/
EPUB：https://aias00.github.io/hotkey-book/hotkey-sourcebook.epub

本书以 f1c8181 源码为基线，12 章，包含源码走读、接入示例、实验步骤、故障边界和容量规划。
原始章节：book/chapters/*.xhtml
生成命令：python3 tools/build_book.py（仅依赖 Python 标准库）
输出：docs/，其中网页与 EPUB 共用同一份章节。
本地预览：python3 -m http.server 8000 --directory docs
打开：http://localhost:8000

验证：EPUBCheck 检查 EPUB 3 结构；网页检查所有本地导航目标并与章节内容对照。
示例部署与流量实验供读者复现，并不代表本书制作时已经完成 Java 服务集成压测。
新增内容及工具遵循仓库 Apache-2.0 许可证。上游原作者归属保留。
