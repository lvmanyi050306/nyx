from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import tempfile
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
ET.register_namespace("w", NS["w"])


def patch_update_fields(docx_path):
    docx_path = Path(docx_path)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        with ZipFile(docx_path, "r") as z:
            z.extractall(td)
        settings = td / "word" / "settings.xml"
        tree = ET.parse(settings)
        root = tree.getroot()
        upd = root.find("w:updateFields", NS)
        if upd is None:
            upd = ET.Element(f"{{{NS['w']}}}updateFields")
            root.append(upd)
        upd.set(f"{{{NS['w']}}}val", "true")
        tree.write(settings, encoding="UTF-8", xml_declaration=True)

        tmp = docx_path.with_suffix(".tmp.docx")
        with ZipFile(tmp, "w", ZIP_DEFLATED) as z:
            for p in td.rglob("*"):
                if p.is_file():
                    z.write(p, p.relative_to(td).as_posix())
        shutil.move(tmp, docx_path)


if __name__ == "__main__":
    patch_update_fields(Path("report") / "Nyx宇宙密度演化可视分析_技术报告_排版优化版.docx")
