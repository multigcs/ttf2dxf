import argparse
import freetype

import ezdxf


def quadratic_bezier(t, points):
    B_x = (1 - t) * ((1 - t) * points[0][0] + t * points[1][0]) + t * (
        (1 - t) * points[1][0] + t * points[2][0]
    )
    B_y = (1 - t) * ((1 - t) * points[0][1] + t * points[1][1]) + t * (
        (1 - t) * points[1][1] + t * points[2][1]
    )
    return B_x, B_y


def move_to(a, ctx):
    point = (
        a.x * ctx["scale"][0] + ctx["pos"][0],
        a.y * ctx["scale"][1] + ctx["pos"][1],
    )
    ctx["max"] = max(ctx["max"], point[0])
    ctx["last"] = point
    ctx["contours"].append([])


def line_to(a, ctx):
    point = (
        a.x * ctx["scale"][0] + ctx["pos"][0],
        a.y * ctx["scale"][1] + ctx["pos"][1],
    )
    ctx["max"] = max(ctx["max"], point[0])
    ctx["lines"].append((ctx["last"], point))
    ctx["last"] = point
    ctx["contours"][-1].append(point)


def conic_to(a, b, ctx):
    start = ctx["last"]
    t = 0.0
    while t <= 1.0:
        point = quadratic_bezier(
            t,
            (
                start,
                (
                    a.x * ctx["scale"][0] + ctx["pos"][0],
                    a.y * ctx["scale"][1] + ctx["pos"][1],
                ),
                (
                    b.x * ctx["scale"][0] + ctx["pos"][0],
                    b.y * ctx["scale"][1] + ctx["pos"][1],
                ),
            ),
        )
        ctx["max"] = max(ctx["max"], point[0])
        ctx["lines"].append((ctx["last"], point))
        ctx["last"] = point
        ctx["contours"][-1].append(point)
        t += 0.1


def cubic_to(a, b, c, ctx):
    print(
        "UNSUPPORTED 2nd Cubic Bezier: {},{} {},{} {},{}".format(
            a.x, a.y, b.x, b.y, c.x, c.y
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font", help="font file", type=str)
    parser.add_argument("-t", "--text", help="text string", type=str, default="ttf2dxf")
    parser.add_argument("-o", "--output", help="dxf file", type=str, default="text.dxf")
    parser.add_argument("-s", "--size", help="font height", type=float, default=50)
    # parser.add_argument("-c", "--centerline", help="draw centerline (experimental)", type=int, default=0)
    parser.add_argument(
        "-c", "--centerline", help="draw centerline (experimental)", action="store_true"
    )
    args = parser.parse_args()

    if args.centerline:
        from ttf2dxf import polyskel

    face = freetype.Face(args.font)
    face.set_char_size(18 * 64)

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    doc.units = ezdxf.units.MM
    if args.centerline:
        clayer = doc.layers.add("centerlines")
        clayer.color = 1

    scale = args.size / 1000

    ctx = {
        "last": (),
        "lines": [],
        "contours": [],
        "pos": [0, 0],
        "max": 0,
        "scale": (scale, scale),
    }

    for char in args.text:
        if char == " ":
            ctx["pos"][0] += 500 * scale
            continue
        if char == "\n":
            ctx["pos"][0] = 0
            ctx["pos"][1] -= 1000 * scale
            continue
        face.load_char(char, freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP)
        face.glyph.outline.decompose(
            ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to
        )

        for line in ctx["lines"]:
            msp.add_line(line[0], line[1])

        if args.centerline:
            contours = ctx["contours"]
            poly = contours[0]
            holes = contours[1:] if len(contours) > 0 else None
            skeleton = polyskel.skeletonize(poly, holes)
            for arc in skeleton:
                for sink in arc.sinks:
                    match = False
                    for contour in contours:
                        for point in contour:
                            if (sink.x, sink.y) == point:
                                match = True
                    if not match:
                        msp.add_line(
                            (arc.source.x, arc.source.y),
                            (sink.x, sink.y),
                            dxfattribs={"layer": "centerlines"},
                        )

        ctx["pos"][0] = ctx["max"]
        ctx["max"] = 0
        ctx["lines"] = []
        ctx["contours"] = []

    for vport in doc.viewports.get_config("*Active"):
        vport.dxf.grid_on = True
        vport.dxf.center = (200, 200)

    print(f"exporting text to dxf-file: {args.output}")
    doc.saveas(args.output)


if __name__ == "__main__":
    main()
