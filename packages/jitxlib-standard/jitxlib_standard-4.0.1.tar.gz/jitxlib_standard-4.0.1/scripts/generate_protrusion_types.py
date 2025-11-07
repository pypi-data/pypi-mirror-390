import argparse
import csv

from dataclasses import dataclass


@dataclass
class Fillets:
    toe: float
    heel: float
    side: float
    courtyard_excess: float

    @staticmethod
    def from_tuple(data):
        toeStr, heelStr, sideStr, excessStr = list(data)
        return Fillets(float(toeStr), float(heelStr), float(sideStr), float(excessStr))

    def __repr__(self) -> str:
        return f"LeadFillets({self.toe}, {self.heel}, {self.side}, {self.courtyard_excess})"


@dataclass
class ProtrusionType:
    name: str
    # Each type has multiple rows, one for each density
    #   level.
    fillets: dict[str, Fillets]


def setup_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--csv", help="path to the CSV file to parse for the protrusion data."
    )
    parser.add_argument(
        "-f",
        "--out-file",
        default="protrusions.py",
        help="Python file to create containing the protrusion definitions. Default is the current directory '%(default)s'.",
    )

    return parser.parse_args()


def extract_data(csv_file) -> dict[str, ProtrusionType]:
    with open(csv_file) as f:
        reader = csv.reader(f, delimiter=",")
        header = None
        prot_table = {}
        for row in reader:
            if not row:
                continue
            if header is None:
                header = row
                continue

            # For each row - we need to extract
            #   out:
            #   Name, DensityLevel, Toe, Heel, Side, Courtyard Excess
            name, density, *fillet_data = list(row)
            name = name.strip()
            density = density.strip(' "')
            entry = prot_table.setdefault(name, ProtrusionType(name, {}))
            if density in entry.fillets:
                print(
                    f"Density '{density}' already exists for protrusion type '{name}' - overwriting"
                )
            entry.fillets[density] = Fillets.from_tuple(fillet_data)

    return prot_table


def generate_protrusion_file(prot_table: dict[str, ProtrusionType], opts):
    with open(opts.out_file, "w") as f:
        f.write("# Auto-Generated File\n")
        f.write("\n")
        f.write("from jitxstd.landpatterns.ipc import DensityLevel\n")
        f.write("from jitxstd.landpatterns.leads.fillets import LeadFillets\n")
        f.write("from jitxstd.landpatterns.leads.protrusion import LeadProtrusion\n")

        f.write("\n")
        for name, data in prot_table.items():
            f.write(f'{name} = LeadProtrusion(\n    "{name}",\n    {{\n')
            for level, fillets in data.fillets.items():
                f.write(f"        DensityLevel.{level}: {repr(fillets)},\n")
            f.write("    },\n)\n")


def main():
    opts = setup_opts()

    prot_table = extract_data(opts.csv)

    generate_protrusion_file(prot_table, opts)


if __name__ == "__main__":
    main()
