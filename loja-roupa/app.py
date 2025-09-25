import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
from datetime import date
#NOMES:ELIAS-DANIEL,JUAN-PABLO,VICTOR-HUGO-KIFFER,JULIO-CESAR,LEONARDO-COSTA,GRUPO 9

# ========== BANCO DE USUÁRIOS ==========
def criar_tabela_usuarios():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            senha_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def usuario_existe(email):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('SELECT email FROM usuarios WHERE email=?', (email,))
    existe = c.fetchone() is not None
    conn.close()
    return existe

def cadastrar_no_banco(email, senha_hash):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('INSERT INTO usuarios (email, senha_hash) VALUES (?, ?)', (email, senha_hash))
    conn.commit()
    conn.close()

def validar_login(email, senha_hash):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('SELECT senha_hash FROM usuarios WHERE email=?', (email,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == senha_hash:
        return True
    return False

# ========== BANCO DE PRODUTOS ==========
def conectar():
    return sqlite3.connect("estoque.db")

def criar_tabela_produtos():
    conn = conectar()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    vendidos INTEGER DEFAULT 0,
                    data TEXT
                )''')
    conn.commit()
    conn.close()

# ========== TELA PRINCIPAL ==========
def abrir_main():
    main = tk.Tk()
    main.title("Controle de Estoque de Roupas")
    main.geometry("700x400")

    criar_tabela_produtos()

    # Cadastro de produto
    frame_cadastro = tk.LabelFrame(main, text="Adicionar Produto")
    frame_cadastro.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0)
    entry_nome = tk.Entry(frame_cadastro)
    entry_nome.grid(row=0, column=1)

    tk.Label(frame_cadastro, text="Quantidade:").grid(row=0, column=2)
    entry_qtd = tk.Entry(frame_cadastro)
    entry_qtd.grid(row=0, column=3)

    def adicionar_produto():
        nome = entry_nome.get()
        try:
            qtd = int(entry_qtd.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido para quantidade")
            return

        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO produtos (nome, quantidade, vendidos, data) VALUES (?, ?, ?, ?)",
                  (nome, qtd, 0, str(date.today())))
        conn.commit()
        conn.close()
        listar_produtos()
        entry_nome.delete(0, tk.END)
        entry_qtd.delete(0, tk.END)

    btn_add = tk.Button(frame_cadastro, text="Adicionar", command=adicionar_produto)
    btn_add.grid(row=0, column=4, padx=5)

    # Registrar venda
    frame_venda = tk.LabelFrame(main, text="Registrar Venda")
    frame_venda.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_venda, text="ID Produto:").grid(row=0, column=0)
    entry_id = tk.Entry(frame_venda)
    entry_id.grid(row=0, column=1)

    tk.Label(frame_venda, text="Quantidade Vendida:").grid(row=0, column=2)
    entry_venda = tk.Entry(frame_venda)
    entry_venda.grid(row=0, column=3)

    def registrar_venda():
        try:
            id_prod = int(entry_id.get())
            qtd_vendida = int(entry_venda.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos")
            return

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT quantidade, vendidos FROM produtos WHERE id=?", (id_prod,))
        produto = c.fetchone()

        if produto:
            qtd_atual, vendidos = produto
            if qtd_atual >= qtd_vendida:
                novo_estoque = qtd_atual - qtd_vendida
                novos_vendidos = vendidos + qtd_vendida
                c.execute("UPDATE produtos SET quantidade=?, vendidos=? WHERE id=?",
                          (novo_estoque, novos_vendidos, id_prod))
                conn.commit()
            else:
                messagebox.showwarning("Estoque insuficiente", "Não há estoque suficiente.")
        else:
            messagebox.showerror("Erro", "Produto não encontrado.")
        conn.close()
        listar_produtos()
        entry_id.delete(0, tk.END)
        entry_venda.delete(0, tk.END)

    btn_venda = tk.Button(frame_venda, text="Registrar Venda", command=registrar_venda)
    btn_venda.grid(row=0, column=4, padx=5)

    # Lista de produtos
    frame_lista = tk.LabelFrame(main, text="Produtos em Estoque")
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

    colunas = ("ID", "Nome", "Quantidade", "Vendidos", "Data")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill="both", expand=True)

    # Configura tags para cores
    tree.tag_configure('estoque_baixo', background='#fff3cd')   # amarelo claro
    tree.tag_configure('estoque_zero', background='#ffcccc')    # vermelho claro

    def listar_produtos():
        for i in tree.get_children():
            tree.delete(i)
        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT id, nome, quantidade, vendidos, data FROM produtos")
        for row in c.fetchall():
            # Estoque zerado
            if row[2] == 0:
                tree.insert("", tk.END, values=row, tags=('estoque_zero',))
            # Estoque baixo (1 a 10)
            elif 1 <= row[2] <= 10:
                tree.insert("", tk.END, values=row, tags=('estoque_baixo',))
            else:
                tree.insert("", tk.END, values=row)
        conn.close()

    # Atualizar estoque
    frame_atualiza = tk.LabelFrame(main, text="Atualizar Estoque (Compra de Produto)")
    frame_atualiza.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_atualiza, text="ID Produto:").grid(row=0, column=0)
    entry_id_atualiza = tk.Entry(frame_atualiza)
    entry_id_atualiza.grid(row=0, column=1)

    tk.Label(frame_atualiza, text="Quantidade Comprada:").grid(row=0, column=2)
    entry_qtd_atualiza = tk.Entry(frame_atualiza)
    entry_qtd_atualiza.grid(row=0, column=3)

    def atualizar_estoque():
        try:
            id_prod = int(entry_id_atualiza.get())
            qtd_comprada = int(entry_qtd_atualiza.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos")
            return

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT quantidade FROM produtos WHERE id=?", (id_prod,))
        produto = c.fetchone()

        if produto:
            qtd_atual = produto[0]
            novo_estoque = qtd_atual + qtd_comprada
            c.execute("UPDATE produtos SET quantidade=? WHERE id=?", (novo_estoque, id_prod))
            conn.commit()
            messagebox.showinfo("Estoque Atualizado", f"Novo estoque do produto {id_prod}: {novo_estoque}")
        else:
            messagebox.showerror("Erro", "Produto não encontrado.")
        conn.close()
        listar_produtos()
        entry_id_atualiza.delete(0, tk.END)
        entry_qtd_atualiza.delete(0, tk.END)

    btn_atualiza = tk.Button(frame_atualiza, text="Atualizar Estoque", command=atualizar_estoque)
    btn_atualiza.grid(row=0, column=4, padx=5)

    listar_produtos()
    main.mainloop()

# ========== TELA DE LOGIN E CADASTRO ==========
def iniciar_login():
    criar_tabela_usuarios()
    login = tk.Tk()
    login.title("LOGIN RENNER")
    login.geometry("400x520")
    login.configure(bg="white")

    # Frame de Login
    frame_login = tk.Frame(login, bg="white")

    label_logo = tk.Label(frame_login, text="RENNER", font=("Arial", 24, "bold"), fg="#0077b6", bg="white")
    label_logo.pack(pady=10)

    label_matricula = tk.Label(frame_login, text="E-mail", anchor="center", bg="white")
    label_matricula.pack(pady=(0,2))
    entry_matricula = tk.Entry(
        frame_login, width=30, relief="flat",
        highlightthickness=2, highlightbackground="#bdbdbd", highlightcolor="#0077b6"
    )
    entry_matricula.pack(pady=5)

    label_senha = tk.Label(frame_login, text="Senha", anchor="center", bg="white")
    label_senha.pack(pady=(10,2))
    senha_frame = tk.Frame(frame_login, bg="white")
    senha_frame.pack(pady=5)
    entry_senha = tk.Entry(
        senha_frame, width=30, show="*", relief="flat",
        highlightthickness=2, highlightbackground="#bdbdbd", highlightcolor="#0077b6"
    )
    entry_senha.pack(side="left")

    def fazer_login():
        matricula = entry_matricula.get().strip().lower()
        senha = entry_senha.get()
        if " " in matricula:
            messagebox.showwarning("Erro", "O e-mail não pode conter espaços.")
            return
        if not matricula or not senha:
            messagebox.showwarning("Erro", "Preencha todos os campos.")
        elif "@" not in matricula or "." not in matricula:
            messagebox.showwarning("Erro", "Digite um e-mail válido.")
        elif not usuario_existe(matricula):
            messagebox.showwarning("Erro", "E-mail não cadastrado.")
        else:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if validar_login(matricula, senha_hash):
                messagebox.showinfo("Login", f"Logado com sucesso!\nBem-vindo, {matricula}")
                login.destroy()
                abrir_main()
            else:
                messagebox.showwarning("Erro", "Senha incorreta.")

    btn_login = tk.Button(frame_login, text="Entrar", bg="#0077b6", fg="white", font=("Arial", 11, "bold"), width=30, command=fazer_login)
    btn_login.pack(pady=15)

    btn_cadastrar = tk.Button(frame_login, text="Cadastrar", font=("Arial", 10, "underline"), fg="#0077b6", bg="white", bd=0, cursor="hand2", command=lambda: alternar_frames())
    btn_cadastrar.pack(pady=(0, 10))

    frame_login.pack(expand=True)

    # Frame de Cadastro
    frame_cadastro = tk.Frame(login, bg="white")

    label_cad = tk.Label(frame_cadastro, text="Cadastro", font=("Arial", 24, "bold"), fg="#0077b6", bg="white")
    label_cad.pack(pady=10)

    label_email_cad = tk.Label(frame_cadastro, text="E-mail", anchor="center", bg="white")
    label_email_cad.pack(pady=(0, 2))
    entry_email_cad = tk.Entry(
        frame_cadastro, width=30, relief="flat",
        highlightthickness=2, highlightbackground="#bdbdbd", highlightcolor="#0077b6"
    )
    entry_email_cad.pack(pady=5)

    label_senha_cad = tk.Label(frame_cadastro, text="Senha", anchor="center", bg="white")
    label_senha_cad.pack(pady=(10, 2))
    senha_frame_cad = tk.Frame(frame_cadastro, bg="white")
    senha_frame_cad.pack(pady=5)
    entry_senha_cad = tk.Entry(
        senha_frame_cad, width=23, show="*", relief="flat",
        highlightthickness=2, highlightbackground="#bdbdbd", highlightcolor="#0077b6"
    )
    entry_senha_cad.pack(side="left")

    label_confirma_cad = tk.Label(frame_cadastro, text="Confirmar Senha", anchor="center", bg="white")
    label_confirma_cad.pack(pady=(10, 2))
    confirma_frame_cad = tk.Frame(frame_cadastro, bg="white")
    confirma_frame_cad.pack(pady=5)
    entry_confirma_cad = tk.Entry(
        confirma_frame_cad, width=23, show="*", relief="flat",
        highlightthickness=2, highlightbackground="#bdbdbd", highlightcolor="#0077b6"
    )
    entry_confirma_cad.pack(side="left")

    def cadastrar_usuario():
        email = entry_email_cad.get().strip().lower()
        senha = entry_senha_cad.get()
        confirma = entry_confirma_cad.get()
        if " " in email:
            messagebox.showwarning("Erro", "O e-mail não pode conter espaços.")
            return
        if " " in senha:
            messagebox.showwarning("Erro", "A senha não pode conter espaços.")
            return
        if not email or not senha or not confirma:
            messagebox.showwarning("Erro", "Preencha todos os campos.")
        elif "@" not in email or "." not in email:
            messagebox.showwarning("Erro", "Digite um e-mail válido.")
        elif usuario_existe(email):
            messagebox.showwarning("Erro", "E-mail já cadastrado.")
        elif len(senha) < 6:
            messagebox.showwarning("Erro", "A senha deve ter pelo menos 6 caracteres.")
        elif senha != confirma:
            messagebox.showwarning("Erro", "As senhas não coincidem.")
        else:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            cadastrar_no_banco(email, senha_hash)
            messagebox.showinfo("Cadastro", "Usuário cadastrado com sucesso! Faça login.")
            entry_email_cad.delete(0, tk.END)
            entry_senha_cad.delete(0, tk.END)
            entry_confirma_cad.delete(0, tk.END)
            alternar_frames(voltar=True)

    btn_finalizar_cad = tk.Button(frame_cadastro, text="Cadastrar", bg="#0077b6", fg="white", font=("Arial", 11, "bold"), width=30, command=cadastrar_usuario)
    btn_finalizar_cad.pack(pady=15)

    btn_voltar = tk.Button(frame_cadastro, text="Voltar", font=("Arial", 10, "underline"), fg="#0077b6", bg="white", bd=0, cursor="hand2", command=lambda: alternar_frames(voltar=True))
    btn_voltar.pack(pady=(0, 10))

    # Alternância entre login/cadastro
    def alternar_frames(voltar=False):
        if not voltar:
            frame_login.pack_forget()
            frame_cadastro.pack(expand=True)
        else:
            frame_cadastro.pack_forget()
            frame_login.pack(expand=True)

    # Rodapé
    label_footer = tk.Label(login, text="Desenvolvido por você mesmo 😁", font=("Arial", 8), fg="gray", bg="white")
    label_footer.pack(side="bottom", pady=5)

    login.mainloop()

if __name__ == "__main__":
    iniciar_login()