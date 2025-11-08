

import fire 



class ENTRY(object):
    def hello(self):
        print("hello")


def main() -> None:
    fire.Fire(ENTRY)