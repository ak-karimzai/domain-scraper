FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libappindicator3-1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libglu1-mesa \
    libxss1 \
    libxtst6 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libdrm2 \
    libvulkan1 \
    xdg-utils \
    libfontconfig1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.110/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /opt/ && \
    mv /opt/chrome-linux64 /opt/google-chrome && \
    chmod +x /opt/google-chrome/chrome && \
    rm chrome-linux64.zip

RUN wget https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.110/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip -d /opt/ && \
    mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip /opt/chromedriver-linux64

ENV CHROME_BIN=/opt/google-chrome/chrome
ENV PATH=$PATH:/usr/local/bin

RUN /opt/google-chrome/chrome --version && chromedriver --version

WORKDIR /app

COPY . /app

RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/app/venv/bin:$PATH"

CMD ["python", "scraper.py"]
