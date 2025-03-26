<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-jmcomic

_✨ NoneBot JMcomic下载后转换成pdf上传群文件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/watshon14/nonebot-plugin-jmcomic.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-template">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-jmcomic.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>


## 📖 介绍

基于[Python API For JMComic](https://github.com/hect0x7/JMComic-Crawler-Python)下载本子图片到本地然后通过[image2pdf](https://github.com/salikx/image2pdf)整合成单个pdf然后上传到群文件

***请保证群文件有空间上传，否则会报错***

~因为看见了qq群转发的核心科技所以自己也想搞一个~

纯编程小白，头一次写头一次搞插件也是头一次写github文档，出了问题会尽量去修的



## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-jmcomic

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-jmcomic
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-jmcomic
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-jmcomic
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-jmcomic
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-jmcomic"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| 配置项1 | 是 | 无 | 配置说明 |
| 配置项2 | 否 | 无 | 配置说明 |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| /jm | 群员 | 否 | 群聊 | 空一格后输入神秘数字即可 |

### 效果图
![下载效果图](./doc/sample_screenshot.jpg)


## 🙏 鸣谢

- [Python API For JMComic](https://github.com/hect0x7/JMComic-Crawler-Python) - jm的API以及图片下载方式
- [image2pdf](https://github.com/salikx/image2pdf) - 图片整合pdf
- [NoneBot2](https://github.com/nonebot/nonebot2) - 跨平台 Python 异步机器人框架

