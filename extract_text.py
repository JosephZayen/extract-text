from PyPDF2 import PdfReader
import traceback
from pptx import Presentation
from threading import Thread
import threading
from ai_parser import parse_tool, parser_init
from argparse import ArgumentParser
from configs import OUTPUT_DIR, EXTRACT_DIR, configs
from pathlib import Path


def read_pptx(p):
    prs = Presentation(p)
    text_runs = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if(not shape.has_text_frame):
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    text_runs.append(run.text)
        text_runs.append("\n")
    return " ".join(text_runs)


def read_pdf(p):
    reader = PdfReader(p)
    texts = []
    n = len(reader.pages)
    for i in range(n):
        page = reader.pages[i]
        try:
            texts.append(page.extract_text())
        except Exception as e:
            print(type(e).__name__, repr(e), traceback.format_exc())
    return "\n".join(texts)


def read_by_fname(suffix, p):
    if(suffix == ".pptx"):
        print("reading pptx")
        return read_pptx(p)
    elif(suffix == ".pdf"):
        print("reading pdf")
        return read_pdf(p)
    else:
        print("read None, suffix not supported")
        return ""

def read_block():
    block = ""
    started = False
    while(True):
        ipt = input()
        if(started):
            if(ipt == "}"):
                break
            else:
                block += ipt + "\n"
        elif(ipt == r"{"):
            started = True
    return block


def iter_ofiles(ofiles, recursive):
    if(recursive):
        for d in ofiles:
            for f in d.rglob("*"):
                if(f.is_file()):
                    yield f
    else:
        yield from ofiles



def read_txtfile(r):
    print("input paths")
    text = read_block()

    ofiles_str = text.strip().split(",")
    ofiles = []
    for s in ofiles_str:
        if(s.strip()):
            p = Path(s.strip())
            ofiles.append(p)

    n = 0
    for f in iter_ofiles(ofiles, r):
        try:
            text = read_by_fname(f.suffix, f.absolute())
            store_path = OUTPUT_DIR / (f.stem + str(n) + ".txt")
            with store_path.open("w", encoding="utf-8") as fh:
                fh.write(text)
            n += 1
        except Exception as e:
            print(type(e).__name__, repr(e), traceback.format_exc())



def parse_write(lock, wpath, client, sysprompt, user_content, count_input):
    try:
        response_txt = parse_tool(client, sysprompt, user_content)
    except Exception as e:
        print(type(e).__name__, repr(e), traceback.format_exc())
    else:
        with lock:
            print(response_txt)
            count_input["count"] = count_input["count"] + 1
            with wpath.open("a", encoding="utf-8") as f:
                f.write(response_txt + "\n\n")

def parse_output(c):
    count_input = {"count": 0}

    if(c):
        sysprompt = read_block()
    else:
        sysprompt = configs.get("sysprompt")

    lock = threading.Lock()
    # threads
    threads = []
    user_content_size = configs.get("user_content_size")
    client = parser_init()
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    for out_file in OUTPUT_DIR.iterdir():
        print(f"Searching the output directory for text to be analyzed: {out_file.name}")
        wpath = EXTRACT_DIR / out_file.name
        if(out_file.is_file() and out_file.suffix == ".txt"):
            with out_file.open("r", encoding="utf-8") as fh:
                ftxt = fh.read()
            with wpath.open("w", encoding="utf-8") as fh:
                pass
            for i in range(0, len(ftxt), user_content_size):
                thread = Thread(target=parse_write, 
                                kwargs={"client": client, "sysprompt": sysprompt.strip(), "user_content":ftxt[i:i+user_content_size], "wpath": wpath, "lock": lock, "count_input": count_input}
                                )
                threads.append(thread)

    max_threads = configs.get("max_threads")
    for i in range(0, len(threads), max_threads):
        for thread in threads[i: i+max_threads]:
            thread.start()
        for thread in threads[i: i+max_threads]:
            thread.join()
    print(count_input)



def __cli():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    parser = ArgumentParser(usage=r"""
        python module.py [options]
        options: -r (recursively search through directory)
        the script will continuously prompt for input, use { to start and } to stop
        ',' for splitting file paths
    """)
    subparsers = parser.add_subparsers(dest="command")
    subparser_read = subparsers.add_parser(name="read")
    subparser_read.add_argument("-r", "--recursive", action="store_true", help="-r to search through directories")
    subparser_parse = subparsers.add_parser(name="parse")
    subparser_parse.add_argument("-c", "--custom-prompt", action="store_true")
    args = parser.parse_args()
    

    # get text -----------------------------------------------------------------------------------------------------
    if(args.command == "read"):
        r = True if args.r else False
        read_txtfile(r)
    #parse text -----------------------------------------------------------------------------------------------------
    if (args.command == "parse"):
        c = True if args.custom_prompt else False
        parse_output(c)

def main():
    __cli()


if __name__ == "__main__":
    __cli()
