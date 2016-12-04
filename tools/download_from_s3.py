from multiprocessing import Process
import boto3

thread = 40


def download(filelist, group):
    s3 = boto3.client('s3')
    for f in filelist:
        if hash(f) % thread == group:
            s3.download_file("12306captchas", f, 'missing/%s' % f)


def main():
    with open('download_list.txt') as f:
        lines = f.readlines()
    filelist = [l.strip() for l in lines if l.strip()]
    processes = list()
    for i in xrange(thread):
        processes.append(Process(target=download, args=(filelist, i)))
    for p in processes:
        p.start()
    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
