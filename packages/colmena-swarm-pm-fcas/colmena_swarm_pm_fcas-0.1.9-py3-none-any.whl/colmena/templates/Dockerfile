FROM {{BASE_IMAGE}}
COPY . /home
WORKDIR /home
RUN python3 -m pip install .
ENTRYPOINT ["start"]
