from PyPDF2 import PdfReader
import traceback
from pptx import Presentation
from threading import Thread
import threading
from ai_parser import parse_tool, parser_init


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
        print("read pptx")
        return read_pptx(p)
    elif(suffix == ".pdf"):
        print("read pdf")
        return read_pdf(p)
    else:
        print("read None")
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



def main():
    from argparse import ArgumentParser
    from configs import OUTPUT_DIR, EXTRACT_DIR
    from pathlib import Path

    

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    parser = ArgumentParser(usage=r"""
        python module.py [options]
        options: -r (recursively search through directory)
        the script will continuously prompt for input, use { to start and } to stop
        ',' for splitting file paths
    """)
    parser.add_argument("-r", "--recursive", action="store_true", help="-r to search through directories")
    parser.add_argument("-p", "--parse", action="store_true", help="-p to parse outputs")
    args = parser.parse_args()
    r = args.recursive
    to_parse = args.parse

    # get text -----------------------------------------------------------------------------------------------------

    text = ""
    started = False
    print("input paths")
    text = read_block()

    ofiles_str = text.strip().split(",")
    ofiles = []
    for s in ofiles_str:
        try:
            if(s.strip()):
                p = Path(s.strip())
            else:
                continue
        except Exception as e:
            print(type(e).__name__, repr(e), traceback.format_exc())
        else:
            ofiles.append(p)
    n = 0
    if r:
        for d in ofiles:
            for f in d.rglob("*"):
                if(f.is_file()):
                    try:
                        text = read_by_fname(f.suffix, f.absolute())
                        store_path = OUTPUT_DIR / (f.stem + str(n) + ".txt")
                        with store_path.open("w", encoding="utf-8") as fh:
                            fh.write(text)
                        n += 1
                    except Exception as e:
                        print(type(e).__name__, repr(e), traceback.format_exc())
    
    else:
        for f in ofiles:
            try:
                text = read_by_fname(f.suffix, f.absolute())
                store_path = OUTPUT_DIR / (f.stem + str(n) + ".txt")
                with store_path.open("w", encoding="utf-8") as fh:
                    fh.write(text)
                n += 1
            except Exception as e:
                print(type(e).__name__, repr(e), traceback.format_exc())
    #parse text -----------------------------------------------------------------------------------------------------
    if to_parse:
        # get sysprompt
        print("input prompts")
        sysprompt = read_block()

        #
        lock = threading.Lock()
        def parse_write(wpath, client, sysprompt, messages):
            response_txt = parse_tool(client, sysprompt, messages)
            print(response_txt)
            with lock:
                with wpath.open("a", encoding="utf-8") as f:
                    f.write(response_txt + "\n\n")
            

        # threads
        ftxt = ""
        threads = []
        size = 1000
        client = parser_init()
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        for out_file in OUTPUT_DIR.iterdir():
            print(out_file.name)
            if(out_file.is_file() and out_file.suffix == ".txt"):
                with out_file.open("r", encoding="utf-8") as fh:
                    ftxt = fh.read()
                    wpath = EXTRACT_DIR / out_file.name
                    with wpath.open("w", encoding="utf-8") as fh:
                        pass
                    for i in range(0, len(ftxt), size):
                        thread = Thread(target=parse_write, 
                                        kwargs={"client": client, "sysprompt": sysprompt.strip(), "messages":ftxt[i:i+size], "wpath": wpath}
                                        )
                        threads.append(thread)
        for i in range(0, len(threads), 100):
            for thread in threads[i: i+100]:
                thread.start()
            for thread in threads[i: i+100]:
                thread.join()

            


if __name__ == "__main__":
    main()