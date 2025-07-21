FROM python:3.9-slim
RUN apt update && apt install -y subfinder amass nuclei masscan
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "recon_tool.py"]