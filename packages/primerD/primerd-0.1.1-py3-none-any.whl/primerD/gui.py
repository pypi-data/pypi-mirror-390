# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from .core import generate_primers

def run_gui():
    primers_df = None
    dna_sequence = ""
    primer_len = 18

    def load_file():
        filepath = filedialog.askopenfilename(filetypes=[("FASTA files","*.fasta *.fa *.txt")])
        if filepath:
            with open(filepath,"r") as f:
                lines = [line.strip() for line in f if not line.startswith(">")]
                seq = "".join(lines)
                dna_entry.config(state=tk.NORMAL)
                dna_entry.delete(1.0, tk.END)
                dna_entry.insert(tk.END, seq)
                dna_entry.config(state=tk.DISABLED)
                length_entry.delete(0, tk.END)
                length_entry.insert(0,str(min(18,max(12,len(seq)//50))))

    def calculate_primers_gui():
        nonlocal primers_df, dna_sequence, primer_len
        dna_sequence = dna_entry.get(1.0, tk.END).strip().upper()
        try:
            primer_len = int(length_entry.get())
        except:
            messagebox.showerror("Error","Please enter a valid primer length")
            return
        if not dna_sequence:
            messagebox.showerror("Error","Please enter a DNA sequence")
            return

        primers = generate_primers(dna_sequence, primer_len)
        primers_df = pd.DataFrame(primers)
        primers_df = primers_df.sort_values(by="Quality", ascending=False).reset_index(drop=True)

        text_result.config(state=tk.NORMAL)
        text_result.delete(1.0, tk.END)
        header = f"{'Forward':<20} {'GC':<6} {'Tm':<6} {'Quality':<8} {'Reverse':<20} {'GC':<6} {'Tm':<6}\n"
        text_result.insert(tk.END, header)
        text_result.insert(tk.END, "-"*85 + "\n")

        for idx, row in primers_df.iterrows():
            line = f"{row['Forward']:<20} {row['GC_F']:<6.1f} {row['Tm_F']:<6} {row['Quality']:<8} {row['Reverse']:<20} {row['GC_R']:<6.1f} {row['Tm_R']:<6}\n"
            start_index = text_result.index(tk.END)
            text_result.insert(tk.END, line)
            end_index = text_result.index(tk.END)
            if row['Quality'] == "Good" and idx < 3:
                text_result.tag_add(f"green{idx}", start_index, end_index)
                text_result.tag_config(f"green{idx}", foreground="green")

        text_result.config(state=tk.DISABLED)

    def save_result():
        nonlocal primers_df
        if primers_df is None:
            messagebox.showerror("Error","No primers calculated")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if save_path:
            primers_df.to_csv(save_path, index=False)
            fig, axes = plt.subplots(1, 3, figsize=(15,5))
            axes[0].hist(primers_df["GC_F"], bins=20, alpha=0.7, label="Forward", color="blue")
            axes[0].hist(primers_df["GC_R"], bins=20, alpha=0.7, label="Reverse", color="brown")
            axes[0].set_title("GC Content Distribution")
            axes[0].set_xlabel("%GC")
            axes[0].set_ylabel("Count")
            axes[0].legend()

            axes[1].hist(primers_df["Tm_F"], bins=20, alpha=0.7, label="Forward", color="blue")
            axes[1].hist(primers_df["Tm_R"], bins=20, alpha=0.7, label="Reverse", color="brown")
            axes[1].set_title("Tm Distribution")
            axes[1].set_xlabel("Tm (°C)")
            axes[1].set_ylabel("Count")
            axes[1].legend()

            counts = primers_df["Quality"].value_counts()
            axes[2].pie(counts, labels=counts.index, autopct="%1.1f%%", colors=["green","red"])
            axes[2].set_title("Primer Quality")

            plot_path = save_path.replace(".csv","_plots.png")
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()

            messagebox.showinfo("Saved",f"Primers report saved!\nCSV: {save_path}\nPlots: {plot_path}")

    # ===========================
    # Main GUI
    # ===========================
    root = tk.Tk()
    root.title("PCR Primer Designer - Developed by Sarah")
    root.geometry("800x500")
    root.resizable(False, False)

    frame_input = tk.Frame(root, padx=10, pady=10)
    frame_input.pack(fill="x")

    tk.Label(frame_input,text="Enter DNA sequence:").grid(row=0,column=0,sticky="w")
    dna_entry = tk.Text(frame_input,height=5,width=60)
    dna_entry.grid(row=1,column=0,columnspan=2,pady=5,sticky="w")

    tk.Button(frame_input,text="Load FASTA file",command=load_file,width=15).grid(row=0,column=2,padx=5)
    tk.Label(frame_input,text="Primer length:").grid(row=2,column=0,sticky="w", pady=5)
    length_entry = tk.Entry(frame_input,width=10)
    length_entry.grid(row=2,column=1,sticky="w")
    length_entry.insert(0,"18")

    tk.Button(frame_input,text="Calculate Primers",command=calculate_primers_gui,width=15).grid(row=2,column=2,padx=5)
    tk.Button(frame_input,text="Save Result",command=save_result,width=15).grid(row=3,column=2,pady=5)

    frame_table = tk.Frame(root)
    frame_table.pack(fill="both", expand=True)
    text_scroll = tk.Scrollbar(frame_table)
    text_scroll.pack(side=tk.RIGHT,fill=tk.Y)
    text_result = tk.Text(frame_table,height=15,width=95,yscrollcommand=text_scroll.set)
    text_result.pack(side="left",fill="both")
    text_scroll.config(command=text_result.yview)

    root.mainloop()
