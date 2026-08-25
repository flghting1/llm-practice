from pathlib import Path

from PIL import Image


ASSETS = Path(__file__).resolve().parent / "assets"
FRAME_NAMES = [
    "rag-demo-frame-1.png",
    "rag-demo-frame-2.png",
]
OUTPUT = ASSETS / "rag-llm-walkthrough.gif"


def main():
    frames = [Image.open(ASSETS / name).convert("RGB") for name in FRAME_NAMES]
    target_size = frames[0].size
    frames = [frame.resize(target_size) for frame in frames]
    frames = [frame.convert("P", palette=Image.ADAPTIVE) for frame in frames]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=[1600, 4200],
        loop=0,
        optimize=True,
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
