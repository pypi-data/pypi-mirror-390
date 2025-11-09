from PIL import Image, ImageOps
import typer
from typing_extensions import Annotated

app = typer.Typer(
    help="Image to Half-block ANSI art with IRC color codes.",
    add_completion=False,
    no_args_is_help=True
)

# Source: https://modern.ircdocs.horse/formatting#colors-16-98

modernPalette = [
        (71, 0, 0), (71, 33, 0), (71, 71, 0), (50, 71, 0), (0, 71, 0), (0, 71, 44), (0, 71, 71), (0, 39, 71), (0, 0, 71), (46, 0, 71), (71, 0, 71), (71, 0, 42),
        (116, 0, 0), (116, 58, 0), (116, 116, 0), (81, 116, 0), (0, 116, 0), (0, 116, 73), (0, 116, 116), (0, 64, 116), (0, 0, 116), (75, 0, 116), (116, 0, 116), (116, 0, 69),
        (181, 0, 0), (181, 99, 0), (181, 181, 0), (125, 181, 0), (0, 181, 0), (0, 181, 113), (0, 181, 181), (0, 99, 181), (0, 0, 181), (117, 0, 181), (181, 0, 181), (181, 0, 107),
        (255, 0, 0), (255, 140, 0), (255, 255, 0), (178, 255, 0), (0, 255, 0), (0, 255, 160), (0, 255, 255), (0, 140, 255), (0, 0, 255), (165, 0, 255), (255, 0, 255), (255, 0, 152),
        (255, 89, 89), (255, 180, 89), (255, 255, 113), (207, 255, 96), (111, 255, 111), (101, 255, 201), (109, 255, 255), (89, 180, 255), (89, 89, 255), (196, 89, 255), (255, 102, 255), (255, 89, 188),
        (255, 156, 156), (255, 211, 156), (255, 255, 156), (226, 255, 156), (156, 255, 156), (156, 255, 219), (156, 255, 255), (156, 211, 255), (156, 156, 255), (220, 156, 255), (255, 156, 255), (255, 148, 211),
        (0, 0, 0), (19, 19, 19), (40, 40, 40), (54, 54, 54), (77, 77, 77), (101, 101, 101), (129, 129, 129), (159, 159, 159), (188, 188, 188), (226, 226, 226), (255, 255, 255)
]

# Source: https://www.mirc.com/colors.html

legacyPalette = [
    (255, 255, 255), (0, 0, 0),
    (0, 0, 127), (0, 147, 0),
    (255, 0, 0), (127, 0, 0),
    (156, 0, 156), (252, 127, 0),
    (255, 255, 0), (0, 252, 0),
    (0, 147, 147), (0, 255, 255),
    (0, 0, 252), (255, 0, 255),
    (127, 127, 127), (210, 210, 210)
]

def rgb2irc(r, g, b, legacy=False):
    if legacy:
        return str(min(range(len(legacyPalette)), key=lambda i: (r - legacyPalette[i][0])**2 + (g - legacyPalette[i][1])**2 + (b - legacyPalette[i][2])**2))
    else:
        return str(min(range(len(modernPalette)), key=lambda i: (r - modernPalette[i][0])**2 + (g - modernPalette[i][1])**2 + (b - modernPalette[i][2])**2) + 16)

def convert(image, nearest: bool = False, size: int = 64, post: bool = False, legacy: bool = False):
    im = Image.open(image).convert("RGBA")
    if post:
        rgb = im.convert("RGB")
        alpha = im.getchannel("A")
        impost = ImageOps.posterize(rgb, bits=2)
        im = Image.merge("RGBA", (*impost.split(), alpha))
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
                ctop = rgb2irc(r,g,b, legacy).zfill(2)
                cbot = rgb2irc(r1,g1,b1, legacy).zfill(2)
                if ctop == cbot:
                    if lastcolor[0] == "fullblock" and lastcolor[1] == ctop:
                        row += "█"
                    else:
                        lastcolor = ["fullblock", ctop, None]
                        row += f"\x03{ctop}█"
                else:
                    if lastcolor[0] == "bothblock" and lastcolor[1] == ctop and lastcolor[2] == cbot:
                        row += "▀"
                    else:
                        lastcolor = ["bothblock", ctop, cbot]
                        row += f"\x03{ctop},{cbot}▀"
            elif top:
                c = rgb2irc(r,g,b, legacy).zfill(2)
                if lastcolor[0] == "oneblock" and lastcolor[1] == c:
                    row += "▀"
                else:
                    lastcolor = ["oneblock", c, None]
                    row += f"\x03{c},99▀"
            elif bot:
                c = rgb2irc(r1,g1,b1, legacy).zfill(2)
                if lastcolor[0] == "oneblock" and lastcolor[1] == c:
                    row += "▄"
                else:
                    lastcolor = ["oneblock", c, None]
                    row += f"\x03{c},99▄"
            else:
                if lastcolor[0] == "nothing":
                    row += " "
                else:
                    lastcolor = ["nothing", None, None]
                    row += "\x0f "
        img += (row + "\n").encode("utf-8").decode()
    return img

@app.command()
def main(
    img: Annotated[str, typer.Argument(metavar="IMAGE")],
    out: Annotated[str, typer.Option("-o", "--output", help="Output to file instead of stdout")] = "-",
    near: Annotated[bool, typer.Option("-n", "--nearest", help="Resize image with nearest neighbor")] = False,
    size: Annotated[int, typer.Option("-s", "--width", help="Size for image to resize to (width)")] = 64,
    posterize: Annotated[bool, typer.Option("-p", "--posterize", help="Use 4-bit posterization on the image")] = False,
    legacypal: Annotated[bool, typer.Option("-l", "--legacy-pallete", help="Use the legacy 16-color mIRC pallete")] = False
):
    output = convert(img, near, size, posterize, legacypal)
    if out == "-":
        print(output)
    else:
        open(out, "w").write(output)

if __name__ == "__main__":
    app()
