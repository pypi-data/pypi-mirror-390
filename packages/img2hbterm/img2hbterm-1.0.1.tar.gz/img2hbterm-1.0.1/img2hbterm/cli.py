from PIL import Image
import typer
from typing_extensions import Annotated
from x256 import x256

app = typer.Typer(
    help="Image to Half-block ANSI art with 256-color XTerm codes.",
    add_completion=False,
    no_args_is_help=True
)

def convert(image, nearest: bool = False, size: int = 128, true: bool = False):
    im = Image.open(image).convert("RGBA")
    if im.width > size:
        new_height = int((size / im.width) * im.height)
        if nearest:
            im = im.resize((size, new_height), Image.NEAREST)
        else:
            im = im.resize((size, new_height))
    px = im.load()
    img = ""
    empty = 128
    for y in range(0, im.height, 2):
        row = ""
        lastcolor = ["", "", ""] # type["fullblock","bothblock","oneblock","nothing"], color code 1, color code 2 (if type = "topblockbg")
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if y + 1 < im.height:
                r1, g1, b1, a1 = px[x, y+1]
            else:
                r1, g1, b1, a1 = 0, 0, 0, 0
            top = a >= empty
            bot = a1 >= empty
            # Top block will be used if both exist
            if top and bot:
                if not true:
                    ctop = x256.from_rgb(r,g,b)
                    cbot = x256.from_rgb(r1,g1,b1)
                else:
                    ctop = (r,g,b)
                    cbot = (r1,g1,b1)
                if ctop == cbot:
                    if lastcolor[0] == "fullblock" and lastcolor[1] == ctop:
                        row += "█"
                    else:
                        lastcolor = ["fullblock", ctop, None]
                        if true:
                            row += f"\033[38;2;{r};{g};{b}m\033[49m█"
                        else:
                            row += f"\033[38;5;{ctop}m\033[49m█"
                else:
                    if lastcolor[0] == "bothblock" and lastcolor[1] == ctop and lastcolor[2] == cbot:
                        row += "▀"
                    else:
                        lastcolor = ["bothblock", ctop, cbot]
                        if true:
                            row += f"\033[38;2;{r};{g};{b}m\033[48;2;{r1};{g1};{b1}m▀"
                        else:
                            row += f"\033[38;5;{ctop}m\033[48;5;{cbot}m▀"
            elif top:
                if true:
                    c = (r,g,b)
                else:
                    c = x256.from_rgb(r,g,b)
                if lastcolor[0] == "oneblock" and lastcolor[1] == c:
                    row += "▀"
                else:
                    lastcolor = ["oneblock", c, None]
                    if true:
                        row += f"\033[38;2;{r};{g};{b}m\033[49m▀"
                    else:
                        row += f"\033[38;5;{c}m\033[49m▀"
            elif bot:
                if true:
                    c = (r1,g1,b1)
                else:
                    c = x256.from_rgb(r1,g1,b1)
                if lastcolor[0] == "oneblock" and lastcolor[1] == c:
                    row += "▄"
                else:
                    lastcolor = ["oneblock", c, None]
                    if true:
                        row += f"\033[38;2;{r1};{g1};{b1}m\033[49m▄"
                    else:
                        row += f"\033[38;5;{c}m\033[49m▄"
            else:
                if lastcolor[0] == "nothing":
                    row += " "
                else:
                    lastcolor = ["nothing", None, None]
                    row += "\033[0m "
        img += (row + "\033[0m\n").encode("utf-8").decode()
    return img

@app.command()
def main(
    img: Annotated[str, typer.Argument(metavar="IMAGE")],
    out: Annotated[str, typer.Option("-o", "--output", help="Output to file instead of stdout")] = "-",
    near: Annotated[bool, typer.Option("-n", "--nearest", help="Resize image with nearest neighbor")] = False,
    size: Annotated[int, typer.Option("-s", "--width", help="Size for image to resize to (width)")] = 128,
    true: Annotated[bool, typer.Option("-t", "--true-color", help="Use true color instead of 256 colors (less support)")] = False
):
    output = convert(img, near, size, true)
    if out == "-":
        print(output)
    else:
        open(out, "w").write(output)

if __name__ == "__main__":
    app()

