# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify,url_for,render_template,request,g
import sqlalchemy
import time
from multiprocessing import Value

# time list for first connection on server.
# It only needs one element since currently I can only consider the server connect time as start
time_list = [time.time()]

#visitor counter for each api, limit set to 7 hits 
counter = Value('i', 7)
events_hourly_counter = Value('i', 7)
events_daily_counter = Value('i', 7)
stats_hourly_counter = Value('i', 7)
stats_daily_counter = Value('i', 7)
poi_counter = Value('i', 7)

# web app
app = Flask(__name__,template_folder="templates")

# database engine
engine = sqlalchemy.create_engine("postgresql://readonly:w2UIO@#bg532!@work-samples-db.cx4wctygygyq.us-east-1.rds.amazonaws.com:5432/work_samples")


def rate_limit(page_template,title,time_list,counter,data,extra_data):
    current_time = time.time()
    #sleep time for cancel the restriction
    wait_time = 10

    # interval = current_time - time_list[0]
    # for further development, interval value would be used to limit request number per second
    message="hits number reaches,next hit will be waiting 10 seconds"
    if counter.value > 0:
        with counter.get_lock():
            counter.value -= 1
            print("you still got",counter.value,"hits")
            try:
                return render_template(page_template,
                                        title= title,
                                        count = counter.value,
                                        fromtime=time_list[0],
                                        now=time.time(),
                                        wait_time=wait_time,
                                        message=message,
                                        data=data,
                                        extra_data=extra_data)
            except Exception as e:
                return render_template("error_handler/500.html",error=e)  
    else:
        time.sleep(wait_time)
        with counter.get_lock():
             counter.value = 5
        return render_template(page_template,
                                title= title,
                                count = counter.value,
                                fromtime=time_list[0],
                                now=time.time(),
                                wait_time=wait_time,
                                message=message,
                                data=data,
                                extra_data=extra_data)

@app.route('/')
def index():
    title= 'Welcome to EQ Works 😎'
    return rate_limit("index.html",title,time_list,counter,data="nothing here",extra_data="nothing again")
    # current_time = time.time()
    # wait_time = 10
    # interval = current_time - time_list[0]
    # message="hits number reaches,wait 10 seconds and try again"
    # if counter.value > 0:
    #     with counter.get_lock():
    #         counter.value -= 1
    #         print("you still got",counter.value,"hits")
    #         try:
    #             return render_template('index.html', title= title,count = counter.value,fromtime=time_list[0],now=time.time(),wait_time=wait_time,message=message)
    #         except Exception as e:
    #             return render_template("error_handler/404.html",error=e)  
    # else:
    #     time.sleep(wait_time)
    #     with counter.get_lock():
    #          counter.value = 5
    #     return render_template('index.html', title= title,count = counter.value,fromtime=time_list[0],now=time.time(),wait_time=wait_time,message=message)
        # if (interval)<15:
        # return render_template("error_handler/wait_for_reset.html",wait_time=interval) 

        # else:
        #     with counter.get_lock():
        #         counter.value = 5
        #     return render_template('index.html', title= title,count = counter.value,fromtime=time_list[-1],now=time.time())

@app.route('/events/hourly')
def events_hourly():
    title ="events/hourly"
    e_h = queryHelper('''
        SELECT date, hour, events
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''').get_json()
    # try:
    #     return render_template('events_hourly.html', title='events/hourly',e_h= e_h)
    # except Exception as e:
    #     return render_template("template/500.html",error=str(e))
    return rate_limit('events_hourly.html',title,time_list,events_hourly_counter,e_h,extra_data="nothing")
   
@app.route('/events/daily')
def events_daily():
    title ="events/daily"
    e_d = queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''').get_json()
    # try:
    #     return render_template('events_daily.html', title='event/daily',e_d= e_d)
    # except Exception as e:
    #     return render_template("error_handler/500.html",error=str(e))
    return rate_limit('events_daily.html',title,time_list,events_daily_counter,e_d,extra_data="nothing")


@app.route('/stats/hourly')
def stats_hourly():
    title='/stats/hourly'
    s_h=queryHelper('''
        SELECT date, hour, impressions, clicks, revenue
        FROM public.hourly_stats
        ORDER BY date, hour
        LIMIT 168;
    ''').get_json()
    # try:
    #     return render_template('stats_hourly.html', title='stats/hourly',s_h= s_h)
    # except Exception as e:
    #     return render_template("error_handler/500.html",error=str(e))
    return rate_limit('stats_hourly.html',title,time_list,stats_hourly_counter,s_h,extra_data="nothing")

@app.route('/stats/daily')
def stats_daily():
    title='/stats/daily'
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
    # try:    
    #     return render_template('stats_daily.html', title='stats/daily',s_d= s_d)
    # except Exception as e:
    #     return render_template("error_handler/500.html",error=str(e))
    return rate_limit('stats_daily.html',title,time_list,stats_daily_counter,s_d,extra_data="nothing")

@app.route('/poi')
def poi():
    title='/poi'
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
    # try:
    #     return render_template('poi.html',title="poi",locations=locations,new_table=new_table)
    # except Exception as e:
    #     return render_template("error_handler/500.html",error=str(e))
    return rate_limit('poi.html',title,time_list,poi_counter,data=locations,extra_data=new_table)

app.run(processes = 8)

def queryHelper(query):
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return jsonify([dict(row.items()) for row in result])
