import tarfile
from getpass import getpass
from pathlib import Path

from fabric import Connection, Config

from .log_config import app_logger

logger = app_logger


def compress_dir(blog_path: Path) -> Path:
    """
    将指定目录压缩为 public.tar.gz
    """
    logger.info(f'压缩目录: {blog_path}')
    output_tar = blog_path.parent / 'public.tar.gz'

    with tarfile.open(output_tar, "w:gz") as tar:
        tar.add(str(blog_path), arcname="public")

    logger.info(f'压缩完成: {output_tar}')
    return output_tar


def deploy_blog(server_name: str, local_tar_path: Path, remote_web_root: str):
    """
    将 tar.gz 文件部署到远程服务器
    """
    logger.info(f'开始部署 -> 服务器: {server_name}，文件: {local_tar_path}')

    sudo_pass = getpass("[sudo]: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    c = Connection(host=server_name, user='koril', config=config, connect_kwargs={'password': sudo_pass})

    remote_home_path = f'/home/{c.user}'
    remote_tar_path = f'{remote_home_path}/{local_tar_path.name}'
    remote_target_path = f'{remote_web_root}blog'

    try:
        # 上传
        c.put(str(local_tar_path), remote=remote_home_path)
        logger.info('上传完成')

        # 删除旧备份
        c.sudo(f'rm -rf {remote_web_root}blog.bak')
        logger.info('旧 blog.bak 删除')

        # 备份 blog
        c.sudo(f'mv {remote_target_path} {remote_target_path}.bak')
        logger.info('blog -> blog.bak')

        # 移动 tar.gz 并解压
        c.sudo(f'mv {remote_tar_path} {remote_web_root}')
        c.sudo(f'tar -xzf {remote_web_root}{local_tar_path.name} -C {remote_web_root}')
        logger.info('解压完成')

        # 清理
        c.sudo(f'rm {remote_web_root}{local_tar_path.name}')
        c.sudo(f'mv {remote_web_root}public {remote_target_path}')
        logger.info('部署完成')

    except Exception as e:
        logger.exception(f"部署失败")
        raise