import pandas as pd
import sys

def generate_latex(csv_file):

    data = pd.read_csv(csv_file)

    latex_rows = ""
    for index, row in data.iterrows():
        latex_rows += (
            f"{row['Unnamed: 0']} & "
            f"-{row['st_swe']:.1f} & "
            f"{row['wt_rof']:.1f} & "
            f"{row['pt_pre']:.1f} & "
            f"{100*row['ft_fsw']:.0f} & "
            f"{row['Num']} & "
            f"{row['Event Length']:.1f} & "
            f"-{row['Average dSWE']:.1f} & "
            f"{row['Average Runoff']:.1f} & "
            f"{row['Average Precip']:.1f} \\\\\n"
        )

    print(latex_rows)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python stats-to-latex.py <path_to_csv_file>")
        print("Ex: python stats-to-latex.py ../output/srb/csv/table_stats_95.csv")
        sys.exit(1)

    csv_file = sys.argv[1]
    generate_latex(csv_file)
