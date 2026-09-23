"""OpenPyXL example: write a small quantity workbook."""

from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Quantity"
    sheet["A1"] = "Component"
    sheet["B1"] = "Volume m3"
    sheet.append(["Beam B1", 1.08])
    sheet.append(["Column C1", 1.30])

    output_path = output_dir / "quantity.xlsx"
    workbook.save(output_path)
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
