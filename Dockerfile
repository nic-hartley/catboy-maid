FROM python:3 AS build
RUN mkdir source/
COPY . ./source
RUN pip wheel ./source

FROM python:alpine AS run
COPY --from=build *.whl .
RUN pip install catboy_maid-*.whl

ENTRYPOINT [ "catboy-maid", "-c", "/cm" ]
