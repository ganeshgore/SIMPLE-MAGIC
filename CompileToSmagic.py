from z3 import *
import pandas as pd
import svgwrite
import os
import re
import argparse
from Netlist_to_Z3_latency_nor2 import netlist_to_z3

parser = argparse.ArgumentParser(
    description='This script generates assembly sequence \
                 from synthesised NOR/INV netlist')
parser.add_argument('--input', default="outputNorInv.v_python_Z3input.txt",
                    help='Z3 Contraints file')
parser.add_argument('--output', default="main",
                    help='Output Filename (.smagic appended by default)')
args = parser.parse_args()


def main():
    # load contraints from fil
    # Replace external file with python script to generate final contarint list
    ConstraintFileName = args.input
    ConstraintFileName = os.path.join("tmp", ConstraintFileName)
    outputFileName = args.output + ".smagic"

    LATENCY = Int('Latency')
    s = Optimize()
    print "Reading from file " + ConstraintFileName
    s.from_file(ConstraintFileName)
    h = s.minimize(LATENCY)

    Status = s.check()
    print "Expression " + str(Status) + "isfied"
    model = s.model()
    Variables = model.decls()
    TRow, TCol = model[Int('ROWNUM')].as_long(), model[Int('COLNUM')].as_long()

    # Sort information into Clock sequence information
    # and Gate positioning information
    mat, sequence, inputcell = [], [], []
    for each in Variables:
        if each.name()[0] == "g":
            if each.name()[-2:] == "_T":
                sequence.append(
                    [each.name().split("_")[0],
                     each.name(),
                     model[each].as_long()])
            else:
                gateNo = re.findall("_(\w)[a-z]*([0-9].*)?", each.name())[0]
                mat.append(
                    [each.name().split("_")[0],
                     gateNo[1] if (gateNo[1] != '') else "0",
                     gateNo[0] if len(gateNo) else "0",
                     each.name(),
                     model[each].as_long()])
        elif each.name()[-4:] in ["_Col", "_Row"]:
            eachInput = re.findall("_(\w)", each.name())[0]
            inputcell.append(
                [each.name().split("_")[0],
                 eachInput[0] if len(eachInput) else "0",
                 each.name(),
                 model[each].as_long()])

    dfMat = pd.DataFrame(
        mat, columns=["gate", "type", "dir", "signal", "cell"])
    dfMat = dfMat.groupby("gate")
    dfSequence = pd.DataFrame(
        sequence, columns=["gate", "signal", "cell"])
    dfSequence = dfSequence.sort_values(by=["cell"]).groupby("cell")
    dfinputcell = pd.DataFrame(
        inputcell, columns=["label", "dir", "signal", "cell"])
    print dfinputcell
    # Open smagic assembly file
    fp = open(outputFileName, "w")
    fp.write(".GRID %d %d\r\n" % (TRow, TCol))

    # Write inputs to assembly file
    for eachInput in dfinputcell.label.unique():
        OpR = dfinputcell[(dfinputcell.dir == "R") & (
            dfinputcell.label == eachInput)].cell.values[0]
        OpC = dfinputcell[(dfinputcell.dir == "C") & (
            dfinputcell.label == eachInput)].cell.values[0]
        fp.write("INPUT %s R%dC%d \r\n" % (eachInput, OpR, OpC))

    for clk, clkGates in dfSequence:
        print "-------------------", clk
        for _, eachGate in clkGates.iterrows():
            tempdf = dfMat.get_group(eachGate["gate"])
            Gate = "NOR" if dfMat.get_group(
                eachGate["gate"]).shape[0] > 4 else "NOT"
            print "*****Gate********", Gate
            fp.write("%s " % Gate)

            for gateNo in range(int(tempdf["type"].max()) + 1):
                OpR = tempdf[(tempdf.dir == "R") & (
                    tempdf.type == str(gateNo))].cell.values[0]
                OpC = tempdf[(tempdf.dir == "C") & (
                    tempdf.type == str(gateNo))].cell.values[0]
                fp.write("R%dC%d " % (int(OpR), int(OpC)))
            fp.write("\r\n")
    fp.close()
    print "Instruction sequence added in -> " + outputFileName


if __name__ == "__main__":
    main()
