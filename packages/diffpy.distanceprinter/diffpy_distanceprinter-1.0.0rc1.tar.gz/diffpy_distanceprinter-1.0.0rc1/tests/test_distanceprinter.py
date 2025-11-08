import os
from io import open

from diffpy.distanceprinter.distanceprinter import main


def test_distanceprinter(monkeypatch):
    current_module_dir = os.path.dirname(__file__)
    example_file_dir = os.path.join(current_module_dir, "data")
    # must be cif, stru, or xyz file
    strufile = os.path.join(example_file_dir, "Ni-9008476.cif")
    # atoms typically pull from list of elements in output of PDFFitStructure.
    # 'all' is always first option
    atomi = "all"
    atomj = "all"
    # lb and ub are lower an upper bound of distance to list in angstroms
    lb = 1
    ub = 10
    # 1 means keep duplicate atom pairs with same inter-atomic distance
    # 0 means not to
    comp = "1"
    monkeypatch.setattr(
        "sys.argv",
        [
            "distanceprinter",
            strufile,
            atomi,
            atomj,
            lb,
            ub,
            comp,
            "tests\\outputs\\actual.res",
        ],
    )
    cwd = os.getcwd()
    main()
    generated_file_path = os.path.join(cwd, "tests\\outputs\\actual.res")
    f = open(generated_file_path, "r", encoding="utf-8")
    rv0 = f.readlines()
    rv0 = "".join(rv0)
    resultstr = rv0
    output_file_dir = os.path.join(current_module_dir, "outputs")
    example_output = os.path.join(output_file_dir, "expected.res")
    f = open(example_output, "r", encoding="utf-8")
    rv1 = f.readlines()
    rv1 = "".join(rv1)
    teststr = rv1

    # Remove stru file path when comparing as it may differ between machines
    resultstr = resultstr.split("\n", 2)[2]
    teststr = teststr.split("\n", 2)[2]

    # Remove irrelevant whitespace when comparing
    resultstr = "".join(resultstr.split())
    teststr = "".join(teststr.split())

    assert resultstr == teststr
