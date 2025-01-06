from importlib.metadata import distributions

# Đọc các thư viện được import từ file code
with open("server_emission.py", "r", encoding="utf-8") as file:
    lines = file.readlines()

libraries = set()
for line in lines:
    if line.startswith("import") or line.startswith("from"):
        parts = line.split()
        lib = parts[1].split(".")[0]  # Lấy tên thư viện
        libraries.add(lib)

# Lấy phiên bản của các thư viện
installed_packages = {dist.metadata['Name']: dist.metadata['Version'] for dist in distributions()}
requirements = []
for lib in libraries:
    if lib in installed_packages:
        requirements.append(f"{lib}=={installed_packages[lib]}")

# Ghi vào file requirements.txt
with open("requirements.txt", "w") as f:
    for req in requirements:
        f.write(req + "\n")

print("File requirements.txt đã được tạo.")
