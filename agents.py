import csv,io,math
from datetime import datetime
from collections import defaultdict

class TrafficDataAgent:
    def run(self,source):
        rows=list(csv.DictReader(io.StringIO(source)));out=[];seen=set()
        if not rows or len(rows)>10000:raise ValueError('Provide 1 to 10,000 CSV rows.')
        for i,r in enumerate(rows,2):
            try:
                timestamp=datetime.fromisoformat(r['timestamp']).isoformat()
                names={k:r[k].strip() for k in ('junction','approach','route')}
                values={k:float(r[k]) for k in ('vehicles','duration_minutes','lanes','avg_speed_kmph')}
                if not all(names.values()) or not all(math.isfinite(v) for v in values.values()):raise ValueError()
                if values['vehicles']<0 or not values['vehicles'].is_integer() or values['duration_minutes']<=0 or values['lanes']<1 or not values['lanes'].is_integer() or values['avg_speed_kmph']<0:raise ValueError()
                key=(timestamp,names['junction'],names['approach'])
                if key in seen:raise ValueError()
                seen.add(key);out.append({'timestamp':timestamp,**names,**values})
            except (KeyError,ValueError):raise ValueError(f'Row {i}: check required fields, ISO timestamp, integer vehicle counts and lanes, positive duration, and duplicates.')
        return out

class ContextAgent:
    def run(self,weather,event):
        if weather not in ('clear','rain','heavy rain','fog'):raise ValueError('Select a supported weather condition.')
        event=float(event)
        if not math.isfinite(event) or not 0<=event<=100:raise ValueError('Event demand increase must be 0–100%.')
        return {'weather':weather,'capacity_factor':{'clear':1,'rain':.85,'heavy rain':.7,'fog':.75}[weather],'event_increase_percent':event}

class CongestionAgent:
    def run(self,rows,context):
        groups=defaultdict(list)
        for r in rows:groups[(r['junction'],r['approach'],r['route'])].append(r)
        out=[]
        for (junction,approach,route),readings in groups.items():
            count=sum(r['vehicles'] for r in readings);minutes=sum(r['duration_minutes'] for r in readings)
            lane_minutes=sum(r['lanes']*r['duration_minutes'] for r in readings)
            flow=count*60/lane_minutes
            adjusted=flow*(1+context['event_increase_percent']/100)
            proxy=adjusted/(900*context['capacity_factor'])
            speed=sum(r['avg_speed_kmph']*r['duration_minutes'] for r in readings)/minutes
            out.append({'junction':junction,'approach':approach,'route':route,'observed_vehicles':count,'flow_per_lane_hour':round(flow,1),'demand_per_lane_hour':round(adjusted,1),'average_speed':round(speed,1),'load_proxy':round(proxy,3),'status':'high' if proxy>=1 else 'moderate' if proxy>=.65 else 'low'})
        return out

class SignalAgent:
    def run(self,traffic,cycle):
        cycle=float(cycle)
        if not math.isfinite(cycle) or not 40<=cycle<=180:raise ValueError('Cycle must be 40–180 seconds.')
        groups=defaultdict(list)
        for r in traffic:groups[r['junction']].append(r)
        plans=[]
        for junction,rows in groups.items():
            # Treat each supplied approach as a separate illustrative phase.
            n=len(rows);lost=4*n;budget=cycle-lost
            if budget<10*n:raise ValueError(f'{junction}: cycle too short for {n} assumed phases and 10-second minimum greens.')
            total=sum(r['demand_per_lane_hour'] for r in rows)
            remaining=budget-10*n
            phases=[{'approach':r['approach'],'green_seconds':round(10+remaining*(r['demand_per_lane_hour']/total if total else 1/n),2)} for r in rows]
            phases[-1]['green_seconds']=round(budget-sum(p['green_seconds'] for p in phases[:-1]),2)
            plans.append({'junction':junction,'cycle_seconds':cycle,'assumed_lost_seconds':lost,'phases':phases})
        return plans

class RouteAgent:
    def run(self,traffic):
        routes=defaultdict(list)
        for r in traffic:routes[r['route']].append(r['load_proxy'])
        return [{'route':k,'mean_load_proxy':round(sum(v)/len(v),3),'sampled_segments':len(v)} for k,v in sorted(routes.items(),key=lambda x:sum(x[1])/len(x[1]))]

def analyze(source,weather='clear',event=0,cycle=90):
    rows=TrafficDataAgent().run(source);context=ContextAgent().run(weather,event)
    traffic=CongestionAgent().run(rows,context);signals=SignalAgent().run(traffic,cycle);routes=RouteAgent().run(traffic)
    return {'context':context,'traffic':traffic,'signals':signals,'routes':routes,'total_vehicles':sum(r['vehicles'] for r in rows),'trace':[f'TrafficDataAgent validated {len(rows)} intervals','ContextAgent applied user-supplied weather and event scenarios','CongestionAgent aggregated approach demand','SignalAgent allocated illustrative green times','RouteAgent ranked supplied candidate routes'],'limitations':'Educational advisory simulation. Weather factors and 900 vehicles/hour/lane reference are illustrative assumptions, not calibrated road capacity. Load proxy is not measured congestion or true volume-to-capacity ratio. Signal phases assume one phase per supplied approach, four seconds lost per phase, and ten seconds minimum green; pedestrian timings, turning conflicts, queues, and road geometry are not modeled. No traffic controls are changed. Route ranking uses sampled load averages, not navigation, travel times, or a connected road network; compare only routes serving the same origin and destination with equivalent coverage. Supply complete comparable intervals and avoid overlap. No live weather, event, or traffic feeds are used.'}
