from PIL import Image, ImageEnhance, ImageOps, ImageDraw
from math import ceil, floor

def gen_background(block, width=1920, height=1080, upscale=8, upper_blocks=1.5, lower_blocks=2):
    block = block.convert("RGBA").resize((block.width*upscale, block.height*upscale), Image.NEAREST)
    foreground_block = ImageEnhance.Brightness(block).enhance(0.25)
    background_block = ImageEnhance.Brightness(foreground_block).enhance(0.5)

    background = fill_image(Image.new('RGBA', (width, height)), background_block)
    foreground = fill_image(Image.new('RGBA', (width, height)), foreground_block)

    foreground_cutout = Image.new('RGBA', (width, height-floor(block.height*upper_blocks)-floor(block.height*lower_blocks)))
    gradient = Image.new('RGBA', (width, floor(block.height/8)), (255, 255, 255))
    mult = 254 / gradient.height
    draw = ImageDraw.Draw(gradient)
    for h in range(1, gradient.height+1):
        # fill the line with the closest shade of transparent
        draw.line(((0, h-1), (width, h-1)), (0, 0, 0, floor(mult*h)))

    foreground_cutout.paste(gradient.copy(), (0, foreground_cutout.height-gradient.height))
    foreground_cutout.paste(ImageOps.flip(gradient))
    foreground.paste(foreground_cutout, (0, floor(block.height*upper_blocks)))

    return Image.alpha_composite(background, foreground)

def fill_image(image, block):
    for w in range(ceil(image.width/block.width)):
        w *= block.width
        for h in range(ceil(image.height/block.height)):
            h *= block.height
            image.paste(block.copy(), (w, h))
    return image

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Generate Minecraft-styled background images.')
    parser.add_argument('-t','--texture', help='What block texture to generate the background out of.', required=True)
    parser.add_argument('-w','--width', help='How wide should the background be.', default=1920, type=int)
    parser.add_argument('-k','--height', help='How tall should the background be.', default=1080, type=int)
    parser.add_argument('-u','--upscale', help='How large each pixel should be.', default=8, type=int)
    parser.add_argument('-a','--upper', help='How tall the top part of the foreground should be.', default=1.5, type=float)
    parser.add_argument('-l','--lower', help='How tall the bottom part of the foreground should be.', default=2, type=float)
    parser.add_argument('-o','--open', help='Whether or not to open the image once generated.', action='store_true')
    args = parser.parse_args()
    try:
        image = gen_background(Image.open(args.texture), args.width, args.height, args.upscale, args.upper, args.lower)
        image.save('bg.png')
        if args.open:
            image.show()
    except FileNotFoundError:
        print(f"Unknown file named '{args.texture}'")
