FROM python:3.8-alpine3.14

COPY ./crontab /var/spool/cron/crontabs/root

RUN pip install gspread oauth2client beautifulsoup4

RUN apk --no-cache add curl
RUN apk --no-cache add grep
RUN apk --no-cache add sed

CMD crond -l 2 -f && tail -f /var/log/cron.log