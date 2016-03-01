# github.com/PurelyApplied/rsine_hash_and_cache

r.sine.com generates random content, presumably using some php
scripting to present a random item from its library.  (Named items can
be statically resolved at r.sine.com/[name].)

This script requests a page from r.sine.com, hashes the content, and
comparse the hash against its cache.  If the hash is not present, the
content is saved.

In addition, the number of successful downloads, failed downloads, and
colliding hashes are recorded.  Hash collisions are surprisingly rare,
indicating an expansive library on r.sine.com.
