# password_manager.py
import json
import base64
import os
import hashlib
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

VAULT_FILE = "vault.dat"
MASTER_FILE = "master.key"

# -------------------- CRYPTO -------------------- #

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def dict_to_bytes(vault: dict) -> bytes:
    return json.dumps(vault).encode("utf-8")

def bytes_to_dict(b: bytes) -> dict:
    if not b:
        return {}
    return json.loads(b.decode("utf-8"))

def derive_key(password: str, salt: bytes, iterations: int = 200000, key_len: int = 32) -> bytes:
    return PBKDF2(password, salt, dkLen=key_len, count=iterations)

def encrypt_vault(vault_dict: dict, password: str) -> dict:
    data = dict_to_bytes(vault_dict)
    salt = get_random_bytes(16)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

def decrypt_vault(package: dict, password: str) -> dict:
    salt = base64.b64decode(package["salt"])
    nonce = base64.b64decode(package["nonce"])
    tag = base64.b64decode(package["tag"])
    ciphertext = base64.b64decode(package["ciphertext"])
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return bytes_to_dict(data)

def save_vault_file(vault_dict: dict, master_password: str):
    package = encrypt_vault(vault_dict, master_password)
    with open(VAULT_FILE, "wb") as f:
        f.write(json.dumps(package).encode())

def load_vault_file(master_password: str) -> dict:
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, "rb") as f:
        data = json.loads(f.read().decode())
    return decrypt_vault(data, master_password)

# -------------------- INTERFACE -------------------- #

def logout(main_win):
    # ferme la fenêtre principale puis revient à l'écran de login
    try:
        main_win.destroy()
    except Exception:
        pass
    login_screen()

def change_master_password_window(vault: dict, old_master_password: str):
    win = tb.Toplevel(title="Changer le mot de passe", resizable=(False, False))

    tb.Label(win, text="Ancien mot de passe :").pack(padx=10, pady=(10,0))
    entry_old = tb.Entry(win, show="*")
    entry_old.pack(padx=10, pady=(0,10))

    tb.Label(win, text="Nouveau mot de passe :").pack(padx=10)
    entry_new = tb.Entry(win, show="*")
    entry_new.pack(padx=10, pady=(0,10))

    def change_pw():
        # lire hash stocké
        if not os.path.exists(MASTER_FILE):
            messagebox.showerror("Erreur", "Fichier master introuvable")
            return
        with open(MASTER_FILE, "r") as f:
            stored = f.read().strip()
        if hash_password(entry_old.get()) != stored:
            messagebox.showerror("Erreur", "Ancien mot de passe incorrect")
            return

        new_pw = entry_new.get()
        if len(new_pw) < 4:
            messagebox.showerror("Erreur", "Mot de passe trop court (min 4 caractères)")
            return

        # stocker nouveau hash
        with open(MASTER_FILE, "w") as f:
            f.write(hash_password(new_pw))

        # ré-encrypter vault avec le nouveau mot de passe
        save_vault_file(vault, new_pw)
        messagebox.showinfo("OK", "Mot de passe maître modifié.")
        win.destroy()

    tb.Button(win, text="Modifier", bootstyle=SUCCESS, command=change_pw).pack(pady=10)

def add_entry_window(vault: dict, master_password: str, listbox: tk.Listbox):
    win = tb.Toplevel(title="Ajouter", resizable=(False, False))

    tb.Label(win, text="Site :").pack(padx=10, pady=(10,0))
    entry_site = tb.Entry(win)
    entry_site.pack(padx=10, pady=(0,5))

    tb.Label(win, text="Utilisateur :").pack(padx=10)
    entry_user = tb.Entry(win)
    entry_user.pack(padx=10, pady=(0,5))

    tb.Label(win, text="Mot de passe :").pack(padx=10)
    entry_pwd = tb.Entry(win)
    entry_pwd.pack(padx=10, pady=(0,10))

    def add():
        site = entry_site.get().strip()
        user = entry_user.get().strip()
        pwd = entry_pwd.get().strip()
        if not site or not user or not pwd:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
            return
        if site in vault:
            messagebox.showerror("Erreur", "Site déjà existant")
            return
        vault[site] = {"user": user, "password": pwd}
        save_vault_file(vault, master_password)
        listbox.insert(tk.END, site)
        win.destroy()

    tb.Button(win, text="Ajouter", bootstyle=SUCCESS, command=add).pack(pady=10)

def show_main_screen(master_password: str):
    main = tb.Window(title="Password Manager", themename="darkly")
    main.geometry("640x480")

    # Charger le vault (protéger contre mot de passe incorrect)
    try:
        vault = load_vault_file(master_password)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger le vault : {e}")
        vault = {}

    tb.Label(main, text="Coffre-fort", font=("Arial", 20)).pack(pady=12)

    # Utiliser tk.Listbox (ttkbootstrap ne propose pas Listbox)
    listbox = tk.Listbox(
        main,
        height=15,
        bg="#1b1e23",
        fg="white",
        selectbackground="#0d6efd",
        highlightbackground="#2d2f33",
        relief="flat"
    )
    listbox.pack(pady=10, fill="both", padx=20, expand=True)

    # Charger les sites
    for site in vault:
        listbox.insert(tk.END, site)

    frame = tb.Frame(main)
    frame.pack(pady=8)

    tb.Button(frame, text="Ajouter", bootstyle=SUCCESS,
              command=lambda: add_entry_window(vault, master_password, listbox)).grid(row=0, column=0, padx=8)

    def on_view():
        sel = listbox.curselection()
        if not sel:
            messagebox.showerror("Erreur", "Aucun site sélectionné")
            return
        site = listbox.get(sel[0])
        info = vault.get(site, {})
        messagebox.showinfo(site, f"Utilisateur : {info.get('user','')}\nMot de passe : {info.get('password','')}")

    tb.Button(frame, text="Voir", bootstyle=INFO, command=on_view).grid(row=0, column=1, padx=8)

    tb.Button(frame, text="Supprimer", bootstyle=DANGER,
              command=lambda: delete_site(vault, master_password, listbox)).grid(row=0, column=2, padx=8)

    tb.Button(main, text="Modifier mot de passe maître", bootstyle=WARNING,
              command=lambda: change_master_password_window(vault, master_password)).pack(pady=6)

    tb.Button(main, text="Déconnexion", bootstyle=SECONDARY,
              command=lambda: logout(main)).pack(pady=6)

    main.mainloop()

def delete_site(vault: dict, master_password: str, listbox: tk.Listbox):
    sel = listbox.curselection()
    if not sel:
        messagebox.showerror("Erreur", "Aucun site sélectionné")
        return
    index = sel[0]
    site = listbox.get(index)
    if messagebox.askyesno("Supprimer ?", f"Supprimer {site} ?"):
        if site in vault:
            del vault[site]
        listbox.delete(index)
        save_vault_file(vault, master_password)

# -------------------- LOGIN -------------------- #

def login_screen():
    login = tb.Window(title="Connexion", themename="darkly")
    login.geometry("380x220")

    tb.Label(login, text="Password Manager", font=("Arial", 18)).pack(pady=12)

    # Première connexion ?
    if not os.path.exists(MASTER_FILE):
        tb.Label(login, text="Créer un mot de passe maître :").pack(pady=(6,0))
        entry = tb.Entry(login, show="*")
        entry.pack(padx=20, pady=6)

        def create_master():
            pw = entry.get()
            if len(pw) < 4:
                messagebox.showerror("Erreur", "Mot de passe trop court (min 4 caractères)")
                return
            with open(MASTER_FILE, "w") as f:
                f.write(hash_password(pw))
            # créer vault vide chiffré avec le mot de passe
            save_vault_file({}, pw)
            login.destroy()
            show_main_screen(pw)

        tb.Button(login, text="Créer", bootstyle=SUCCESS, command=create_master).pack(pady=8)

    else:
        tb.Label(login, text="Mot de passe maître :").pack(pady=(6,0))
        entry = tb.Entry(login, show="*")
        entry.pack(padx=20, pady=6)

        def check():
            pw = entry.get()
            with open(MASTER_FILE, "r") as f:
                stored = f.read().strip()
            if hash_password(pw) != stored:
                messagebox.showerror("Erreur", "Mot de passe incorrect")
                return
            login.destroy()
            show_main_screen(pw)

        tb.Button(login, text="Connexion", bootstyle=PRIMARY, command=check).pack(pady=8)

    login.mainloop()

# -------------------- LANCEMENT -------------------- #
if __name__ == "__main__":
    login_screen()
