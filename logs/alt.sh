cd /d/Research-Publishing/07-ncert-deletions/full-corpus
for p in gess1:20210813011729 gess3:20200508031850 iess4:20210814004017 hess3:20210814170507 jess3:20200517154230 jess4:20200517045511 kehs1:20200615215721; do
  ../venv/Scripts/python -X utf8 -I code/fetch_alt.py ${p%%:*} ${p##*:} old_alt
done
