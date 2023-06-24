import pdfplumber
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tabulate import tabulate

def converter_pdf_para_texto(caminho_arquivo_pdf):
    texto = ""
    with pdfplumber.open(caminho_arquivo_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text()
    return texto

def buscar_valores_debitos(texto_pdf, arquivo_nomes_debitos):
    with open(arquivo_nomes_debitos, "r", encoding="utf-8") as arquivo_nomes:
        nomes_debitos = arquivo_nomes.readlines()

    resultados = {}

    nome_debito_atual = None

    for linha in texto_pdf.splitlines():
        for nome_debito in nomes_debitos:
            nome_debito = nome_debito.strip()
            padrao_busca = r"\b{}\b".format(re.escape(nome_debito))
            match = re.search(padrao_busca, linha, re.IGNORECASE)
            if match and "DEVEDOR" in linha.upper():
                nome_debito_atual = nome_debito
                break

        if nome_debito_atual:
            valores = re.findall(r"(\d{1,3}(?:\.\d{3})*,\d{2})", linha)
            if valores:
                valor = float(valores[1].replace(".", "").replace(",", "."))
                if nome_debito_atual in resultados:
                    resultados[nome_debito_atual] += valor
                else:
                    resultados[nome_debito_atual] = valor
                nome_debito_atual = None

    resultados = {nome: round(valor, 2) for nome, valor in resultados.items()}

    return resultados

def selecionar_arquivo_pdf():
    arquivo = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if arquivo:
        texto_pdf = converter_pdf_para_texto(arquivo)
        caminhos_arquivo = "Debitos.txt"
        debitos = buscar_valores_debitos(texto_pdf, caminhos_arquivo)
        exibir_resultado(debitos)
    else:
        messagebox.showinfo("Aviso", "Nenhum arquivo selecionado.")

def exibir_resultado(debitos):
    janela_resultado = tk.Toplevel(janela)
    janela_resultado.title("Resultado")
    janela_resultado.geometry("500x300")
    janela_resultado.configure(bg="#f0f0f0")

    tabela = []
    for nome, valor in debitos.items():
        tabela.append([nome, valor])

    headers = ["Nome do Débito", "Valor"]
    resultado_table = tabulate(tabela, headers, tablefmt="fancy_grid")

    resultado_label = tk.Label(
        janela_resultado,
        text=resultado_table,
        justify="left",
        font=("Courier New", 12),
        bg="#f0f0f0",
    )
    resultado_label.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

janela = tk.Tk()
janela.title("Extrair Débitos de PDF")
janela.geometry("500x300")
janela.configure(bg="#f0f0f0")

logo_image = tk.PhotoImage(file="color.png")

logo_label = tk.Label(janela, image=logo_image)
logo_label.pack()

titulo_label = tk.Label(
    janela,
    text="Extrair Débitos de PDF",
    font=("Arial", 14),
    bg="#f0f0f0",
)
titulo_label.pack(pady=20)

selecionar_button = tk.Button(
    janela,
    text="Selecionar PDF",
    font=("Arial", 12),
    command=selecionar_arquivo_pdf,
)
selecionar_button.pack(pady=10)

janela.mainloop()