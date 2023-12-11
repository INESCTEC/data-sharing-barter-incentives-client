# Step 1 Build RUST library Python bindings required for the project
FROM python:3.8-buster as build
WORKDIR /build_dir

RUN apt-get update && apt-get install -y git build-essential curl libudev-dev clang
# musl-dev

# install rust for python bindings
RUN git clone -b production https://github.com/iotaledger/wallet.rs.git
RUN git clone -b production https://github.com/iotaledger/iota.rs.git
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN rustup target add x86_64-unknown-linux-musl
RUN pip install maturin
RUN cd wallet.rs/bindings/python/native && maturin build --manylinux off
RUN cd iota.rs/bindings/python/native && maturin build --manylinux off

# RUN cd wallet.rs/bindings/python/native && cargo build --release
# RUN cd iota.rs/bindings/python/native && cargo build --release


# Step 2 Build Final version
FROM python:3.8-buster

#change working directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements
COPY requirements.txt /app/requirements.txt

COPY --from=build  /build_dir/wallet.rs/bindings/python/native/target/wheels/ /app

RUN export LD_LIBRARY_PATH=/usr/local/lib
RUN apt-get update && apt-get install -y build-essential openssh-client nano

# update PIP
RUN pip install --upgrade pip
# install required packages
RUN pip install -r requirements.txt

RUN pip install *.whl

# copy project
COPY . /app
# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]