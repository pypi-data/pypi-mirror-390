import shutil
import time
from collections import deque, OrderedDict
from importlib import resources
from pathlib import Path

import markdown
from bs4 import BeautifulSoup
from jinja2 import Template

from .log_config import app_logger

logger = app_logger

ignore_item = ['.git', 'LICENSE']

def load_template(name: str) -> str:
    """读取 static/template/ 下的模板文件"""
    file_path = resources.files("djhx_blogger.static.template").joinpath(name)
    return file_path.read_text(encoding="utf-8")


class Node:
    cache_map = {}

    def __init__(self, source_path, destination_path, node_type):
        # 该节点的源目录路径
        self.source_path = source_path
        # 该节点生成的结果目录路径
        self.destination_path = destination_path
        # 子节点
        self.children = []
        # 节点类型：
        # 1. category 包含多个子目录
        # 2. article 包含一个 index.md 文件和 images 目录
        # 3. leaf index.md 或者 images 目录
        self.node_type = node_type
        # 描述分类或者文章的元信息（比如：文章的标题，简介和日期）
        self.metadata = None

        Node.cache_map[source_path] = self

    def __str__(self):
        return f'path={self.source_path}'


def walk_dir(dir_path_str: str, destination_blog_dir_path_str: str, target_name: str='public') -> Node:
    """
    遍历目录，构造树结构
    :param dir_path_str: 存放博客 md 文件的目录的字符串
    :param destination_blog_dir_path_str: 生成博客目录的地址
    :param target_name: 生成博客的目录名称
    :return: 树结构的根节点
    """

    start = int(time.time() * 1000)
    q = deque()
    dir_path = Path(dir_path_str)
    q.append(dir_path)

    # 生成目录的根路径
    destination_root_dir = Path(destination_blog_dir_path_str).joinpath(target_name)
    logger.info(f'源路经: {dir_path}, 目标路径: {destination_root_dir}')

    root = None

    # 层次遍历
    while q:
        item = q.popleft()
        if item.name in ignore_item:
            logger.info(f'略过: {item.name}')
            continue
        if Path.is_dir(item):
            [q.append(e) for e in item.iterdir()]

        # node 类型判定
        node_type = 'leaf'
        if Path.is_dir(item):
            node_type = 'category'
            # 如果目录包含 index.md 则是文章目录节点
            for e in item.iterdir():
                if e.name == 'index.md':
                    node_type = 'article'
                    break

        if not root:
            root = Node(item, destination_root_dir, node_type)
        else:
            cur_node = Node.cache_map[item.parent]
            # 计算相对路径
            relative_path = item.relative_to(dir_path)
            # 构造目标路径
            destination_path = destination_root_dir / relative_path
            if destination_path.name == 'index.md':
                destination_path = destination_path.parent / Path('index.html')
            n = Node(item, destination_path, node_type)
            cur_node.children.append(n)
    end = int(time.time() * 1000)
    logger.info(f'构造树耗时: {end - start} ms')

    return root


def md_to_html(md_file_path: Path) -> str:
    """
    markdown -> html
    :param md_file_path: markdown 文件的路径对象
    :return: html str
    """

    def remove_metadata(content: str) -> str:
        """
        删除文章开头的 YAML 元信息
        :param content: markdown 内容
        """
        lines = content.splitlines()
        if lines and lines[0] == '---':
            for i in range(1, len(lines)):
                if lines[i] == '---':
                    return '\n'.join(lines[i + 1:])
        return md_content

    with open(md_file_path, mode='r', encoding='utf-8') as md_file:
        md_content = md_file.read()
        md_content = remove_metadata(md_content)
        return markdown.markdown(
            md_content,
            extensions=[
                'markdown.extensions.toc',
                'markdown.extensions.tables',
                'markdown.extensions.sane_lists',
                'markdown.extensions.fenced_code'
            ]
        )


def gen_article_index(md_file_path: Path, article_name):

    bs1 = BeautifulSoup(load_template('article.html'), "html.parser")
    bs2 = BeautifulSoup(md_to_html(md_file_path), "html.parser")

    article_metadata = read_metadata(md_file_path)

    article_tag = bs1.find('article')
    # 添加 h1 标题
    h1_tag = bs1.new_tag('h1')
    h1_tag.string = article_name
    article_tag.insert(0, h1_tag)

    # 添加日期信息
    time_tag = bs1.new_tag('time', datetime=article_metadata["date"])
    time_tag.string = '时间: ' + article_metadata["date"]

    # 添加摘要信息
    summary_tag = bs1.new_tag('p')
    summary_tag.string = '摘要: ' + article_metadata["summary"]

    # 包裹元信息
    meta_wrapper = bs1.new_tag('div', **{"class": "article-meta"})
    meta_wrapper.append(time_tag)
    meta_wrapper.append(bs1.new_tag('br'))
    meta_wrapper.append(summary_tag)

    # 插入到 h1 之后
    h1_tag.insert_after(meta_wrapper)

    # 添加标题和正文之间的换行符
    article_tag.append(bs1.new_tag('hr'))
    # 添加正文内容
    article_tag.append(bs2)
    # 修改页面标题
    bs1.find('title').string = f'文章 | {article_name}'

    return bs1.prettify()


def gen_category_index(categories: list, category_name) -> str:
    template = Template(load_template('category.html'))
    html = template.render(categories=categories, category_name=category_name)
    return html


def sort_categories(item):
    """
    对 categories 排序，type = category 排在所有 type = article 前
    category 按照 name 字典顺序 a-z 排序
    article 按照 metadata 的 date 字段（格式：2024-02-03T14:44:42+08:00）降序排列。
    :param item:
    :return:
    """
    from datetime import datetime
    if item['type'] == 'category':
        # 分类优先，按 name 排序
        return 0, item['name'].lower()
    elif item['type'] == 'article':
        # 文章按日期降序排序，优先级次于 category
        # 将日期解析为 datetime 对象，若无日期则排在最后
        date = item['metadata'].get('date')
        parsed_date = datetime.fromisoformat(date) if date else datetime(year=1970, month=1, day=1)
        return 1, -parsed_date.timestamp()


def gen_blog_dir(root: Node):
    """
    根据目录树构造博客目录
    :param root: 树结构根节点
    :return:
    """

    start = int(time.time() * 1000)

    q = deque()
    q.append(root)

    # 清理之前生成的 root destination
    if Path.exists(root.destination_path):
        logger.info(f'存在目标目录: {root.destination_path}，进行删除')
        shutil.rmtree(root.destination_path)

    while q:
        node = q.popleft()
        [q.append(child) for child in node.children]

        # 对三种不同类型的节点分别进行处理

        if node.node_type == 'category' and node.source_path.name != 'images':
            Path.mkdir(node.destination_path, parents=True, exist_ok=True)
            category_index = node.destination_path / Path('index.html')
            categories = []
            for child in node.children:
                if child:
                    if child.node_type == 'article':
                        child.metadata = read_metadata(child.source_path / Path('index.md'))
                    relative_path = child.destination_path.name / Path('index.html')
                    categories.append({
                        'type': child.node_type,
                        'name': child.destination_path.name,
                        'href': relative_path,
                        'metadata': child.metadata,
                    })
            categories.sort(key=sort_categories)
            with open(category_index, mode='w', encoding='utf-8') as f:
                f.write(gen_category_index(categories, node.source_path.name))

        if node.node_type == 'category' and node.source_path.name == 'images':
            Path.mkdir(node.destination_path, parents=True, exist_ok=True)

        if node.node_type == 'article':
            Path.mkdir(node.destination_path, parents=True, exist_ok=True)

        if node.node_type == 'leaf':
            Path.mkdir(node.destination_path.parent, parents=True, exist_ok=True)
            if node.source_path.name == 'index.md':
                with open(node.destination_path, mode='w', encoding='utf-8') as f:
                    f.write(gen_article_index(node.source_path, node.source_path.parent.name))
            else:
                shutil.copy(node.source_path, node.destination_path)

    end = int(time.time() * 1000)
    logger.info(f'生成目标目录耗时: {end - start} ms')


def gen_blog_archive(blog_dir_str: str, blog_target_dir_str: str, root: Node, target_name: str='public'):
    """
    生成博客 archive 页面
    按照年份分栏，日期排序，展示所有的博客文章
    """

    root_node_path = root.destination_path
    blog_dir = Path(blog_dir_str)

    q = deque()
    q.append(root)
    articles = []
    while q:
        node = q.popleft()
        [q.append(child) for child in node.children]
        if node.node_type == 'article':
            articles.append(node)

    archives = OrderedDict()
    # 先将所有文章按日期降序排列
    articles_sorted = sorted(articles, key=lambda a: a.metadata['date'], reverse=True)

    for article in articles_sorted:
        article_name = article.source_path.name
        full_path = article.destination_path / Path('index.html')
        base_path = Path(blog_target_dir_str) / Path(target_name)
        url = full_path.relative_to(base_path)

        article_datetime = article.metadata.get('date')
        article_year = article_datetime[:4]
        article_date = article_datetime[:10]
        if article_year not in archives:
            archives[article_year] = {
                'articles': [],
                'total': 0,
            }

        archives[article_year]['articles'].append({
            'date': article_date,
            'title': article_name,
            'url': url
        })
        archives[article_year]['total'] += 1


    template = Template(load_template('archive.html'))
    html = template.render(archives=archives)

    root_node_path.joinpath('archive.html').write_text(data=html, encoding='utf-8')


def cp_resource(blog_target_path_str: str):
    """将包内 static 资源复制到目标目录下的 public/"""
    public_dir = Path(blog_target_path_str) / "public"

    # 1. 复制 css/
    css_src = str(resources.files("djhx_blogger.static").joinpath("css"))
    css_dst = public_dir / "css"
    shutil.copytree(css_src, css_dst, dirs_exist_ok=True)

    # 2. 复制 images/
    images_src = str(resources.files("djhx_blogger.static").joinpath("images"))
    images_dst = public_dir / "images"
    shutil.copytree(images_src, images_dst, dirs_exist_ok=True)


def read_metadata(md_file_path):
    import re
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 正则提取元数据
    match = re.match(r'^---\n([\s\S]*?)\n---\n', content)
    if match:
        metadata = match.group(1)
        return parse_metadata(metadata)
    return {}


def parse_metadata(metadata):
    """
    将元数据解析为字典
    title, date, summary
    """
    meta_dict = {}
    for line in metadata.split('\n'):
        if ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            meta_dict[key] = value
    return meta_dict


def generate_blog(blog_dir: str, blog_target: str):
    start = time.time()

    logger.info("开始生成博客文件结构...")
    root_node = walk_dir(blog_dir, blog_target)
    gen_blog_dir(root_node)
    gen_blog_archive(blog_dir, blog_target, root_node)
    cp_resource(blog_target)

    end = time.time()
    logger.info(f'生成静态博客 {blog_dir}, 任务完成, 总耗时: {int((end-start)*1000)} ms')
    return root_node
