import time

with open('contraseña.txt', 'r', encoding='utf-8') as f:
            contenido = f.read()
if contenido != "":
    print("El archivo esta vacio")
else:
    data = [u.strip().replace('"', '') for u in contenido.split(',') if u.strip()]
    
    


