import os
import json
import zipfile
import shutil
import glob
import tempfile
import logging
from pathlib import Path

logging.basicConfig(
    filename="/home/container/addons/install_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

UPLOAD_DIR = "/home/container/addons/uploads"
INSTALLED_DIR = "/home/container/addons/installed"
BEHAVIOR_PACKS_DIR = "/home/container/behavior_packs"
RESOURCE_PACKS_DIR = "/home/container/resource_packs"
SERVER_PROPERTIES = "/home/container/server.properties"
WORLDS_DIR = "/home/container/worlds"

def get_default_world():
    try:
        with open(SERVER_PROPERTIES, "r") as f:
            for line in f:
                if line.startswith("level-name="):
                    world_name = line.split("=", 1)[1].strip()
                    if world_name:
                        return world_name
        logging.warning("No level-name found in server.properties, using default 'world'.")
    except FileNotFoundError:
        logging.error("server.properties not found, using default 'world'.")
    return "world"

def process_mcpack(mcpack_path):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(mcpack_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            manifest_path = Path(temp_dir) / "manifest.json"
            if not manifest_path.exists():
                logging.error(f"manifest.json not found in {mcpack_path}")
                return
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            header = manifest.get("header", {})
            pack_name = header.get("name", "Unknown")
            uuid = header.get("uuid")
            version = header.get("version", [1, 0, 0])
            if not uuid:
                logging.error(f"No UUID found in manifest.json for {mcpack_path}")
                return
            modules = manifest.get("modules", [])
            pack_type = None
            for module in modules:
                module_type = module.get("type")
                if module_type == "data":
                    pack_type = "behavior"
                    break
                elif module_type == "resources":
                    pack_type = "resource"
                    break
            if not pack_type:
                logging.error(f"Could not determine pack type for {mcpack_path}")
                return
            target_dir = (
                Path(BEHAVIOR_PACKS_DIR) / uuid if pack_type == "behavior"
                else Path(RESOURCE_PACKS_DIR) / uuid
            )
            target_dir.mkdir(parents=True, exist_ok=True)
            for item in Path(temp_dir).rglob("*"):
                dest = target_dir / item.relative_to(temp_dir)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if item.is_file():
                    shutil.copy2(item, dest)
            world_name = get_default_world()
            world_dir = Path(WORLDS_DIR) / world_name
            world_dir.mkdir(parents=True, exist_ok=True)
            json_file = (
                world_dir / "world_behavior_packs.json" if pack_type == "behavior"
                else world_dir / "world_resource_packs.json"
            )
            packs = []
            if json_file.exists():
                try:
                    with open(json_file, "r") as f:
                        packs = json.load(f)
                except json.JSONDecodeError:
                    logging.warning(f"Invalid JSON in {json_file}, resetting to empty list.")
                    packs = []
            pack_entry = {"pack_id": uuid, "version": version}
            existing_index = next((i for i, p in enumerate(packs) if p.get("pack_id") == uuid), None)
            if existing_index is not None:
                packs[existing_index] = pack_entry
            else:
                packs.append(pack_entry)
            with open(json_file, "w") as f:
                json.dump(packs, f, indent=4)
            logging.info(f"Successfully installed {pack_type} pack: {pack_name} ({uuid})")
    except Exception as e:
        logging.error(f"Failed to process {mcpack_path}: {str(e)}")

def main():
    for directory in [UPLOAD_DIR, INSTALLED_DIR, BEHAVIOR_PACKS_DIR, RESOURCE_PACKS_DIR]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    mcpack_files = glob.glob(os.path.join(UPLOAD_DIR, "*.mcpack"))
    if not mcpack_files:
        logging.info("No .mcpack files found in upload directory.")
        return
    for mcpack_file in mcpack_files:
        try:
            process_mcpack(mcpack_file)
            shutil.move(mcpack_file, os.path.join(INSTALLED_DIR, os.path.basename(mcpack_file)))
            logging.info(f"Moved {os.path.basename(mcpack_file)} to installed directory.")
        except Exception as e:
            logging.error(f"Error handling {mcpack_file}: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting addon installation process...")
    main()
    logging.info("Addon installation process completed.")
