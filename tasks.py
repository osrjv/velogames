from glob import glob
from invoke import task

CLEAN_PATTERNS = [
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    "**/__pycache__",
    "**/*.pyc",
    "**/*.egg-info",
]


def poetry(ctx, command, **kwargs):
    kwargs.setdefault("echo", True)
    ctx.run(f"poetry {command}", **kwargs)


@task
def clean(ctx):
    """Remove all generated files"""
    for pattern in CLEAN_PATTERNS:
        for path in glob(pattern):
            print(f"Removing: {path}")
            shutil.rmtree(path, ignore_errors=True)


@task
def install(ctx):
    """Install all dependencies"""
    poetry(ctx, "install")


@task(install)
def check(ctx):
    """Run static analysis"""
    poetry(ctx, "run black --check velogames")
    poetry(ctx, "run pylint --rcfile .pylintrc velogames")


@task(install)
def format(ctx):
    """Automatically format code"""
    poetry(ctx, "run black velogames")


@task(install, check)
def build(ctx):
    """Build distributable packages"""
    poetry(ctx, "build -v")
    poetry(ctx, "run pyinstaller velogames.spec")

    print("\nCreated files:")
    print("\n".join(f"  {name}" for name in glob("dist/*")))


@task(clean, build)
def publish(ctx):
    """Publish package to PyPI"""
    poetry(ctx, "publish -v")
