from app.core.config_loader import load_config
from app.vision.model_loader import ModelLoader
from app.core.logger import setup_logger


def main() -> None:
    config = load_config("config.yaml")
    logger = setup_logger(config)
    vision_cfg = config.get("vision", {})
    model_path = vision_cfg.get("ppe_model_path", "models/ppe_model.pt")

    model = ModelLoader.load_yolo_model(
        model_path=model_path,
        use_default_if_missing=vision_cfg.get("use_default_yolo_if_missing", True),
        logger=logger,
    )

    print("Loaded model path:", model_path)
    try:
        names = getattr(model, "names", None)
        print("Model class names (id: name):")
        if isinstance(names, dict):
            for k, v in names.items():
                print(f"{k}: {v}")
        else:
            print(names)
    except Exception as exc:
        print("Error reading model.names:", exc)


if __name__ == "__main__":
    main()
