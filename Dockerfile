FROM python:3.11-slim

WORKDIR /app

# Copia apenas requirements.txt primeiro
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Agora copia o restante do projeto
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
