import svgwrite
import os
import re
import glob
import argparse

parser = argparse.ArgumentParser(
    description='Generate SVG from Assemply Instructions')
parser.add_argument('--input', default="main.smagic",
                    help='Input *.smagic file')
parser.add_argument('--prefix', default="Gate_clk1_.svg",
                    help='Prefix for svg file')
args = parser.parse_args()

OUTPUT_BOX_COLOR = svgwrite.rgb(100, 00, 100, '%')
INPUT_BOX_COLOR = svgwrite.rgb(0, 100, 100, '%')
LABEL_COLOR = svgwrite.rgb(0, 100, 100, '%')

CellColor = {
    "INPUT": INPUT_BOX_COLOR,
    "OUTPUT": OUTPUT_BOX_COLOR,
    "LABEL": LABEL_COLOR
}
ValidInst = ["NOR", "NOT", "INPUT", "OUTPUT"]


class MagicPrinter:

    def __init__(self, Rows, Cols, location='tmp',
                 suffix='Gate_clk%s_.svg',):
        self.Rows = Rows
        self.Cols = Cols
        self.suffix = suffix
        self.dwg = None
        self.TotalClocks = 10
        self.labels = False
        self.clk = 1
        self.location = location
        self.LoadCommons()
        self.temppath = os.path.join(self.location, self.suffix % -1)
        self.dwg = svgwrite.Drawing(self.temppath, profile='full')
        self.AddDevices()
        self.InitialGrid()
        self.ClearSVGImages()
        # self.AddLegends()
        self.DrawDefaultStatusBox()
        self.dwgCurr = self.dwg.copy()

    def re_initiate(self, Rows=None, Cols=None):
        self.Rows = Rows if Rows else self.Rows
        self.Cols = Cols if Cols else self.Cols
        self.LoadCommons()
        self.temppath = os.path.join(self.location, self.suffix % -1)
        self.dwg = svgwrite.Drawing(self.temppath, profile='full')
        self.InitialGrid()
        self.AddDevices()
        self.AddLegends()
        self.DrawDefaultStatusBox()
        self.dwgCurr = self.dwg.copy()

    def ClearSVGImages(self):
        for eachFile in glob.glob(self.get_filename("*")):
            os.remove(eachFile)
        print "Cleared previous SVGs"

    def AddDevices(self):
        # --------------- NOT Gate SVG Defination -------------
        self.device_not = self.dwg.defs.add(
            self.dwg.g(id='device_not'))
        self.device_not.add(self.dwg.line(
            (self.grid_s * -1, 0),
            (self.grid_s * 0, 0),
            stroke_width=5, stroke="black"))
        self.device_not.add(self.dwg.polygon(
            points=[(self.grid_s * -0.25, self.grid_s * 0),
                    (self.grid_s * -0.75, self.grid_s * -0.20),
                    (self.grid_s * -0.75, self.grid_s * 0.20)],
            fill='white', stroke='black', stroke_width=5))
        self.device_not.add(self.dwg.circle(
            (self.grid_s * -0.25, 0),
            fill="white", r=5, stroke_width=4, stroke="black"))
        # self.device_not.add(self.dwg.circle(
        #     (0, 0), fill="green", r=5, stroke_width=1, stroke="black"))

        # --------------- NOR Gate SVG Defination ---------------
        self.device_nor = self.dwg.defs.add(
            self.dwg.g(id='device_nor'))
        self.device_nor.add(self.dwg.line(
            (self.grid_s * -1, 0),
            (self.grid_s * 0, 0),
            stroke_width=5, stroke="black"))
        # self.device_nor.add(self.dwg.circle(
        #     (self.grid_s * 0.5, self.grid_s * 0.5),
        #     r=5, stroke_width=5, stroke="black"))
        # self.device_nor.add(self.dwg.circle(
        #     (self.grid_s * 1.5, self.grid_s * 0.5),
        #     r=5, stroke_width=5, stroke="black"))
        # self.device_nor.add(self.dwg.circle(
        #     (self.grid_s * 2.5, self.grid_s * 0.5),
        #     r=5, stroke_width=5, stroke="black"))
        self.device_nor.add(self.dwg.path(
            d=("M%d %d L %d %d %d %d C %d %d %d %d %d %d " +
               "L %d %d %d %d C %d %d %d %d %d %d") %
            (self.grid_s * -0.80, self.grid_s * -0.25,

             self.grid_s * -0.80, self.grid_s * -0.25,
             self.grid_s * -0.30, self.grid_s * -0.25,

             self.grid_s * -0.40, self.grid_s * -0.25,
             self.grid_s * -0.00, self.grid_s * 0,
             self.grid_s * -0.40, self.grid_s * 0.25,

             self.grid_s * -0.40, self.grid_s * 0.25,
             self.grid_s * -0.80, self.grid_s * 0.25,

             self.grid_s * -0.80, self.grid_s * 0.25,
             self.grid_s * -0.45, self.grid_s * 0,
             self.grid_s * -0.80, self.grid_s * -0.25,
             ),
            fill='white', stroke='black', stroke_width=5))
        self.device_nor.add(self.dwg.circle(
            (self.grid_s * -0.20, 0),
            fill="white", r=5, stroke_width=4, stroke="black"))
        # self.device_nor.add(self.dwg.circle(
        #     (0, 0), fill="green", r=5, stroke_width=1, stroke="black"))

    def AddLegends(self):
        # Adding Gate legends
        self.dwg.add(self.dwg.use(self.device_not, id="legend_notg",
                                  x=self.ConBoxMargin,
                                  y=self.top_m * 0.80
                                  ))
        self.dwg.add(self.dwg.use(self.device_nor, id="legend_norg",
                                  x=self.ConBoxMargin,
                                  y=(self.top_m * 0.80) + (self.grid_s * 0.6)
                                  ))

    def get_filename(self, clk):
        return os.path.join(self.location, self.suffix % clk)

    def LoadCommons(self):
        self.left_m = 100
        self.top_m = 200
        self.grid_s = 100
        self.hgrid_s = self.grid_s / 2
        self.TGrid_Ref = self.top_m - (self.grid_s / 2)
        self.LGrid_Ref = self.left_m - (self.grid_s / 2)
        self.ConBoxMargin = (self.left_m * 1.5) + (self.Cols * self.grid_s)
        self.CntBoxWidth = 300

    def InitialGrid(self, Labels=True):
        for eachCol in range(self.Cols + 1):
            self.dwg.add(self.dwg.line(
                (self.left_m + (eachCol * self.grid_s), self.top_m),
                (self.left_m + (eachCol * self.grid_s),
                 self.top_m + (self.grid_s * self.Cols)),
                stroke=svgwrite.rgb(10, 10, 16, '%')))
            if (eachCol < self.Cols):
                self.dwg.add(self.dwg.text(
                    'C%02d' % (eachCol + 1),
                    x=[self.LGrid_Ref + ((eachCol + 1) * self.grid_s)],
                    y=[self.TGrid_Ref],
                    text_anchor="middle",
                    alignment_baseline="central",
                    font_size="%dpt" % int(self.grid_s * 0.20),
                    font_family="consolas"))

        for eachRow in range(self.Rows + 1):
            self.dwg.add(self.dwg.line(
                (self.left_m, self.top_m + (eachRow * self.grid_s)),
                (self.left_m + (self.grid_s * self.Cols),
                 self.top_m + (eachRow * self.grid_s)),
                stroke=svgwrite.rgb(10, 10, 16, '%')))
            if (eachRow < self.Rows):
                self.dwg.add(self.dwg.text(
                    'R%02d' % (eachRow + 1),
                    x=[self.LGrid_Ref],
                    y=[self.TGrid_Ref + ((eachRow + 1) * self.grid_s)],
                    text_anchor="middle",
                    alignment_baseline="central",
                    font_size="%dpt" % int(self.grid_s * 0.20),
                    font_family="consolas"))

    def DrawDefaultStatusBox(self):
        self.dwg.add(self.dwg.use(
            self.device_not,
            x=self.ConBoxMargin + (self.CntBoxWidth * 0.5)+self.grid_s*0.5,
            y=self.top_m + 20))
        self.dwg.add(self.dwg.text(
            "NOT Gate",
            x=[self.ConBoxMargin + (self.CntBoxWidth * 0.5)],
            y=[self.top_m + 60],
            text_anchor="middle",
            alignment_baseline="central",
            font_size="%dpt" % int(self.grid_s * 0.20),
            font_family="consolas"))
        self.dwg.add(self.dwg.text(
            "NOR Gate",
            x=[self.ConBoxMargin + (self.CntBoxWidth * 0.5)],
            y=[self.top_m + 170],
            text_anchor="middle",
            alignment_baseline="central",
            font_size="%dpt" % int(self.grid_s * 0.20),
            font_family="consolas"))
        self.dwg.add(self.dwg.use(
            self.device_nor,
            x=self.ConBoxMargin + (self.CntBoxWidth * 0.5)+self.grid_s*0.5,
            y=self.top_m + 120))
        self.dwg.add(self.dwg.rect(
            (self.ConBoxMargin, self.top_m * 2),
            (self.CntBoxWidth, 80),
            rx=10, ry=10,
            fill=svgwrite.rgb(100, 100, 100, '%'),
            stroke=svgwrite.rgb(0, 0, 0, '%')))
        self.dwg.add(self.dwg.text(
            "Current Inst",
            x=[self.ConBoxMargin + (self.CntBoxWidth * 0.5)],
            y=[self.top_m * 2.7],
            text_anchor="middle",
            alignment_baseline="central",
            font_size="%dpt" % int(self.grid_s * 0.30),
            font_family="consolas"))

    def UpdateStatusBox(self, clk=0, CurrCmd=""):
        self.dwgCurr.add(self.dwg.text(
            "Clk = %d" % (clk),
            x=[self.ConBoxMargin + (self.CntBoxWidth * 0.5)],
            y=[self.top_m * 2 + 40],
            text_anchor="middle",
            alignment_baseline="central",
            font_size="%dpt" % int(self.grid_s * 0.40),
            font_family="consolas"
        ))
        for Index, eachInst in enumerate(CurrCmd.split("|")):
            self.dwgCurr.add(self.dwg.text(
                eachInst,
                x=[self.ConBoxMargin + (self.CntBoxWidth * 0.5)],
                y=[self.top_m * 3 + (40*Index)],
                text_anchor="middle",
                alignment_baseline="central",
                font_size="%dpt" % int(self.grid_s * 0.25),
                font_family="consolas"
            ))

    def AddCellInfo(self, row, col, symbol="", Btype="INPUT"):
        if ((row < self.Rows) and (col < self.Cols)):
            # Add Rectangle for Label
            ele = self.dwg.rect(
                (self.left_m + ((col - 1) * self.grid_s),
                 self.top_m + ((row - 1) * self.grid_s)),
                (self.grid_s, self.grid_s),
                rx=2, ry=2, opacity=0.50,
                fill=CellColor[Btype],
                stroke=svgwrite.rgb(0, 0, 0, '%'))
            self.dwg.add(ele)
            self.dwgCurr.add(ele)
            # Add Text in Cell
            ele = self.dwg.text(
                symbol,
                x=[(col * self.grid_s) + self.LGrid_Ref],
                y=[(row * self.grid_s) + self.TGrid_Ref],
                text_anchor="middle",
                opacity=0.50,
                alignment_baseline="central",
                font_size="%dpt" % int(self.grid_s * 0.40),
                font_family="consolas"
            )
            self.dwg.add(ele)
            self.dwgCurr.add(ele)
            # self.dwgCurr = self.dwg.copy()
        else:
            print "Skipped Adding box labels"

    def SaveTemplate(self, clk=0, CurrentInst=""):
        print ""
        print "*" * 10, "Saving file ", self.get_filename(clk), "*" * 10
        self.UpdateStatusBox(clk, CurrentInst)
        self.dwgCurr.saveas(self.get_filename(clk),
                            pretty=True)
        Mp.clk = Mp.clk + 1
        self.dwgCurr = self.dwg.copy()

    def AddInv(self, Output, Inputs):
        print "Adding NOT",
        OutputLabel = Output[3]
        Output = tuple([int(p) for p in Output[:2]])
        Inputs = tuple([tuple([int(q) for q in p[:2]]) for p in Inputs])
        direction = 0
        # Add Output Tag Info
        if OutputLabel:
            self.AddCellInfo(Output[0], Output[1], OutputLabel, "LABEL")

        if ((Output[0] - Inputs[0][0]) == 0):
            direction = 0 if ((Output[1] - Inputs[0][1]) > 0) else 2
        elif ((Output[1] - Inputs[0][1]) == 0):
            direction = 1 if ((Output[0] - Inputs[0][0]) > 0) else 3
        for eachInput in Inputs + (Output,):
            self.dwgCurr.add(self.dwgCurr.circle(
                ((self.grid_s * eachInput[1]) + self.LGrid_Ref,
                 (self.grid_s * eachInput[0]) + self.TGrid_Ref),
                r=5, stroke_width=5, stroke="black"))
            self.dwgCurr.add(self.dwgCurr.line(
                ((self.grid_s * eachInput[1]) + self.LGrid_Ref,
                 (self.grid_s * eachInput[0]) + self.TGrid_Ref),
                ((Output[1] * self.grid_s) + self.LGrid_Ref,
                 (Output[0] * self.grid_s) + self.TGrid_Ref),
                stroke_width=5, stroke="black"))
            self.dwgCurr.add(self.dwgCurr.use(
                self.device_not,
                x=((Output[1] * self.grid_s) + self.LGrid_Ref),
                y=((Output[0] * self.grid_s) + self.TGrid_Ref),
                transform="rotate(%d, %d, %d)" %
                (90 * direction,
                 (Output[1] * self.grid_s) + self.LGrid_Ref,
                 (Output[0] * self.grid_s) + self.TGrid_Ref)
            ))

    def AddNor(self, Output, Inputs):
        print "Adding NOR",
        OutputLabel = Output[3]
        Output = tuple([int(p) for p in Output[:2]])
        Inputs = tuple([tuple([int(q) for q in p[:2]]) for p in Inputs])
        direction = 0
        # Add Output Tag Info
        if OutputLabel:
            self.AddCellInfo(Output[0], Output[1], OutputLabel, "LABEL")

        if ((Output[0] - Inputs[0][0]) == 0):
            direction = 0 if ((Output[1] - Inputs[0][1]) > 0) else 2
        elif ((Output[1] - Inputs[0][1]) == 0):
            direction = 1 if ((Output[0] - Inputs[0][0]) > 0) else 3
        for eachInput in Inputs + (Output,):
            self.dwgCurr.add(self.dwgCurr.circle(
                ((self.grid_s * eachInput[1]) + self.LGrid_Ref,
                 (self.grid_s * eachInput[0]) + self.TGrid_Ref),
                r=5, stroke_width=5, stroke="black"))
            self.dwgCurr.add(self.dwgCurr.line(
                ((self.grid_s * eachInput[1]) + self.LGrid_Ref,
                 (self.grid_s * eachInput[0]) + self.TGrid_Ref),
                ((Output[1] * self.grid_s) + self.LGrid_Ref,
                 (Output[0] * self.grid_s) + self.TGrid_Ref),
                stroke_width=5, stroke="black"))
            self.dwgCurr.add(self.dwgCurr.use(
                self.device_nor,
                x=((Output[1] * self.grid_s) + self.LGrid_Ref),
                y=((Output[0] * self.grid_s) + self.TGrid_Ref),
                transform="rotate(%d, %d, %d)" %
                (90 * direction,
                 (Output[1] * self.grid_s) + self.LGrid_Ref,
                 (Output[0] * self.grid_s) + self.TGrid_Ref)
            ))

    def __str__(self):
        return "Rows %d Cols %d " % (self.Rows, self.Cols)


def parseDirective(code):
    global Mp
    print "Executing line " + code
    words = code[1:].split()
    directive = words[0]
    if (directive == "GRID"):
        Mp = MagicPrinter(int(words[1]), int(words[2]))
    else:
        return "Unknown directive"
    return


def executeLine(code):
    for eachInst in code.split(" | "):
        eachInst = eachInst.rstrip()
        updateClock = False
        print "Parsing line ", eachInst
        mnemonics = re.compile(
            u"^(?P<operation>[%s]{3,6})*\s(?P<oprnd>.*)" %
            ("|".join(ValidInst))).match(eachInst)
        if (mnemonics):
            mnemonics = mnemonics.groupdict()
            if mnemonics["operation"] in ["NOR", "NOT"]:
                # oprnd = re.compile(
                #     u"R(?P<x1>[0-9]*)C(?P<y1>[0-9]*)").findall(
                #         mnemonics["oprnd"])
                oprnd = re.compile(
                    u"R(?P<x1>[0-9]*)C(?P<y1>[0-9]*)(\(([\S]*)\))?").findall(
                        mnemonics["oprnd"])
                if (mnemonics["operation"] == "NOR"):
                    Mp.AddNor(oprnd[0], oprnd[1:])
                elif (mnemonics["operation"] == "NOT"):
                    Mp.AddInv(oprnd[0], oprnd[1:])
                updateClock = True
            elif mnemonics["operation"] in ["INPUT", "OUTPUT"]:
                lbl, locations = mnemonics["oprnd"].split(" ", 1)
                oprnd = re.compile(
                    u"R(?P<x1>[0-9]*)C(?P<y1>[0-9]*)").findall(locations)
                if (mnemonics["operation"] == "INPUT"):
                    for eachIn in oprnd:
                        Mp.AddCellInfo(int(eachIn[0]), int(eachIn[1]),
                                       lbl, Btype="INPUT")
                elif (mnemonics["operation"] == "OUTPUT"):
                    for eachIn in oprnd:
                        Mp.AddCellInfo(int(eachIn[0]), int(eachIn[1]), lbl,
                                       Btype="OUTPUT")
            else:
                print "Unknown Command"
        else:
            print "Skipped execution of code " + eachInsts
    if updateClock:
        Mp.SaveTemplate(Mp.clk, code)
    return


if __name__ == "__main__":
    # Default grid
    Mp = MagicPrinter(5, 5)
    asmcode = open(args.input, "r").readlines()
    print "Reading %d lines" % len(asmcode)
    for index, eachLine in enumerate(asmcode):
        eachLine = eachLine.rstrip()
        if eachLine[0] == ".":
            parseDirective(eachLine)
        elif eachLine[0] == "#":
            pass
        else:
            executeLine(eachLine)
