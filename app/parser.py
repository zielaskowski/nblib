"""
parse ipynb json
parsed data store as list of dict:
    {lev1_name:{
        file_name:{
            cell_id:"uuid",
            content:"string",
            code:"string",
            kids:{lev2_name:{....}}
        },
        file_name:{...}
     }

"""

import json
import pathlib
import re
from pathlib import Path
from typing import Dict, List, Tuple


class Nblib:
    """
    class parsing notebook json and store paragraphs structure
    """

    def __init__(self) -> None:
        self.lib = {}
        self.conf = pathlib.Path("./conf/nblib.json")

    def dump(self) -> str:
        """dump stored data in json format to string"""
        return json.dumps(self.lib)

    def flatten(self) -> List:
        """convert dictionary to flat list
        [id:lev1/lev2/lev3...,fileneme:file1, content:content,source:source]
        """
        out = []

        def walk(level_dict: Dict, from_lev=""):
            for lev, files in level_dict.items():
                for fname, data in files.items():
                    f = pathlib.Path(fname)
                    paragraph = f"{from_lev}/{lev}"
                    id_disp = f"{paragraph} from {f.name}"

                    out.append(
                        {
                            "id_disp": id_disp,
                            "uuid": data.get("uuid", ""),
                            "content": data.get("content", ""),
                            "code": data.get("code", ""),
                        }
                    )

                    kids = data.get("kids", {})
                    if kids:
                        walk(kids, paragraph)

        walk(self.lib, "")
        return out

    def load(self) -> int:
        """load json file with previous scan form conf
        return 0 if file do not exists
        """
        if not self.conf.exists():
            return 0
        try:
            with self.conf.open("r", encoding="UTF8") as f:
                self.lib = json.load(f)
            return 1
        except json.JSONDecodeError as e:
            print(f"Error: invalid json format of `{self.conf}`")
            print(f"Failed at row#: {e.pos}")
            print(e.msg)
            return 0

    def save(self) -> None:
        """Save data to json file"""
        if not self.conf.parent.exists():
            pathlib.Path.mkdir(self.conf.parent)
        with self.conf.open("w", encoding="UTF8") as f:
            json.dump(self.lib, f)

    def parse(self, nb: Dict, name: Path):
        """
        parse notebook and store internally
        if paragraph repeat, add file name of notebook only
        """
        lib, _ = self.__find_kids__(nb, start_id="", fname=name)
        self.__update_dict__(self.lib, lib)

    def __level__(self, txt: str) -> int:
        """calculate level based on number of #
        if empty string returns 1
        if # not found return 0
        """
        if not txt:
            return 1
        pat = re.compile(r"^#{1,6}(?!#)")
        if m := pat.match(txt):
            return len(m.group())
        return 0

    def __update_dict__(self, current: Dict, new: Dict) -> None:
        """add missing keys at any value
        append fname when adding key
        """
        for key, value in new.items():
            if (
                key in current
                and isinstance(current[key], dict)
                and isinstance(value, dict)
            ):
                self.__update_dict__(current[key], value)

            else:
                if key not in current:
                    current[key] = value

    def __rm_eol__(self, old: List[str]) -> List[str]:
        """remove eol from elements in list"""
        new = [e.replace("\n", "") for e in old]
        return new

    def __fill_current__(
        self,
        current: Dict,
        fname: Path,
        uuid: str,
        code: List,
        source: List,
        kids: Dict,
    ) -> None:
        """
        at the last element of paragraph level
        move all collected data to final struct
        reset arrays for next paragraph
        """
        if source:
            new = {
                source[0].replace("\n", ""): {
                    str(fname): {
                        "uuid": uuid,
                        "content": "\n".join(self.__rm_eol__(source)),
                        "code": "\n".join(self.__rm_eol__(code)),
                        "kids": kids.copy(),
                    }
                }
            }
            self.__update_dict__(current, new)
        code.clear()
        source.clear()
        kids.clear()

    def __find_kids__(self, nb: Dict, fname: Path, start_id="") -> Tuple[Dict, str]:
        """
        parse document and store each paragraph data and structure
        """
        begin = 0
        line_id = ""
        level = 0

        uuid = ""
        current = {}  # data struct for current file
        source = []  # content of markdown cells for current level
        code = []  # content of code cells for current level
        kids = {}  # dict of data structs for lower level paragraphs

        for cell in nb["cells"]:
            if cell["cell_type"] == "markdown":
                line = cell["source"][0]
                if not line:  # just skip empty cells
                    continue
                lev = self.__level__(line)
                line_id = cell["id"]
                if not begin and (start_id == line_id or not start_id):
                    # not begin yet but start_id match line_id
                    # also when exiting from kids
                    begin = 1
                    if not level or lev == level:
                        # exiting from kids into the same level
                        # or
                        # this is first time for a level
                        # set level and store data and continue
                        uuid = line_id
                        source += cell["source"]
                        level = lev
                        continue

                if not begin:
                    continue
                if lev == level:
                    # finished paragraph: another paragraph on the same level
                    # write data and continue on the same level
                    # include current line
                    self.__fill_current__(
                        current=current,
                        uuid=line_id,
                        fname=fname,
                        code=code,
                        source=source,
                        kids=kids,
                    )
                    uuid = line_id
                    source += cell["source"]
                    continue
                if not lev:
                    # another markdown cell on current level
                    # just add content to source
                    source += cell["source"]
                    continue
                if lev > level:
                    # cell on higher level: means kids
                    # parse kids and finish this paragraph
                    # no paragraph continuity after kid
                    # possibly new paragraph on the same level
                    k, start_id = self.__find_kids__(nb, start_id=line_id, fname=fname)
                    self.__update_dict__(kids, k)
                    begin = 0
                    self.__fill_current__(
                        current=current,
                        uuid=uuid,
                        fname=fname,
                        code=code,
                        source=source,
                        kids=kids,
                    )
                    continue
                if lev < level:
                    # finished this level: another paragraph on lower level
                    # write data and break
                    self.__fill_current__(
                        current=current,
                        uuid=uuid,
                        fname=fname,
                        code=code,
                        source=source,
                        kids=kids,
                    )
                    break
            if cell["cell_type"] == "code":
                if begin:
                    code += cell["source"]
        if not current:
            self.__fill_current__(
                current=current,
                uuid=uuid,
                fname=fname,
                code=code,
                source=source,
                kids=kids,
            )

        return current, line_id
