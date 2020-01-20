# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify,url_for,render_template,request,g
import sqlalchemy
import time
from multiprocessing import Value

counter = Value('i', 0)
# web app
app = Flask(__name__,template_folder="templates")

# database engine
engine = sqlalchemy.create_engine("postgresql://readonly:w2UIO@#bg532!@work-samples-db.cx4wctygygyq.us-east-1.rds.amazonaws.com:5432/work_samples")



@app.route('/')
def index():
    with counter.get_lock():
        counter.value += 1
    
    title= 'Welcome to EQ Works 😎'
    return render_template('index.html', title= title,count = counter.value)
   

app.run(processes = 8)

@app.route('/events/hourly')
def events_hourly():
    e_h = queryHelper('''
        SELECT date, hour, events
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''').get_json()
    try:
        return render_template('events_hourly.html', title='events/hourly',e_h= e_h)
    except Exception as e:
        return render_template("template/500.html",error=str(e))
   
@app.route('/events/daily')
def events_daily():
    e_d = queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''').get_json()
    try:
        return render_template('events_daily.html', title='event/daily',e_d= e_d)
    except Exception as e:
        return render_template("error_handler/500.html",error=str(e))


@app.route('/stats/hourly')
def stats_hourly():
    s_h=queryHelper('''
        SELECT date, hour, impressions, clicks, revenue
        FROM public.hourly_stats
        ORDER BY date, hour
        LIMIT 168;
    ''').get_json()
    try:
        return render_template('stats_hourly.html', title='stats/hourly',s_h= s_h)
    except Exception as e:
        return render_template("error_handler/500.html",error=str(e))

    


@app.route('/stats/daily')
def stats_daily():
    s_d = queryHelper('''
        SELECT date,
            SUM(impressions) AS impressions,
            SUM(clicks) AS clicks,
            SUM(revenue) AS revenue
        FROM public.hourly_stats
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''').get_json()
    try:    
        return render_template('stats_daily.html', title='stats/daily',s_d= s_d)
    except Exception as e:
        return render_template("error_handler/500.html",error=str(e))

@app.route('/poi')
def poi():
    locations=queryHelper('''
        SELECT *
        FROM public.poi;
    ''').get_json()
    new_table = queryHelper('''
        SELECT *
        FROM public.hourly_events
        INNER JOIN public.poi ON public.hourly_events.poi_id = public.poi.poi_id
        ORDER BY date, hour
        LIMIT 20;
    ''').get_json()
    try:
        return render_template('poi.html',title="poi",locations=locations,new_table=new_table)
    except Exception as e:
        return render_template("error_handler/500.html",error=str(e))

def queryHelper(query):
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return jsonify([dict(row.items()) for row in result])

