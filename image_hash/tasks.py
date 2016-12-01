import os
from fc7_feature_extractor import process_captcha


def main():
    captcha_dir = '/data2/heqingy/captchas'
    captcha_path_list = '/data2/haonans/captcha_path_list.txt'

    with open(captcha_path_list) as reader:
        for i, line in enumerate(reader):
            path = os.path.join(captcha_dir, line.strip())
            process_captcha.delay(path)


if __name__ == '__main__':
    main()
