import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import ttk

# Cria o banco de dados e as tabelas
def criar_banco():
    conn = sqlite3.connect("produtos.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade_vendida INTEGER,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Salvar produto no banco
def salvar_produto():
    nome = entrada_nome.get()
    qtd = entrada_qtd.get()
    preco = entrada_preco.get()

    if nome and qtd and preco:
        try:
            conn = sqlite3.connect("produtos.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)",
                           (nome, int(qtd), float(preco)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            entrada_nome.delete(0, tk.END)
            entrada_qtd.delete(0, tk.END)
            entrada_preco.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos.")
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos.")

# Registrar uma venda
def registrar_venda(produto_id, quantidade):
    conn = sqlite3.connect("produtos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vendas (produto_id, quantidade_vendida) VALUES (?, ?)", (produto_id, quantidade))
    conn.commit()
    conn.close()

# Retornar total vendido
def quantidade_vendida(produto_id):
    conn = sqlite3.connect("produtos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(quantidade_vendida) FROM vendas WHERE produto_id = ?", (produto_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0

# Retornar estoque atual
def estoque_atual(produto_id):
    conn = sqlite3.connect("produtos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        cadastrado = resultado[0]
        return cadastrado - quantidade_vendida(produto_id)
    else:
        return None

# Função para registrar venda
def vender_produto():
    try:
        id_produto = int(entry_id.get())
        qtd_venda = int(entry_venda.get())
        atual = estoque_atual(id_produto)
        if atual is None:
            messagebox.showerror("Erro", f"Produto ID {id_produto} não encontrado.")
            return

        if qtd_venda <= atual:
            registrar_venda(id_produto, qtd_venda)
            messagebox.showinfo("Venda registrada", f"Estoque atualizado: {estoque_atual(id_produto)} unidades restantes.")
        else:
            messagebox.showerror("Erro", f"Estoque insuficiente. Disponível: {atual} unidades.")
    except ValueError:
        messagebox.showerror("Erro", "Informe valores numéricos válidos para ID e quantidade.")


def listar_produtos():
    for item in tabela.get_children():
        tabela.delete(item)

    conn = sqlite3.connect("produtos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    for p in produtos:
        id_produto, nome, qtd, preco = p
        estoque = estoque_atual(id_produto)
        tabela.insert("", "end", values=(id_produto, nome, f"{preco:.2f}", estoque))


# Interface Gráfica
criar_banco()
janela = tk.Tk()
janela.title("Cadastro de Produtos + Vendas")
janela.geometry("350x450")

# Cadastro de produtos
tk.Label(janela, text="Nome do Produto").pack()
entrada_nome = tk.Entry(janela)
entrada_nome.pack()

tk.Label(janela, text="Quantidade Inicial").pack()
entrada_qtd = tk.Entry(janela)
entrada_qtd.pack()

tk.Label(janela, text="Preço (R$)").pack()
entrada_preco = tk.Entry(janela)
entrada_preco.pack()

tk.Button(janela, text="Cadastrar Produto", command=salvar_produto).pack(pady=10)

# Registro de venda
tk.Label(janela, text="ID do Produto").pack()
entry_id = tk.Entry(janela)
entry_id.pack()

tk.Label(janela, text="Quantidade Vendida").pack()
entry_venda = tk.Entry(janela)
entry_venda.pack()

tk.Button(janela, text="Registrar Venda", command=vender_produto).pack(pady=10)
tk.Button(janela, text="Listar Produtos", command=listar_produtos).pack(pady=10)


frame_tabela = tk.Frame(janela)
frame_tabela.pack(pady=10)

colunas = ("ID", "Nome", "Preço", "Estoque")
tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=8)

for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, anchor=tk.CENTER, width=80)

# Barra de rolagem
scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
tabela.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tabela.pack()

listar_produtos()
janela.mainloop()