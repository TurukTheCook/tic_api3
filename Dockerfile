# inheriting python 3 image here. this image does
# not particularly care what OS runs underneath
FROM python:3.6

# RUN apt-get clean \
#     && apt-get -y update
# RUN apt-get -y install python3-dev \
#     && apt-get -y install build-essential

# create the directory and instruct Docker to operate
# from there from now on
WORKDIR /app
COPY . /app

# requirements : in order to install
# Python dependencies
RUN pip install --trusted-host pypi.python.org -r requirments.txt

# testing with pipenv
# RUN pip install pipenv
# RUN pipenv install --system --deploy --ignore-pipfile
# RUN pipenv shell

EXPOSE 1407

CMD ["python", "run.py"]