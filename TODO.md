## For the channel loader:

- [x] collect fwd from id, title
- [ ] collect fwd from name handle
- [ ] add mentions
- [ ] try and get entities from the message itself to avoid reaching the limit (or use asincio await)
- [ ] do some refactoring (with handler function)
- [ ] set variable source for channels list 

## For the network analysis

- [ ] compiling the motivated list of seed channels
- [ ] building the weighted directed graph (calculate betweenness?)
- [ ] take a closer look at https://global.oup.com/academic/product/networks-9780198805090
- [ ] explore https://networkx.org/, https://github.com/swamiiyer/robustness (for betweenness)
- [ ] collect 3? cascades of references, estimate the spread
- [ ] distill the research data on main algos for maximizing the influence
- [ ] implement and finalize the dataset
