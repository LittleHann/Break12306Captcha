# encoding: UTF-8


def load_chinese_phrases(path="./chinese_phrases/chinese_phrases.txt"):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))

    print "%s Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases


def text_2_image(text,
                 image_dir_path="./images",
                 font_size=40,
                 left_right_padding=10,
                 up_down_padding=5,
                 does_show=False,
                 does_save=False):
    """ Units are all pixels"""
    import os
    import StringIO
    from PIL import Image  # pip install pillow
    import pygame

    pygame.init()

    if isinstance(text, str):
        text = text.decode("utf8")

    num_characters = len(text)
    width = left_right_padding * 2 + num_characters * font_size
    height = up_down_padding * 2 + font_size  # just one line

    image = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))

    font = pygame.font.Font(os.path.join("fonts", "youyuan.ttf"), font_size)
    rendered_text = font.render(text, True, (0, 0, 0), (255, 255, 255))

    string_io = StringIO.StringIO()
    pygame.image.save(rendered_text, string_io)
    string_io.seek(0)

    line = Image.open(string_io)
    image.paste(line, (left_right_padding, up_down_padding))

    if does_show:
        image.show()

    if does_save:
        image.save(os.path.join(image_dir_path, "%s.png" % text))


if __name__ == '__main__':
    text_2_image(text="电话机", does_show=True)
    # load_chinese_phrases()
