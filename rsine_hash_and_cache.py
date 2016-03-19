#!/usr/bin/python3
'''Repeatedly accesses r.sine.com and considers the content.
Content is hashed and compared against an existing library.
If it is new, it is saved.  If not, the collision is noted.'''

try:
    import magic
except:
    print("Could not import file magic.",
          "All files will have extension 'unknown'")

import os, sys, time
import urllib.request as req
import argparse

#%%
def main(passes=100, delay=5):
    D = Data(cache="cache")
    try:
        for i in range(passes):
            fetch_one(D, delay)
    except Exception as e:
        print("Critical failure", e, file=sys.stderr)
    print(D.data(), file=sys.stderr)

def fetch_one(D, delay=0):
    try:
        print(D, file=sys.stderr)
        content = fetch_content()
        assert content, "Could not fetch content."
        process_page(content, D)
    except Exception as ex:
        D.failure += 1
        print("Handling error,", ex, file=sys.stderr)
    time.sleep(delay)

#%%
def fetch_content(attempts=1):
    for i in range(attempts):
        try:
            page = req.urlopen("https://r.sine.com")
            assert page.code == 200, "Fetched page did not return with code 200"
            return page.read()
        except Exception as e:
            print("Attempt {} (of max {}) to fetch page failed.\n".format(i+1, attempts),
                  "Failure: {}\n".format(e),
                  file=sys.stderr)
    print("Maximum failures reached.  Returning None.",
          file=sys.stderr)
    return None

#%%
def get_extension(content):
    try:
        with magic.Magic() as M:
            return "." + M.id_buffer(content).split()[0].lower()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        return ".unknown"

_hex_len = len(hex(sys.maxsize))
def myHash(content):
    '''We use a modified hash function to convert content into an
    indentifying string.  Content is hashed using Python's standard
    hashing function.  This is converted to hex for shorter strings
    and, well, because hex.  On *nix machines, files with a leading
    negative are an annoyance.  To this end, we prepend the string
    \"rs\" to the hash key.  Additionally, for uniformity in file
    length, we prepend zeros on short keys and add \"+\" to those
    hashs that are positive.

    '''

    n = hash(content)
    key = hex(n)
    if not key[0] == "-":
        key = "+" + key
    if len(key) < _hex_len + 1:
        # [+-]0x[key]
        key = key[:3] + "0" * (_hex_len + 1 - len(key)) + key[3:]
    key = "rs" + key
    return key

#%%
def process_page(content, D):
    key = myHash(content)
    if D.has(key):
        D.collide += 1
        D.time_to_collide.append(D.since_last_collision)
        D.since_last_collision = 0
        print("%%%%%%%%%%\n",D.data(),"%%%%%%%%%%", file=sys.stderr)
    else:
        D.add(key)
        D.success += 1
        D.since_last_collision += 1
        open("cache/{}{}".format(key, get_extension(content)),
             "wb").write(content)

class Data:
    def __init__(self, cache=None):
        self.success=0
        self.collide=0
        self.failure=0
        self.since_last_collision=0
        self.time_to_collide = []
        self.cache = set()
        if cache:
            self.load(cache)

    def __repr__(self):
        return "<Data +{}/-{}/!{}/n{}/t{}>".format(
            self.success,
            self.collide,
            self.failure,
            len(self.cache),
            self.since_last_collision)

    def has(self, key):
        return (str(key) in self.cache)

    def add(self, key):
        self.cache.add(key)

    def load(self, folder):
        files = os.listdir(folder)
        keys = [ f.split('.')[0] for f in files if f[:2] == "rs" ]
        self.cache.update(keys)

    def data(self):
        s  = "Failure: {}\n".format(self.failure)
        s += "Success: {}\n".format(self.success)
        s += "Collide: {}\n".format(self.collide)
        s += "Average time to collision: {}\n".format( sum(self.time_to_collide) / len(self.time_to_collide))
        s += "Recent Collisions: {}\n".format(self.time_to_collide[-5:])
        s += "Recent average: {}\n".format( sum(self.time_to_collide[-5:]) / len(self.time_to_collide[-5:]))
        return s



if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("delay",
                       help="Delay between http calls; increase to keep bandwidth low.",
                       type=int)
    parse.add_argument("passes",
                       help="Number of download attempts to make.",
                       type=int)
    args = parse.parse_args()
    print("Current working directory:", os.getcwd(), file=sys.stderr)
    print("main(delay={}, passes={})".format(args.delay, args.passes), file=sys.stderr)
    main(args.delay, args.passes)
