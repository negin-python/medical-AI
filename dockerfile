FROM python:3.13 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
FROM python:3.13 AS runner
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . . 
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
