import click
import yaml
from fusekit.Common import env

@click.group()
def cli():
    """FuseKit CLI utilities."""
    pass


@cli.command()
def init():
    """Initialize the FuseKit configuration and directory structure."""
    root = env.ROOT.expanduser().resolve()
    print(f"🧩  Initializing FuseKit in {root}")

    dirs = {
        "apikeys": env.APIKEYS_DIR,
        "models": env.MODELS_DIR,
        "datasets": env.DATASETS_DIR,
        "artifacts": env.ARTIFACTS_DIR,
    }

    for name, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"{name:<10} → {path}")

    cfg_path = env.CONFIG_FILE.expanduser().resolve()
    if not cfg_path.exists():
        print(f"Creating default config.yml at {cfg_path}")
        cfg = {
            "root": str(root),
            "apikeys": str(env.APIKEYS_DIR),
            "models": str(env.MODELS_DIR),
            "datasets": str(env.DATASETS_DIR),
            "artifacts": str(env.ARTIFACTS_DIR),
        }
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cfg_path, "w") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)
    else:
        print(f"Config already exists at {cfg_path}")

    print("\nFuseKit environment initialized successfully!\n")


if __name__ == "__main__":
    cli()
