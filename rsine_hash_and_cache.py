#!/usr/bin/python3
'''Repeatedly accesses r.sine.com and considers the content.
Content is hashed and compared against an existing library.
If it is new, it is saved.  If not, the collision is noted.'''


import os, time
import urllib.request as req

class Data:
    def __init__(self):
        self.success=0
        self.collide=0
        self.failure=0
        self.since_last_collision=0
        self.time_to_collide = []
        self.cache = set()
    
    def __repr__(self):
        return "<Data +{}/-{}/!{}/n{}/t{}>".format(self.success, self.collide, self.failure, len(self.cache), self.since_last_collision)

    def has(self, key):
        return (str(key) in self.cache)
    
    def add(self, key):
        self.cache.add(key)
    
    def load(self, folder):
        self.cache.update(os.listdir(folder))
            
    def data(self):
        s  = "Failure: {}\n".format(self.failure)
        s += "Success: {}\n".format(self.success)
        s += "Collide: {}\n".format(self.collide)
        s += "Average time to collision: {}\n".format( sum(self.time_to_collide) / len(self.time_to_collide))
        s += "Recent Collisions: {}\n".format(self.time_to_collide[-5:])
        s += "Recent average: {}\n".format( sum(self.time_to_collide[-5:]) / len(self.time_to_collide[-5:]))
        return s
    

#%%
def main(delay=5, repeat=1000000):
    print("Current working directory:", os.getcwd())
    try:
        D = Data()
        D.load("cache")
        for i in range(repeat):
            try:
                print(D)
                page = req.urlopen("https://r.sine.com")                        
                if page.code == 200:
                    process_page(page, D)
                else:
                    D.failure += 1
            except Exception as ex:
                D.failure += 1
                print("Handling error,", ex)
            time.sleep(delay)
    except Exception as e:
        print("Critical failure", e)
    open("metric.txt", "w").write(D.data())

#%%
def process_page(page, D):
    content = page.read()
    key = hash(content)
    if D.has(key):
        D.collide += 1
        D.time_to_collide.append(D.since_last_collision)
        D.since_last_collision = 0
        print("%%%%%%%%%%\n",D.data(),"%%%%%%%%%%")
    else:
        D.add(key)
        D.success += 1
        D.since_last_collision += 1
        open("cache/{}".format(key), "wb").write(content)


def hash_to_filename(h):
    