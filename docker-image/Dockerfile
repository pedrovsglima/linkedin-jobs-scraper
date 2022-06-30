FROM python:3.8-alpine3.14

COPY ./crontab /var/spool/cron/crontabs/root

RUN apk --no-cache add curl grep sed dos2unix

RUN dos2unix /var/spool/cron/crontabs/root

RUN pip install gspread oauth2client beautifulsoup4

CMD crond -l 2 -f && tail -f /var/log/cron.log