FROM ubuntu:latest

# Установка необходимых пакетов, включая git
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libboost-all-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    git  # Добавляем установку git

# Клонирование репозитория SentencePiece
WORKDIR /app
RUN git clone https://github.com/google/sentencepiece.git

# Переход в директорию SentencePiece
WORKDIR /app/sentencepiece

# Сборка C++ библиотеки
RUN mkdir build
RUN cd build && cmake .. -DSPM_ENABLE_SHARED=OFF -DCMAKE_INSTALL_PREFIX=../root
RUN cd build && cmake --build . --config Release --target install

# Переход в директорию Python
WORKDIR /app/sentencepiece/python

# Установка зависимостей и сборка wheel-файла
RUN pip3 install wheel setuptools
RUN python3 setup.py bdist_wheel

# Копирование wheel-файла в текущую директорию
RUN cp dist/sentencepiece*.whl /app/
