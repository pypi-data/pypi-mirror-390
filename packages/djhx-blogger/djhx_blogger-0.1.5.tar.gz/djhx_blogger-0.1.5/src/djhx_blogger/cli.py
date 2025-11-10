from pathlib import Path

import typer

from .deploy import compress_dir, deploy_blog
from .gen import generate_blog, init_new_blog
from .log_config import log_init, app_logger

log_init()

logger = app_logger

app = typer.Typer()


@app.command()
def run(
    # origin: Path = typer.Argument(..., exists=True, readable=True, help="原始博客内容目录（必填）"),
    origin: Path = typer.Option(
        None,
        "--origin", '-o',
        help='静态模块目录源地址',
    ),
    target: Path = typer.Option(
        Path.cwd(),
        "--target", "-t",
        help="生成的静态博客输出目录，默认为当前目录。",
    ),
    server: str = typer.Option(
        None,
        "--server", "-s",
        help="目标服务器（域名或 IP 地址），可选。",
    ),
    server_target: str = typer.Option(
        None,
        "--server-target", "-T",
        help="目标服务器的部署路径"
    ),
    deploy: bool = typer.Option(
        False,
        "--deploy/--no-deploy",
        help="是否将静态博客部署到远程服务器。",
    ),
    new_blog: Path = typer.Option(
        None,
        "--new-blog", "-n",
        help="生成一个简单的示例博客",
    )
):
    typer.echo(f"原始目录: {origin}")
    typer.echo(f"输出目录: {target}")
    typer.echo(f"目标服务器: {server or '(未指定)'}")
    typer.echo(f"目标服务器部署地址: {server_target}")
    typer.echo(f"是否部署: {'是' if deploy else '否'}")

    if new_blog:
        logger.info(f'在 {new_blog} 下生成一个新的博客目录')
        init_new_blog(str(new_blog))
        return

    if not origin:
        logger.warning(f'需要指定 origin')
        return

    root_node = generate_blog(str(origin), str(target))

    if deploy and server and server_target:
        tar_path = compress_dir(root_node.destination_path)
        deploy_blog(server, tar_path, server_target)