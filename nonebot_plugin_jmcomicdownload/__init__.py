import os
import tempfile
import img2pdf
import shutil
import time
from jmcomic import create_option_by_file, JmDownloader
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, ActionFailed
from nonebot.plugin import PluginMetadata
from nonebot.exception import FinishedException  # Corrected import
import asyncio
from nonebot.log import logger
import traceback
import re

#Meta
__plugin_meta__ = PluginMetadata(
    name="jmcomicdownload",
    description="一个 NoneBot 插件，用于下载 JM 漫画并生成 PDF 文件，上传到群聊。",
    type="application",
    usage="使用方法：/jm <漫画ID> 示例：/jm 12345",
    homepage="https://github.com/watshon14/nonebot_plugin_jmcomicdownload",
    supported_adapters={"~onebot.v11"},
)



# 定义命令处理器，监听 "/jm" 命令
jm = on_command("jm", aliases=(), permission=None)

# 获取项目根目录（动态获取 nonebot2 项目的根目录）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# 生成 PDF 文件的函数
def generate_pdf(comic_id: str) -> str:
    temp_dir = None  # To store the temporary directory path for cleanup
    default_chapter_dirs = []  # To store the default download directories for cleanup
    try:
        
# 步骤 1: 指定配置文件路径（从环境变量或项目根目录加载）
        config_path = os.getenv("JM_PDF_CONFIG_PATH", os.path.join(project_root, "config.yml"))
        logger.info(f"步骤 1: 配置文件路径: {config_path}")
        
# 检查配置文件是否存在，如果不存在则创建默认 config.yml
        if not os.path.exists(config_path):
            logger.warning(f"配置文件未找到: {config_path}. 创建默认 config.yml...")
            default_config = """\
client:
  impl: api  # 使用 JmApiClient
  retry_times: 5
  postman:
    meta_data:
      proxies: system
      headers:  # 设置与浏览器一致的 headers
        User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        Accept-Language: "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        Referer: "https://18comic.vip/"
      cookies:
        AVS: ""  # 真实的 AVS 值
        __cflb: ""  # 您提供的 __cflb 值
        cf_clearance: ""  # 从浏览器中获取
download:
  cache: true
  image:
    decode: true
    suffix: .jpg
  threading:
    image: 30
  path: "./downloads"
  thread: 4
dir_rule:
  base_dir: "./downloads"
  rule: Bd_Ptitle
"""
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(default_config)
            logger.info(f"已创建默认 config.yml: {config_path}")
        
        # 步骤 2: 使用配置文件生成 option 对象
        option = create_option_by_file(config_path)
        if option is None:
            raise ValueError("步骤 2 失败: option 对象为 None")
        logger.info(f"步骤 2: 成功生成 option 对象: {option}")

        # 步骤 3: 使用 option.build_jm_client() 创建客户端
        client = option.build_jm_client()
        if client is None:
            raise ValueError("步骤 3 失败: 客户端创建失败")
        logger.info(f"步骤 3: 成功创建客户端: {client}")

        # 步骤 4: 获取漫画信息
        try:
            comic = client.get_album_detail(comic_id)
            if comic is None:
                raise ValueError("步骤 4 失败: 无法获取漫画信息")
            logger.info(f"步骤 4: 成功获取漫画信息: {comic}")
        except Exception as e:
            logger.error(f"步骤 4 失败: 获取漫画信息时出错: {str(e)}")
            logger.error(f"异常堆栈: {traceback.format_exc()}")
            raise Exception(f"步骤 4 失败: 获取漫画信息时出错: {str(e)}")

        # 步骤 5: 获取章节信息
        try:
            # 使用 comic.episode_list 获取章节信息
            episode_list = comic.episode_list
            if not episode_list:
                raise ValueError("步骤 5 失败: 漫画没有章节")
            
            # 获取每个章节的详细信息
            chapters = []
            for episode in episode_list:
                photo_id, photo_index, photo_title, photo_pub_date = episode
                chapter = client.get_photo_detail(photo_id)
                if chapter is None:
                    logger.warning(f"无法获取章节 {photo_id} 的信息")
                    continue
                chapters.append(chapter)
            logger.info(f"步骤 5: 成功获取 {len(chapters)} 个章节")
        except Exception as e:
            logger.error(f"步骤 5 失败: 获取章节信息时出错: {str(e)}")
            logger.error(f"异常堆栈: {traceback.format_exc()}")
            raise Exception(f"步骤 5 失败: 获取章节信息时出错: {str(e)}")

        # 步骤 6: 下载漫画章节并移动到临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"创建临时目录: {temp_dir}")
            downloader = JmDownloader(option)  # 使用 JmDownloader
            for chapter in chapters:
                chapter_dir = os.path.join(temp_dir, chapter.title)
                os.makedirs(chapter_dir, exist_ok=True)
                logger.debug(f"创建章节临时目录: {chapter_dir}")
                try:
                    # 下载章节到默认目录（由 config.yml 的 dir_rule.base_dir 指定）
                    default_chapter_dir = os.path.join(option.dir_rule.base_dir, chapter.title)
                    downloader.download_photo(chapter.photo_id)
                    # 等待下载完成（JmDownloader may be asynchronous）
                    time.sleep(1)  # Wait for 1 second to ensure downloads are complete
                    logger.info(f"步骤 6: 成功下载章节到默认目录: {default_chapter_dir}")
                    # 调试：检查默认目录内容
                    logger.debug(f"默认章节目录内容: {os.listdir(default_chapter_dir)}")

                    # 移动图片到临时目录
                    for file in os.listdir(default_chapter_dir):
                        src_path = os.path.join(default_chapter_dir, file)
                        dst_path = os.path.join(chapter_dir, file)
                        shutil.move(src_path, dst_path)
                    logger.info(f"步骤 6: 成功移动图片到临时目录: {chapter_dir}")
                    # 调试：检查临时目录内容
                    logger.debug(f"临时章节目录内容: {os.listdir(chapter_dir)}")
                    # 调试：列出所有文件（包括子目录）
                    all_files = []
                    for root, _, files in os.walk(chapter_dir):
                        for file in files:
                            all_files.append(os.path.join(root, file))
                    logger.debug(f"临时章节目录所有文件: {all_files}")

                    # 记录默认目录以便后续清理
                    default_chapter_dirs.append(default_chapter_dir)

                except Exception as e:
                    logger.error(f"步骤 6 失败: 下载或移动章节 {chapter.title} 时出错: {str(e)}")
                    logger.error(f"异常堆栈: {traceback.format_exc()}")
                    raise Exception(f"步骤 6 失败: 下载或移动章节 {chapter.title} 时出错: {str(e)}")

            # 步骤 7: 收集图片文件
            image_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):  # Added .webp
                        image_files.append(os.path.join(root, file))
            image_files.sort()
            if not image_files:
                raise ValueError("步骤 7 失败: 未找到任何图片文件")
            logger.info(f"步骤 7: 成功收集 {len(image_files)} 张图片")
            logger.debug(f"收集到的图片文件: {image_files}")

            # 步骤 8: 生成 PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                pdf_path = tmp_pdf.name
                with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(image_files))
                if not os.path.exists(pdf_path):
                    raise FileNotFoundError(f"PDF 文件未生成: {pdf_path}")
                logger.info(f"步骤 8: 成功生成 PDF: {pdf_path}")

            return pdf_path

    except Exception as e:
        logger.error(f"PDF 生成失败: {str(e)}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        raise Exception(f"PDF 生成失败: {str(e)}")

    finally:
        # 确保临时目录被删除
        if temp_dir and os.path.exists(temp_dir):
            logger.debug(f"清理临时目录: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            if os.path.exists(temp_dir):
                logger.warning(f"临时目录 {temp_dir} 未被完全删除，可能有文件仍在使用")
            else:
                logger.debug(f"临时目录 {temp_dir} 已成功删除")

        # 清理默认下载目录
        for default_chapter_dir in default_chapter_dirs:
            if os.path.exists(default_chapter_dir):
                logger.debug(f"清理默认下载目录: {default_chapter_dir}")
                shutil.rmtree(default_chapter_dir, ignore_errors=True)
                if os.path.exists(default_chapter_dir):
                    logger.warning(f"默认下载目录 {default_chapter_dir} 未被完全删除，可能有文件仍在使用")
                else:
                    logger.debug(f"默认下载目录 {default_chapter_dir} 已成功删除")

# 处理命令的异步函数
@jm.handle()
async def handle_jm(bot: Bot, event: GroupMessageEvent):
    args = event.get_plaintext().strip().split()
    if len(args) < 2:
        await jm.finish("请提供漫画 ID，例如：/jm 12345")
    comic_id = args[1]

    await jm.send("正在处理，请稍等...")

    loop = asyncio.get_running_loop()
    pdf_path = None
    try:
        pdf_path = await loop.run_in_executor(None, generate_pdf, comic_id)
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
        
        # 上传 PDF 到群文件
        logger.info(f"步骤 9: 准备上传 PDF 到群 {event.group_id}")
        await bot.call_api(
            "upload_group_file",
            group_id=event.group_id,
            file=pdf_path,
            name=f"{comic_id}.pdf"
        )
        logger.info("步骤 9: PDF 上传成功")
        await jm.finish("PDF 上传成功！")

    except FinishedException:
        # Ignore FinishedException, as it is part of normal control flow
        pass
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        logger.error(error_msg)
        try:
            await jm.finish(error_msg)
        except ActionFailed as send_error:
            logger.error(f"发送错误消息失败: {str(send_error)}")
            # 无法发送消息，记录日志后继续

    finally:
        # 清理 PDF 文件
        if pdf_path and os.path.exists(pdf_path):
            logger.info(f"步骤 10: 清理临时文件: {pdf_path}")
            os.remove(pdf_path)
        else:
            logger.debug("PDF 文件不存在，无需清理")
