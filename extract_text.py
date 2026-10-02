from PyPDF2 import PdfReader
import traceback
from pathlib import Path
from configs import BASE_DIR, OUTPUT_DIR
from pptx import Presentation

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
            print(type(e).__name__, repr(e), traceback.format_exec())
    return "\n".join(texts)


def read_by_fname(name):
    if(name == ".pptx"):
        print("read pptx")
        return read_pptx(name)
    elif(name == ".pdf"):
        print("read pdf")
        return read_pdf(name)
    else:
        print("read None")
        return ""



def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(usage=r"""
        python module.py [options]
        options: -r (recursively search through directory)
        the script will continuously prompt for input, use { to start and } to stop
        ',' for splitting file paths
    """)
    parser.add_argument("-r", "--recursive", action="store_true", help="-r to search through directories")
    args = parser.parse_args()
    r = args.recursive
    text = ""
    while(True):
        ipt = input()
        if(ipt == "{"):
            started = True
            continue
        if(started):
            if(ipt == "}"):
                break
            else:
                text += ipt
        else:
            continue

    ofiles_str = text.strip().split(",")
    ofiles = {"ofiles":[], "flag":""}
    if(r):
        ofiles["flag"] = "d"
    else:
        ofiles["flag"] = "-"
    for s in ofiles_str:
        try:
            p = Path(s.strip())
        except Exception as e:
            print(type(e).__name__, repr(e), traceback.format_exec())
        else:
            ofiles["ofiles"].append(p)

    if(ofiles["flag"] == "d"):
        for d in ofiles["ofiles"]:
            for f in d.iterdir():
                text = read_pdf(f.absolute())
                store_path = OUTPUT_DIR / f.name
                with store_path.open("w", encoding="utf-8") as fh:
                    fh.write(text)
    else:
        for f in ofiles["ofiles"]:
            text = read_pdf(f.absolute())
            store_path = OUTPUT_DIR / f.name
            with store_path.open("w", encoding="utf-8") as fh:
                fh.write(text)
            

if __name__ == "__main__":
    main()