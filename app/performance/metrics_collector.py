import csv,time,os
class MetricsCollector:
    def __init__(self,path='data/performance_metrics.csv'):
        self.path=path; self.rows=[]
    def record(self,row): self.rows.append(row)
    def save(self):
        if not self.rows:return
        os.makedirs(os.path.dirname(self.path),exist_ok=True)
        with open(self.path,'w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=self.rows[0].keys());w.writeheader();w.writerows(self.rows)
