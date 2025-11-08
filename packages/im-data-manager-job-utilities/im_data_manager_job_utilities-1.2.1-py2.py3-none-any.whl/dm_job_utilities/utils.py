"""The content of the virtual-screening repository's utils.py.
"""

# Extracted 19th March 2024
#
# Use this new module with "from dm_job_utilities import utils"
#
# Includes style changes to align with the pre-existing modules
# and the following modifications/changes: -
#
# 'get_path_from_digest()' has been removed because it is obsolete.
#
# 'round_to_significant_number()' has been removed. Its implementation
# was inaccurate and is easily replaced by round() from the sigfig package.

import os
import sys
from typing import Any, List, Optional, Tuple


def log(*args, **kwargs) -> None:
    """Log output to STDERR"""
    print(*args, file=sys.stderr, **kwargs)


def expand_path(path) -> None:
    """Create any necessary directories to ensure that the file path is valid.
    The path is a filename or directory that might or not exist.
    """
    head_tail = os.path.split(path)
    if head_tail[0]:
        if not os.path.isdir(head_tail[0]):
            log("Creating directories for", head_tail[0])
            os.makedirs(head_tail[0], exist_ok=True)


def update_charge_flag_in_atom_block(atom_block) -> str:
    """See https://sourceforge.net/p/rdkit/mailman/message/36425493/
    """
    # To simply fix the missing END, found during unit testing
    # we simply add a line-feed to the input if it needs one.
    if not atom_block.endswith("\n"):
        atom_block += "\n"
    formatter = "{:>10s}" * 3 + "{:>2}{:>4s}" + "{:>3s}" * 11
    chgs = []  # list of charges
    lines = atom_block.split("\n")
    if atom_block[0] == "" or atom_block[0] == "\n":
        del lines[0]
    connection_table = lines[2]
    atom_count = int(connection_table.split()[0])
    # parse mb line per line
    for line in lines:
        # look for M CHG property
        if line[0:6] == "M  CHG":
            records = line.split()[
                3:
            ]  # M  CHG X is not needed for parsing, the info we want comes afterwards
            # record each charge into a list
            for index in range(0, len(records), 2):
                idx = records[index]
                chg = records[index + 1]
                chgs.append((int(idx), int(chg)))  # sort tuples by first element?
            break  # stop iterating

    # sort by idx in order to parse the molblock only once more
    chgs = sorted(chgs, key=lambda x: x[0])

    # that we have a list for the current molblock, attribute each charges
    for chg in chgs:
        index = 3
        while (
            index < 3 + atom_count
        ):  # do not read from beginning each time, rather continue parsing mb!
            # when finding the idx of the atom we want to update,
            # extract all fields and rewrite whole sequence
            if (
                index - 2 == chg[0]
            ):  # -4 to take into account the CTAB headers, +1 because idx begin at 1 and not 0
                fields = lines[index].split()
                x = fields[0]   # pylint: disable=invalid-name
                y = fields[1]   # pylint: disable=invalid-name
                z = fields[2]   # pylint: disable=invalid-name
                symb = fields[3]
                mass_diff = fields[4]
                charge = fields[5]
                sp = fields[6]   # pylint: disable=invalid-name
                hc = fields[7]   # pylint: disable=invalid-name
                scb = fields[8]
                v = fields[9]   # pylint: disable=invalid-name
                hd = fields[10]   # pylint: disable=invalid-name
                nu1 = fields[11]
                nu2 = fields[12]
                aamn = fields[13]
                irf = fields[14]
                ecf = fields[15]
                # update charge flag
                if chg[1] == -1:
                    charge = "5"
                elif chg[1] == -2:
                    charge = "6"
                elif chg[1] == -3:
                    charge = "7"
                elif chg[1] == 1:
                    charge = "3"
                elif chg[1] == 2:
                    charge = "2"
                elif chg[1] == 3:
                    charge = "1"
                else:
                    print(
                        "ERROR! "
                        + str(lines[0])
                        + "unknown charge flag: "
                        + str(chg[1])
                    )  # print name then go to next chg
                    break
                # update modatom block line
                lines[index] = formatter.format(
                    x,
                    y,
                    z,
                    symb,
                    mass_diff,
                    charge,
                    sp,
                    hc,
                    scb,
                    v,
                    hd,
                    nu1,
                    nu2,
                    aamn,
                    irf,
                    ecf,
                )
            index += 1
    # print("\n".join(lines))
    del lines[-1]  # remove empty element left because last character before $$$$ is \n
    upmb = "\n" + "\n".join(lines)
    return upmb


def read_delimiter(input_specifier: str) -> Optional[str]:
    """Returns the character (string) for the given delimiter specifier.
    If the input specifier is None, then the delimiter is None.
    If the input specifier is not recognized, then the input_specifier is returned."""
    if input_specifier:
        if input_specifier == "tab":
            delimiter = "\t"
        elif input_specifier == "space":
            delimiter = None
        elif input_specifier == "comma":
            delimiter = ","
        elif input_specifier == "pipe":
            delimiter = "|"
        else:
            delimiter = input_specifier
    else:
        delimiter = None
    return delimiter


def calc_geometric_mean(scores: List[float]) -> float:
    """Returns the geometric mean o f the lust of supplied numbers.
    """
    total = 1.0
    for score in scores:
        total = total * score
    return total ** (1.0 / len(scores))


def is_type(value, typ) -> Tuple[int, Any]:
    """Returns a tuple of the form (status, value) where status is
    -1 if the value cannot be of the given type, and 0 if it is. The value
    returned is cast to the given type on success.
    """
    if value is None:
        return 0, value
    try:
        i = typ(value)
        return 1, i
    except:  # pylint: disable=bare-except
        return -1, value
