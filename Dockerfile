FROM rust:alpine AS build

COPY . .
RUN cargo install --path .

ENTRYPOINT ["catboy-maid"]
CMD ["-c", "/config"]
