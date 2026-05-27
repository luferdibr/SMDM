import bcrypt

senha = "1234"

hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

print(hash_senha.decode())
